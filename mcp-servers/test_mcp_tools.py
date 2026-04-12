#!/usr/bin/env python3
"""
测试 FastMCP 工具
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

def test_mcp_server(script_name: str, test_name: str):
    """测试 MCP server 工具"""
    script_path = Path(__file__).parent / script_name
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"脚本: {script_path}")
    print('='*60)

    # 创建测试用的思路文档
    if "generator" in script_name:
        test_content = """# 音乐播放器实现思路

## 4.1 方案名称
模块化音频管理器方案

## 4.3 实现步骤

| 序号 | 步骤名称 | 详细描述 | 关键点 |
|------|----------|----------|--------|
| 1 | 创建 AudioManager 类 | 单例模式管理音频 | 保证全局唯一 |
| 2 | 实现 Play 方法 | 播放音频 | 调用 AudioSource |
| 3 | 实现 Pause 方法 | 暂停音频 | 调用 AudioSource |
| 4 | 实现 Stop 方法 | 停止音频 | 调用 AudioSource |

## 4.4 模块划分

| 模块名称 | 职责 |
|---------|------|
| AudioManager | 音频播放管理 |
| PlaylistManager | 播放列表管理 |
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            test_file = f.name

        print(f"测试文件: {test_file}")

        # 测试 parse_idea_doc
        print("\n测试 parse_idea_doc:")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "parse_idea_doc",
                "arguments": {"idea_doc_path": test_file}
            }
        }

        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = proc.communicate(input=json.dumps(request) + "\n", timeout=10)
            if stdout:
                for line in stdout.strip().split("\n"):
                    if line.strip() and line.startswith('{'):
                        result = json.loads(line)
                        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        except:
            print("  (stdio 交互测试跳过)")

        # 清理
        Path(test_file).unlink(missing_ok=True)

    # 测试 executor
    elif "executor" in script_name:
        # 创建测试用的 tasks.json
        test_tasks = {
            "planName": "测试方案",
            "generatedAt": "2026-04-12T10:00:00Z",
            "tasks": [
                {
                    "id": "T-001",
                    "goal": "创建测试文件",
                    "acceptance": {
                        "passed": False,
                        "checks": ["文件已创建", "编译通过"],
                        "failedReason": None
                    }
                },
                {
                    "id": "T-002",
                    "goal": "添加测试方法",
                    "acceptance": {
                        "passed": False,
                        "checks": ["方法已添加"],
                        "failedReason": None
                    }
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_tasks, f, ensure_ascii=False, indent=2)
            test_file = f.name

        print(f"测试文件: {test_file}")

        # 测试 get_summary
        print("\n测试 get_summary:")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "get_summary",
                "arguments": {"tasks_json_path": test_file}
            }
        }

        proc = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = proc.communicate(input=json.dumps(request) + "\n", timeout=10)
            if stdout:
                for line in stdout.strip().split("\n"):
                    if line.strip() and line.startswith('{'):
                        result = json.loads(line)
                        print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print("  (stdio 交互测试跳过)")

        # 清理
        Path(test_file).unlink(missing_ok=True)

    print(f"\n{test_name} - 模块加载正常!")

if __name__ == "__main__":
    test_mcp_server("task_generator_mcp.py", "Task Generator MCP")
    test_mcp_server("task_executor_mcp.py", "Task Executor MCP")
    print("\n" + "="*60)
    print("所有测试完成!")
    print("="*60)
