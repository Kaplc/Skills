---
name: skl-task-documentor
description: >
  将文档拆解为任务清单。当用户有一份现成的文档（思路文档、设计文档、架构文档、.md 文件）并想把它转换成结构化任务列表时，调用此技能。
  典型场景：把 .md 文档转成 tasks.json、将设计文档的步骤拆成可执行任务、从实现思路生成任务文件。
  Use this skill when the user wants to convert an existing document into a tasks.json file —
  each task representing one function with goal and implementationIdea fields.
  Do NOT use for executing tasks, writing code directly, or pure architecture planning with no source document.
---

# Task-Documentor - 任务 JSON 生成器（追加式工作流）

**核心目标**: 将实现思路文档逐条转换为标准化的任务 JSON，确保每个任务一个函数，包含实现思路

**输入**: Idea-Documentor 生成的 `.md` 格式实现思路文档
**输出**: `tasks.json` 文件（支持审查 → 修正 → 再审查）

**MCP 工具**: 使用 `task-generator-mcp` 的 7 个工具（4 个生成 + 3 个执行）

---

## MCP 前置检查

在执行任何操作前，先确认 `task-generator-mcp` 已配置并可用。

### Step 1：识别当前 AI 助手环境

| 环境 | 配置文件路径 |
|------|-------------|
| Claude Code | `~/.claude/settings.json` |
| Cursor | `.cursor/mcp.json` 或 `~/.cursor/mcp.json` |
| VS Code | `.vscode/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| 不确定 | 询问用户当前使用哪个 AI 助手 |

### Step 2：检查 `task-generator-mcp` 是否已配置

读取对应配置文件，查找 `task-generator-mcp` 或 `task-generator` 条目。

- **已配置且工具可用** → 直接进入工作流程
- **未配置** → 执行 Step 3

### Step 3：未配置时自动配置

1. 用 `WebSearch` 搜索当前 AI 助手的 MCP 配置官方文档，关键词：`<AI助手名> MCP server configuration python fastmcp`
2. 确认 `task_generator_mcp.py` 脚本路径（在本 skill 的 `scripts/` 目录下）
3. 将以下配置写入对应文件：

```json
"task-generator-mcp": {
  "command": "python",
  "args": ["<skill目录>/scripts/task_generator_mcp.py"],
  "env": {}
}
```

4. 提示用户重启 AI 助手，重启后重新触发本 skill

---

## MCP 工具使用

### Generator 工具（生成阶段）

#### 1. init_tasks_json

初始化一个空的 tasks.json 文件框架。

```
输入: output_path (输出文件绝对路径)
      plan_name  (方案名称)
输出: { success, outputPath, planName }
```

#### 2. append_task

向 tasks.json 逐条追加任务（每次只追加一个）。自动生成递增 id。

```
输入: tasks_json_path     (JSON 文件路径)
      goal                (任务目标，一句话，必须包含函数名)
      implementation_idea (实现思路，2-4 句话说明如何实现)
      module              (所属模块名)
      checks              (验收检查项列表，string[])
输出: { success, taskId, totalCount }
```

**goal 示例**:
- "实现 Play(AudioClip clip) 方法，播放音频剪辑"
- "创建 AudioManager 类骨架，继承 MonoBehaviour，声明字段和构造函数"

**implementation_idea 示例**:
- "通过 AudioSource.clip 赋值，调用 AudioSource.Play()，添加 clip 空值检查保护"
- "声明 _instance 静态字段、_audioSource 组件引用，创建空构造函数"

#### 3. review_tasks

审查所有已追加的任务，检查质量问题。**只读不修改**。

```
输入: tasks_json_path (JSON 文件路径)
输出: { success, totalCount, issues, summary }
```

**审查规则**:
1. goal 必须包含函数名（含括号或"方法/函数"关键词）
2. implementationIdea 必须有实质内容（非空，>10字）
3. checks 至少有 2 条
4. goal 不能重复
5. module 不能为空

**Issues 字段**:
```
{
  taskId: "T-001",
  issueType: "missing_function_name" | "weak_implementation_idea" | "insufficient_checks" | "duplicate_goal" | "missing_module",
  description: "具体问题描述",
  suggestion: "建议的修复方案"
}
```

#### 4. update_task

修改指定任务的内容（用于审查后修正）。

```
输入: tasks_json_path     (JSON 文件路径)
      task_id             (任务 id，如 "T-001")
      goal                (新的任务目标，可选)
      implementation_idea (新的实现思路，可选)
      module              (新的模块名，可选)
      checks              (新的验收检查项列表，可选)
输出: { success, taskId }
```

### Executor 工具（执行阶段）

#### 5. get_next_task

获取下一个未完成（passed=false）的任务。

```
输入: tasks_json_path (JSON 文件路径)
输出: { success, task }
```

#### 6. update_task_result

更新任务的执行结果（验收结果）。

```
输入: tasks_json_path (JSON 文件路径)
      task_id         (任务 id)
      passed          (是否通过)
      failed_reason   (失败原因，passed=false 时填写)
输出: { success, taskId }
```

#### 7. get_summary

获取任务完成情况摘要。

```
输入: tasks_json_path (JSON 文件路径)
输出: { success, planName, total, passed, failed, pending, tasks[] }
```

---

## 工作流程（4 阶段）

```
阶段1: 初始化
  → init_tasks_json()

阶段2: 逐条追加
  → append_task() × N (每个函数一条)

阶段3: 全局审查 + 自动修正
  → review_tasks()
  → 发现问题 → Claude 调用 update_task() 修复
  → 再次 review_tasks() 确认通过

阶段4: 输出结果
  → 报告最终任务数量和文件路径
```
---

## 解析思路文档

Claude 直接读取思路文档，识别以下信息：

| 提取项 | 来源 |
|--------|------|
| 方案名称 | 4.1 方案名称 |
| 实现步骤 | 4.3 实现步骤表格 |
| 模块划分 | 4.4 模块划分表格 |

对于每个实现步骤，Claude 将其拆分为细粒度的函数级任务，每个函数对应一条 JSON 任务。

---

## 新 JSON Schema

新增 `implementationIdea` 字段，每个任务严格对应一个函数：

```json
{
  "planName": "方案名称",
  "generatedAt": "ISO时间戳",
  "tasks": [
    {
      "id": "T-001",
      "goal": "实现 Play(AudioClip clip) 方法",
      "implementationIdea": "通过 AudioSource.clip 赋值，调用 AudioSource.Play()，添加 clip 空值检查保护",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["Play 方法已定义", "clip 空值检查存在", "调用 AudioSource.Play()", "编译通过"],
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
| `goal` | 任务目标，一句话描述要做什么（必须包含函数名） |
| `implementationIdea` | 实现思路，2-4 句话说明如何实现 |
| `module` | 所属模块名 |
| `acceptance` | 验收结果 |
| `acceptance.passed` | 是否通过 |
| `acceptance.checks` | 验收检查项 |
| `acceptance.failedReason` | 失败原因 |

---

## 任务生成规则

### 核心原则

1. **一任务一函数** - 每个任务严格对应一个函数
2. **细粒度拆分** - 每个任务约 300 行代码，理想为单个方法
3. **包含实现思路** - 每个任务必须有 implementationIdea 字段

### 拆分示例

原始步骤：`创建 AudioManager 单例类，包含 Play、Stop、Pause 方法`

应拆分为：

| 任务 | goal | implementationIdea |
|------|------|-------------------|
| T-001 | 创建 AudioManager 类骨架，继承 MonoBehaviour，声明字段和构造函数 | 声明 _instance 静态字段、_audioSource 组件引用，编写构造函数 |
| T-002 | 实现 Instance 属性（单例模式） | 使用 if (_instance == null) 模式检查，调用 DontDestroyOnLoad() |
| T-003 | 实现 Play(AudioClip clip) 方法 | 赋值 clip，调用 AudioSource.Play()，添加空值检查 |
| T-004 | 实现 Stop() 方法 | 调用 AudioSource.Stop() |
| T-005 | 实现 Pause() 方法 | 调用 AudioSource.Pause() |

---

## 具体工作流示例

### 阶段1: 初始化

```
Claude: 我将为"音乐播放器方案"创建 tasks.json

→ init_tasks_json(
    output_path: "/path/to/tasks_音乐播放器_20260413.json",
    plan_name: "音乐播放器方案"
  )

✓ 返回: { success: true, outputPath: "..." }
```

### 阶段2: 逐条追加

```
Claude: 读取 idea 文档，识别出 5 个函数

→ append_task(
    tasks_json_path: "...",
    goal: "创建 AudioManager 类骨架，继承 MonoBehaviour，声明字段和构造函数",
    implementation_idea: "声明 _instance 静态字段、_audioSource 组件引用，编写空构造函数",
    module: "AudioManager",
    checks: ["AudioManager.cs 文件已创建", "类继承 MonoBehaviour", "字段声明完整", "编译通过"]
  )

✓ 返回: { success: true, taskId: "T-001", totalCount: 1 }

→ append_task(...) # T-002 Instance 属性
→ append_task(...) # T-003 Play 方法
→ append_task(...) # T-004 Stop 方法
→ append_task(...) # T-005 Pause 方法

✓ 所有 5 个任务已追加
```

### 阶段3: 全局审查 + 自动修正

```
Claude: 所有任务追加完毕，进行全局审查

→ review_tasks(tasks_json_path: "...")

✓ 返回示例:
{
  success: true,
  totalCount: 5,
  issues: [
    {
      taskId: "T-004",
      issueType: "weak_implementation_idea",
      description: "implementationIdea 内容不足",
      suggestion: "补充更多细节"
    }
  ],
  summary: "共 5 个任务，4 个通过，1 个任务存在问题"
}

Claude: 发现 1 个问题，自动修正

→ update_task(
    tasks_json_path: "...",
    task_id: "T-004",
    implementation_idea: "调用 AudioSource.Stop() 停止音频播放，清理播放状态"
  )

✓ 返回: { success: true, taskId: "T-004" }

Claude: 再次审查确认通过

→ review_tasks(tasks_json_path: "...")

✓ 返回: { success: true, totalCount: 5, issues: [], summary: "共 5 个任务，5 个通过" }
```

### 阶段4: 输出结果

```
Claude: 审查通过，任务生成完毕

✓ 生成成功！
  方案名: 音乐播放器方案
  任务数: 5
  文件: /path/to/tasks_音乐播放器_20260413.json
  
  下一步: 调用 executor 工具执行任务
```

---

## 调用 executor（execution 阶段）

任务生成完成后，developer 可调用 executor 工具执行任务：

```
1. get_next_task(tasks_json_path) → 获取下一个待做任务
2. 实现该任务（编写代码）
3. update_task_result(tasks_json_path, task_id, passed, failed_reason) → 更新结果
4. 重复 1-3 直到所有任务完成
5. get_summary(tasks_json_path) → 查看完成情况
```

---

## 输出路径

```
{思路文档所在目录}/tasks_{方案名}_{日期}.json
```

---

## 完整示例

输入 `docs/需求文档/音乐播放器.md` → 输出 `docs/需求文档/tasks_音乐播放器_20260413.json`

```json
{
  "planName": "音乐播放器方案",
  "generatedAt": "2026-04-13T10:00:00Z",
  "tasks": [
    {
      "id": "T-001",
      "goal": "创建 AudioManager 类骨架，继承 MonoBehaviour，声明字段和构造函数",
      "implementationIdea": "声明 _instance 静态字段用于单例、_audioSource 组件引用。编写空构造函数确保编译通过。",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["AudioManager.cs 文件已创建", "类继承 MonoBehaviour", "字段声明完整", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-002",
      "goal": "实现 Instance 属性（单例模式）",
      "implementationIdea": "使用 if (_instance == null) 检查实例，first-time 时进行初始化，调用 DontDestroyOnLoad() 保证跨场景持久化。",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["Instance 属性已定义", "单例模式正确（null 检查 + DontDestroyOnLoad）", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-003",
      "goal": "实现 Play(AudioClip clip) 方法",
      "implementationIdea": "接收 AudioClip 参数，先进行空值检查，然后赋值给 _audioSource.clip，最后调用 _audioSource.Play()。",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["Play 方法已定义", "参数非空检查存在", "调用 AudioSource.Play()", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-004",
      "goal": "实现 Stop() 方法",
      "implementationIdea": "调用 _audioSource.Stop() 停止当前播放，无需额外参数处理。",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["Stop 方法已定义", "正确调用 AudioSource.Stop()", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-005",
      "goal": "实现 Pause() 方法",
      "implementationIdea": "调用 _audioSource.Pause() 暂停当前播放，在需要时可用 Play() 恢复。",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["Pause 方法已定义", "正确调用 AudioSource.Pause()", "编译通过"],
        "failedReason": null
      }
    }
  ]
}
```

---

## 检查清单

- [ ] idea 文档路径准备好
- [ ] 调用 init_tasks_json() 初始化 tasks.json
- [ ] 识别所有函数，逐条调用 append_task()
- [ ] 调用 review_tasks() 检查质量
- [ ] 根据 issues 调用 update_task() 修复
- [ ] 再次 review_tasks() 确认通过
- [ ] tasks.json 生成完毕，准备开始执行
