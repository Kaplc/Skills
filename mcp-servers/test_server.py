#!/usr/bin/env python3
"""
测试 MCP Server 工具调用
"""

import json
import subprocess
import sys
from pathlib import Path

def send_request(cmd: list, request: dict) -> dict:
    """发送 JSON-RPC 请求到 MCP server"""
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    request_json = json.dumps(request) + "\n"
    stdout, stderr = proc.communicate(input=request_json, timeout=10)

    if stderr:
        print(f"STDERR: {stderr}", file=sys.stderr)

    if stdout:
        for line in stdout.strip().split("\n"):
            if line.strip():
                try:
                    return json.loads(line)
                except:
                    pass

    return {}

def test_server():
    """测试 MCP Server"""
    server_path = Path(__file__).parent / "task-mcp-server.py"

    # 测试 1: 列出工具
    print("=" * 50)
    print("测试 1: 列出工具 (list_tools)")
    print("=" * 50)

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }

    result = send_request(["python", str(server_path)], request)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 测试 2: 获取摘要 (用示例 tasks.json)
    print("\n" + "=" * 50)
    print("测试 2: 获取摘要 (task_get_summary)")
    print("=" * 50)

    # 创建测试用的 tasks.json
    test_tasks = {
        "planName": "测试方案",
        "generatedAt": "2026-04-12T10:00:00Z",
        "tasks": [
            {
                "id": "T-001",
                "goal": "创建测试文件",
                "acceptance": {
                    "passed": True,
                    "checks": ["文件已创建"],
                    "failedReason": None
                }
            },
            {
                "id": "T-002",
                "goal": "添加方法",
                "acceptance": {
                    "passed": False,
                    "checks": ["方法已添加"],
                    "failedReason": None
                }
            }
        ]
    }

    test_file = Path(__file__).parent / "test_tasks.json"
    test_file.write_text(json.dumps(test_tasks, ensure_ascii=False, indent=2), encoding='utf-8')

    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "task_get_summary",
            "arguments": {
                "tasks_json_path": str(test_file)
            }
        }
    }

    result = send_request(["python", str(server_path)], request)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 清理测试文件
    test_file.unlink(missing_ok=True)

    print("\n" + "=" * 50)
    print("测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    test_server()
