# Task-Documentor MCP 快速参考

## ⚡ 快速开始

### 环境信息
- 🐍 **Python**: 3.12.10（`~/.claude/mcp-env`）
- 📦 **FastMCP**: 3.2.3
- ✅ **状态**: 已配置完成

### 一键验证
```bash
cd C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe test_mcp_venv.py
```

---

## 🛠️ 7 个 MCP 工具

### Generator（创建和审查）
| 工具 | 功能 | 返回 |
|------|------|------|
| `init_tasks_json(path, name)` | 创建空框架 | `{success, outputPath, planName}` |
| `append_task(path, goal, idea, module, checks)` | 追加单个任务 | `{success, taskId, totalCount}` |
| `review_tasks(path)` | 全局审查 | `{success, totalCount, issues[], summary}` |
| `update_task(path, id, goal?, idea?, module?, checks?)` | 修复任务 | `{success, taskId}` |

### Executor（执行和跟踪）
| 工具 | 功能 | 返回 |
|------|------|------|
| `get_next_task(path)` | 获取待做任务 | `{success, task}` |
| `update_task_result(path, id, passed, reason?)` | 记录结果 | `{success, taskId}` |
| `get_summary(path)` | 完成情况 | `{success, planName, total, passed, failed, pending, tasks[]}` |

---

## 📋 工作流

```
1️⃣ init_tasks_json("tasks.json", "我的方案")
   ↓
2️⃣ 对每个函数，append_task(...)
   ├─ goal: "实现 FunctionName() 方法"
   ├─ implementation_idea: "2-4 句话说明实现路径"
   ├─ module: "模块名"
   └─ checks: ["检查1", "检查2", ...]
   ↓
3️⃣ review_tasks(...) → 找出问题
   ↓
4️⃣ 对每个 issue，update_task(...) → 修复
   ↓
5️⃣ review_tasks(...) → 确认无问题
   ↓
6️⃣ get_next_task(...) → 获取待做
   ↓
7️⃣ [实现代码]
   ↓
8️⃣ update_task_result(..., passed=True)
   ↓
9️⃣ 重复 6-8 直到完成
   ↓
🔟 get_summary(...) → 最终摘要
```

---

## ✅ 审查规则（5条）

| # | 规则 | 失败条件 | 修复方法 |
|---|------|---------|---------|
| 1 | goal 包含函数名 | 无 `FunctionName()` 或 `方法`/`函数` 关键词 | 在 goal 中加入函数名 |
| 2 | implementationIdea 充分 | 长度 ≤10 字 | 补充 2-4 句实现细节 |
| 3 | checks 足够 | 少于 2 条 | 至少添加 2 条检查项 |
| 4 | goal 唯一 | 与其他任务重复 | 修改 goal 使其唯一 |
| 5 | module 不为空 | 字段为空或空字符串 | 填写模块名称 |

---

## 📝 JSON 文件格式

```json
{
  "planName": "方案名",
  "generatedAt": "ISO时间戳",
  "tasks": [
    {
      "id": "T-001",
      "goal": "实现 Play(AudioClip clip) 方法",
      "implementationIdea": "在 AudioSource.clip 赋值，调用 AudioSource.Play()",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["方法已定义", "参数检查", "编译通过"],
        "failedReason": null
      }
    }
  ]
}
```

---

## 🔧 路径速查

```
虚拟环境：          C:\Users\v_zhyyzheng\.claude\mcp-env
Python 解释器：     C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe
MCP 脚本：          scripts/task_generator_mcp.py
MCP 配置：          .claude/settings.json
测试脚本：          test_mcp_venv.py
完整文档：          MCP_SETUP_GUIDE.md
工作流文档：        SKILL.md
JSON Schema：       references/task-json-schema.md
```

---

## 💡 实用命令

### 检查虚拟环境
```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe --version
```

### 列出已安装包
```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\pip list
```

### 升级 FastMCP
```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\pip install --upgrade fastmcp
```

### 运行测试
```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe test_mcp_venv.py
```

---

## ❌ 常见错误排除

### "FastMCP 版本不对"
→ 升级：`pip install --upgrade fastmcp`

### "找不到模块"
→ 检查虚拟环境：`python --version` 应该显示 3.12.x

### "JSON 解析错误"
→ 检查 tasks.json 格式，使用 jq 验证：`jq . tasks.json`

### "MCP 工具不显示"
→ 重启 Claude Code，检查 `.claude/settings.json` 配置

---

## 🎯 下一步

1. ✅ 虚拟环境已配置
2. ✅ FastMCP 已安装
3. ✅ MCP 工具已就绪
4. → **现在可以开始创建任务方案了！**

📖 详细文档见 `MCP_SETUP_GUIDE.md`
