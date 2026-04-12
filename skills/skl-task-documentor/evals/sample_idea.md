# 音乐播放器实现思路文档

> **需求概述**: 游戏内音乐播放器，支持播放、暂停、切歌、列表管理

## 1. 需求概述

### 1.1 背景与动机
游戏内需要背景音乐系统，提供舒适的听觉体验。

### 1.2 核心功能
- 播放/暂停当前音乐
- 上一首/下一首切换
- 播放列表管理（添加、删除、排序）

### 1.3 预期目标
玩家可以控制游戏背景音乐的播放和切换。

---

## 4. 实现思路

### 4.1 方案名称
模块化音频管理器方案

### 4.2 核心思路
使用 Unity AudioSource 和 AudioMixer 管理音频播放。

### 4.3 实现步骤

| 序号 | 步骤名称 | 详细描述 | 关键点 |
|------|----------|----------|--------|
| 1 | 创建AudioManager类 | 单例模式，管理所有音频播放 | 保证全局唯一 |
| 2 | 创建Playlist数据类 | 存储播放列表信息 | 包含当前索引、循环模式 |
| 3 | 实现播放控制 | Play/Pause/Stop方法 | 与AudioSource交互 |
| 4 | 实现切歌逻辑 | Next/Previous方法 | 处理列表边界 |
| 5 | 创建播放列表UI | 显示歌曲列表、当前播放 | 使用UGUI |

### 4.4 模块划分

| 模块名称 | 职责 | 主要接口 | 依赖关系 |
|---------|------|---------|---------|
| AudioManager | 音频播放管理 | Play(), Pause(), Stop() | 无 |
| PlaylistManager | 播放列表管理 | Add(), Remove(), Sort() | AudioManager |
| MusicPlayerUI | 播放界面 | Show(), Hide(), Refresh() | PlaylistManager |

### 4.5 数据结构设计

```csharp
public class Playlist {
    public string Name;
    public List<AudioClip> Tracks;
    public int CurrentIndex;
    public bool IsLooping;
    public PlayMode Mode;
}

public enum PlayMode {
    Sequential,  // 顺序播放
    Shuffle,     // 随机
    RepeatOne,   // 单曲循环
    RepeatAll    // 列表循环
}
```

---

## 9. 实施建议

### 9.1 优先级建议

| 优先级 | 模块/任务 | 理由 |
|--------|-----------|------|
| P0 | AudioManager | 核心播放功能 |
| P1 | PlaylistManager | 列表管理 |
| P2 | MusicPlayerUI | 界面交互 |
