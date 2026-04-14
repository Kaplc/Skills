# Task-Documentor MCP 环境设置指南

## 📋 完成状态

✅ **所有设置已完成** | 2026-04-13

### 环境配置清单

| 项目 | 状态 | 详情 |
|------|------|------|
| Python 3.12 虚拟环境 | ✅ 完成 | `~/.claude/mcp-env` |
| FastMCP 框架安装 | ✅ 完成 | 版本 3.2.3 |
| MCP 服务器配置 | ✅ 完成 | `task_generator_mcp.py` |
| Claude Code 集成 | ✅ 完成 | `.claude/settings.json` |
| 功能测试 | ✅ 通过 | 7 个工具全部可用 |

---

## 🔧 虚拟环境详情

### 路径配置

```
虚拟环境：  C:\Users\v_zhyyzheng\.claude\mcp-env
Python 3.12 路径：
  - 可执行文件: C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe
  - pip: C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\pip.exe

MCP 服务器脚本：
  C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py

Claude Code 设置：
  C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\.claude\settings.json
```

### 已安装的关键包

- **fastmcp** `3.2.3` - FastMCP 框架（核心依赖）
- **mcp** `1.27.0` - MCP SDK
- **pydantic** `2.12.5` - 数据验证
- **rich** `15.0.0` - 终端输出格式化
- **uvicorn** `0.44.0` - ASGI 服务器
- 其他依赖：见 `pip list` 输出

---

## 🛠️ MCP 服务器配置

### settings.json 配置

位置：`.claude/settings.json`

```json
{
  "mcpServers": {
    "task-generator": {
      "command": "C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\scripts\\task_generator_mcp.py"
      ],
      "env": {}
    }
  }
}
```

此配置告诉 Claude Code：
- 使用 Python 3.12 虚拟环境作为解释器
- 启动 `task_generator_mcp.py` 作为 MCP 服务器
- 暴露所有 7 个 MCP 工具给 Claude Code

---

## 📦 MCP 工具清单

### Generator 工具（4 个）- 任务创建和审查

#### 1. `init_tasks_json(output_path, plan_name)`
初始化一个空的 tasks.json 文件框架
```python
{
  "success": True,
  "outputPath": "/path/to/tasks.json",
  "planName": "我的方案"
}
```

#### 2. `append_task(tasks_json_path, goal, implementation_idea, module, checks)`
向已有 tasks.json 追加一条任务（自动递增 ID）
```python
{
  "success": True,
  "taskId": "T-001",
  "totalCount": 1
}
```

#### 3. `review_tasks(tasks_json_path)`
审查所有任务，检测质量问题（只读不修改）
```python
{
  "success": True,
  "totalCount": 5,
  "issues": [
    {
      "taskId": "T-002",
      "issueType": "missing_function_name",
      "description": "goal 中未包含函数名或括号...",
      "suggestion": "在 goal 中明确写出函数名..."
    }
  ],
  "summary": "共 5 个任务，4 个通过，1 个任务存在问题"
}
```

#### 4. `update_task(tasks_json_path, task_id, goal, implementation_idea, module, checks)`
修改指定任务的内容（用于审查后修正）
```python
{
  "success": True,
  "taskId": "T-001"
}
```

### Executor 工具（3 个）- 任务执行和跟踪

#### 5. `get_next_task(tasks_json_path)`
获取下一个未完成的任务
```python
{
  "success": True,
  "task": {
    "id": "T-001",
    "goal": "实现 Play(AudioClip clip) 方法",
    "implementationIdea": "...",
    "module": "AudioManager",
    "acceptance": {...}
  }
}
```

#### 6. `update_task_result(tasks_json_path, task_id, passed, failed_reason)`
更新任务执行结果
```python
{
  "success": True,
  "taskId": "T-001"
}
```

#### 7. `get_summary(tasks_json_path)`
获取任务完成情况摘要
```python
{
  "success": True,
  "planName": "我的方案",
  "total": 5,
  "passed": 2,
  "failed": 1,
  "pending": 2,
  "tasks": [...]
}
```

---

## ✅ 验证步骤

### 1. 验证虚拟环境

```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe --version
# 输出: Python 3.12.10
```

### 2. 验证 FastMCP 安装

```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe -c "import fastmcp; print(fastmcp.__version__)"
# 输出: 3.2.3
```

### 3. 运行完整测试

```bash
cd C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe test_mcp_venv.py
```

预期输出：所有项目标记为 ✅

---

## 🚀 使用工作流

### 完整工作流示例

```
【阶段1】初始化
→ 创建 idea 文档（如 idea.md）
→ 确认输出路径
→ 调用 init_tasks_json("output/tasks.json", "我的方案")

【阶段2】逐条追加任务
→ 读取 idea 文档中的实现步骤
→ 对每个函数/方法：
    - 提炼 goal（函数名 + 行为）
    - 思考 implementationIdea（2-4 句话）
    - 生成 checks（至少 2 条）
    - 调用 append_task(...)
    
【阶段3】全局审查
→ 所有任务追加完毕后，调用 review_tasks(...)
→ 对每个 issue，调用 update_task(...) 修复
→ 再次调用 review_tasks(...)，确认 issues 为空

【阶段4】执行任务
→ 调用 get_next_task(...) 获取待做任务
→ 实现代码
→ 调用 update_task_result(..., passed=True)
→ 重复直到所有任务完成

【阶段5】查看摘要
→ 调用 get_summary(...) 获取最终状态
```

---

## 📊 JSON Schema

### 任务结构

```json
{
  "planName": "音乐播放器方案",
  "generatedAt": "2026-04-13T15:30:00.000000",
  "tasks": [
    {
      "id": "T-001",
      "goal": "实现 Play(AudioClip clip) 方法",
      "implementationIdea": "通过 AudioSource.clip 赋值，调用 AudioSource.Play()，添加 clip 空值检查保护",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": [
          "Play 方法已定义",
          "clip 空值检查存在",
          "调用 AudioSource.Play()",
          "编译通过"
        ],
        "failedReason": null
      }
    }
  ]
}
```

### 审查规则

| 规则 | 检查内容 | 通过条件 |
|------|---------|---------|
| goal 包含函数名 | 使用 `[A-Z][a-zA-Z]*[\(\（]` 或 `[\(（][^\)）]*[\)\）]` 或关键词 `方法\|函数` | 至少匹配一个 |
| implementationIdea 充分 | 字符长度检查 | >10 字 |
| checks 足够 | 验收项数量 | ≥2 条 |
| goal 唯一性 | 去重检查 | 无重复 |
| module 不为空 | 字段检查 | 非空字符串 |

---

## 🔗 相关文件

```
skl-task-documentor/
├── scripts/
│   └── task_generator_mcp.py          ← MCP 服务器实现（7 个工具）
├── SKILL.md                           ← 工作流文档
├── references/
│   └── task-json-schema.md            ← JSON Schema 文档
├── .claude/
│   └── settings.json                  ← MCP 配置（新增）
├── test_workflow.py                   ← 工作流测试
├── test_regex_fix.py                  ← 正则表达式测试
├── test_final.py                      ← 最终综合测试
├── test_mcp_venv.py                   ← MCP 虚拟环境验证测试（新增）
└── TEST_REPORT.md                     ← 测试报告
```

---

## 💡 常见问题

### Q1: 如何卸载并重新创建虚拟环境？

```bash
# 卸载
rm -rf C:\Users\v_zhyyzheng\.claude\mcp-env

# 重新创建
C:\Users\v_zhyyzheng\AppData\Local\Programs\Python\Python312\python.exe -m venv C:\Users\v_zhyyzheng\.claude\mcp-env

# 重新安装 fastmcp
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\pip install fastmcp
```

### Q2: 如何更新 fastmcp？

```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\pip install --upgrade fastmcp
```

### Q3: 如何验证 MCP 服务器是否正常运行？

```bash
# 运行验证测试
C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\test_mcp_venv.py
```

### Q4: Claude Code 如何找到这个 MCP 服务器？

Claude Code 会：
1. 读取当前项目的 `.claude/settings.json`
2. 找到 `mcpServers.task-generator` 配置
3. 启动指定的 Python 解释器和脚本
4. 自动暴露所有 `@mcp.tool()` 装饰的函数

---

## ✨ 下一步

1. **在 Claude Code 中使用 MCP**：
   - 打开项目后，MCP 服务器会自动加载
   - 在 Claude Code 中调用任何 MCP 工具时，会自动使用虚拟环境

2. **创建第一个任务方案**：
   - 使用 `init_tasks_json()` 创建框架
   - 使用 `append_task()` 逐条添加任务
   - 使用 `review_tasks()` 进行全局审查

3. **执行任务**：
   - 使用 `get_next_task()` 获取待做任务
   - 完成实现后使用 `update_task_result()` 记录
   - 使用 `get_summary()` 查看整体进度

---

## 📞 技术信息

| 项 | 值 |
|----|-----|
| Python 版本 | 3.12.10 |
| FastMCP 版本 | 3.2.3 |
| MCP SDK 版本 | 1.27.0 |
| 工具总数 | 7 个 |
| 审查规则数 | 5 条 |
| 支持语言 | Python 3.12+ |
| 虚拟环境位置 | `~/.claude/mcp-env` |

---

✅ **所有配置已完成，可以开始使用！**
