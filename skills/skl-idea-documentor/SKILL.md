---
name: skl-idea-documentor
description: >
  当用户想构建某个功能或系统、需要规划实现方案时使用。
  典型触发场景：用户描述了一个想做的功能（如背包系统、音乐播放器、任务队列、AI机器人），并询问怎么实现、如何设计架构、给我思路、帮我规划。
  Use this skill when the user describes a feature or system they want to build and asks how to approach it —
  design questions, architecture planning, or implementation roadmaps for new functionality.
  Works for any stack (Unity, web, backend, AI, etc.).
  Output includes requirements analysis, module breakdown, call chains, file list, pros/cons.
  Do NOT use for reading existing files, running commands, or executing defined tasks.
---

# Idea-Documentor

将模糊需求转化为结构化实现思路文档。

**输入**: 用户需求 → **输出**: 实现思路文档（按 TEMPLATE.md 格式）

---

## 工作流程

```
需求 → [澄清] → [收集参考] → [构建方案] → [生成文档]
```

---

## Stage 1: 需求澄清

**目标**: 确认核心要素，避免错误假设

### 必问三要素（不明确时必须问）

| 要素 | 问题 |
|------|------|
| 核心功能 | 具体要实现什么？ |
| 触发条件 | 什么操作/事件触发？ |
| 预期结果 | 期望达到什么效果？ |

### 推断原则

- ✅ 上下文/项目已有代码能推断的：自行推断并在输出中注明假设
- ❌ 三要素不明确时：**必须询问**，不得自行假设

### 询问格式

```
分析后有几点不明确：

❓ {问题1}: {具体描述}
❓ {问题2}: {具体描述}
```

---

## Stage 2: 参考收集

**目标**: 找到可借鉴的实现

### 项目内参考

1. 用 `Grep` / `Glob` 搜索相关类/模块
2. 提取核心方法签名和用途
3. 路径格式：`[文件名.ext](file:///{绝对路径}#L行号)`

### 项目外参考

用 `WebSearch` 搜索最佳实践，记录标题、链接、借鉴内容。

### 输出表格

| 类型 | 名称 | 相关度 | 路径 | 核心方法 | 文档跳转 |
|------|------|--------|------|---------|----------|

相关度：⭐⭐⭐（高）/ ⭐⭐（中）/ ⭐（低）

---

## Stage 3: 构建方案

### 必须包含

| 字段 | 说明 |
|------|------|
| 方案名称 | 清晰易记的名称 |
| 核心思路 | 一句话描述核心思想 |
| 实现步骤 | 序号列表，每步可执行 |
| 模块划分 | 模块名: 职责 |
| 相关文件 | 列出所有需新建或修改的文件路径、操作类型、说明 |
| 数据结构 | 核心数据结构设计 |
| 调用链 | 调用方 → 被调用方 → 方法 → 参数 → 返回值 |

### 调用链格式

```
| 步骤 | 调用方 | 被调用方 | 方法/接口 | 传入参数 | 返回值 | 备注 |
|------|--------|---------|----------|---------|--------|------|
| 1    | UIManager | AudioManager | Play(clip) | AudioClip | void | 点击播放按钮触发 |
| 2    | AudioManager | AudioSource | Play() | - | void | 实际播放 |
```

### 相关文件格式

```
| 文件路径 | 操作 | 说明 |
|---------|------|------|
| Assets/Scripts/AudioManager.cs | 新建 | 单例音频管理器 |
| Assets/Scripts/PlaylistManager.cs | 新建 | 播放列表逻辑 |
| Assets/Scenes/Main.unity | 修改 | 挂载 AudioManager 组件 |
```

操作类型：**新建** / **修改** / **删除**

### 优缺点分析

- **优点**: 至少 2 条，说明为什么
- **缺点**: 至少 2 条，说明 + 缓解措施
- **适用场景**: 至少 1 个
- **不适用场景**: 至少 1 个

---

## Stage 4: 生成文档

1. 读取 `TEMPLATE.md`
2. 替换所有占位符 `{xxx}`
3. 保存到 `{workspace}/docs/需求文档_{日期}.md`

### 约束

- 所有占位符必须填充
- 表格不能留空单元格
- 代码块标注语言

---

## 检查清单

- [ ] 核心三要素已确认
- [ ] 参考实现：项目内 + 项目外
- [ ] 路径使用 Markdown 链接格式
- [ ] 相关文件表格已填写（新建/修改/删除）
- [ ] 调用链有完整的调用方→被调用方→方法→参数→返回值
- [ ] 优缺点各至少 2 条
- [ ] 所有占位符已替换
- [ ] 文档已保存
