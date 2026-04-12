---
name: skl-task-executor
description: 循环读取任务 JSON 文件，根据 goal 描述自主执行任务，验证 acceptance.checks，更新验收结果。通过 Claude 内置工具完成文件操作、代码编写等。
---

# Task-Executor - 任务自动执行器

**核心目标**: 循环读取 tasks.json，根据 goal 自主执行，直到全部完成

**输入**: task-documentor 生成的 `tasks.json`
**输出**: 更新后的 `tasks.json`（acceptance 结果）

**MCP 工具**: 使用 `task-executor` MCP

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
