---
name: skl-task-documentor
description: 将实现思路文档转换为结构化的任务 JSON 文件。每个任务粒度约300行代码，理想情况下只包含单个方法。输入思路文档路径，输出 tasks.json。
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

### 核心原则：细粒度拆分

每个任务必须满足以下粒度约束：

| 约束 | 要求 |
|------|------|
| **代码量** | 每个任务约 **300 行代码**（上限不超过 500 行） |
| **方法数** | 理想情况 **单个方法**，最多不超过 3 个紧密关联的方法 |
| **职责** | 单一职责，一个任务只做一件事 |

### 拆分策略

1. **每个实现步骤 → 拆分为多个细粒度任务**
   - 如果步骤描述的是一个类/模块的创建，按方法拆分
   - 每个方法 → 独立任务
   - 类的骨架（字段+构造函数）→ 独立任务
2. **goal = 方法名/功能名 + 具体行为描述**
3. **checks = 从方法签名和行为推断**
4. **初始 acceptance.passed = false**

### 拆分示例

原始步骤：`创建 AudioManager 单例类，包含 Play、Stop、Pause 方法`

应拆分为：

| 任务 | goal | 预估行数 |
|------|------|----------|
| T-001 | 创建 AudioManager 类骨架，定义字段和构造函数 | ~30行 |
| T-002 | 实现单例模式 Instance 属性 | ~15行 |
| T-003 | 实现 Play(AudioClip) 方法，播放音频剪辑 | ~50行 |
| T-004 | 实现 Stop() 方法，停止当前播放 | ~20行 |
| T-005 | 实现 Pause() 方法，暂停当前播放 | ~20行 |

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
      "goal": "创建 AudioManager 类骨架：定义继承 MonoBehaviour、声明 _instance 字段和 AudioSource 组件引用",
      "acceptance": {
        "passed": false,
        "checks": ["AudioManager.cs 文件已创建", "类继承 MonoBehaviour", "字段声明完整", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-002",
      "goal": "实现 AudioManager 单例模式 Instance 属性",
      "acceptance": {
        "passed": false,
        "checks": ["Instance 属性存在", "单例模式正确（null 检查 + DontDestroyOnLoad）", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-003",
      "goal": "实现 Play(AudioClip clip) 方法：设置 AudioSource.clip 并调用 Play()",
      "acceptance": {
        "passed": false,
        "checks": ["Play 方法签名正确", "参数非空检查", "设置 clip 并播放", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-004",
      "goal": "实现 Stop() 方法：调用 AudioSource.Stop() 停止当前播放",
      "acceptance": {
        "passed": false,
        "checks": ["Stop 方法存在", "正确调用 AudioSource.Stop()", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-005",
      "goal": "实现 Pause() 方法：调用 AudioSource.Pause() 暂停当前播放",
      "acceptance": {
        "passed": false,
        "checks": ["Pause 方法存在", "正确调用 AudioSource.Pause()", "编译通过"],
        "failedReason": null
      }
    }
  ]
}
```

---

## 检查清单

- [ ] 每个实现步骤拆分为方法级细粒度任务
- [ ] 每个任务约 300 行代码，理想为单个方法
- [ ] goal 包含具体方法名和行为描述
- [ ] checks 包含验收检查项
- [ ] JSON 保存到正确路径
