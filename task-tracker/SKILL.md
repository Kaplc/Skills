---
name: task-tracker
description: 从任务文档中提取任务清单，通过内置的任务跟踪系统管理实现进度。用于跟踪和管理开发任务的执行状态，支持查看任务列表、更新任务状态、查看完成进度等操作。
---

# Task-Tracker - 任务跟踪器

**核心目标**: 从任务文档中提取任务清单，提供任务状态跟踪能力

**输入**: 任务文档路径或思路文档路径
**输出**: 任务跟踪状态

---

## 工作流程概览

```
任务文档 → Stage 1 加载任务 → Stage 2 解析任务 → Stage 3 状态跟踪 → Stage 4 进度展示
```

---

## Stage 1: 加载任务文档

**输入**: 文档路径（绝对路径或相对于 workspace 的路径）
**输出**: 文档内容

### 处理步骤

1. **解析路径** - 判断是绝对路径还是相对路径
2. **读取文档** - 使用 `read_file` 读取完整内容
3. **识别文档类型** - 判断是任务文档还是思路文档

### 文档类型识别

| 类型 | 识别特征 | 处理方式 |
|------|----------|----------|
| 任务文档 | 包含 `[T-XXX]` 格式任务ID | 直接解析任务列表 |
| 思路文档 | 包含模块划分表格 | 调用 task-documentor 生成任务文档后再解析 |

### 路径规范

```
绝对路径: e:/UnityProject/Framework/docs/开发任务/SkillData_20260403.md
相对路径: docs/开发任务/SkillData_20260403.md
```

---

## Stage 2: 解析任务列表

**输入**: 文档内容
**输出**: 结构化任务列表

### 处理步骤

1. **提取任务总览表** - 解析任务ID、名称、时间、依赖
2. **提取任务详情** - 解析每个任务的详细步骤
3. **构建任务依赖图** - 确定执行顺序
4. **计算初始状态** - 所有任务默认为 `pending`

### 解析规则

#### 任务ID格式

```
[T-XXX] 或 [Task-XXX]
其中 XXX 为三位数字编号
```

#### 任务字段

| 字段 | 来源 | 说明 |
|------|------|------|
| id | `[T-001]` | 唯一标识 |
| name | 标题行 | 任务名称 |
| module | 所属模块 | 所属模块名称 |
| estimatedTime | 预计时间 | 分钟数 |
| dependency | 依赖 | 依赖的任务ID |
| type | 任务类型 | 创建/修改/配置/集成 |
| status | 状态 | pending/in_progress/completed/cancelled |
| steps | 详细步骤 | 具体代码操作 |
| acceptance | 验收标准 | 验证点列表 |

---

## Stage 3: 任务状态跟踪

**输入**: 任务列表 + 操作指令
**输出**: 更新后的状态

### 状态定义

| 状态 | 说明 | 可转换目标 |
|------|------|------------|
| pending | 待开始 | in_progress |
| in_progress | 进行中 | completed, pending |
| completed | 已完成 | - (不可逆) |
| cancelled | 已取消 | - (不可逆) |

### 操作命令

#### 查看任务列表

```
命令: list
展示: 所有任务或指定模块的任务
选项:
  - --all: 显示所有任务
  - --module {name}: 显示指定模块的任务
  - --status {status}: 显示指定状态的任务
  - --pending: 显示待开始任务
  - --in-progress: 显示进行中任务
  - --completed: 显示已完成任务
```

#### 查看任务详情

```
命令: show
参数: {task_id}
展示: 任务的完整信息，包括步骤和验收标准
```

#### 更新任务状态

```
命令: update
参数: {task_id} {new_status}
示例: update T-001 completed
验证:
  - 状态转换是否合法
  - 依赖任务是否已完成 (如果是开始新任务)
```

#### 标记任务开始

```
命令: start
参数: {task_id}
等价于: update {task_id} in_progress
前置检查:
  - 依赖任务是否全部完成
  - 任务状态是否为 pending
```

#### 标记任务完成

```
命令: done
参数: {task_id}
等价于: update {task_id} completed
验证:
  - 任务状态是否为 in_progress
  - 可选：要求确认验收标准已满足
```

---

## Stage 4: 进度展示

**输入**: 当前任务状态
**输出**: 格式化展示

### 展示格式

#### 简洁模式 (默认)

```
📋 任务跟踪 - {模块名称}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[■■■■□□□□□□] 4/10 (40%)
  ✅ 已完成: 4
  🔄 进行中: 1
  ⏳ 待开始: 5

最近更新:
  • T-004 创建SkillData类 [completed] 2分钟前
  • T-005 添加冷却字段 [in_progress] 进行中
```

#### 详细模式 (--verbose)

```
📋 任务跟踪详情 - {模块名称}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

模块进度: [■■■■■■■□□□] 6/10 (60%)
预计剩余时间: 25分钟

任务列表:
  ✅ [T-001] 创建SkillData类 (3分钟)
  ✅ [T-002] 添加cooldown字段 (2分钟)
  🔄 [T-003] 实现CanExecute方法 (5分钟) ← 进行中
  ⏳ [T-004] 实现Execute方法 (5分钟)
  ⏳ [T-005] 实现Cancel方法 (3分钟)
```

#### 看板模式 (--board)

```
🎯 任务看板 - {模块名称}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 待办 (5)
  ⏳ T-004 实现Execute方法
  ⏳ T-005 实现Cancel方法
  ⏳ T-006 添加资源消耗
  ...

🚀 进行中 (1)
  🔄 T-003 实现CanExecute方法
     依赖: T-001, T-002 ✅
     进度: 第2步/5步

✅ 已完成 (4)
  ✅ T-001 创建SkillData类
  ✅ T-002 添加cooldown字段
  ...
```

---

## 任务跟踪系统

### 内置任务清单存储

任务状态保存在 `~/.codebuddy/task-tracker/{document_hash}/tasks.json`

```
结构:
{
  "documentPath": "e:/.../SkillData_开发任务.md",
  "documentHash": "abc123",
  "lastUpdated": "2026-04-03T00:24:00",
  "tasks": [
    {
      "id": "T-001",
      "name": "创建SkillData类",
      "module": "SkillData",
      "status": "completed",
      "startedAt": "2026-04-03T00:20:00",
      "completedAt": "2026-04-03T00:22:00",
      "notes": ""
    }
  ],
  "stats": {
    "total": 10,
    "completed": 4,
    "inProgress": 1,
    "pending": 5,
    "cancelled": 0,
    "totalTime": 45,
    "spentTime": 20,
    "remainingTime": 25
  }
}
```

### 状态持久化

- 每次 `update` 操作自动保存
- 保存路径: `~/.codebuddy/task-tracker/{文档哈希}/`
- 多文档支持: 每个文档独立存储

---

## 常用命令参考

| 命令 | 说明 | 示例 |
|------|------|------|
| `load {path}` | 加载任务文档 | `load docs/开发任务/SkillData.md` |
| `list` | 显示所有任务 | `list --status pending` |
| `show {id}` | 显示任务详情 | `show T-001` |
| `start {id}` | 开始任务 | `start T-003` |
| `done {id}` | 完成任务 | `done T-002` |
| `update {id} {status}` | 更新状态 | `update T-004 cancelled` |
| `progress` | 显示进度 | `progress --verbose` |
| `board` | 看板视图 | `board --module SkillData` |
| `reset` | 重置所有状态 | `reset --confirm` |
| `export` | 导出进度报告 | `export --format markdown` |

---

## 注意事项

1. **状态转换限制**: 只有 `pending` 才能转为 `in_progress`，只有 `in_progress` 才能转为 `completed`
2. **依赖检查**: `start` 命令会检查依赖任务是否已完成
3. **文档更新**: 如果源文档被修改，需要重新 `load`
4. **数据安全**: 任务数据保存在用户目录下，不会随项目删除

---

## 执行检查清单

执行命令前，逐项确认：

- [ ] 文档路径正确
- [ ] 文档已正确加载
- [ ] 目标任务存在
- [ ] 状态转换合法
- [ ] 依赖任务条件满足（如适用）
