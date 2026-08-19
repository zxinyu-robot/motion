# 3D SLAM → 具身多模态世界模型底座 —— 系统梳理与瞄点计划

> **定位**：认知梳理 + 学术瞄点规划，**不纳入** P0 产品交付 WBS；与 RL 支线（`多机器人协同_RL支线计划.md`）并行，可共享弱网 benchmark 与协议数据。  
> **核心判断**：单纯优化 SLAM 前端（LIO 精度/速度）不是当前与未来重点；需要对 3D SLAM 有足够认知，但**创新应落在「几何事实 → 任务相关空间记忆 → 多机共享信念」**，而非再写一个 SLAM。  
> **对齐**：主规划论文 P1（`06-产出/论文/P1-弱网协同世界模型/meta.md`）、架构 canonical（`02-架构设计/Go2-VLA-SLAM-Token技术方案.md`）、Streaming Spatial Data Pipeline（`02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md`）。  
> **更新**：2026-07-23（统一为 parking 学术瞄点，不形成当前年度工程承诺）

---

## 1. 一句话定位

用**五级能力阶梯 + 四条演化轴**系统梳理 3D SLAM 如何扩展为具身多模态世界模型的几何底座；个人/项目瞄点收敛为：**弱网多机器人场景下，任务条件的共享空间信念（Shared Spatial Belief）如何以最小增量维持协同语义导航能力**。

---

## 2. 概念边界（写作与立项必守）

| 概念 | 回答的问题 | 本项目当前阶段 |
|------|-----------|----------------|
| **3D SLAM / LIO** | 我在哪？静态几何是什么？ | 前端可插拔，Super-LIO 等为生产者 |
| **语义空间记忆** | 什么东西在哪里？ | M5 方向：Graph Node + 语义标签 |
| **任务相关空间记忆** | 完成当前任务需读哪部分空间？ | **parking 候选瞄点**：P0-D measured 后再评估 Graph 检索式 VLN |
| **多机共享空间信念** | 各机部分观测下，如何低成本形成一致任务认知？ | **核心创新区**：VoxelDiff + 版本 + 弱网同步 |
| **动作条件世界模型** | 执行 a 后 s' 是什么？可反事实推演？ | **长期**；专利 A3「World Model Delta」方向，申请前不写完整方法 |

**铁律**：有地图 + 语义标签 ≠ 世界模型；能任务检索 + 跨机同步 ≠ 世界模型；具备动作条件预测与 rollout 才接近严格意义 world model。对外表述优先用「共享空间信念 / 空间记忆」，慎用「我们已做世界模型」。

---

## 3. 五级能力阶梯（全文主线）

```text
L1 几何状态估计     pose + point cloud / occupancy / TSDF
L2 语义空间记忆     object / scene graph / open-vocab 3D grounding
L3 任务相关空间记忆  text + pose + scope → 检索 Graph 子图 / SpatialChunk
L4 多机共享空间信念  跨机对齐 + 增量同步 + 不确定性 + 弱网补偿
L5 动作条件世界模型  dynamics + action-conditioned prediction + rollout
```

**【推断】** 项目方案设计处在 **L2→L3**，工程验证 **【待补充】**。本文作为 parking 学术瞄点：L3 单机、L4 双机弱网实验均须等待当前 P0-D 形成 measured 证据后再评估恢复；L5 仅作文献与专利储备，不做训练型大模型。

---

## 4. 四条演化轴（系统梳理骨架）

### 4.1 表征轴：空间怎样被存储

```text
点/多边形 → Occupancy/Octree → TSDF/Surfel
→ KD-tree/ikd-Tree → Hash Voxel (iVox/OctVox)
→ Scene Graph / Object Map → NeRF/3DGS/Neural Field
→ 混合显式—隐式空间记忆
```

**写作要点**：比较精度、增量更新、近邻查询、自由空间、语义挂载、可微性、动态性——不是算法排行榜。LIO 的 iVox/OctVox 是「高效局部几何容器」，不是终点。

| 代表 | 数据结构侧重 | 典型矛盾 |
|------|-------------|----------|
| Thrun ICRA 2000 | 多分辨率 compact 3D（多边形简化） | 大尺度可存，非标准 octree occupancy |
| OctoMap 2013 | 概率 octree occupancy | 自由空间明确，更新成本高 |
| LOAM / FAST-LIO2 | 特征点 + ikd-Tree | 实时强，非全局稠密语义 |
| Faster-LIO | iVox 哈希体素 | O(1) 查，密度不可控 |
| Super-LIO | OctVox + cap 子体素 | 密度可预测 + 去噪 |
| KinectFusion | TSDF 体素 | 稠密小场景 |
| NeRF/3DGS-SLAM | 神经场/高斯 | 可微/外观强，实时与动态弱 |

### 4.2 状态估计轴：从离散位姿到动态/非惯性

```text
离散 pose → 滑窗/位姿图 → 连续时间轨迹 (CT-LIO)
→ 动态对象状态 → 可交互对象 → 动作条件未来状态
```

Elevator-LIO（非惯性系解耦）、CT-LIO/SLICT2（连续时间）归入此轴——说明 SLAM 在扩展**状态模型**，仍不等于 world model。

### 4.3 语义与多模态轴

```text
几何 → RGB-D → 语义 SLAM → Scene Graph
→ 开放词汇 3D grounding → 语言条件检索 → VLN/VLA 闭环
```

LL3DA、3D-LLM、NaVILA/MobileVLA-R1 作为**消费者**引用；本项目创新不在重训 VLA，而在**输入契约与检索上下文**。

### 4.4 具身与协同轴（**个人差异化主战场**）

```text
被动 SLAM → Active SLAM → 任务驱动感知
→ 多机地图融合 → 弱网增量同步 → 共享空间信念 → 协同决策
```

与 RL 支线（`PLAN-RL-SIDE-001`）交界：RL 可学「何时共享什么」；本计划定义「共享什么的数据结构与评估」。

---

## 5. 推荐研究瞄点（收敛后）

### 5.1 主瞄点（推荐）

**弱网多机器人：任务条件的共享空间信念**

- **问题**：带宽/延迟/丢包约束下，应同步哪些 KeyFrame / SpatialChunk / 语义摘要，才能维持多机对**当前任务**的一致空间认知？
- **输入**：VoxelDiff、位姿+协方差、Graph Node 引用、任务 Folder scope、网络状态
- **输出**：同步决策（规则 / 事件触发 / 后续 RL 策略）+ 跨机 merge 后的可检索子图
- **成功标准**：同等 SR 下 ↓ 传输量；或同等 MB/success 下 ↑ SR/SPL（对齐 `40-验证/P0-Benchmark-模板.md`）

**学术化名称（草案）**：*Task-conditioned Shared Spatial Belief under Bandwidth-constrained Multi-Robot Embodiment*

### 5.2 次瞄点（与主规划/专利同源）

| 瞄点 | 与主规划关系 | 披露 |
|------|-------------|------|
| 带宽-置信度感知关键帧/增量调度 | 论文 P3、主专利双触发 | **patent filed 前不写完整方法** |
| Graph 检索式 VLN 上下文 | M5、架构 §3.4 | 可写问题 formulation，细节待 filed |
| 异构混编共享记忆 | 论文 P2、明年 P1 平台 | 明年 |

### 5.3 明确不做（今年）

- 重训 7B+ VLA / 世界模型 video generator
- 以 ATE/RPE 为主指标的 LIO 前端 SOTA 竞赛
- 宣称已实现 L5 动作条件 world model rollout

---

## 6. 与项目架构的咬合点

**【事实】** 架构已定义三条空间链（见 `Go2-VLA-SLAM-Token技术方案.md`）：

| 链 | 承载 | 契约 |
|----|------|------|
| 增量体素 | 空间里有什么、能否通行 | `SpatialChunk/VoxelDiff` |
| 位姿图 | 内容在哪里、跨机如何对齐 | Pose Graph / GraphEdge |
| 图索引 | 当前任务应读哪些空间内容 | Graph Node → KeyFrame/RGB/Chunk/语义 |

**研究叙事**：SLAM 前端（iVox/OctVox/Hash）是**可换生产者**；稳定抽象是 **SpatialChunk + Graph Node**；VLA 是**下游消费者**，只收检索后的上下文，不读全量点云。

与 P1 论文 meta 差异化一致：「弱网/边缘、多机、SLAM 位姿图几何锚定」——本计划把「几何锚定」具体化为**版本化增量 + 任务检索 + 弱网同步**。

---

## 7. 产出规划

| 产出 | 类型 | 时间 | 说明 |
|------|------|------|------|
| **内部 Survey** | 文档 | 4–6 周 | 本文档扩展为 `04-文献阅读/` 笔记 + 能力矩阵表；不急于对外投稿 |
| **能力卡** | `05-知识沉淀/` | 与 Survey 同步 | CAP-SPATIAL-MEM-001 等 |
| **Perspective 草稿** | `06-产出/论文/` 新 meta 或 P1 附属 | C 族 filed 后 | 题目见 §8 |
| **弱网同步实验** | `40-验证/P1-*` | M2/M4 后 | 四基线对比（§9） |
| **与 RL 支线汇合** | 可选 | R2/R4 后 | 规则基线 → RL 学同步策略 |

---

## 8. Survey / Perspective 建议结构

**中文题目（草案）**：从 3D 几何重建到具身共享空间记忆：SLAM 作为多模态世界模型底座的演进与挑战

**英文题目（草案）**：*From 3D Geometric Reconstruction to Shared Embodied Spatial Memory: Evolution of SLAM as a Foundation for Multimodal World Models*

| 章 | 内容 |
|----|------|
| 1 引言 | SLAM=过去态估计；WM=未来态+反事实；本文论点：几何锚点而非替代 |
| 2 概念与边界 | 五级阶梯；与 semantic mapping / episodic memory / WM 区分 |
| 3 表征演进 | §4.1 轴 + 能力矩阵 |
| 4 状态与时间 | §4.2 轴 |
| 5 多模态与语义 | §4.3 轴 |
| 6 多机器人缺口 | 部分观测、弱网、异构、任务相关同步 |
| 7 案例：Streaming Spatial Pipeline | 项目契约，**不写专利敏感伪码** |
| 8 Open Challenges | 实时混合表示、物理一致性、interactive mapping |
| 9 个人研究议程 | §5 瞄点 + WBS |

---

## 9. 验证实验设计（与产品同源）

### 9.1 同步策略基线

| ID | 策略 | 描述 |
|----|------|------|
| B0 | 全量点云周期广播 | 通信上限参考 |
| B1 | 固定频率 KeyFrame | 传统 Fleet 常见 |
| B2 | 几何变化触发 VoxelDiff | 架构双触发之子集（公开可写部分） |
| B3 | **任务条件增量** | text + Folder scope + 位姿 → 选择 Chunk/Node 同步 |

### 9.2 指标（扩展 P0 Benchmark）

| 指标 | 说明 |
|------|------|
| SR / SPL | 任务成功 |
| MB/success | 每成功任务传输量 |
| 断网恢复时间 (s) | 协同恢复 |
| Graph 检索命中率 | 命中节点含所需空间块 |
| 地图陈旧错误 waypoint 比例 | 信念不一致代价 |
| 跨机语义目标一致率 | 多机认知对齐 |

### 9.3 场景

- [ ] 单机：Graph 检索 VLN 闭环（M5 前）
- [ ] 双 Go2 + x86 网关 + WiFi 弱网（M3/M4）
- [ ] GrAco bag 离线验证同步策略对 C-SLAM 的影响（M1 复用）

---

## 10. 里程碑与 WBS（约 4 个月首周期）

| 阶段 | 时间 | 目标 | 交付 |
|------|------|------|------|
| **S0 框架立住** | 第 1–2 周 | 五级阶梯 + 四轴 + 能力矩阵空表 | 本文档 §3–§4 定稿 |
| **S1 文献闭环** | 第 3–5 周 | 每轴 5 篇核心文献 + 阅读笔记 | `04-文献阅读/notes/09-SLAM-空间记忆/` |
| **S2 内部 Survey** | 第 6–8 周 | 8 章提纲 + 案例章（项目架构引用） | 长文草稿（internal） |
| **S3 瞄点实验设计** | 第 9 周 | B0–B3 定义 + 指标表 | `40-验证/` 模板扩展草案 |
| **S4 单机验证** | parking；P0-D measured 后复核 | Graph 检索 + 现成 VLN inference | 首组 SR/检索命中率 |
| **S5 双机弱网** | S4 与 Swarm Gate 通过后 | B2 vs B3 传输量与 SR 对比 | P1 benchmark 首组数据 |
| **S6 沉淀** | 滚动 | 能力卡 + 更新 P1 meta `knowledge_refs` | CAP 卡 + meta 回链 |

**与主里程碑**：当前仅保留 S0–S2 的低强度文献整理入口；S3～S5 均不占 active WIP，恢复条件以 `ProjectState.md` 与 ForkSpatialLink 方向稿为准。

---

## 11. 文献阅读清单（首批 20 篇，按轴分组）

> 已有 PDF 优先从 `10-收集箱/papers/` 读；缺失则标注【待补充】。

### 表征 / LIO

- [ ] Thrun et al., ICRA 2000 — 3D mapping + SLAM 早期代表
- [ ] Hornung et al., OctoMap, IROS 2013
- [ ] Zhang & Singh, LOAM, RSS 2014
- [ ] Xu et al., FAST-LIO2, TRO 2022
- [ ] Bai et al., Faster-LIO, RA-L 2022
- [ ] Wang et al., Super-LIO, RA-L 2026

### 语义 / 多模态 / VLA

- [ ] LL3DA, CVPR 2024（主规划 §7.1）
- [ ] NaVILA / MobileVLA-R1（架构 §4.1 对标）
- [ ] 收集箱 `08-世界模型-多模态/` 内待读 PDF【待补充清单】

### 多机 / 协同 SLAM

- [ ] `10-收集箱/papers/03-多机协同-Swarm/2106.14386v2.pdf` — Swarm-SLAM 相关
- [ ] COVINS-G / C-SLAM 综述类 1–2 篇【待补充】

### 世界模型 / Survey

- [ ] Embodied AI World Model survey（arXiv，功能-时间-空间三轴）【待补充准确 citation】
- [ ] 主规划 §8.1 论文点① 引用链补全

### 近期 LIO 扩展（状态轴）

- [ ] Elevator-LIO, arXiv 2605.24495, 2026
- [ ] SLICT2 / CT-LIO 类连续时间 LIO, RA-L 2024【待读】

---

## 12. 与 RL 支线、论文、专利的关系

```text
                    ┌─ PLAN-SPATIAL-MEM-001（本计划）
                    │    定义：共享什么、如何评估、Survey 叙事
主规划 PLAN-MAIN ───┼─ PLAN-RL-SIDE-001
                    │    定义：何时共享、谁做任务（MARL）
                    └─ P1 论文 meta / P3 压缩 meta
                         产品专利 C 族 filed 后 → 方法章节展开
```

| 边界 | 说明 |
|------|------|
| vs RL 支线 | 本计划管**数据结构与信念指标**；RL 管**同步/任务策略**；可共用 B0–B3 实验 |
| vs P1 论文 | P1 偏「世界模型 + 几何锚定」顶会叙事；本 Survey 偏认知框架；实验数据同源 |
| vs 专利 | 双触发、World Model Delta、完整同步算法 → **confidentiality: patent-sensitive**；Survey 只写公开文献 + 问题 formulation |

---

## 13. 风险与应对

| 风险 | 应对 |
|------|------|
| 题太大、写散 | 强制每章回扣「五级阶梯」；案例章只写项目契约层 |
| 与「优化 SLAM」混淆 | 摘要首句点明：前端可插拔，创新在记忆与同步 |
| 过早称 world model | 对外用「共享空间信念」；L5 仅作 challenge |
| 专利披露 | Survey 内部版；公开版剔除未 filed 方法细节 |
| 工程验证不足 | 阶段表述标【待补充】；引 `40-验证/` 而非「已在跑」 |

---

## 14. 近期行动清单

- [ ] 填写 §4 能力矩阵表（表征 × 七维能力：精度/增量/查询/自由空间/语义/可微/动态）
- [ ] 创建 `04-文献阅读/notes/09-SLAM-空间记忆/` 目录并在首批 6 篇（Super/Faster/FAST-LIO2/Thrun/Swarm PDF/LL3DA）写笔记
- [ ] 将 B0–B3 实验定义同步到 `40-验证/` 扩展模板（Ask/Agent 模式另开）
- [ ] 读 `Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md`，对齐案例章小节标题
- [ ] C 族 filed 后：开 P1 outline 或独立 perspective meta

---

## 15. 相关文档索引

| 文档 | 路径 |
|------|------|
| 主规划 | `01-工作计划/多机器人协同_详细技术与科研规划.md` |
| RL 支线 | `01-工作计划/多机器人协同_RL支线计划.md` |
| SLAM-Token 架构 | `02-架构设计/Go2-VLA-SLAM-Token技术方案.md` |
| Pipeline 阅读路线 | `02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` |
| 汇报材料 §7 产品线/学术线 | `02-架构设计/SLAM-Token弱网中间件-汇报材料.md` |
| P1 论文 meta | `06-产出/论文/P1-弱网协同世界模型/meta.md` |
| P0 Benchmark | `40-验证/P0-Benchmark-模板.md` |
| 专利族谱 | `06-产出/专利/专利族谱映射.md` |
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | PLAN-SPATIAL-MEM-001 |
| type | plan |
| stage | design |
| status | parking |
| canonical | false |
| evidence_level | proposal |
| parent | PLAN-MAIN-001 |
| updated | 2026-07-23 |
| next | 不占 P0 WIP；P0-D 有 measured 后再评估是否恢复学术瞄点 |
