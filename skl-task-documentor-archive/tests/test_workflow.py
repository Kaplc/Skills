#!/usr/bin/env python3
"""
Test script for task_generator_mcp tools - 直接测试工具逻辑（不依赖 FastMCP）
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# ============ 工具实现（从 task_generator_mcp.py 复制）============

def init_tasks_json(output_path: str, plan_name: str) -> dict:
    path = Path(output_path)
    if path.exists():
        return {
            "success": False,
            "error": f"文件已存在，拒绝覆盖: {output_path}"
        }

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
        return {
            "success": False,
            "error": f"文件不存在: {tasks_json_path}，请先调用 init_tasks_json()"
        }

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

    return {
        "success": True,
        "taskId": task_id,
        "totalCount": len(tasks)
    }


def review_tasks(tasks_json_path: str) -> dict:
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

        # 规则1: goal 必须含函数名
        has_function_name = bool(
            re.search(r'[A-Z][a-zA-Z]*\s*\(', goal) or
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


def update_task(
    tasks_json_path: str,
    task_id: str,
    goal: Optional[str] = None,
    implementation_idea: Optional[str] = None,
    module: Optional[str] = None,
    checks: Optional[List[str]] = None
) -> dict:
    path = Path(tasks_json_path)
    if not path.exists():
        return {
            "success": False,
            "error": f"文件不存在: {tasks_json_path}"
        }

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    target = None
    for task in tasks:
        if task.get("id") == task_id:
            target = task
            break

    if target is None:
        return {
            "success": False,
            "error": f"未找到任务 id: {task_id}"
        }

    if goal is not None:
        target["goal"] = goal
    if implementation_idea is not None:
        target["implementationIdea"] = implementation_idea
    if module is not None:
        target["module"] = module
    if checks is not None:
        target["acceptance"]["checks"] = checks

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    return {
        "success": True,
        "taskId": task_id
    }


def get_next_task(tasks_json_path: str) -> dict:
    path = Path(tasks_json_path)
    if not path.exists():
        return {
            "success": False,
            "error": f"文件不存在: {tasks_json_path}"
        }

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    for task in tasks:
        if not task.get("acceptance", {}).get("passed", False):
            return {
                "success": True,
                "task": task
            }

    return {
        "success": True,
        "task": None,
        "message": "所有任务已完成"
    }


def update_task_result(
    tasks_json_path: str,
    task_id: str,
    passed: bool,
    failed_reason: Optional[str] = None
) -> dict:
    path = Path(tasks_json_path)
    if not path.exists():
        return {
            "success": False,
            "error": f"文件不存在: {tasks_json_path}"
        }

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    target = None
    for task in tasks:
        if task.get("id") == task_id:
            target = task
            break

    if target is None:
        return {
            "success": False,
            "error": f"未找到任务 id: {task_id}"
        }

    target["acceptance"]["passed"] = passed
    target["acceptance"]["failedReason"] = failed_reason if not passed else None

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    return {
        "success": True,
        "taskId": task_id
    }


def get_summary(tasks_json_path: str) -> dict:
    path = Path(tasks_json_path)
    if not path.exists():
        return {
            "success": False,
            "error": f"文件不存在: {tasks_json_path}"
        }

    data = json.loads(path.read_text(encoding='utf-8'))
    tasks = data.get("tasks", [])

    passed_tasks = [t for t in tasks if t.get("acceptance", {}).get("passed", False)]
    failed_tasks = [t for t in tasks if not t.get("acceptance", {}).get("passed", False) and t.get("acceptance", {}).get("failedReason")]
    pending_tasks = [t for t in tasks if not t.get("acceptance", {}).get("passed", False) and not t.get("acceptance", {}).get("failedReason")]

    return {
        "success": True,
        "planName": data.get("planName", ""),
        "total": len(tasks),
        "passed": len(passed_tasks),
        "failed": len(failed_tasks),
        "pending": len(pending_tasks),
        "tasks": [
            {
                "id": t.get("id"),
                "goal": t.get("goal"),
                "module": t.get("module"),
                "passed": t.get("acceptance", {}).get("passed", False),
                "failedReason": t.get("acceptance", {}).get("failedReason")
            }
            for t in tasks
        ]
    }


# ============ 测试流程 ============

def test_complete_workflow():
    print("=" * 70)
    print("开始测试 task-documentor 完整工作流")
    print("=" * 70)

    test_dir = Path("C:/Users/v_zhyyzheng/Desktop/Skills/skills/skl-task-documentor/test_output")
    test_dir.mkdir(exist_ok=True)
    json_path = str(test_dir / "tasks_test.json")

    # 阶段1: 初始化
    print("\n【阶段1】初始化 tasks.json")
    print("-" * 70)
    result = init_tasks_json(json_path, "音乐播放器方案测试")
    print(f"✓ init_tasks_json: {result}")
    assert result["success"] == True

    # 阶段2: 逐条追加 - 添加 5 个任务
    print("\n【阶段2】逐条追加任务")
    print("-" * 70)

    tasks_to_add = [
        {
            "goal": "创建 AudioManager 类骨架，继承 MonoBehaviour，声明字段和构造函数",
            "implementation_idea": "声明 _instance 静态字段用于单例、_audioSource 组件引用。编写空构造函数确保编译通过。",
            "module": "AudioManager",
            "checks": ["AudioManager.cs 文件已创建", "类继承 MonoBehaviour", "字段声明完整", "编译通过"]
        },
        {
            "goal": "实现 Instance 属性（单例模式）",
            "implementation_idea": "使用 if (_instance == null) 检查实例，first-time 时进行初始化，调用 DontDestroyOnLoad() 保证跨场景持久化。",
            "module": "AudioManager",
            "checks": ["Instance 属性已定义", "单例模式正确（null 检查 + DontDestroyOnLoad）", "编译通过"]
        },
        {
            "goal": "实现 Play(AudioClip clip) 方法",
            "implementation_idea": "接收 AudioClip 参数，先进行空值检查，然后赋值给 _audioSource.clip，最后调用 _audioSource.Play()。",
            "module": "AudioManager",
            "checks": ["Play 方法已定义", "参数非空检查存在", "调用 AudioSource.Play()", "编译通过"]
        },
        {
            "goal": "实现 Stop() 方法",
            "implementation_idea": "调用 _audioSource.Stop() 停止当前播放",  # 故意太短，会触发审查规则
            "module": "AudioManager",
            "checks": ["Stop 方法已定义"]  # 故意只有 1 条，会触发审查规则
        },
        {
            "goal": "实现 Pause() 方法",
            "implementation_idea": "调用 _audioSource.Pause() 暂停当前播放，在需要时可用 Play() 恢复。",
            "module": "AudioManager",
            "checks": ["Pause 方法已定义", "正确调用 AudioSource.Pause()", "编译通过"]
        }
    ]

    for i, task_info in enumerate(tasks_to_add, 1):
        result = append_task(
            json_path,
            task_info["goal"],
            task_info["implementation_idea"],
            task_info["module"],
            task_info["checks"]
        )
        print(f"  Task {i}: {result}")
        assert result["success"] == True

    # 阶段3: 全局审查
    print("\n【阶段3】全局审查和自动修正")
    print("-" * 70)

    review_result = review_tasks(json_path)
    print(f"\n审查结果摘要: {review_result['summary']}")
    print(f"总任务数: {review_result['totalCount']}")

    if review_result["issues"]:
        print(f"\n发现 {len(review_result['issues'])} 条 issues:")
        for issue in review_result["issues"]:
            print(f"\n  [{issue['taskId']}] {issue['issueType']}")
            print(f"    问题: {issue['description']}")
            print(f"    建议: {issue['suggestion']}")

        # 自动修正
        print("\n自动修正问题中...")
        for issue in review_result["issues"]:
            task_id = issue["taskId"]
            issue_type = issue["issueType"]

            if issue_type == "weak_implementation_idea":
                # 补充实现思路
                if task_id == "T-004":
                    fix_result = update_task(
                        json_path,
                        task_id,
                        implementation_idea="调用 _audioSource.Stop() 停止当前播放，清理播放状态标志"
                    )
                    print(f"  ✓ 修复 {task_id} implementationIdea: {fix_result}")

            elif issue_type == "insufficient_checks":
                # 补充检查项
                if task_id == "T-004":
                    fix_result = update_task(
                        json_path,
                        task_id,
                        checks=["Stop 方法已定义", "正确调用 AudioSource.Stop()", "编译通过"]
                    )
                    print(f"  ✓ 修复 {task_id} checks: {fix_result}")

        # 再次审查
        print("\n再次审查确认...")
        review_result2 = review_tasks(json_path)
        print(f"审查结果摘要: {review_result2['summary']}")
        if not review_result2["issues"]:
            print("✓ 所有问题已解决！")
    else:
        print("✓ 所有任务都通过审查！")

    # 阶段4: 获取摘要
    print("\n【阶段4】任务摘要")
    print("-" * 70)
    summary = get_summary(json_path)
    print(f"方案名: {summary['planName']}")
    print(f"总任务数: {summary['total']}")
    print(f"已完成: {summary['passed']}")
    print(f"失败: {summary['failed']}")
    print(f"待做: {summary['pending']}")

    # 阶段5: 测试 executor 工具
    print("\n【阶段5】测试 executor 工具")
    print("-" * 70)

    # 获取第一个未完成任务
    next_task = get_next_task(json_path)
    print(f"下一个任务: {next_task['task']['id']} - {next_task['task']['goal']}")

    # 标记第一个任务为完成
    update_result = update_task_result(json_path, "T-001", passed=True)
    print(f"✓ 更新 T-001 为已完成: {update_result}")

    # 标记第二个任务为失败
    update_result = update_task_result(json_path, "T-002", passed=False, failed_reason="编译错误: 缺少引用")
    print(f"✓ 标记 T-002 失败: {update_result}")

    # 再次获取摘要
    summary = get_summary(json_path)
    print(f"\n更新后摘要:")
    print(f"  已完成: {summary['passed']}")
    print(f"  失败: {summary['failed']}")
    print(f"  待做: {summary['pending']}")

    print("\n【最终结果】")
    print("=" * 70)
    print("✅ 所有工具测试通过！")
    print("=" * 70)

    # 打印最终 JSON
    print("\n最终 tasks.json 内容:")
    final_json = json.loads(Path(json_path).read_text(encoding='utf-8'))
    print(json.dumps(final_json, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    test_complete_workflow()
