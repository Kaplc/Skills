#!/usr/bin/env python3
"""
Task MCP Server
提供任务生成和执行相关的工具
"""

import json
import os
import re
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# MCP Server 基础库
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    from mcp.server.server import NotificationOptions
    import mcp.server.stdio
except ImportError:
    print("需要安装 mcp: pip install mcp", file=__import__('sys').stderr)
    raise

# ============ 配置 ============

SERVER_NAME = "task-mcp-server"
SERVER_VERSION = "1.0.0"

# 默认工作目录
DEFAULT_WORKSPACE = Path.cwd()

# ============ 辅助函数 ============

def load_tasks_json(tasks_path: Path) -> dict:
    """加载任务 JSON 文件"""
    if not tasks_path.exists():
        raise FileNotFoundError(f"任务文件不存在: {tasks_path}")
    with open(tasks_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks_json(tasks_path: Path, data: dict):
    """保存任务 JSON 文件"""
    with open(tasks_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_next_pending_task(tasks_data: dict) -> Optional[dict]:
    """获取下一个可执行的任务（依赖都已完成）"""
    completed_ids = {t['taskId'] for t in tasks_data.get('tasks', []) if t.get('status') == 'completed'}
    blocked_ids = {t['taskId'] for t in tasks_data.get('tasks', []) if t.get('status') == 'blocked'}

    for task in tasks_data.get('tasks', []):
        if task.get('status') != 'pending':
            continue

        deps = task.get('dependencies', [])
        if any(dep not in completed_ids for dep in deps):
            # 有依赖未完成，标记为 blocked
            if task['taskId'] not in blocked_ids:
                task['status'] = 'blocked'
                task['blockReason'] = f"等待依赖: {[d for d in deps if d not in completed_ids]}"
            continue

        # 检查依赖已完成，任务是 pending
        if task['taskId'] in blocked_ids:
            task['status'] = 'pending'
            task.pop('blockReason', None)

        return task

    return None

def check_acceptance_criteria(criteria: list, workspace: Path) -> tuple[bool, list]:
    """检查验收标准"""
    results = []

    for criterion in criteria:
        criterion_type = criterion.get('type')
        passed = False
        evidence = ""

        try:
            if criterion_type == 'file_exists':
                path = workspace / criterion['path']
                passed = path.exists()
                evidence = f"{'存在' if passed else '不存在'}: {criterion['path']}"

            elif criterion_type == 'file_not_exists':
                path = workspace / criterion['path']
                passed = not path.exists()
                evidence = f"{'已删除' if passed else '仍存在'}: {criterion['path']}"

            elif criterion_type == 'has_class':
                path = workspace / criterion['file']
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    class_pattern = rf"class\s+{criterion['class']}\s*[:<]"
                    passed = bool(re.search(class_pattern, content))
                    evidence = f"{'找到' if passed else '未找到'}类 {criterion['class']}"
                else:
                    evidence = f"文件不存在: {criterion['file']}"

            elif criterion_type == 'has_method':
                path = workspace / criterion['file']
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    method = criterion['method']
                    if criterion.get('signature'):
                        passed = criterion['signature'] in content
                        evidence = f"{'找到' if passed else '未找到'}方法签名: {criterion['signature']}"
                    else:
                        # 简单匹配方法名
                        pattern = rf"(public|private|protected|internal)?\s+(static)?\s*\w+\s+{method}\s*\("
                        passed = bool(re.search(pattern, content))
                        evidence = f"{'找到' if passed else '未找到'}方法: {method}"
                else:
                    evidence = f"文件不存在: {criterion['file']}"

            elif criterion_type == 'has_field':
                path = workspace / criterion['file']
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    field = criterion['field']
                    pattern = rf"(public|private|protected|internal)?\s+(static)?\s*\w+\s+{field}\s*;"
                    passed = bool(re.search(pattern, content))
                    evidence = f"{'找到' if passed else '未找到'}字段: {field}"
                else:
                    evidence = f"文件不存在: {criterion['file']}"

            elif criterion_type == 'contains':
                path = workspace / criterion['file']
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    passed = criterion['pattern'] in content
                    evidence = f"{'包含' if passed else '不包含'}: {criterion['pattern']}"
                else:
                    evidence = f"文件不存在: {criterion['file']}"

            elif criterion_type == 'compiles':
                # 尝试编译项目
                result = subprocess.run(
                    ['dotnet', 'build'],
                    cwd=workspace,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                passed = result.returncode == 0
                evidence = f"编译{'成功' if passed else '失败'}: {result.stdout[:200] if not passed else 'OK'}"

            elif criterion_type == 'command_success':
                result = subprocess.run(
                    criterion.get('command', 'echo test'),
                    cwd=criterion.get('workingDirectory', workspace),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                passed = result.returncode == 0
                evidence = f"命令{'成功' if passed else '失败'}: {result.stdout[:100] if not passed else 'OK'}"

        except Exception as e:
            passed = False
            evidence = f"检查失败: {str(e)}"

        results.append({
            'type': criterion_type,
            'description': criterion.get('description', ''),
            'passed': passed,
            'evidence': evidence
        })

    all_passed = all(r['passed'] for r in results)
    return all_passed, results

# ============ MCP 工具定义 ============

# 工具列表
TOOLS = [
    Tool(
        id="task_generate",
        name="task_generate",
        description="从思路文档生成任务 JSON（供 task-documentor 使用）",
        inputSchema={
            "type": "object",
            "properties": {
                "idea_doc_path": {
                    "type": "string",
                    "description": "思路文档路径（绝对路径）"
                },
                "output_path": {
                    "type": "string",
                    "description": "输出任务 JSON 路径（绝对路径）"
                }
            },
            "required": ["idea_doc_path", "output_path"]
        }
    ),
    Tool(
        id="task_get_next",
        name="task_get_next",
        description="获取下一个可执行的任务",
        inputSchema={
            "type": "object",
            "properties": {
                "tasks_json_path": {
                    "type": "string",
                    "description": "任务 JSON 文件路径"
                }
            },
            "required": ["tasks_json_path"]
        }
    ),
    Tool(
        id="task_update_status",
        name="task_update_status",
        description="更新任务状态",
        inputSchema={
            "type": "object",
            "properties": {
                "tasks_json_path": {
                    "type": "string",
                    "description": "任务 JSON 文件路径"
                },
                "task_id": {
                    "type": "string",
                    "description": "任务 ID"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed", "cancelled", "blocked"],
                    "description": "新状态"
                },
                "notes": {
                    "type": "string",
                    "description": "备注信息"
                }
            },
            "required": ["tasks_json_path", "task_id", "status"]
        }
    ),
    Tool(
        id="task_execute_step",
        name="task_execute_step",
        description="执行任务的单个步骤",
        inputSchema={
            "type": "object",
            "properties": {
                "task": {
                    "type": "object",
                    "description": "任务对象"
                },
                "step_order": {
                    "type": "integer",
                    "description": "要执行的步骤序号"
                },
                "workspace_path": {
                    "type": "string",
                    "description": "工作区路径"
                }
            },
            "required": ["task", "step_order", "workspace_path"]
        }
    ),
    Tool(
        id="task_check_acceptance",
        name="task_check_acceptance",
        description="检查任务验收标准",
        inputSchema={
            "type": "object",
            "properties": {
                "tasks_json_path": {
                    "type": "string",
                    "description": "任务 JSON 文件路径"
                },
                "task_id": {
                    "type": "string",
                    "description": "任务 ID"
                },
                "workspace_path": {
                    "type": "string",
                    "description": "工作区路径"
                }
            },
            "required": ["tasks_json_path", "task_id", "workspace_path"]
        }
    ),
    Tool(
        id="task_get_summary",
        name="task_get_summary",
        description="获取任务执行摘要",
        inputSchema={
            "type": "object",
            "properties": {
                "tasks_json_path": {
                    "type": "string",
                    "description": "任务 JSON 文件路径"
                }
            },
            "required": ["tasks_json_path"]
        }
    )
]

# ============ 工具实现 ============

def task_generate(idea_doc_path: str, output_path: str) -> dict:
    """
    从思路文档生成任务 JSON
    这是一个占位实现，实际由 Skill 读取思路文档并生成 JSON
    """
    return {
        "success": False,
        "message": "task_generate 应由 task-documentor Skill 调用。直接使用 task_parse_and_save 从思路文档生成任务 JSON。",
        "todo": "需要在 Skill 层面实现文档解析"
    }

def task_get_next(tasks_json_path: str) -> dict:
    """获取下一个可执行的任务"""
    try:
        tasks_path = Path(tasks_json_path)
        data = load_tasks_json(tasks_path)

        task = get_next_pending_task(data)
        if task:
            save_tasks_json(tasks_path, data)
            return {
                "success": True,
                "task": task,
                "hasMore": True
            }
        else:
            return {
                "success": True,
                "task": None,
                "hasMore": False,
                "message": "没有更多可执行的任务"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

def task_update_status(tasks_json_path: str, task_id: str, status: str, notes: str = "") -> dict:
    """更新任务状态"""
    try:
        tasks_path = Path(tasks_json_path)
        data = load_tasks_json(tasks_path)

        task = next((t for t in data['tasks'] if t['taskId'] == task_id), None)
        if not task:
            return {"success": False, "error": f"找不到任务: {task_id}"}

        old_status = task.get('status')
        task['status'] = status

        if status == 'completed':
            task['completedAt'] = datetime.now().isoformat()
        if notes:
            task['notes'] = notes

        save_tasks_json(tasks_path, data)

        return {
            "success": True,
            "taskId": task_id,
            "oldStatus": old_status,
            "newStatus": status,
            "completedAt": task.get('completedAt')
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def task_execute_step(task: dict, step_order: int, workspace_path: str) -> dict:
    """执行任务的单个步骤"""
    try:
        workspace = Path(workspace_path)
        step = next((s for s in task.get('steps', []) if s['order'] == step_order), None)

        if not step:
            return {"success": False, "error": f"找不到步骤: {step_order}"}

        action = step.get('action')
        description = step.get('description', '')

        if action == 'create_file':
            file_path = workspace / step['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(step.get('content', ''), encoding='utf-8')
            return {"success": True, "action": action, "path": str(file_path), "description": description}

        elif action == 'add_code':
            target_path = workspace / step['target']
            if not target_path.exists():
                return {"success": False, "error": f"目标文件不存在: {step['target']}"}

            content = target_path.read_text(encoding='utf-8')
            code = step.get('code', '')
            location = step.get('location', 'class_body')

            if location == 'class_body':
                # 在类末尾添加
                # 找到最后一个 } 之前插入
                last_brace = content.rfind('}')
                if last_brace != -1:
                    content = content[:last_brace] + '\n' + code + '\n' + content[last_brace:]
                else:
                    content += '\n' + code

            elif location.startswith('method:'):
                # 在方法内部添加
                method_name = location.split(':')[1]
                pattern = rf'({method_name}\s*\([^)]*\)\s*{{)'
                match = re.search(pattern, content)
                if match:
                    insert_pos = match.end()
                    content = content[:insert_pos] + '\n' + code + '\n' + content[insert_pos:]

            target_path.write_text(content, encoding='utf-8')
            return {"success": True, "action": action, "target": step['target'], "description": description}

        elif action == 'edit_code':
            target_path = workspace / step['target']
            if not target_path.exists():
                return {"success": False, "error": f"目标文件不存在: {step['target']}"}

            content = target_path.read_text(encoding='utf-8')
            old_code = step.get('find', '')
            new_code = step.get('replace', '')

            if old_code not in content:
                return {"success": False, "error": f"未找到要替换的代码: {old_code[:50]}..."}

            content = content.replace(old_code, new_code)
            target_path.write_text(content, encoding='utf-8')
            return {"success": True, "action": action, "target": step['target'], "description": description}

        elif action == 'delete_file':
            file_path = workspace / step['path']
            if file_path.exists():
                file_path.unlink()
            return {"success": True, "action": action, "path": str(file_path), "description": description}

        elif action == 'run_command':
            cmd = step.get('command', '')
            cwd = Path(step.get('workingDirectory', workspace))
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "action": action,
                    "command": cmd,
                    "error": result.stderr or result.stdout,
                    "returncode": result.returncode
                }

            return {
                "success": True,
                "action": action,
                "command": cmd,
                "returncode": result.returncode,
                "stdout": result.stdout[:500] if result.stdout else "",
                "description": description
            }

        elif action == 'create_directory':
            dir_path = workspace / step['path']
            dir_path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "action": action, "path": str(dir_path), "description": description}

        elif action == 'write_json':
            file_path = workspace / step['path']
            file_path.parent.mkdir(parents=True, exist_ok=True)
            data = step.get('data', {})
            file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
            return {"success": True, "action": action, "path": str(file_path), "description": description}

        else:
            return {"success": False, "error": f"未知 action: {action}"}

    except Exception as e:
        return {"success": False, "error": str(e)}

def task_check_acceptance(tasks_json_path: str, task_id: str, workspace_path: str) -> dict:
    """检查任务验收标准"""
    try:
        tasks_path = Path(tasks_json_path)
        data = load_tasks_json(tasks_path)

        task = next((t for t in data['tasks'] if t['taskId'] == task_id), None)
        if not task:
            return {"success": False, "error": f"找不到任务: {task_id}"}

        workspace = Path(workspace_path)
        criteria = task.get('acceptanceCriteria', [])

        all_passed, results = check_acceptance_criteria(criteria, workspace)

        return {
            "success": True,
            "taskId": task_id,
            "allPassed": all_passed,
            "results": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def task_get_summary(tasks_json_path: str) -> dict:
    """获取任务执行摘要"""
    try:
        data = load_tasks_json(Path(tasks_json_path))

        tasks = data.get('tasks', [])
        total = len(tasks)
        completed = sum(1 for t in tasks if t.get('status') == 'completed')
        in_progress = sum(1 for t in tasks if t.get('status') == 'in_progress')
        pending = sum(1 for t in tasks if t.get('status') == 'pending')
        blocked = sum(1 for t in tasks if t.get('status') == 'blocked')
        cancelled = sum(1 for t in tasks if t.get('status') == 'cancelled')

        total_time = sum(t.get('estimatedMinutes', 0) for t in tasks)
        completed_time = sum(t.get('estimatedMinutes', 0) for t in tasks if t.get('status') == 'completed')

        return {
            "success": True,
            "summary": {
                "total": total,
                "completed": completed,
                "inProgress": in_progress,
                "pending": pending,
                "blocked": blocked,
                "cancelled": cancelled,
                "progressPercent": round(completed / total * 100, 1) if total > 0 else 0,
                "totalEstimatedMinutes": total_time,
                "completedMinutes": completed_time,
                "remainingMinutes": total_time - completed_time
            },
            "modules": data.get('modules', [])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============ MCP Server 主循环 ============

async def main():
    """MCP Server 主循环"""
    server = Server(SERVER_NAME)

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result: dict

        if name == "task_generate":
            result = task_generate(
                idea_doc_path=arguments.get("idea_doc_path", ""),
                output_path=arguments.get("output_path", "")
            )

        elif name == "task_get_next":
            result = task_get_next(
                tasks_json_path=arguments.get("tasks_json_path", "")
            )

        elif name == "task_update_status":
            result = task_update_status(
                tasks_json_path=arguments.get("tasks_json_path", ""),
                task_id=arguments.get("task_id", ""),
                status=arguments.get("status", ""),
                notes=arguments.get("notes", "")
            )

        elif name == "task_execute_step":
            result = task_execute_step(
                task=arguments.get("task", {}),
                step_order=arguments.get("step_order", 1),
                workspace_path=arguments.get("workspace_path", "")
            )

        elif name == "task_check_acceptance":
            result = task_check_acceptance(
                tasks_json_path=arguments.get("tasks_json_path", ""),
                task_id=arguments.get("task_id", ""),
                workspace_path=arguments.get("workspace_path", "")
            )

        elif name == "task_get_summary":
            result = task_get_summary(
                tasks_json_path=arguments.get("tasks_json_path", "")
            )

        else:
            result = {"success": False, "error": f"未知工具: {name}"}

        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]

    options = NotificationOptions(
        tools_changed=True
    )
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(options)
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
