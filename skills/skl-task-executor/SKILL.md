---
name: skl-task-executor
description: >
  自动执行 tasks.json 里的开发任务。当用户想让 Claude 逐一完成任务清单中的待执行任务（goal 描述的编码工作），并在完成后更新验收状态时，调用此技能。
  关键词：执行任务、完成任务、把任务做完、逐个完成、自动完成开发任务、跑完任务清单、execute tasks、implement tasks from JSON。
  不适用：生成或创建任务列表、仅查看任务状态、规划功能或设计讨论。
---

# Task-Executor - 任务自动执行器

**核心目标**: 循环读取 tasks.json，根据 goal 自主执行，直到全部完成

**输入**: task-documentor 生成的 `tasks.json`
**输出**: 更新后的 `tasks.json`（acceptance 结果）

**MCP 工具**: 使用 `task-executor` MCP

---

## MCP 前置检查

在执行任何操作前，先确认 `task-executor-mcp` 已配置并可用。

### Step 1：识别当前 AI 助手环境

| 环境 | 配置文件路径 |
|------|-------------|
| Claude Code | `~/.claude/settings.json` |
| Cursor | `.cursor/mcp.json` 或 `~/.cursor/mcp.json` |
| VS Code | `.vscode/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| 不确定 | 询问用户当前使用哪个 AI 助手 |

### Step 2：检查 `task-executor-mcp` 是否已配置

读取对应配置文件，查找 `task-executor-mcp` 或 `task-executor` 条目。

- **已配置且工具可用** → 直接进入工作流程
- **未配置** → 执行 Step 3

### Step 3：未配置时自动配置

1. 用 `WebSearch` 搜索当前 AI 助手的 MCP 配置官方文档，关键词：`<AI助手名> MCP server configuration python fastmcp`
2. 确认 `task_executor_mcp.py` 脚本路径（在本 skill 的 `scripts/` 目录下）
3. 将以下配置写入对应文件：

```json
"task-executor-mcp": {
  "command": "python",
  "args": ["<skill目录>/scripts/task_executor_mcp.py"],
  "env": {}
}
```

4. 提示用户重启 AI 助手，重启后重新触发本 skill

---

## MCP 工具使用

| 工具 | 用途 | 参数 |
|------|------|------|
| `get_next_task` | 获取下一个未完成的任务 | tasks_json_path |
| `update_task_result` | 更新任务执行结果 | tasks_json_path, task_id, passed, failed_reason |
| `verify_acceptance` | 验证任务验收标准 | tasks_json_path, task_id, workspace_path |
| `get_summary` | 获取执行进度摘要 | tasks_json_path |
| `run_command` | 执行命令行 | command, working_directory |

---

## 任务 JSON 格式

```json
{
  "planName": "方案名称",
  "generatedAt": "ISO时间戳",
  "tasks": [
    {
      "id": "T-001",
      "goal": "创建 AudioManager 单例类",
      "acceptance": {
        "passed": false,
        "checks": ["文件已创建", "类定义正确", "编译通过"],
        "failedReason": null
      }
    }
  ]
}
```

---

## 核心流程

```
加载 tasks.json
       ↓
获取下一个 acceptance.passed == false 的任务
       ↓
理解 goal 描述
       ↓
使用内置工具执行（read/write/edit/bash）
       ↓
检查 checks，逐项验证
       ↓
更新 acceptance: passed + failedReason
       ↓
循环直到全部 passed == true
```

---

## 执行策略

### 1. 获取任务

从 `tasks.json` 中找到第一个 `acceptance.passed == false` 的任务。

### 2. 理解 goal

解析 `goal` 字段，理解任务目标。例如：
- "创建 AudioManager 单例类" → 需要创建 .cs 文件
- "实现 Play 方法" → 需要添加方法到已有文件

### 3. 执行

使用 Claude Code 内置工具执行：
- `Write` - 创建/覆写文件
- `Edit` - 修改文件内容
- `Bash` - 执行命令（编译、运行测试等）

### 4. 验证 checks

对 `acceptance.checks` 中的每一项进行验证：
- "文件已创建" → 检查文件是否存在
- "类定义正确" → 读取文件，检查内容
- "编译通过" → 运行编译命令

### 5. 更新结果

```json
{
  "acceptance": {
    "passed": true,           // 或 false
    "checks": ["...", "..."], // 更新为实际检查结果
    "failedReason": null      // 如果失败，写明原因
  }
}
```

---

## 循环执行示例

```
========================================
Task Executor - 任务执行器
========================================

加载: tasks_音乐播放器.json
工作区: e:/UnityProject/MyGame

----------------------------------------
[T-001] 创建 AudioManager 单例类
Goal: 创建 AudioManager 单例类，继承 MonoBehaviour

执行中...
✅ 已创建 AudioManager.cs
✅ 单例模式实现正确
✅ 编译通过

验收检查:
  ✅ 文件已创建
  ✅ 类定义正确
  ✅ 编译通过

结果: passed = true

----------------------------------------
[T-002] 实现 Play 方法
Goal: 实现 Play 方法，支持传入 AudioClip

执行中...
...

========================================
执行完成
========================================
总任务数: 9
已完成:   3
待执行:   6
========================================
```

---

## 检查清单

- [ ] 正确加载 tasks.json
- [ ] 按顺序执行未完成的任务
- [ ] goal 理解正确
- [ ] 执行结果验证准确
- [ ] acceptance 更新正确
- [ ] 执行完成后有进度摘要
