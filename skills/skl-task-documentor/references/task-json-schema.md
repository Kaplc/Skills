# 任务 JSON 格式规范

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
      "goal": "创建 AudioManager 单例类",
      "acceptance": {
        "passed": false,
        "checks": ["文件已创建", "类定义存在"],
        "failedReason": "编译失败: 缺少 using UnityEngine"
      }
    },
    {
      "id": "T-002",
      "goal": "实现 Play 方法",
      "acceptance": {
        "passed": true,
        "checks": ["方法已添加", "参数正确", "编译通过"],
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
