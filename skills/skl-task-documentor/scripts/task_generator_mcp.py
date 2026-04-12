#!/usr/bin/env python3
"""
Task Generator MCP - 生成任务 JSON

使用 FastMCP 框架
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from fastmcp import FastMCP
except ImportError:
    print("需要安装 fastmcp: pip install fastmcp", file=__import__('sys').stderr)
    raise

# 创建 MCP Server
mcp = FastMCP("task-generator-mcp")

# ============ 工具实现 ============

@mcp.tool()
def parse_idea_doc(idea_doc_path: str) -> dict:
    """
    解析思路文档，提取任务信息

    Args:
        idea_doc_path: 思路文档的绝对路径

    Returns:
        解析结果，包含 plan_name, modules, tasks
    """
    path = Path(idea_doc_path)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {idea_doc_path}"}

    content = path.read_text(encoding='utf-8')

    # 提取方案名称
    plan_name = extract_plan_name(content)

    # 提取模块划分
    modules = extract_modules(content)

    # 提取实现步骤
    tasks = extract_steps(content, modules)

    return {
        "success": True,
        "planName": plan_name,
        "sourceDocument": idea_doc_path,
        "modules": modules,
        "tasks": tasks
    }

def extract_plan_name(content: str) -> str:
    """提取方案名称"""
    # 匹配 ### 4.1 方案名称 **xxx** 或 ## 4.1 方案名称 **xxx**
    patterns = [
        r'#+\s*\d+\.\d+\s*方案名称\s*\*\*([^\*]+)\*\*',
        r'#+\s*\d+\.\d+\s*方案名称\s*([^\n\*]+)',
        r'方案名称[：:]\s*([^\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    return "未命名方案"

def extract_modules(content: str) -> list:
    """提取模块划分"""
    modules = []

    # 查找模块划分相关章节（允许中间有空行）
    section_match = re.search(r'#+\s*\d+\.\d+\s*模块划分[^\n]*\n+((?:\|[^\n]+\n)+)', content, re.DOTALL)
    if section_match:
        lines = section_match.group(1).strip().split('\n')
        for line in lines:
            # 跳过分隔符行 |---|---|
            if re.match(r'\|[-:\s]+\|', line):
                continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            # 跳过表头行
            if len(cells) >= 2 and any(k in cells[0] or k in cells[1] for k in ['模块', 'Module', '名称', 'Name', '职责', 'Responsibility']):
                continue
            if len(cells) >= 2:
                modules.append({
                    "name": cells[0],
                    "responsibility": cells[1],
                    "dependencies": []
                })

    return modules

def extract_steps(content: str, modules: list) -> list:
    """提取实现步骤"""
    tasks = []
    task_id = 1

    # 查找实现步骤相关章节（允许中间有空行）
    section_match = re.search(r'#+\s*\d+\.\d+\s*实现步骤[^\n]*\n+((?:\|[^\n]+\n)+)', content, re.DOTALL)
    if section_match:
        lines = section_match.group(1).strip().split('\n')
        for line in lines:
            # 跳过分隔符行 |------|------|
            if re.match(r'\|[-:\s]+\|', line):
                continue
            cells = [c.strip() for c in line.split('|') if c.strip()]
            # 跳过表头行（包含 序号、步骤名称 等关键词）
            if len(cells) >= 2 and any(k in cells[0] or k in cells[1] for k in ['序号', '步骤', 'Seq', 'Step']):
                continue
            if len(cells) >= 3:
                step_name = cells[1]
                step_desc = cells[2] if len(cells) > 2 else ""
                module = detect_module_for_step(step_name, step_desc, modules)
                checks = generate_checks(step_name, step_desc)

                tasks.append({
                    "id": f"T-{task_id:03d}",
                    "goal": f"{step_name}：{step_desc}",
                    "module": module,
                    "acceptance": {
                        "passed": False,
                        "checks": checks,
                        "failedReason": None
                    }
                })
                task_id += 1

    # 如果没找到表格，尝试用编号列表
    if not tasks:
        # 匹配 "1. xxx" 或 "1) xxx" 格式
        for match in re.finditer(r'(?:^|\n)\s*(\d+)[.、)]\s*([^\n]+)', content):
            step_name = match.group(2).strip()
            if len(step_name) > 2:
                module = modules[0]["name"] if modules else "Main"
                checks = generate_checks(step_name, "")
                tasks.append({
                    "id": f"T-{task_id:03d}",
                    "goal": step_name,
                    "module": module,
                    "acceptance": {
                        "passed": False,
                        "checks": checks,
                        "failedReason": None
                    }
                })
                task_id += 1

    return tasks

def detect_module_for_step(step_name: str, step_desc: str, modules: list) -> str:
    """根据步骤推断所属模块"""
    text = (step_name + " " + step_desc).lower()
    for module in modules:
        name_lower = module["name"].lower()
        # 去除常见后缀
        key = name_lower.replace("manager", "").replace("handler", "").replace("module", "").strip()
        if key and key in text:
            return module["name"]
    return modules[0]["name"] if modules else "Main"

def generate_checks(step_name: str, step_desc: str) -> list:
    """根据步骤生成验收检查项"""
    checks = []
    text = (step_name + " " + step_desc).lower()

    if any(k in step_name for k in ["创建", "新建", "新增"]):
        checks.append("操作已执行")
        if ".cs" in text or "类" in text or "class" in text:
            checks.append("文件已创建")
            checks.append("编译通过")
        if "方法" in step_name or "method" in text:
            checks.append("方法已添加")
    elif any(k in step_name for k in ["添加", "实现", "加入"]):
        checks.append("代码已添加")
        checks.append("编译通过")
    elif any(k in step_name for k in ["修改", "更新", "调整"]):
        checks.append("代码已修改")
        checks.append("编译通过")
    elif any(k in step_name for k in ["配置", "设置", "注册"]):
        checks.append("配置已生效")
    else:
        checks.append("步骤执行完成")

    if not checks:
        checks.append("步骤执行完成")

    return checks

@mcp.tool()
def generate_tasks_json(idea_doc_path: str, output_dir: Optional[str] = None) -> dict:
    """
    解析思路文档并生成 tasks.json

    Args:
        idea_doc_path: 思路文档路径
        output_dir: 输出目录（默认与思路文档同目录）

    Returns:
        生成结果，包含 output_path
    """
    parse_result = parse_idea_doc(idea_doc_path)
    if not parse_result.get("success"):
        return parse_result

    timestamp = datetime.now().strftime("%Y%m%d")

    tasks_json = {
        "planName": parse_result["planName"],
        "generatedAt": datetime.now().isoformat(),
        "tasks": parse_result["tasks"]
    }

    idea_path = Path(idea_doc_path)
    plan_name_safe = re.sub(r'[^\w\u4e00-\u9fff-]', '_', parse_result['planName'])
    if output_dir:
        output_path = Path(output_dir) / f"tasks_{plan_name_safe}_{timestamp}.json"
    else:
        output_path = idea_path.parent / f"tasks_{plan_name_safe}_{timestamp}.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(tasks_json, ensure_ascii=False, indent=2), encoding='utf-8')

    return {
        "success": True,
        "outputPath": str(output_path),
        "planName": parse_result["planName"],
        "taskCount": len(parse_result["tasks"])
    }

# ============ 启动 ============

if __name__ == "__main__":
    mcp.run()
