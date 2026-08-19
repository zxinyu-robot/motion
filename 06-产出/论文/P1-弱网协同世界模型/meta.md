# 论文 P1：弱网边缘的多机协同世界模型与 SLAM 几何锚定

> 当前为论文 outline 草案，不是可投稿正文。完整方法细节受 `PAT-SLAM-TOKEN-MAIN` 专利分流约束。

## 1. 研究定位与差异化

**【推断】** 现有世界模型导航通常更偏单机、稳定通信或充足算力条件；本方向聚焦弱网、边缘算力、多机器人共享状态，以及由 SLAM 几何状态提供的空间锚定。

**【设计决策】** 论文主张不写成“提出一个通用世界模型”，而限定为：

> 在弱连接条件下，通过 SLAM 几何状态约束协同世界模型的空间一致性，并在有限通信预算下维持可用的多机器人导航状态。

Map API 仅作为 Table / Chunk / Trigger 类空间数据组织的相关工作参考，不等同于本文的 VoxelDiff 协议、Swarm-SLAM 后端或弱网安全机制。

## 2. 摘要草案

多机器人具身导航通常假设稳定通信、充足边缘算力以及单一机器人维护的完整世界模型。在弱网和边缘计算条件下，机器人之间难以持续交换高密度空间信息，世界模型容易出现状态滞后、跨机器人不一致和几何漂移。本文拟研究一种基于 SLAM 几何锚定的多机器人协同世界模型框架，将机器人本地观测转化为空间增量，并通过位姿与空间状态关联实现边缘侧的选择性融合。该框架将几何状态、语义状态和通信状态分离建模，使系统能够根据网络条件和空间信息置信度调节同步粒度，并在通信中断时保持端侧导航与安全降级能力。我们将在多机器人同源数据、不同带宽、延迟、丢包和断连恢复条件下，与本地独立建图、全量地图同步及无几何约束的世界模型方法进行比较，评估定位一致性、任务成功率、通信开销、恢复时间和边缘资源占用。实验将验证 SLAM 几何约束能否降低弱网条件下的跨机器人状态不一致，并在有限通信预算下提升协同导航的可靠性。

> **【待补充】** 摘要中的效果性结论必须在实验完成后替换为真实数据；当前不得填入虚构的提升比例或延迟。

## 3. 论文框架

### 3.1 Introduction

- 弱网下多机器人世界状态同步的实际问题；
- 单机世界模型、全量同步和无几何约束方法的局限；
- SLAM 几何状态作为世界模型空间锚点的必要性；
- 本文问题边界、研究假设和三项贡献。

建议贡献：

1. 提出弱连接条件下的几何锚定协同世界模型框架；
2. 建立空间增量、置信度与通信状态联合调度的抽象机制；
3. 建立包含弱网扰动、跨机器人一致性和断连恢复的可复现实验协议。

### 3.2 Related Work

1. Multi-Robot SLAM：Kimera-Multi、Swarm-SLAM 等；
2. Collaborative / Distributed World Models；
3. Weak-Network Multi-Agent Navigation；
4. Edge Embodied AI and Model Compression；
5. 去中心化地图数据后端：Map API 作为设计参考，明确复用边界。

### 3.3 Problem Formulation

定义：

- 机器人集合、本地观测和局部 SLAM 状态；
- 空间增量、语义状态和网络状态；
- 网关融合状态；
- 弱网约束；
- 任务成功、断连和安全降级条件。

必须明确：

```text
几何状态 ≠ 语义状态 ≠ 通信状态 ≠ 执行状态
```

### 3.4 Method

1. Local spatial state construction；
2. Geometry anchoring；
3. Confidence-aware spatial update；
4. Gateway-side collaborative fusion；
5. Weak-connectivity adaptation；
6. Disconnection and recovery；
7. Local safety fallback。

**【保密边界】** 申请日前只写模块功能与接口级抽象，不展开双触发、Token 字段、事务伪码和权利要求级细节。

### 3.5 System Architecture

```text
Robot observations
        ↓
Local spatial state
        ↓
Weak-network adaptation
        ↓
Edge collaborative fusion
        ↓
Collaborative world model
        ↓
Planning / execution / feedback
```

图中应标出本体端、网关端、可选云端、几何状态、语义状态、网络状态和端侧安全边界。

### 3.6 Experiments

至少包含：

1. 单机与多机对照；
2. 稳定网络与弱网对照；
3. 有无几何锚定；
4. 全量同步与空间增量同步；
5. 连续通信与断连恢复。

指标：

- ATE / RPE；
- 跨机器人地图一致性；
- 任务成功率；
- 更新延迟；
- 带宽与消息数量；
- CPU / 内存；
- 断连恢复时间；
- 失败后的安全降级比例。

### 3.7 Ablation

- 去掉几何锚定；
- 去掉置信度调度；
- 去掉增量同步；
- 去掉网关融合；
- 固定同步频率；
- 不同弱网扰动模型。

### 3.8 Limitations and Conclusion

必须说明：

- 不覆盖拜占庭攻击；
- 不证明全局一致性；
- 不等同于完整世界模型闭环；
- 结果依赖具体 SLAM 前端和网关拓扑；
- 双机真机结果【待补充】。

## 4. 实验前置条件

- KeyFrame 同源 bag；
- 弱网模拟与可复现实验配置；
- 多机空间融合实现；
- Swarm-SLAM Gate 通过；
- Go2 单机基线、N4/N5 和数据回链完成；
- `PAT-SLAM-TOKEN-MAIN` 达到 `filed` 后再展开专利同源方法章节。

## 5. 状态与下一步

**【事实】** 当前未开题，状态为 `idea`；目标为 CVPR / IJCAI / ICRA。  
**【设计决策】** P1 作为主线论文候选，在 P3 形成通信实证后推进。  
**【待补充】** 专利申请日、世界模型接口、双机数据、弱网首组结果。

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | PAPER-P1-001 |
| type | paper |
| title | 弱网边缘的多机协同世界模型与 SLAM 几何锚定 |
| target | CVPR / IJCAI / ICRA |
| stage | idea |
| status | todo |
| priority | ★★★★★ |
| confidentiality | patent-sensitive |
| knowledge_refs | CAP-SLAM-KIMERA-MULTI-REF-001；CAP-SPATIAL-MAPAPI-REF-001 |
| patent_refs | PAT-SLAM-TOKEN-MAIN |
| next | C 族主专利 filed 后 → outline |
| updated | 2026-07-21 |
