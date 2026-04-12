# 任务 JSON 格式规范

## 粒度约束

每个任务必须满足：
- **代码量**：约 300 行代码（上限 500 行）
- **方法数**：理想情况单个方法，最多 3 个紧密关联方法
- **职责**：单一职责，一个任务只做一件事

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
      "goal": "创建 AudioManager 单例类",
      "acceptance": {
        "passed": true,
        "checks": ["文件已创建", "类定义存在", "编译通过"],
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
| `goal` | string | 任务目标，一句话描述要做什么 |
| `acceptance` | object | 验收结果 |
| `acceptance.passed` | bool | 是否通过 |
| `acceptance.checks` | string[] | 验收检查项列表 |
| `acceptance.failedReason` | string? | 失败原因（可选） |

## 示例

```json
{
  "planName": "音乐播放器方案",
  "generatedAt": "2026-04-12T10:00:00Z",
  "tasks": [
    {
      "id": "T-001",
      "goal": "创建 AudioManager 类骨架，继承 MonoBehaviour，声明字段和构造函数",
      "acceptance": {
        "passed": false,
        "checks": ["AudioManager 文件已创建", "类继承 MonoBehaviour", "字段声明完整", "构造函数已创建"],
        "failedReason": "编译失败: 缺少 using UnityEngine"
      }
    },
    {
      "id": "T-002",
      "goal": "实现 Instance 属性",
      "acceptance": {
        "passed": false,
        "checks": ["Instance 方法已定义", "方法逻辑完整", "编译通过"],
        "failedReason": null
      }
    },
    {
      "id": "T-003",
      "goal": "实现 Play(AudioClip clip) 方法",
      "acceptance": {
        "passed": true,
        "checks": ["Play 方法已定义", "方法参数正确", "方法逻辑完整", "编译通过"],
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
