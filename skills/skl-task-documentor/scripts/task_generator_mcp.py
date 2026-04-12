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
    """提取实现步骤，按方法级粒度拆分为细粒度任务"""
    tasks = []
    task_id = 1

    raw_steps = []

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
                raw_steps.append((step_name, step_desc))

    # 如果没找到表格，尝试用编号列表
    if not raw_steps:
        for match in re.finditer(r'(?:^|\n)\s*(\d+)[.、)]\s*([^\n]+)', content):
            step_name = match.group(2).strip()
            if len(step_name) > 2:
                raw_steps.append((step_name, ""))

    # 将每个原始步骤拆分为方法级细粒度任务
    for step_name, step_desc in raw_steps:
        sub_tasks = split_step_to_methods(step_name, step_desc, modules, task_id)
        tasks.extend(sub_tasks)
        task_id += len(sub_tasks)

    return tasks


def split_step_to_methods(step_name: str, step_desc: str, modules: list, start_id: int) -> list:
    """
    将一个实现步骤拆分为方法级的细粒度任务。
    每个任务约 300 行代码，理想情况下只包含单个方法。

    拆分策略：
    1. 如果步骤涉及创建类/模块 → 拆分为：类骨架 + 每个方法各一个任务
    2. 如果步骤本身就是单一方法 → 直接生成一个任务
    3. 如果步骤包含多个动作 → 按动作拆分
    """
    tasks = []
    task_id = start_id
    module = detect_module_for_step(step_name, step_desc, modules)
    combined = step_name + " " + step_desc

    # 检测步骤中是否包含多个方法/动作
    # 匹配中英文方法名模式
    method_patterns = [
        # 中文描述中的方法列表：Play、Stop、Pause
        r'[、，,]\s*([A-Z][a-zA-Z]*)\s*(?:方法)?',
        # 英文方法名括号形式：Play()、Stop()
        r'([A-Z][a-zA-Z]*)\s*\([^)]*\)',
        # 中文方法：播放、停止、暂停
        r'([实现添加创建]*[A-Za-z\u4e00-\u9fff]+(?:方法|函数|功能))',
    ]

    extracted_methods = []

    # 尝试从描述中提取方法名
    # 策略1：查找顿号分隔的方法列表，如 "包含 Play、Stop、Pause 方法"
    method_list_match = re.search(r'(?:包含|包括|实现|支持)\s*([A-Z][a-zA-Z]*(?:\s*[、，,]\s*[A-Z][a-zA-Z]*)+)', combined)
    if method_list_match:
        method_str = method_list_match.group(1)
        extracted_methods = [m.strip() for m in re.split(r'\s*[、，,]\s*', method_str) if m.strip()]
    else:
        # 策略2：查找所有方法签名，如 Play(AudioClip)、Stop()
        sig_matches = re.findall(r'([A-Z][a-zA-Z]*)\s*\([^)]*\)', combined)
        if sig_matches:
            extracted_methods = sig_matches
        else:
            # 策略3：查找中文方法描述
            cn_methods = re.findall(r'(?:实现|创建|添加|编写)\s*([A-Za-z\u4e00-\u9fff]+(?:方法|函数|功能|接口))', combined)
            if cn_methods:
                extracted_methods = cn_methods

    # 如果步骤是创建类/模块，且有多个方法
    is_class_creation = any(kw in combined for kw in ['创建', '新建', '实现', '设计', '开发', '构建', '编写']) and \
                        any(kw in combined for kw in ['类', '模块', '管理器', '控制器', '服务', '组件', 'Manager', 'Controller', 'Service', 'Handler', 'class'])

    if is_class_creation and extracted_methods and len(extracted_methods) > 1:
        # 拆分：类骨架 + 每个方法一个任务
        class_name = extract_class_name(combined)
        parent_class = extract_parent_class(combined)

        # 任务1：类骨架
        skeleton_desc = f"创建 {class_name} 类骨架"
        if parent_class:
            skeleton_desc += f"，继承 {parent_class}"
        skeleton_desc += "，声明字段和构造函数"

        tasks.append({
            "id": f"T-{task_id:03d}",
            "goal": skeleton_desc,
            "module": module,
            "acceptance": {
                "passed": False,
                "checks": generate_class_skeleton_checks(class_name, parent_class),
                "failedReason": None
            }
        })
        task_id += 1

        # 每个方法一个任务
        for method in extracted_methods:
            method_desc = build_method_goal(method, combined)
            tasks.append({
                "id": f"T-{task_id:03d}",
                "goal": method_desc,
                "module": module,
                "acceptance": {
                    "passed": False,
                    "checks": generate_method_checks(method, combined),
                    "failedReason": None
                }
            })
            task_id += 1

    elif is_class_creation and (not extracted_methods or len(extracted_methods) <= 1):
        # 单方法的类：拆分为骨架 + 方法
        class_name = extract_class_name(combined)
        parent_class = extract_parent_class(combined)

        # 类骨架
        skeleton_desc = f"创建 {class_name} 类骨架"
        if parent_class:
            skeleton_desc += f"，继承 {parent_class}"
        skeleton_desc += "，声明字段和构造函数"

        tasks.append({
            "id": f"T-{task_id:03d}",
            "goal": skeleton_desc,
            "module": module,
            "acceptance": {
                "passed": False,
                "checks": generate_class_skeleton_checks(class_name, parent_class),
                "failedReason": None
            }
        })
        task_id += 1

        # 方法
        if extracted_methods:
            method = extracted_methods[0]
            tasks.append({
                "id": f"T-{task_id:03d}",
                "goal": build_method_goal(method, combined),
                "module": module,
                "acceptance": {
                    "passed": False,
                    "checks": generate_method_checks(method, combined),
                    "failedReason": None
                }
            })
            task_id += 1
        else:
            # 没有显式方法名，用原始描述作为方法任务
            tasks.append({
                "id": f"T-{task_id:03d}",
                "goal": f"在 {class_name} 中实现核心逻辑：{step_desc or step_name}",
                "module": module,
                "acceptance": {
                    "passed": False,
                    "checks": generate_checks(step_name, step_desc),
                    "failedReason": None
                }
            })
            task_id += 1

    else:
        # 非类创建步骤（配置、修改等），按动作拆分
        actions = extract_actions(combined)
        if len(actions) > 1:
            for action in actions:
                tasks.append({
                    "id": f"T-{task_id:03d}",
                    "goal": action,
                    "module": module,
                    "acceptance": {
                        "passed": False,
                        "checks": generate_checks(action, ""),
                        "failedReason": None
                    }
                })
                task_id += 1
        else:
            # 单一动作，直接生成一个任务
            tasks.append({
                "id": f"T-{task_id:03d}",
                "goal": f"{step_name}：{step_desc}" if step_desc else step_name,
                "module": module,
                "acceptance": {
                    "passed": False,
                    "checks": generate_checks(step_name, step_desc),
                    "failedReason": None
                }
            })
            task_id += 1

    return tasks


def extract_class_name(text: str) -> str:
    """从文本中提取类名"""
    patterns = [
        r'([A-Z][a-zA-Z]*(?:Manager|Controller|Service|Handler|Provider|Factory|Builder|Repository|Component|Module|System))',
        r'创建\s*([A-Z][a-zA-Z]*)\s*(?:类|模块)',
        r'([A-Z][a-zA-Z]*)\s*(?:类|模块)',
        r'创建\s*([^\s,，、]+?)(?:类|模块|管理器|控制器|服务)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return "UnknownClass"


def extract_parent_class(text: str) -> str:
    """从文本中提取父类名"""
    patterns = [
        r'继承\s*([A-Z][a-zA-Z]*)',
        r'extends\s*([A-Z][a-zA-Z]*)',
        r':\s*([A-Z][a-zA-Z]*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return ""


def build_method_goal(method_name: str, context: str) -> str:
    """构建方法级任务的目标描述"""
    # 检查是否有方法签名（含参数）
    sig_match = re.search(rf'{re.escape(method_name)}\s*\(([^)]*)\)', context)
    if sig_match:
        params = sig_match.group(1).strip()
        return f"实现 {method_name}({params}) 方法"
    return f"实现 {method_name}() 方法"


def generate_class_skeleton_checks(class_name: str, parent_class: str) -> list:
    """生成类骨架的验收检查项"""
    checks = [f"{class_name} 文件已创建"]
    if parent_class:
        checks.append(f"类继承 {parent_class}")
    checks.append("字段声明完整")
    checks.append("构造函数已创建")
    checks.append("编译通过")
    return checks


def generate_method_checks(method_name: str, context: str) -> list:
    """生成方法的验收检查项"""
    checks = [f"{method_name} 方法已定义"]

    sig_match = re.search(rf'{re.escape(method_name)}\s*\(([^)]*)\)', context)
    if sig_match and sig_match.group(1).strip():
        checks.append("方法参数正确")

    checks.append("方法逻辑完整")
    checks.append("编译通过")
    return checks


def extract_actions(text: str) -> list:
    """从文本中提取独立动作，用于拆分非类创建步骤"""
    # 按分号、逗号、顿号分隔多个动作
    parts = re.split(r'[；;]', text)
    actions = [p.strip() for p in parts if len(p.strip()) > 2]
    return actions if len(actions) > 1 else [text]

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
