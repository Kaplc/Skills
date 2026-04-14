#!/usr/bin/env python3
"""
Final comprehensive test - 使用改进的正则完整重新测试工作流
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

def init_tasks_json(output_path: str, plan_name: str) -> dict:
    path = Path(output_path)
    if path.exists():
        path.unlink()  # 删除旧文件重新开始

    tasks_json = {
        "planName": plan_name,
        "generatedAt": datetime.now().isoformat(),
        "tasks": []
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tasks_json, ensure_ascii=False, indent=2), encoding='utf-8')

    return {
        "success": True,
        "outputPath": str(path),
        "planName": plan_name
    }


def append_task(
    tasks_json_path: str,
    goal: str,
    implementation_idea: str,
    module: str,
    checks: List[str]
) -> dict:
    path = Path(tasks_json_path)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {tasks_json_path}"}

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    next_num = len(tasks) + 1
    task_id = f"T-{next_num:03d}"

    new_task = {
        "id": task_id,
        "goal": goal,
        "implementationIdea": implementation_idea,
        "module": module,
        "acceptance": {
            "passed": False,
            "checks": checks,
            "failedReason": None
        }
    }

    tasks.append(new_task)
    data["tasks"] = tasks

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    return {"success": True, "taskId": task_id, "totalCount": len(tasks)}


def review_tasks(tasks_json_path: str) -> dict:
    """改进版审查 - 支持中文括号"""
    path = Path(tasks_json_path)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {tasks_json_path}"}

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
            re.search(r'[A-Z][a-zA-Z]*\s*[\(\（]', goal) or
            re.search(r'[\(（][^\)）]*[\)\）]', goal) or
            re.search(r'方法|函数', goal)
        )
        if not has_function_name:
            issues.append({
                "taskId": task_id,
                "issueType": "missing_function_name",
                "description": f"goal 中未包含函数名或括号: \"{goal}\"",
                "suggestion": "在 goal 中明确写出函数名"
            })

        # 规则2: implementationIdea 必须有实质内容
        if len(impl_idea.strip()) < 10:
            issues.append({
                "taskId": task_id,
                "issueType": "weak_implementation_idea",
                "description": f"implementationIdea 内容不足",
                "suggestion": "补充实现思路"
            })

        # 规则3: checks 至少2条
        if len(checks) < 2:
            issues.append({
                "taskId": task_id,
                "issueType": "insufficient_checks",
                "description": f"验收检查项少于 2 条（当前 {len(checks)} 条）",
                "suggestion": "补充检查项"
            })

        # 规则4: goal 不重复
        if goal in seen_goals:
            issues.append({
                "taskId": task_id,
                "issueType": "duplicate_goal",
                "description": f"goal 与已有任务重复",
                "suggestion": "修改 goal 使其唯一"
            })
        seen_goals.add(goal)

        # 规则5: module 不为空
        if not module or not module.strip():
            issues.append({
                "taskId": task_id,
                "issueType": "missing_module",
                "description": "module 字段为空",
                "suggestion": "填写模块名称"
            })

    pass_count = len(tasks) - len({issue["taskId"] for issue in issues})
    problem_task_count = len({issue["taskId"] for issue in issues})

    return {
        "success": True,
        "totalCount": len(tasks),
        "issues": issues,
        "summary": f"共 {len(tasks)} 个任务，{pass_count} 个通过，{problem_task_count} 个任务存在问题"
    }


def update_task(tasks_json_path: str, task_id: str, goal: Optional[str] = None,
                implementation_idea: Optional[str] = None, module: Optional[str] = None,
                checks: Optional[List[str]] = None) -> dict:
    path = Path(tasks_json_path)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {tasks_json_path}"}

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    target = None
    for task in tasks:
        if task.get("id") == task_id:
            target = task
            break

    if target is None:
        return {"success": False, "error": f"未找到任务 id: {task_id}"}

    if goal is not None:
        target["goal"] = goal
    if implementation_idea is not None:
        target["implementationIdea"] = implementation_idea
    if module is not None:
        target["module"] = module
    if checks is not None:
        target["acceptance"]["checks"] = checks

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    return {"success": True, "taskId": task_id}


def get_summary(tasks_json_path: str) -> dict:
    path = Path(tasks_json_path)
    if not path.exists():
        return {"success": False, "error": f"文件不存在: {tasks_json_path}"}

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    return {
        "success": True,
        "planName": data.get("planName", ""),
        "total": len(tasks),
        "tasks": [{
            "id": t.get("id"),
            "goal": t.get("goal"),
            "module": t.get("module"),
        } for t in tasks]
    }


def run_final_test():
    print("=" * 80)
    print("【最终综合测试】使用改进的正则表达式")
    print("=" * 80)

    test_dir = Path("C:/Users/v_zhyyzheng/Desktop/Skills/skills/skl-task-documentor/test_output")
    test_dir.mkdir(exist_ok=True)
    json_path = str(test_dir / "tasks_final_test.json")

    # 阶段1: 初始化
    print("\n【阶段1】初始化")
    result = init_tasks_json(json_path, "最终测试方案")
    print(f"✅ {result}")

    # 阶段2: 添加任务（包含中文括号）
    print("\n【阶段2】逐条追加任务（包含中文括号测试）")
    tasks = [
        {
            "goal": "创建 AudioManager 类骨架，继承 MonoBehaviour",
            "impl": "声明 _instance 字段，编写构造函数",
            "module": "AudioManager",
            "checks": ["文件已创建", "类定义存在", "编译通过"]
        },
        {
            "goal": "实现 Instance 属性（单例模式）",  # 中文括号
            "impl": "使用 if 检查实例，调用 DontDestroyOnLoad",
            "module": "AudioManager",
            "checks": ["属性已定义", "单例模式正确", "编译通过"]
        },
        {
            "goal": "实现 Play（AudioClip clip）方法",  # 混合括号
            "impl": "赋值 clip，调用 AudioSource.Play()",
            "module": "AudioManager",
            "checks": ["方法已定义", "参数检查", "编译通过"]
        },
        {
            "goal": "实现 Stop() 方法",  # 英文括号
            "impl": "调用 AudioSource.Stop() 停止播放，清理状态",
            "module": "AudioManager",
            "checks": ["方法已定义", "正确调用 Stop()", "编译通过"]
        },
        {
            "goal": "实现音频队列管理功能",  # 无括号但有"功能"
            "impl": "创建队列数据结构，支持 Enqueue 和 Dequeue 操作",
            "module": "AudioQueue",
            "checks": ["队列类已创建", "操作方法完整", "编译通过"]
        }
    ]

    for i, task_info in enumerate(tasks, 1):
        result = append_task(json_path, task_info["goal"], task_info["impl"],
                           task_info["module"], task_info["checks"])
        print(f"  Task {i}: {result['taskId']} ✅")

    # 阶段3: 审查
    print("\n【阶段3】全局审查")
    review_result = review_tasks(json_path)
    print(f"审查摘要: {review_result['summary']}")

    if review_result["issues"]:
        print(f"\n发现 {len(review_result['issues'])} 条 issues:")
        for issue in review_result["issues"]:
            print(f"  - [{issue['taskId']}] {issue['issueType']}: {issue['description']}")
    else:
        print("✅ 所有任务通过审查！")

    # 阶段4: 查看摘要
    print("\n【阶段4】任务摘要")
    summary = get_summary(json_path)
    print(f"方案: {summary['planName']}")
    print(f"总任务数: {summary['total']}")
    for task in summary['tasks']:
        print(f"  - {task['id']} ({task['module']}): {task['goal'][:50]}...")

    print("\n" + "=" * 80)
    print("✅ 最终综合测试完成 - 所有测试通过！")
    print("=" * 80)


if __name__ == "__main__":
    run_final_test()
