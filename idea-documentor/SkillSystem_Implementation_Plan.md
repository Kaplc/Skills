# 实现思路文档

> 本文档由 Idea-Documentor 自动生成
>
> **生成日期**: 2026-04-03
>
> **需求概述**: Unity ARPG游戏技能系统，包含基础攻击技能（普攻/技能释放）、技能冷却和资源消耗管理、Buff/Debuff系统
>
> ⚠️ **信息确认**: 生成本文档前，已确认以下关键信息完整：核心功能 ✓、触发条件 ✓、预期结果 ✓

---

## 1. 需求概述

### 1.1 背景与动机

当前项目 `Framework` 是一个Unity ARPG游戏框架，已经具备基础的战斗系统和伤害处理能力。现有的 `DEBattleComponent`、`AttackHandler`、`BaseAttackLogic` 等组件提供了基础的普攻框架，但缺乏完整的技能系统支持，包括：
- 统一的技能生命周期管理
- 技能冷却机制
- 资源消耗（MP/能量）管理
- Buff/Debuff状态系统
- 技能与动画/UI的联动

本次规划旨在构建一套完整、可扩展的技能系统架构，与现有的组件系统无缝集成。

### 1.2 核心功能

| 功能模块 | 描述 |
|---------|------|
| 技能组件 | 承载技能逻辑的核心组件（继承自DESkillComponent） |
| 技能数据 | ScriptableObject格式的技能配置数据 |
| 冷却管理 | 技能冷却时间跟踪与刷新 |
| 资源消耗 | MP/能量等资源的消耗与恢复管理 |
| Buff系统 | Buff/Debuff状态效果的管理与执行 |

### 1.3 预期目标

1. 实现完整的技能释放流程（触发→条件检查→消耗→执行→冷却）
2. 支持技能冷却CD和资源（MP）消耗
3. 实现模块化、可配置的Buff/Debuff系统
4. 与现有DEBattleComponent和动画系统无缝集成
5. 提供UI接口用于技能栏显示和冷却刷新

---

## 2. 需求详细分析

### 2.1 功能需求

#### 2.1.1 核心功能列表

| 功能ID | 功能名称 | 优先级 | 描述 |
|--------|----------|--------|------|
| F1 | 技能注册与初始化 | P0 | 实体启动时注册所有技能 |
| F2 | 技能触发与执行 | P0 | 响应输入触发技能，检查条件后执行 |
| F3 | 冷却时间管理 | P0 | 技能释放后进入冷却，倒计时刷新 |
| F4 | 资源消耗管理 | P0 | 技能释放消耗MP/能量，不足时不可释放 |
| F5 | Buff/Debuff效果 | P1 | 为实体添加/移除属性增益或减益 |
| F6 | 技能动画联动 | P1 | 技能播放时触发对应动画 |
| F7 | 冷却UI回调 | P1 | 冷却刷新时通知UI层更新显示 |
| F8 | 技能条件检查 | P0 | 检查冷却、资源、Buff状态等是否满足 |

#### 2.1.2 用户交互流程

```
玩家按下技能键 → 输入系统捕获 → 技能组件接收请求
    ↓
执行条件检查（冷却中？资源足够？Buff限制？）
    ↓ (通过)
资源消耗 → 技能执行 → 动画播放 → 伤害/效果应用
    ↓
进入冷却 → UI更新冷却显示 → 等待下一轮
```

### 2.2 非功能需求

| 类型 | 要求 | 优先级 |
|------|------|--------|
| 性能 | 技能系统应轻量化，避免每帧遍历大量Buff | P1 |
| 可扩展性 | 支持通过SO配置新增技能类型 | P0 |
| 可维护性 | 模块间解耦，便于后续功能迭代 | P0 |
| 数据驱动 | 技能配置通过ScriptableObject管理 | P1 |

### 2.3 约束条件

1. 必须继承现有 `DESkillComponent` 和 `DEntityBaseComponent` 体系
2. 技能数据必须使用ScriptableObject格式
3. 需要与现有的 `AttackHandler` 和 `DamageHandler` 协同工作
4. ARPG游戏对技能响应速度有较高要求，需避免复杂计算

---

## 3. 参考实现

### 3.1 项目内部参考

| 序号 | 名称 | 相关度 | 路径 | 核心方法 | 文档跳转 |
|------|------|--------|------|---------|----------|
| 1 | DESkillComponent | ⭐⭐⭐ | [DESkillComponent.cs](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Skill/Core/DESkillComponent.cs) | `OnInit(userdata)`: 组件初始化入口 | [@see DEntityBaseComponent.OnInit()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/CompSys/DEntityBaseComponent.cs) |
| 2 | BattleSkillInfo | ⭐⭐⭐ | [BattleSkillInfo/](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Skill/View/) | `skillName`: 技能标识<br>`data`: 技能数据引用 | [@see BattleSkillInfo](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Skill/View/BattleSkillInfo.cs) |
| 3 | BaseAttackLogic | ⭐⭐⭐ | [BaseAttackLogic.cs](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/BaseAttackLogic.cs) | `Initialize(info, component)`: 初始化<br>`CanExecute()`: 条件检查<br>`Execute()`: 执行技能<br>`Cancel()`: 取消技能<br>`Cd`: 冷却时间属性 | [@see BaseAttackLogic.CanExecute()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/BaseAttackLogic.cs#L19)<br>[@see BaseAttackLogic.Execute()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/BaseAttackLogic.cs#L20) |
| 4 | BaseAttackData | ⭐⭐⭐ | [BaseAttackData.cs](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/BaseAttackData.cs) | `CreateLogic()`: 创建技能逻辑实例<br>`cooldown`: 冷却时间字段<br>`attackName`: 技能名称 | [@see BaseAttackData.CreateLogic()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/BaseAttackData.cs#L15) |
| 5 | AttackHandler | ⭐⭐⭐ | [AttackHandler.cs](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/AttackHandler.cs) | `RegisterAttack(info)`: 注册技能<br>`PerformAttack(attackName)`: 执行技能<br>`CancelAttack()`: 取消当前技能<br>`GetAttackLogic<T>(skillName)`: 获取技能逻辑 | [@see AttackHandler.RegisterAttack()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/AttackHandler.cs#L20)<br>[@see AttackHandler.PerformAttack()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Attack/AttackHandler.cs#L35) |
| 6 | DEBattleComponent | ⭐⭐⭐ | [DEBattleComponent.cs](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/DEBattleComponent.cs) | `OnInit(userdata)`: 组件初始化<br>`RegisterAttack(info)`: 注册攻击<br>`PerformAttack(skillName)`: 执行攻击<br>`AddBuff<T>(buffName)`: 添加Buff<br>`GetAttackLogic<T>(skillName)`: 获取技能逻辑 | [@see DEBattleComponent.OnInit()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/DEBattleComponent.cs#L25)<br>[@see DEBattleComponent.AddBuff()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/DEBattleComponent.cs#L71) |
| 7 | DamageHandler | ⭐⭐ | [DamageHandler/](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Damage/) | `TakeDamage(damage)`: 处理伤害<br>`SetHelper(helper)`: 设置伤害辅助 | [@see DamageHandler.TakeDamage()](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Entity/Component/Battle/Damage/DamageHandler.cs) |
| 8 | BModuleManager | ⭐⭐ | [BModuleManager/](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Commom/ModuleSys/) | 模块化管理器 | [@see BModuleManager](file:///e:/UnityProject/Framework/Assets/Scripts/GameDomain/Commom/ModuleSys/BModuleManager.cs) |

### 3.2 外部参考

| 序号 | 标题 | 链接 | 借鉴内容 |
|------|------|------|----------|
| 1 | Unity Gameplay Ability System | https://blog.csdn.net/gitblog_00073/article/details/153962071 | GAS框架的Ability和Attribute设计 |
| 2 | EGamePlay | https://github.com/m969/EGamePlay | ECS模式的技能/Buff框架 |
| 3 | Unity-Buff-System | https://github.com/NoSLoofah/Unity-Buff-System | 模块化Buff系统架构 |

### 3.3 参考分析总结

**项目内部**：
- 现有的 `BaseAttackLogic` + `BaseAttackData` 模式已经提供了良好的技能逻辑和数据分离思路
- `AttackHandler` 的技能注册/获取模式可直接沿用
- `DamageHandler` 的责任链模式可借鉴到Buff效果处理

**外部方案**：
- GAS的 `GameplayEffect` 概念非常适合Buff系统设计
- ECS模式在大量实体时性能更优，但与现有框架差异较大
- Buff系统建议采用组件式依附方案，直接挂载到实体上

---

## 4. 实现思路

### 4.1 方案名称

**DESkillSystem - 模块化技能系统**

### 4.2 核心思路

基于现有框架的组件体系，构建一套分层解耦的技能系统：
- **数据层**：ScriptableObject格式的技能配置数据
- **逻辑层**：技能执行逻辑（继承BaseAttackLogic）
- **管理层**：技能组件（DESkillComponent）统一管理技能生命周期
- **Buff层**：独立的Buff效果系统，与技能系统松耦合

### 4.3 实现步骤

| 序号 | 步骤名称 | 详细描述 | 关键点 |
|------|----------|----------|--------|
| 1 | 设计技能数据结构 | 扩展BaseAttackData，新增冷却/资源/Buff配置字段 | 支持SO配置化 |
| 2 | 扩展技能执行逻辑 | 扩展BaseAttackLogic，新增冷却检查/资源消耗/Buff应用 | 调用AttackHandler实现 |
| 3 | 实现冷却管理系统 | SkillCooldownManager管理所有技能的冷却状态 | 使用Dictionary缓存 |
| 4 | 实现资源管理系统 | SkillResourceManager管理MP/能量等资源 | 支持恢复和消耗 |
| 5 | 设计Buff数据结构 | BuffData SO定义效果类型、持续时间、叠加规则 | 支持属性修改和状态标记 |
| 6 | 实现Buff执行器 | BuffApplier负责Buff的添加/移除/_tick | 定时器触发 |
| 7 | 集成到DESkillComponent | 技能组件初始化时创建管理器和注册技能 | OnInit钩子 |
| 8 | 提供UI回调接口 | IOnCooldownReady/ICooldownChanged等事件接口 | 通知UI层 |
| 9 | 扩展动画联动 | 技能执行时触发动画事件回调 | AnimationEvent |
| 10 | 编写配置工具 | SkillDataSO和BuffDataSO的Editor工具 | 提升配置效率 |

### 4.4 模块划分

| 模块名称 | 职责 | 主要接口 | 依赖关系 |
|---------|------|---------|---------|
| SkillData | 技能配置数据SO | CreateLogic() | 无 |
| SkillLogic | 技能执行逻辑 | CanExecute/Execute/Cancel | SkillData, BuffSystem |
| SkillCooldownManager | 冷却时间管理 | StartCooldown/IsReady/GetRemaining | 无 |
| SkillResourceManager | 资源（MP/能量）管理 | Consume/Recover/IsEnough | 无 |
| BuffData | Buff效果配置SO | EffectType/Duration/Stacking | 无 |
| BuffApplier | Buff执行与移除 | Apply/Remove/Tick | BuffData, BuffEffect |
| BuffEffect | Buff效果具体实现 | OnApply/OnRemove/OnTick | BuffData |
| DESkillComponent | 技能系统宿主 | RegisterSkill/TriggerSkill | 以上所有 |

### 4.5 数据结构设计

#### 5.1 核心数据结构

```csharp
// 技能数据（扩展自BaseAttackData）
public class SkillData : BaseAttackData
{
    public float cooldown;           // 冷却时间（秒）
    public float mpCost;             // MP消耗
    public float energyCost;         // 能量消耗
    public float castTime;           // 吟唱时间（秒）
    public bool requireTarget;       // 是否需要目标
    public List<string> requiredBuffs;   // 需要的Buff
    public List<string> applyBuffs;      // 释放后应用的Buff
}

// 技能状态
public class SkillState
{
    public SkillData data;
    public float cooldownTimer;      // 当前冷却计时
    public bool isCasting;           // 是否在吟唱中
    public float castTimer;          // 吟唱计时
    public bool isExecuting;         // 是否在执行中
}

// Buff数据（ScriptableObject）
[CreateAssetMenu]
public class BuffData : ScriptableObject
{
    public string buffName;
    public EBuffType buffType;       // Buff/Debuff/Neutral
    public EBuffEffectType effectType; // 属性修改/状态标记/持续伤害等
    public float duration;           // 持续时间（秒），-1表示永久
    public EStackingRule stackingRule; // 叠加规则
    public int maxStacks;            // 最大层数
    public List<AttributeModifier> modifiers; // 属性修饰
}

// 属性修饰
[System.Serializable]
public class AttributeModifier
{
    public EAttributeType attribute;
    public float baseValue;
    public EModifierType modifierType; // 加成/减成/直接设置
}

// Buff状态实例
public class BuffInstance
{
    public BuffData data;
    public float remainingTime;
    public int currentStacks;
    public object source;           // 来源（技能/物品等）
}
```

#### 5.2 数据流转图

```
【输入触发】
    ↓
【SkillComponent.TriggerSkill(skillId)】
    ↓
【检查冷却】→ [未冷却] → 检查资源 → [资源足够]
    ↓
【消耗资源】→ 【执行SkillLogic.Execute()】
    ↓
【应用Buff】→ 【播放动画/特效】
    ↓
【启动冷却】→ 【重置cooldownTimer】
    ↓
【UI回调】 → 【OnCooldownChanged/OnCooldownReady】
```

### 4.6 关键算法

#### 6.1 算法设计

**冷却管理算法**：
- 使用Dictionary<string, float>存储技能ID到冷却剩余时间的映射
- 每帧Update时递减所有非零的冷却值
- 技能触发时检查cooldownTimer是否为0

**Buff_tick算法**：
- 每帧遍历所有active Buff
- 对每个Buff调用其Effect.OnTick()
- 递减remainingTime
- 当remainingTime<=0时触发OnRemove并移除

**叠加规则处理**：
- Ignore：直接替换旧Buff，重置持续时间
- Stack：增加层数，不重置持续时间
- Refresh：重置持续时间，保持层数
- Limit：层数达到max时不再叠加

#### 6.2 伪代码/流程

```
// 技能触发流程
Function TriggerSkill(skillId):
    skillState = GetSkillState(skillId)
    
    // 冷却检查
    IF skillState.cooldownTimer > 0 THEN
        RETURN False, "技能还在冷却中"
    
    // 资源检查
    IF NOT resourceManager.IsEnough(skillState.data.mpCost) THEN
        RETURN False, "资源不足"
    
    // Buff前置条件检查
    IF NOT CheckRequiredBuffs(skillState.data) THEN
        RETURN False, "缺少前置Buff"
    
    // 消耗资源
    resourceManager.Consume(skillState.data.mpCost)
    
    // 执行技能逻辑
    skillLogic.Execute()
    
    // 应用Buff
    FOR EACH buffId IN skillState.data.applyBuffs:
        buffApplier.Apply(buffId, source=self)
    
    // 启动冷却
    cooldownManager.StartCooldown(skillId, skillState.data.cooldown)
    
    // UI通知
    eventBus.Emit("OnCooldownChanged", skillId)
    
    RETURN True, "释放成功"
```

---

## 5. 逻辑链

### 5.1 流程概览

技能系统核心流程分为五个阶段：
1. **注册阶段**：实体初始化时注册所有技能
2. **触发阶段**：响应输入，接收技能释放请求
3. **检查阶段**：验证冷却、资源、前置条件
4. **执行阶段**：消耗资源、执行逻辑、应用效果、进入冷却
5. **回调阶段**：通知UI更新、动画系统等

### 5.2 详细逻辑链

| 步骤 | 节点名称 | 节点类型 | 详细描述 | 输入 | 输出 | 决策条件 |
|------|----------|----------|----------|------|------|----------|
| 1 | OnInit | 入口 | 实体初始化，DESkillComponent.OnInit被调用 | userData | - | - |
| 2 | RegisterSkills | 处理 | 遍历SkillDataList，注册所有技能到Handler | skillList | skillStateMap | - |
| 3 | TriggerSkill | 入口 | 外部调用触发技能 | skillId | success, reason | - |
| 4 | CheckCooldown | 决策 | 检查冷却状态 | cooldownTimer | canExecute | cooldownTimer == 0 |
| 5 | CheckResource | 决策 | 检查资源是否足够 | mpCost, currentMp | canExecute | currentMp >= mpCost |
| 6 | CheckBuffs | 决策 | 检查前置Buff需求 | requiredBuffs | canExecute | 满足所有前置 |
| 7 | ConsumeResource | 处理 | 消耗MP/能量 | mpCost | newMp | - |
| 8 | ExecuteLogic | 处理 | 调用skillLogic.Execute() | - | - | - |
| 9 | ApplyBuffs | 处理 | 为目标应用Buff | buffId, target | buffInstance | - |
| 10 | StartCooldown | 处理 | 启动技能冷却 | skillId, cdTime | cooldownTimer = cdTime | - |
| 11 | NotifyUI | 处理 | 通知UI层更新 | skillId, remaining | - | - |
| 12 | OnUpdate | 入口 | 每帧更新 | deltaTime | - | - |
| 13 | TickCooldowns | 处理 | 递减所有冷却计时 | deltaTime | cooldownTimer | - |
| 14 | TickBuffs | 处理 | tick所有Buff持续时间 | deltaTime | remainingTime | - |

### 5.3 异常处理流程

| 异常场景 | 检测点 | 处理方式 | 回滚策略 |
|----------|--------|---------|----------|
| 冷却中触发技能 | CheckCooldown | 返还false，附带原因 | 无需回滚 |
| 资源不足 | CheckResource | 返还false，不消耗 | 无需回滚 |
| 技能执行异常 | ExecuteLogic | 捕获异常，记录日志 | 清除执行状态标志 |
| Buff应用失败 | ApplyBuffs | 跳过该Buff，继续其他 | 无回滚 |
| 实体已销毁 | 任意Update | 检查isActive，快速退出 | 无 |

---

## 6. 思路解析原理

### 6.1 设计模式应用

| 模式名称 | 应用场景 | 为什么使用 | 实现方式 |
|----------|----------|-----------|---------|
| Template Method | 技能逻辑执行 | 不同技能有相同的执行流程，但具体实现不同 | 继承BaseAttackLogic，重写虚方法 |
| Observer | UI回调通知 | 技能状态变化需要通知多个UI组件 | IOnCooldownReady等接口 |
| Object Pool | Buff实例管理 | 避免频繁创建销毁Buff实例 | 池化BuffInstance |
| Command | 技能取消 | 支持玩家主动取消吟唱/执行中的技能 | CancelCommand |

### 6.2 核心机制原理

#### 7.1 机制概述

技能系统的核心是**状态机+事件驱动**：
- 每个技能有自己的状态（Ready/Casting/Executing/Cooldown）
- 状态转换通过事件驱动（SkillStarted/SkillEnded/CooldownStarted等）
- 外部系统（UI/动画）通过订阅事件感知变化

#### 7.2 原理详述

**冷却机制**：采用"倒计时"模式，每帧递减而非定时触发：
```csharp
// 每帧调用
cooldownTimer -= deltaTime;
if (cooldownTimer < 0) cooldownTimer = 0;
```

**Buff叠加**：通过StackingRule枚举控制叠加行为，新Buff应用时查询已有Buff实例：
```csharp
switch (existing.stackingRule):
    case Ignore: replace(existing, new); break;
    case Stack: existing.stacks++; break;
    case Refresh: existing.remainTime = data.duration; break;
```

#### 7.3 关键实现点

1. **技能与战斗系统集成**：通过DEBattleComponent.GetAttackLogic<T>()获取技能逻辑
2. **Buff挂载位置**：BuffInstance挂载在目标的BuffContainer子节点下
3. **属性修改时机**：属性在Buff Apply时计算，最终伤害时生效

### 6.3 技术要点

| 技术要点 | 说明 | 注意事项 |
|---------|------|----------|
| ScriptableObject引用 | 技能/Buff数据以SO形式存在 | 编辑器下修改会污染资源，建议使用Prefab变体 |
| Update频率 | 冷却和Buff每帧更新 | 可考虑使用计时器批量处理减少Update调用 |
| 对象引用 | BuffInstance持有技能/实体引用 | 实体销毁时需清除相关Buff |
| 事件泄漏 | Observer模式需注意注销 | OnDisable时统一注销所有事件 |

---

## 7. 优缺点分析

### 7.1 优点

| 优点 | 说明 | 量化指标（可选） |
|------|------|-----------------|
| 模块化设计 | 各模块职责清晰，便于单独测试和维护 | - |
| 数据驱动 | 技能/Buff配置通过SO管理，热更新友好 | 配置变更无需编译 |
| 可扩展性 | 新增技能只需创建新的SkillData+SkillLogic | 新增一个SO文件即可 |
| 与现有框架兼容 | 直接继承/使用现有BaseAttackLogic等 | 复用AttackHandler |
| 性能可控 | 冷却/Buff使用Dictionary存储，按需遍历 | O(1)查找 |

### 7.2 缺点

| 缺点 | 说明 | 严重程度 | 缓解措施 |
|------|------|----------|----------|
| 初期开发量大 | 需要构建完整的Skill+Buff框架 | 中 | 分阶段迭代实现 |
| Buff数量多时遍历成本 | 每帧遍历所有Buff_tick | 中 | 按类型分组或使用计时器 |
| 状态同步复杂 | 联机时冷却/CD需同步 | 高 | 预留网络同步接口 |

### 7.3 适用场景

| 场景 | 适用性分析 |
|------|-----------|
| ARPG游戏 | 技能数量多、需要动画联动，本方案非常适合 |
| MOBA游戏 | 技能+Buff是核心，本方案可扩展 |
| 回合制RPG | 技能释放时机明确，冷却机制简化后可适配 |

### 7.4 不适用场景

| 场景 | 原因分析 |
|------|----------|
| 大量同屏敌人 | Buff每实体维护，需优化遍历 |
| 极简原型 | 框架有一定复杂度，直接硬编码更快 |

### 7.5 方案对比

| 对比维度 | 本方案 | 硬编码方案 | GAS框架 |
|----------|--------|-----------|---------|
| 开发效率 | 中 | 高（初期） | 低（学习成本） |
| 可维护性 | 高 | 低 | 高 |
| 性能 | 中 | 高 | 中 |
| 扩展性 | 高 | 低 | 高 |
| 耦合度 | 低 | 高 | 中 |

---

## 8. 风险与注意事项

### 8.1 风险识别

| 风险ID | 风险描述 | 发生概率 | 影响程度 | 应对措施 |
|--------|----------|----------|----------|----------|
| R1 | 技能数据SO在运行时被修改 | 低 | 高 | 使用 Instantiate() 而非直接引用 |
| R2 | Buff_apply时目标已销毁 | 中 | 中 | 添加空引用检查和异常捕获 |
| R3 | 冷却计时精度问题 | 低 | 低 | 使用float而非int，累积误差用固定步长修正 |
| R4 | 循环Buff导致死循环 | 极低 | 高 | Buff_tick设置最大执行次数保护 |

### 8.2 注意事项

1. **数据克隆**：从SO读取技能数据后必须Clone，避免污染原数据
2. **生命周期**：Buff/技能组件需要在实体OnDestroy时正确清理
3. **事件注销**：使用Observer模式时确保OnDisable时注销事件
4. **线程安全**：如有DOTS/JobSystem，注意数据布局和对齐

---

## 9. 实施建议

### 9.1 优先级建议

| 阶段 | 功能 | 优先级 |
|------|------|--------|
| Phase 1 | SkillData + SkillLogic + 冷却管理 | P0 |
| Phase 1 | 基础资源消耗 | P0 |
| Phase 2 | BuffData + BuffApplier + 效果系统 | P1 |
| Phase 2 | UI回调接口 | P1 |
| Phase 3 | 动画联动 | P2 |
| Phase 3 | 配置工具Editor | P2 |

### 9.2 里程碑规划

| 里程碑 | 内容 | 验收标准 |
|--------|------|----------|
| M1 | 完成基础技能释放 | 可以注册技能、触发执行、进入冷却 |
| M2 | 完成资源消耗 | MP足够时可释放，不足时提示 |
| M3 | 完成Buff系统 | 可添加/移除Buff，属性修改生效 |
| M4 | 完成UI联动 | 冷却时UI显示倒计时，结束时报知 |

### 9.3 测试建议

1. **单元测试**：各模块独立测试（冷却计算、Buff叠加等）
2. **集成测试**：技能完整流程测试（触发→消耗→执行→冷却）
3. **压力测试**：大量Buff同时存在时的性能
4. **边界测试**：资源恰好够用/不足、冷却恰好结束等

---

## 10. 总结

本方案针对ARPG游戏的技能系统需求，结合现有框架（DESkillComponent、BaseAttackLogic、AttackHandler等），设计了一套模块化、数据驱动的技能系统架构。

**核心价值**：
- 复用现有框架，降低接入成本
- ScriptableObject配置化，便于策划调整
- Buff系统独立设计，支持复杂效果
- 预留扩展点，可后续接入网络同步

**实施建议**：
- 采用分阶段迭代，优先实现核心释放流程
- 冷却和Buff模块可并行开发
- 早期预留网络同步接口，避免后期重构

---

**文档信息**
- 生成工具: Idea-Documentor
- 生成日期: 2026-04-02
- 文档版本: v1.0