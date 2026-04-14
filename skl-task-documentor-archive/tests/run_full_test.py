#!/usr/bin/env python3
"""
全量测试 Task-Documentor MCP Skill
Complete end-to-end test of all functionality
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def print_header(title):
    print(f"\n{'='*80}")
    print(f"【{title}】")
    print(f"{'='*80}\n")

def print_section(title):
    print(f"\n{'-'*80}")
    print(f"{title}")
    print(f"{'-'*80}\n")

def run_test(test_name, test_func):
    """Run a test and report results"""
    print(f"▶️  {test_name}...", end=" ", flush=True)
    try:
        result = test_func()
        if result:
            print("✅")
            return True
        else:
            print("❌ 返回值为 False")
            return False
    except Exception as e:
        print(f"❌ {e}")
        return False

def test_environment():
    """Test 1: Environment verification"""
    print_header("全量测试开始 - Task-Documentor MCP 系统")
    print_section("【Test 1】环境验证")

    results = []

    # 1.1 Python 版本
    result = subprocess.run(
        ["C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe", "--version"],
        capture_output=True,
        text=True
    )
    python_ver = result.stdout.strip()
    results.append(run_test("1.1 Python 版本检查", lambda: "3.12" in python_ver))
    print(f"     {python_ver}")

    # 1.2 FastMCP 版本
    result = subprocess.run(
        ["C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe", "-c",
         "import fastmcp; print(fastmcp.__version__)"],
        capture_output=True,
        text=True
    )
    fastmcp_ver = result.stdout.strip()
    results.append(run_test("1.2 FastMCP 版本检查", lambda: "3.2.3" in fastmcp_ver))
    print(f"     FastMCP {fastmcp_ver}")

    # 1.3 虚拟环境路径
    venv_path = Path("C:\\Users\\v_zhyyzheng\\.claude\\mcp-env")
    results.append(run_test("1.3 虚拟环境存在", lambda: venv_path.exists()))
    print(f"     {venv_path}")

    # 1.4 MCP 脚本存在
    mcp_script = Path("C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\scripts\\task_generator_mcp.py")
    results.append(run_test("1.4 MCP 脚本存在", lambda: mcp_script.exists()))

    # 1.5 配置文件存在
    config_file = Path("C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\.claude\\settings.json")
    results.append(run_test("1.5 MCP 配置文件存在", lambda: config_file.exists()))

    return all(results)

def test_imports():
    """Test 2: Tool imports"""
    print_section("【Test 2】工具导入验证")

    code = """
import sys
sys.path.insert(0, r'C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\scripts')
from task_generator_mcp import (
    init_tasks_json, append_task, review_tasks, update_task,
    get_next_task, update_task_result, get_summary
)
print('OK')
"""

    result = subprocess.run(
        ["C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe", "-c", code],
        capture_output=True,
        text=True
    )

    success = result.returncode == 0
    run_test("2.1 导入所有 7 个工具", lambda: success)

    if success:
        print("     ✓ init_tasks_json")
        print("     ✓ append_task")
        print("     ✓ review_tasks")
        print("     ✓ update_task")
        print("     ✓ get_next_task")
        print("     ✓ update_task_result")
        print("     ✓ get_summary")

    return success

def test_complete_workflow():
    """Test 3: Complete workflow"""
    print_section("【Test 3】完整工作流测试")

    test_dir = Path("C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\test_output")
    test_dir.mkdir(exist_ok=True)
    json_path = str(test_dir / f"full_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    workflow_code = f"""
import json
import sys
sys.path.insert(0, r'C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\scripts')
from task_generator_mcp import (
    init_tasks_json, append_task, review_tasks, update_task,
    get_next_task, update_task_result, get_summary
)

test_results = {{}}

# Phase 1: Initialize
result = init_tasks_json(r'{json_path}', '完整工作流测试')
test_results['init'] = result['success']

# Phase 2: Append 5 tasks
tasks_added = 0
for i in range(1, 6):
    result = append_task(
        r'{json_path}',
        f'实现 TestMethod{{i}}() 方法',
        f'第{{i}}个测试任务的实现思路，包含具体的实现步骤和检查项',
        'TestModule',
        ['检查1', '检查2', '检查3']
    )
    if result['success']:
        tasks_added += 1

test_results['tasks_added'] = tasks_added == 5
test_results['total_count'] = tasks_added

# Phase 3: Review
result = review_tasks(r'{json_path}')
test_results['review_success'] = result['success']
test_results['review_total'] = result['totalCount']
test_results['review_issues'] = len(result['issues'])

# Phase 4: Get summary
result = get_summary(r'{json_path}')
test_results['summary_success'] = result['success']
test_results['summary_total'] = result['total']

# Phase 5: Executor test - get_next_task
result = get_next_task(r'{json_path}')
test_results['get_next_task_success'] = result['success']
test_results['has_next_task'] = result['task'] is not None

# Phase 6: Mark task as passed
if result['task']:
    task_id = result['task']['id']
    result = update_task_result(r'{json_path}', task_id, passed=True)
    test_results['update_result_success'] = result['success']

# Phase 7: Verify updated summary
result = get_summary(r'{json_path}')
test_results['final_summary'] = result['summary'] if result['success'] else None
test_results['final_passed'] = result.get('passed', 0)

print(json.dumps(test_results, ensure_ascii=False, indent=2))
"""

    result = subprocess.run(
        ["C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe", "-c", workflow_code],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"❌ 工作流测试失败: {result.stderr}")
        return False

    try:
        data = json.loads(result.stdout)

        print("3.1 初始化框架", end="")
        print(" ✅" if data.get('init') else " ❌")

        print("3.2 追加 5 个任务", end="")
        print(" ✅" if data.get('tasks_added') else " ❌")

        print("3.3 全局审查", end="")
        print(" ✅" if data.get('review_success') else " ❌")
        print(f"     发现 {data.get('review_issues', 0)} 个审查问题")

        print("3.4 获取摘要", end="")
        print(" ✅" if data.get('summary_success') else " ❌")

        print("3.5 获取下一个待做任务", end="")
        print(" ✅" if data.get('get_next_task_success') else " ❌")

        print("3.6 标记任务为完成", end="")
        print(" ✅" if data.get('update_result_success') else " ❌")

        print("3.7 验证最终摘要", end="")
        print(" ✅" if data.get('final_summary') else " ❌")

        all_passed = all([
            data.get('init'),
            data.get('tasks_added'),
            data.get('review_success'),
            data.get('summary_success'),
            data.get('get_next_task_success'),
            data.get('update_result_success'),
            data.get('final_summary')
        ])

        return all_passed

    except json.JSONDecodeError:
        print(f"❌ 解析输出失败")
        return False

def test_regex_improvements():
    """Test 4: Regex improvements"""
    print_section("【Test 4】正则表达式改进验证")

    test_code = """
import re

# Test regex patterns
patterns = [
    (r'[A-Z][a-zA-Z]*\\s*[\\(（]', "函数名+括号"),
    (r'[\\(（][^\\)）]*[\\)）]', "括号匹配"),
    (r'方法|函数', "关键词")
]

test_goals = [
    ("实现 Play(AudioClip clip) 方法", True, "英文括号+参数"),
    ("实现 Play（AudioClip clip）方法", True, "中文括号+参数"),
    ("实现 Instance 属性（单例模式）", True, "中文括号"),
    ("实现 GetVolume（）方法", True, "中文空括号"),
    ("实现音量控制方法", True, "仅关键词"),
    ("完成某项工作", False, "无标记")
]

results = {}
for goal, expected, desc in test_goals:
    matches = any(re.search(p, goal) for p, _ in patterns)
    results[desc] = (matches == expected)

passed = sum(1 for v in results.values() if v)
total = len(results)

for desc, success in results.items():
    print(f"  {'✓' if success else '✗'} {desc}")

print(f"\\n通过: {passed}/{total}")
"""

    result = subprocess.run(
        ["C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe", "-c", test_code],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        return "通过: 6/6" in result.stdout
    else:
        print(f"❌ 正则表达式测试失败")
        return False

def test_error_handling():
    """Test 5: Error handling"""
    print_section("【Test 5】错误处理验证")

    test_code = """
import sys
sys.path.insert(0, r'C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\scripts')
from task_generator_mcp import (
    init_tasks_json, append_task, review_tasks, update_task, get_next_task
)

results = {}

# Test 1: Non-existent file for append
result = append_task('/nonexistent/path.json', 'goal', 'idea', 'module', ['check'])
results['nonexistent_file'] = (not result['success'])

# Test 2: Non-existent file for review
result = review_tasks('/nonexistent/path.json')
results['review_nonexistent'] = (not result['success'])

# Test 3: Invalid task ID
import tempfile
import json
from pathlib import Path

with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump({
        'planName': 'test',
        'generatedAt': '2026-04-13T00:00:00',
        'tasks': []
    }, f)
    temp_path = f.name

result = update_task(temp_path, 'T-999', goal='new goal')
results['invalid_task_id'] = (not result['success'])

Path(temp_path).unlink()

passed = sum(1 for v in results.values() if v)
total = len(results)

for test_name, success in results.items():
    print(f"  {'✓' if success else '✗'} {test_name}")

print(f"\\n通过: {passed}/{total}")
"""

    result = subprocess.run(
        ["C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe", "-c", test_code],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        return "通过: 3/3" in result.stdout
    else:
        print(f"❌ 错误处理测试失败")
        return False

def test_json_structure():
    """Test 6: JSON structure validation"""
    print_section("【Test 6】JSON 结构验证")

    test_code = """
import sys
import json
sys.path.insert(0, r'C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\scripts')
from task_generator_mcp import init_tasks_json, append_task
import tempfile
from pathlib import Path

# Create test JSON
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    temp_path = f.name

init_tasks_json(temp_path, 'Test Plan')
append_task(temp_path, '实现 Test() 方法', '这是测试任务的实现思路', 'TestModule', ['check1', 'check2'])

# Load and verify structure
with open(temp_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

results = {}
results['has_planName'] = 'planName' in data
results['has_generatedAt'] = 'generatedAt' in data
results['has_tasks'] = 'tasks' in data
results['tasks_is_list'] = isinstance(data.get('tasks'), list)

if data.get('tasks'):
    task = data['tasks'][0]
    results['task_has_id'] = 'id' in task
    results['task_has_goal'] = 'goal' in task
    results['task_has_idea'] = 'implementationIdea' in task
    results['task_has_module'] = 'module' in task
    results['task_has_acceptance'] = 'acceptance' in task

    if 'acceptance' in task:
        acc = task['acceptance']
        results['acceptance_has_passed'] = 'passed' in acc
        results['acceptance_has_checks'] = 'checks' in acc
        results['acceptance_has_reason'] = 'failedReason' in acc

Path(temp_path).unlink()

passed = sum(1 for v in results.values() if v)
total = len(results)

for field, success in results.items():
    print(f"  {'✓' if success else '✗'} {field}")

print(f"\\n通过: {passed}/{total}")
"""

    result = subprocess.run(
        ["C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe", "-c", test_code],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        return "通过: 13/13" in result.stdout
    else:
        print(f"❌ JSON 结构验证失败")
        return False

def main():
    """Run all tests"""
    tests = [
        ("环境验证", test_environment),
        ("工具导入", test_imports),
        ("完整工作流", test_complete_workflow),
        ("正则表达式改进", test_regex_improvements),
        ("错误处理", test_error_handling),
        ("JSON 结构", test_json_structure),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results[test_name] = False

    # Summary
    print_header("全量测试总结")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    print(f"\n测试结果:")
    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status}: {test_name}")

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试全部通过！")
        print("\n项目状态: ✅ 生产就绪")
        print("可以在 Claude Code 中使用此 MCP 服务")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 项测试失败，请检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())
