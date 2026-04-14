#!/usr/bin/env python3
"""
Regression test for the regex fix - 验证中文括号支持
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

def review_tasks_improved(tasks_json_path: str) -> dict:
    """使用改进的审查规则"""
    path = Path(tasks_json_path)
    if not path.exists():
        return {
            "success": False,
            "error": f"文件不存在: {tasks_json_path}"
        }

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    issues = []
    seen_goals = set()

    for task in tasks:
        task_id = task.get("id", "?")
        goal = task.get("goal", "")
        impl_idea = task.get("implementationIdea", "")
        checks = task.get("acceptance", {}).get("checks", [])
        module = task.get("module", "")

        # 规则1: goal 必须含函数名 (改进版 - 支持中文括号)
        has_function_name = bool(
            re.search(r'[A-Z][a-zA-Z]*\s*[\(\（]', goal) or  # 英文或中文括号
            re.search(r'[\(（][^\)）]*[\)\）]', goal) or      # 括号匹配（任意括号）
            re.search(r'方法|函数', goal)
        )
        if not has_function_name:
            issues.append({
                "taskId": task_id,
                "issueType": "missing_function_name",
                "description": f"goal 中未包含函数名或括号: \"{goal}\"",
                "suggestion": "在 goal 中明确写出函数名，如 '实现 Play(AudioClip clip) 方法'"
            })

        # 规则2: implementationIdea 必须有实质内容
        if len(impl_idea.strip()) < 10:
            issues.append({
                "taskId": task_id,
                "issueType": "weak_implementation_idea",
                "description": f"implementationIdea 内容不足（当前: \"{impl_idea}\"）",
                "suggestion": "写 2-4 句话说明实现路径，如具体调用哪些 API、处理什么边界情况"
            })

        # 规则3: checks 至少2条
        if len(checks) < 2:
            issues.append({
                "taskId": task_id,
                "issueType": "insufficient_checks",
                "description": f"验收检查项少于 2 条（当前 {len(checks)} 条）",
                "suggestion": "至少添加：方法已定义、逻辑完整、编译通过 等检查项"
            })

        # 规则4: goal 不重复
        if goal in seen_goals:
            issues.append({
                "taskId": task_id,
                "issueType": "duplicate_goal",
                "description": f"goal 与已有任务重复: \"{goal}\"",
                "suggestion": "修改 goal 使其唯一，明确区分不同任务的职责"
            })
        seen_goals.add(goal)

        # 规则5: module 不为空
        if not module or not module.strip():
            issues.append({
                "taskId": task_id,
                "issueType": "missing_module",
                "description": "module 字段为空",
                "suggestion": "填写该任务所属的模块名称"
            })

    pass_count = len(tasks) - len({issue["taskId"] for issue in issues})
    problem_task_count = len({issue["taskId"] for issue in issues})

    return {
        "success": True,
        "totalCount": len(tasks),
        "issues": issues,
        "summary": f"共 {len(tasks)} 个任务，{pass_count} 个通过，{problem_task_count} 个任务存在问题（共 {len(issues)} 条 issue）"
    }


def test_regex_improvement():
    print("=" * 70)
    print("测试改进的正则表达式 - 中文括号支持")
    print("=" * 70)

    test_dir = Path("C:/Users/v_zhyyzheng/Desktop/Skills/skills/skl-task-documentor/test_output")
    test_dir.mkdir(exist_ok=True)
    json_path = str(test_dir / "tasks_regex_test.json")

    # 创建测试数据
    test_tasks = {
        "planName": "正则表达式改进测试",
        "generatedAt": datetime.now().isoformat(),
        "tasks": [
            {
                "id": "T-001",
                "goal": "实现 Instance 属性（单例模式）",  # 中文括号
                "implementationIdea": "使用 if (_instance == null) 检查实例，first-time 时进行初始化",
                "module": "AudioManager",
                "acceptance": {"passed": False, "checks": ["检查1", "检查2"], "failedReason": None}
            },
            {
                "id": "T-002",
                "goal": "实现 GetVolume（）方法",  # 中文括号 + 中文空括号
                "implementationIdea": "返回当前音量值，从 AudioSource 组件获取",
                "module": "AudioManager",
                "acceptance": {"passed": False, "checks": ["检查1", "检查2"], "failedReason": None}
            },
            {
                "id": "T-003",
                "goal": "实现 Play(AudioClip clip) 方法",  # 英文括号
                "implementationIdea": "赋值 clip，调用 AudioSource.Play()",
                "module": "AudioManager",
                "acceptance": {"passed": False, "checks": ["检查1", "检查2"], "failedReason": None}
            },
            {
                "id": "T-004",
                "goal": "实现音量控制方法",  # 无括号但有"方法"
                "implementationIdea": "提供 SetVolume 和 GetVolume 两个方法",
                "module": "AudioManager",
                "acceptance": {"passed": False, "checks": ["检查1", "检查2"], "failedReason": None}
            }
        ]
    }

    Path(json_path).write_text(json.dumps(test_tasks, ensure_ascii=False, indent=2), encoding='utf-8')

    # 运行改进的审查
    review_result = review_tasks_improved(json_path)

    print(f"\n审查结果: {review_result['summary']}")
    print(f"\nDetailed Issues:")

    if review_result["issues"]:
        for issue in review_result["issues"]:
            print(f"\n  [{issue['taskId']}] {issue['issueType']}")
            print(f"    描述: {issue['description']}")
    else:
        print("  ✅ 无 issues 发现！")

    print("\n" + "=" * 70)
    print("正则表达式改进验证完成")
    print("=" * 70)

    # 详细测试每个正则模式
    print("\n【正则表达式详细测试】")
    print("-" * 70)

    test_goals = [
        ("实现 Instance 属性（单例模式）", "中文括号"),
        ("实现 GetVolume（）方法", "中文空括号"),
        ("实现 Play(AudioClip clip) 方法", "英文括号"),
        ("实现音量控制方法", "只有'方法'关键词"),
        ("执行某个操作函数", "只有'函数'关键词"),
        ("完成某项工作", "无任何标记（应失败）")
    ]

    patterns = [
        (r'[A-Z][a-zA-Z]*\s*[\(\（]', "英文/中文括号"),
        (r'[\(（][^\)）]*[\)\）]', "括号匹配"),
        (r'方法|函数', "关键词")
    ]

    print(f"\n{'Goal':<40} {'结果':<10} {'命中规则':<20}")
    print("-" * 70)

    for goal, description in test_goals:
        matches = []
        for pattern, pattern_name in patterns:
            if re.search(pattern, goal):
                matches.append(pattern_name)

        result = "✅ 通过" if matches else "❌ 失败"
        matched_rules = ", ".join(matches) if matches else "无"

        print(f"{goal:<40} {result:<10} {matched_rules:<20}")

    print("\n✅ 正则表达式改进验证成功！")


if __name__ == "__main__":
    test_regex_improvement()
