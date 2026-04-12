# Skills 使用文档

## 目录结构

```
skills/
├── idea-documentor/          # 需求 → 思路文档
│   ├── SKILL.md
│   ├── TEMPLATE.md           # 文档模板
│   └── references/
│       └── (参考文档)
│
├── task-documentor/          # 思路文档 → 任务 JSON
│   ├── SKILL.md
│   ├── scripts/
│   │   └── task_generator_mcp.py  # MCP Server
│   └── references/
│       └── task-json-schema.md     # JSON 格式规范
│
├── task-executor/            # 执行任务 JSON
│   ├── SKILL.md
│   └── scripts/
│       └── task_executor_mcp.py    # MCP Server
│
└── task-tracker/             # 任务状态跟踪
    └── SKILL.md
```

---

## MCP 配置

MCP Server 已集成到各 Skill 目录的 `scripts/` 下。

### settings.json 配置

```json
{
  "mcpServers": {
    "task-generator": {
      "command": "python",
      "args": ["E:/Project/Skills/skills/task-documentor/scripts/task_generator_mcp.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    },
    "task-executor": {
      "command": "python",
      "args": ["E:/Project/Skills/skills/task-executor/scripts/task_executor_mcp.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### 验证 MCP 是否正常运行

Claude Code 中输入：
```
/mcp
```
查看两个 MCP 是否显示为 running。

---

## 工作流程

```
用户: "我需要一个音乐播放器"
         ↓
   idea-documentor
         ↓ (需求分析)
   思路文档.md
         ↓
   task-documentor
         ↓ (MCP 解析)
   tasks.json
         ↓
   task-executor
         ↓ (循环执行)
   完成的任务状态
```

---

## 任务 JSON 格式

```json
{
  "planName": "音乐播放器方案",
  "generatedAt": "2026-04-12T10:00:00Z",
  "tasks": [
    {
      "id": "T-001",
      "goal": "创建 AudioManager 单例类",
      "acceptance": {
        "passed": false,
        "checks": ["文件已创建", "编译通过"],
        "failedReason": null
      }
    }
  ]
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `id` | 任务编号 |
| `goal` | 任务目标描述 |
| `acceptance.passed` | 是否通过 |
| `acceptance.checks` | 验收检查项 |
| `acceptance.failedReason` | 失败原因 |

---

## 使用示例

### 1. 生成任务 JSON

```
你: 把 docs/需求文档/音乐播放器.md 转成任务

Claude: 调用 task-generator MCP 的 generate_tasks_json
        → 生成 tasks.json
```

### 2. 执行任务

```
你: 执行 tasks.json 中的任务

Claude: 调用 task-executor MCP
        1. get_next_task 获取任务
        2. 理解 goal，使用内置工具执行
        3. verify_acceptance 验证
        4. update_task_result 更新结果
        5. 循环直到全部完成
```

---

## MCP 工具列表

### task-generator MCP

| 工具 | 说明 |
|------|------|
| `parse_idea_doc` | 解析思路文档，返回结构化数据 |
| `generate_tasks_json` | 解析并生成 tasks.json 文件 |

### task-executor MCP

| 工具 | 说明 |
|------|------|
| `get_next_task` | 获取下一个未完成的任务 |
| `update_task_result` | 更新任务执行结果 |
| `verify_acceptance` | 验证任务验收标准 |
| `get_summary` | 获取执行进度摘要 |
| `run_command` | 执行命令行命令 |

---

## 依赖安装

```bash
pip install fastmcp
```

---

## 文件路径

| 组件 | 路径 |
|------|------|
| skill-creator | `C:\Users\Kaplc\.claude\skills\skill-creator` |
| idea-documentor | `E:\Project\Skills\skills\idea-documentor` |
| task-documentor | `E:\Project\Skills\skills\task-documentor` |
| task-executor | `E:\Project\Skills\skills\task-executor` |
| task-tracker | `E:\Project\Skills\skills\task-tracker` |
| MCP (generator) | `E:\Project\Skills\skills\task-documentor\scripts\task_generator_mcp.py` |
| MCP (executor) | `E:\Project\Skills\skills\task-executor\scripts\task_executor_mcp.py` |
