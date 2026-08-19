# 论文 P2：异构运动学平台混编与跨楼层协同 SLAM / 定位

> 跨楼层是学术攻关点，不进入当前产品承诺。本文档为研究框架，尚无跨楼层 measured 证据。

## 1. 研究定位与差异化

**【设计决策】** 本方向研究异构机器人在多层环境中的协同定位，不把“不同平台接入网关”直接包装成论文创新。

核心问题是：

- 传感器配置不同；
- 运动学约束不同；
- 局部坐标系和楼层坐标系不同；
- 楼梯、电梯、坡道等跨层连接关系需要显式建模；
- 错误的跨层匹配可能造成全局地图错误闭环。

**【待补充】** 当前尚未确认跨楼层观测、平台组合、数据集和可复现实验场景。

## 2. 摘要草案

异构机器人协同定位面临传感器配置、运动学约束、观测视角和可通行区域不同等问题。当机器人分布在不同楼层或高度层时，传统的二维地图对齐和统一位姿图优化难以表达楼层间的拓扑关系，也难以处理不同机器人运动模型带来的观测不一致。本文拟研究一种面向异构机器人和多层环境的拓扑感知协同定位框架，将局部几何地图、楼层拓扑、机器人运动学约束和跨层观测关联进行统一表示。各机器人首先在本地估计自身状态及局部结构，随后通过跨层连接区域、共享语义标志或相对观测建立层间约束，并由协同后端执行全局状态优化。我们计划在四足、轮式和人形机器人组合，以及不同传感器配置和通信条件下进行评估，比较二维平面拼接、无拓扑约束的三维融合和本文方法在定位误差、跨层匹配准确率、地图一致性和通信开销方面的差异。该研究旨在验证显式建模多层拓扑和异构运动约束是否能够提高复杂建筑环境中的协同定位可靠性。

> **【待补充】** 摘要中的效果性结论必须由跨楼层实验确认，当前不能写入具体提升数值。

## 3. 论文框架

### 3.1 Introduction

- 异构机器人协同定位的传感器和运动学差异；
- 跨楼层不是普通二维地图拼接问题；
- 传统三维融合缺少楼层拓扑和可行运动约束；
- 错误跨层关联对全局优化的风险；
- 本文问题、假设和贡献。

建议贡献：

1. 提出面向多层环境的异构机器人拓扑表示；
2. 将跨层连接和异构运动约束纳入协同定位；
3. 建立跨平台、跨楼层和弱网条件下的对照实验协议。

### 3.2 Related Work

1. Heterogeneous Multi-Robot SLAM；
2. Multi-Floor / Multi-Level Mapping；
3. Topological Navigation；
4. Cross-Modal Place Recognition；
5. Distributed Pose Graph Optimization。

### 3.3 Problem Formulation

定义：

- 多层空间拓扑图；
- 机器人局部坐标系与楼层坐标系；
- 跨层连接边；
- 机器人运动学可行域；
- 异构传感器观测模型；
- 跨机器人相对约束；
- 错误关联拒绝和回退条件。

### 3.4 Method

1. Multi-level spatial representation；
2. Heterogeneous robot state model；
3. Cross-floor connection detection；
4. Topology-aware inter-robot constraints；
5. Distributed global optimization；
6. Incorrect association rejection；
7. Failure recovery and local fallback。

其中“错误关联拒绝”是安全关键环节，不能只展示成功匹配案例。

### 3.5 System and Data Flow

```text
Heterogeneous robot observations
        ↓
Local geometric states
        ↓
Cross-floor / cross-modal association
        ↓
Topology-aware constraints
        ↓
Collaborative optimization
        ↓
Multi-level map and localization feedback
```

### 3.6 Experimental Setup

平台组合候选：

- 四足 + 轮式；
- 四足 + 人形；
- 激光 + RGB-D；
- 同层与跨层混合。

场景候选：

- 楼梯；
- 电梯；
- 坡道；
- 结构相似但外观不同的楼层区域；
- 动态障碍或临时封闭连接区域。

**【待补充】** 平台、场景、传感器标定和跨层真值来源需在立项前确认。

### 3.7 Baselines and Metrics

对照方法：

- 独立单机定位后拼接；
- 普通多机位姿图；
- 无拓扑约束的三维融合；
- 仅使用视觉地点识别的方法；
- 本文拓扑约束方法。

指标：

- ATE / RPE；
- 跨层匹配 Precision / Recall；
- 错误闭环率；
- 地图融合误差；
- 多机器人任务成功率；
- 优化时间；
- 通信开销；
- 失败恢复时间。

### 3.8 Ablation

- 去掉楼层拓扑；
- 去掉运动学约束；
- 去掉跨层连接检测；
- 去掉错误关联拒绝；
- 不同传感器组合；
- 不同楼层数量；
- 稳定网络与弱网条件。

### 3.9 Limitations and Conclusion

需要明确：

- 跨层连接检测依赖可观测结构；
- 电梯等动态环境可能破坏静态拓扑假设；
- 时间同步和跨平台标定是工程约束；
- 本方向不代表当前产品 P0 已支持跨楼层；
- 当前跨楼层结果【待补充】。

## 4. 实验前置条件

- 明确跨楼层问题定义和平台组合；
- 获得带楼层真值或可复现的场景数据；
- 完成异构传感器时间与坐标标定；
- 建立跨层关联错误注入与拒绝测试；
- 先完成 Go2 / Swarm-SLAM P0 基线，再决定是否进入实现。

## 5. 状态与下一步

**【事实】** 当前状态为 `idea`，目标为 ICRA / IROS。  
**【设计决策】** P2 仅作为学术攻关线，不进入当前产品主线承诺。  
**【待补充】** 跨楼层数据、平台组合、拓扑表示、基线实现和实测结果。

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | PAPER-P2-001 |
| type | paper |
| title | 异构运动学平台混编与跨楼层协同 SLAM/定位 |
| target | ICRA / IROS |
| stage | idea |
| status | todo |
| priority | ★★★★☆ |
| confidentiality | internal |
| knowledge_refs | CAP-SLAM-SWARM-SLAM-GATE-001；CAP-SLAM-KIMERA-MULTI-REF-001 |
| patent_refs | 【待补充】 |
| next | 先完成跨楼层问题定义与数据可行性评估 |
| updated | 2026-07-21 |
