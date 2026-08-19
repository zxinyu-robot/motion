# 论文 P3：带宽—置信度感知的关键帧压缩与调度

> 本方向优先形成可验证通信论文。与主专利同源部分必须进行方法分流：专利保护产品机制，论文公开经裁剪后的压缩与调度实验。

## 1. 研究定位与差异化

**【推断】** 协同 SLAM 中，关键帧对定位、回环和地图融合的贡献并不相同。固定压缩率、固定发送频率或只看图像质量的策略，难以同时适应空间价值和网络变化。

**【设计决策】** 本文将研究问题限定为：

> 在有限通信预算下，如何根据关键帧的几何贡献、空间覆盖、状态置信度和网络状态，选择信息保留比例与传输优先级。

Map API 的 Chunk / Trigger 仅作为空间增量组织的相关设计参考，不作为本文压缩算法的直接实现或等价基线。

## 2. 摘要草案

协同 SLAM 中，关键帧传输同时受到带宽、延迟、机器人算力和地图更新价值的约束。现有方法通常采用固定压缩率、固定发送频率或仅依据图像质量选择关键帧，难以区分对定位、回环和地图融合具有不同贡献的空间信息。本文拟研究一种面向通信受限协同 SLAM 的关键帧压缩与调度框架，根据关键帧的几何贡献、回环价值、空间覆盖、状态置信度和当前网络条件，联合决定信息保留比例、传输优先级和发送时机。该方法将关键帧表示为可分级的空间增量，使高价值几何约束优先传输，并允许在带宽下降或链路中断时进行延迟发送和恢复同步。我们将在相同 SLAM 前端、相同场景和可控网络扰动下，对比固定压缩、固定频率、全量传输以及不同启发式调度策略，评估定位精度、回环成功率、地图一致性、带宽占用、端到端延迟和资源消耗。实验将验证置信度感知的传输调度在有限通信预算下是否能够更好地保持协同 SLAM 的关键几何约束。

> **【待补充】** 任何“更好地保持”或性能提升结论，都必须由 WeakNet Bench 原始数据支持。

## 3. 论文框架

### 3.1 Introduction

- 协同 SLAM 在带宽受限条件下的关键帧传输问题；
- 不同关键帧的定位、回环和地图价值不相同；
- 单纯提高压缩率不能保证协同定位质量；
- 调度需要同时考虑空间价值与网络状态；
- 本文问题、假设和贡献。

建议贡献：

1. 定义关键帧的几何—空间—通信价值；
2. 提出置信度感知的压缩与调度框架；
3. 建立可复现的 WeakNet Collaborative Bench；
4. 通过消融实验分析压缩和调度的独立贡献。

### 3.2 Related Work

1. Communication-Efficient SLAM；
2. Keyframe Selection；
3. Point Cloud / Voxel Compression；
4. Multi-Robot SLAM Communication；
5. Adaptive Scheduling under Weak Networks。

相关工作中应区分：

- 无损压缩；
- 有损几何压缩；
- 关键帧选择；
- 网络感知调度；
- 面向协同 SLAM 任务指标的联合优化。

### 3.3 Problem Formulation

输入：

- 关键帧；
- 局部位姿；
- 特征、点云或体素信息；
- 回环候选；
- 网络状态；
- 目标带宽预算。

输出：

- 压缩等级；
- 传输优先级；
- 发送或延迟决策；
- 接收端恢复状态。

高层目标：

```text
在通信预算约束下，最大化定位、回环和地图一致性收益。
```

正式目标函数、权重和阈值应在 schema 与指标冻结后确定，避免先验调参。

### 3.4 Method

1. Keyframe utility estimation；
2. Geometry-aware representation；
3. Confidence-aware compression；
4. Network-aware scheduling；
5. Receiver-side reconstruction；
6. Missing update detection and recovery；
7. Local fallback when communication is unavailable。

**【保密边界】** 申请日前不公开完整双触发逻辑、Token 字段、事务伪码和独权级组合。论文可使用“事件触发式更新条件”等抽象表述，但必须确保与专利交底书分流。

### 3.5 Experimental Protocol

网络变量：

- 带宽；
- 延迟；
- 抖动；
- 丢包；
- 突发断连；
- 恢复时间。

数据变量：

- 场景规模；
- 机器人数量；
- 关键帧密度；
- 重复区域；
- 回环数量；
- 动态物体比例。

### 3.6 Baselines and Metrics

对照方法：

- 全量关键帧传输；
- 固定间隔关键帧；
- 固定压缩率；
- 仅几何质量的关键帧选择；
- 仅网络状态的调度；
- 本文联合方法。

指标：

- ATE / RPE；
- 回环检测成功率；
- 地图一致性；
- 带宽占用；
- 端到端延迟；
- 压缩率；
- CPU / 内存；
- 丢包后恢复时间。

可增加：

```text
单位通信预算下的定位收益
```

但综合指标的权重、归一化方式和统计区间必须公开。

### 3.7 Ablation

- 只压缩、不调度；
- 只调度、不压缩；
- 去掉几何价值；
- 去掉回环价值；
- 去掉网络状态；
- 去掉接收端恢复；
- 不同压缩等级。

### 3.8 Limitations and Conclusion

必须说明：

- 关键帧价值估计可能依赖具体 SLAM 后端；
- 不同传感器的压缩策略不能直接复用；
- 当前 KeyFrame / SpatialChunk / VoxelDiff schema 仍为草案；
- 当前项目尚未形成完整 WeakNet measured 数据；
- 本文不声称解决通用分布式一致性或安全攻击问题。

## 4. 实验前置条件

- T-003：KeyFrame / SpatialChunk / VoxelDiff v0.1 schema；
- T-010：WeakNet Bench 工具与首扫；
- T-004：Go2 单机基线和数据回链；
- 相同前端、相同场景、相同网络扰动的可复现实验；
- 明确压缩质量与定位 / 回环质量的统计关系；
- 专利主案 filed 后完成同源方法分流核校。

## 5. 状态与下一步

**【事实】** 当前状态为 `idea`，目标为 IROS / RA-L。  
**【设计决策】** P3 作为第一篇优先验证的论文方向。  
**【待补充】** schema、首组弱网数据、压缩基线、统计方法和专利申请日。

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | PAPER-P3-001 |
| type | paper |
| title | 带宽-置信度感知的关键帧压缩与调度（通信高效 C-SLAM） |
| target | IROS / RA-L |
| stage | idea |
| status | todo |
| priority | ★★★★☆ |
| confidentiality | patent-sensitive |
| knowledge_refs | CAP-COMM-TRANSPORT-STACK-001；CAP-SPATIAL-MAPAPI-REF-001 |
| patent_refs | PAT-SLAM-TOKEN-MAIN |
| next | 完成 schema v0.1 与 WeakNet Bench 首扫 → outline |
| updated | 2026-07-21 |
