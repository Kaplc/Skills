# 任务 JSON 格式规范

## 粒度约束

每个任务必须满足：
- **代码量**：约 300 行代码（上限 500 行）
- **方法数**：理想情况单个方法，最多 3 个紧密关联方法
- **职责**：单一职责，一个任务只做一件事
- **一函数原则**：每个任务严格对应一个函数

拆分策略：
1. 创建类/模块 → 类骨架（字段+构造函数）为独立任务 + 每个方法为独立任务
2. 单一方法实现 → 直接一个任务
3. 多动作步骤 → 按动作拆分为多个任务

## 整体结构

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

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 任务唯一标识，T-001, T-002... |
| `goal` | string | 任务目标，一句话描述要做什么（**必须包含函数名**） |
| `implementationIdea` | string | 实现思路，2-4 句话说明**如何实现**（新增字段） |
| `module` | string | 所属模块名 |
| `acceptance` | object | 验收结果 |
| `acceptance.passed` | bool | 是否通过 |
| `acceptance.checks` | string[] | 验收检查项列表 |
| `acceptance.failedReason` | string? | 失败原因（可选，passed=false 时填写） |

## 示例

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
      "goal": "实现 Play(AudioClip clip) 方法，播放音频剪辑",
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
      "goal": "实现 Stop() 方法，停止当前播放",
      "implementationIdea": "调用 _audioSource.Stop() 停止播放，无需额外参数处理。",
      "module": "AudioManager",
      "acceptance": {
        "passed": false,
        "checks": ["Stop 方法已定义", "正确调用 AudioSource.Stop()", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-005",
      "goal": "实现 Pause() 方法，暂停当前播放",
      "implementationIdea": "调用 _audioSource.Pause() 暂停播放，可用 Play() 恢复。",
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

## 状态

验收结果中的 `passed` 字段表示执行结果：
- `true` = 任务完成
- `false` = 任务失败，查看 `failedReason`

## 审查规则

当调用 `review_tasks()` MCP 工具时，会检查以下规则：

1. **goal 包含函数名** - 必须包含括号 `()` 或关键词 `方法`、`函数`
2. **implementationIdea 有实质内容** - 非空，长度 > 10 字
3. **checks 至少 2 条** - 验收检查项必须充分
4. **goal 不重复** - 每个任务的 goal 必须唯一
5. **module 不为空** - 必须指定所属模块
