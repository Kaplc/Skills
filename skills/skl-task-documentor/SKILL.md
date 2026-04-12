---
name: skl-task-documentor
description: 将实现思路文档转换为结构化的任务 JSON 文件。每个任务只包含 id、目标和验收结果。输入思路文档路径，输出 tasks.json。
---

# Task-Documentor - 任务 JSON 生成器

**核心目标**: 将实现思路文档转换为标准化的任务 JSON

**输入**: Idea-Documentor 生成的 `.md` 格式实现思路文档
**输出**: `tasks.json` 文件

**MCP 工具**: 使用 `task-generator` MCP 的 `generate_tasks_json` 工具

---

## MCP 工具使用

### generate_tasks_json

解析思路文档，生成 tasks.json

```
输入: idea_doc_path (思路文档路径)
      output_dir (可选，输出目录)
输出: { success, outputPath, planName, taskCount }
```

### parse_idea_doc

仅解析思路文档，返回解析结果（不生成文件）

```
输入: idea_doc_path (思路文档路径)
输出: { success, planName, modules, tasks }
```

---

## 工作流程

```
思路文档 → 解析 → 生成 JSON → 保存
```

---

## 解析思路文档

从思路文档提取：

| 提取项 | 来源 |
|--------|------|
| 方案名称 | 4.1 方案名称 |
| 实现步骤 | 4.3 实现步骤表格 |
| 模块划分 | 4.4 模块划分表格 |

---

## 输出格式

```json
{
  "planName": "方案名称",
  "generatedAt": "ISO时间戳",
  "tasks": [
    {
      "id": "T-001",
      "goal": "任务目标描述",
      "acceptance": {
        "passed": false,
        "checks": ["检查项1", "检查项2"],
        "failedReason": null
      }
    }
  ]
}
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `id` | 任务编号，T-001, T-002... |
| `goal` | 任务目标，一句话描述要做什么 |
| `acceptance` | 验收结果（执行后更新） |
| `acceptance.passed` | 是否通过 |
| `acceptance.checks` | 验收检查项 |
| `acceptance.failedReason` | 失败原因 |

---

## 任务生成规则

1. 每个实现步骤 → 一个任务
2. goal = 步骤名称 + 核心描述
3. checks = 从验收标准推断
4. 初始 acceptance.passed = false

---

## 输出路径

```
{思路文档所在目录}/tasks_{方案名}_{日期}.json
```

---

## 示例

输入 `docs/需求文档/音乐播放器.md` → 输出 `docs/需求文档/tasks_音乐播放器_20260412.json`

```json
{
  "planName": "音乐播放器方案",
  "generatedAt": "2026-04-12T10:00:00Z",
  "tasks": [
    {
      "id": "T-001",
      "goal": "创建 AudioManager 单例类，继承 MonoBehaviour，包含实例引用",
      "acceptance": {
        "passed": false,
        "checks": ["AudioManager.cs 已创建", "单例模式正确", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-002",
      "goal": "实现 Play 方法，支持传入 AudioClip 播放",
      "acceptance": {
        "passed": false,
        "checks": ["Play 方法存在", "参数为 AudioClip", "编译通过"],
        "failedReason": null
      }
    }
  ]
}
```

---

## 检查清单

- [ ] 每个实现步骤生成一个任务
- [ ] goal 清晰描述任务目标
- [ ] checks 包含验收检查项
- [ ] JSON 保存到正确路径
