# 外部技术与标准对标：SuperMap（RSS-2026）与 ITU-T Y.3663

> 整理自公开项目页 / ITU 工作计划与已公开 bDDN 系列（2026-07-14）。  
> 本文属 L3 **技术分析（外部对标）**，非代码阅读笔记；不写入专利独权细节。  
> 标注约定：【事实】【推断】【待补充】。

---

## 0. 一句话结论

| 对象 | 对本项目的价值 | 优先级 |
|------|----------------|--------|
| **SuperMap** | SLAM↔VLN「语义记忆层」最贴近的学术基线：4D scene graph + 动态实例一致性 | **列入调研** |
| **ITU-T Y.3663** | bDDN「知识构建」国际标准叙事参考；可映射网关知识生命周期话术，非机器人协议 | **仅存档 / 标准跟踪** |

二者都指向「从原始感知/数据 → 可查询知识 → 下游决策」这一层；本项目差异化仍在 **弱网多机、KeyFrame/VoxelDiff 协议不变量、Folder/Trigger 编排**。

---

## 1. SuperMap：4D 时空语义 SLAM × 视觉语言导航

### 1.1 该工作是什么？

**【事实】**

| 项 | 内容 |
|----|------|
| 标题 | SuperMap: A Spatio-Temporal SLAM System for Visual-Language Navigation |
| Venue | Robotics: Science and Systems (**RSS 2026**) |
| 单位 | Carnegie Mellon University — AirLab |
| 作者 | Shibo Zhao, Guofei Chen, Honghao Zhu, Zhiheng Li, Changwei Yao, Nader Zantout, Seungchan Kim, Wenshan Wang, Ji Zhang, Sebastian Scherer |
| 项目页 | https://superodometry.com/supermap |
| 录用列表 | https://roboticsconference.org/program/papers/（Localization & Mapping） |

**问题**：开放词汇视觉基础模型强在帧级识别，却无法维持长期物体身份，也无法推理场景随时间演化；VLN 缺一层持久、可查询的空间记忆。

**方法概要（公开摘要级）**：

1. **Geometric Layer**：SuperOdometry 提供位姿与稠密三维（RGB + depth/LiDAR + IMU）。
2. **Instance Layer**：GroundingDINO + SAM2；混合 2D–3D 关联；存在/标签置信度更新，处理遮挡与场景变化（出现 / 消失 / 挪动）。
3. **Topological Layer**：场景图 \(G=(V, E_s, E_t)\)——空间边（on / beside / under）+ 时间边（物体轨迹史）；序列化为结构化文本供 VLM 组合查询。

**验证与开源承诺（项目页）**：ScanNet 类别/实例分割、时空变化检测；校园室内外约 2 小时连续部署；宣称机载实时、免训练；计划全系统开源。

### 1.2 三层管线示意

```text
RGB / Depth|LiDAR / IMU
        │
        ▼
┌───────────────────────┐
│ Geometric: SuperOdometry │  位姿 + 稠密几何
└───────────┬───────────┘
            │
            ▼
┌───────────────────────────────────────────┐
│ Instance: GroundingDINO+SAM2 + 2D–3D 跟踪 │
│ 存在/标签置信度 · 动态剪枝                  │
└───────────┬───────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────┐
│ Topological: G=(V, Es, Et) 4D scene graph │
│ → 文本序列化 → VLM / VLN grounding         │
└───────────────────────────────────────────┘
```

### 1.3 公开指标摘录（项目页表格）

**【事实】** 以下数字来自项目页 Results，非本仓实测。

| 对比维 | 结论摘要 |
|--------|----------|
| ScanNet class-level | SuperMap mIoU 27.42 / Acc 55.48，优于 ConceptGraphs、HOV-SG（同表） |
| ScanNet instance (mAP50) | Chair/Window/Fridge 等显著高于 HOV-SG / ConceptGraphs |
| 时空变化检测 Recall | Appeared / Disappeared 多桶上强于 DualMap 等 |

**【待补充】** 完整论文 PDF、runtime 表、真机 VLN 成功率未在本仓落盘；开源仓库 URL 发布后补链。

### 1.4 与本项目关系（借鉴矩阵）

对照：`02-架构设计/Go2-VLA-SLAM-Token技术方案.md`、主规划 §6.2（图检索式 VLN）。

| SuperMap 内容 | 本项目模块 | 可借鉴？ | 优先级 | 备注 |
|---------------|-----------|----------|--------|------|
| 几何 SLAM + 异步开放词汇感知解耦 | 前端 LIO + 网关语义 | 是 | 列入调研 | 与「前后端分离」同构 |
| \(G=(V,E_s,E_t)\) 可查询场景图 | GraphNode / QueryGraph | 是 | **列入调研** | 补时间边 \(E_t\)、动态实例 ID |
| 存在/标签置信度剪枝 | 语义置信度 Trigger | 是 | 列入调研 | 可映射行为树条件 |
| GroundingDINO + SAM2 机载 | Go2 边端感知 | 否/慎用 | 仅存档 | 算力与 A 线激光主栈冲突 |
| 单机校园级 4D 记忆 | 多机网关 merge | 部分 | 列入调研 | 本项目差异在弱网多机 |
| 文本序列化喂 VLM | VLN Adapter / Folder | 是 | 列入调研 | 对齐「不直接喂全量点云」 |
| KeyFrame / VoxelDiff / 弱网协议 | 中间件核心 | 否 | — | SuperMap 未覆盖 |
| Swarm-SLAM / 跨机回环 | C-SLAM | 否 | — | 公开材料以单机为主 |

**一句话**：SuperMap 是「单机语义记忆层」参考实现；本项目应吸收其 **实例一致性 + 时间边**，继续押注 **增量体素协议 + 多机 Graph + 弱网编排**。

### 1.5 对本项目的设计启示（非专利细节）

**【推断】** 在不改动 P0 协议主线前提下，可在 Graph 语义扩展清单中跟踪：

1. GraphNode 是否需要显式 **instance_id 生命周期**（active / occluded / pruned）。
2. GraphEdge 是否区分 **空间谓词边** 与 **时间轨迹边**。
3. Trigger 是否增加「语义置信度下降 / 物体消失」类条件（行为树已有 `DetectObject` 可演进）。

**【待补充】** 是否写入 schema v0.1 → 待 T-003 冻结时人工拍板；本文不预设字段名。

---

## 2. ITU-T Y.3663：大数据驱动网络的知识构建架构与机制

### 2.1 该标准是什么？

**【事实】**

| 项 | 内容 |
|----|------|
| 编号 | **Y.3663**（ex **Y.bDDN-MecArch-KC**；会议稿亦作 ArchMec-KC） |
| 全称 | Big data driven networking – Architecture and mechanism of **knowledge construction** |
| 归口 | ITU-T **SG13 Q7/13**（Network awareness and network intelligence，含 bDDN） |
| 工作计划 | https://www.itu.int/itu-t/workprog/wp_search.aspx?Q=7%2F13 |
| 计划时间 | 工作计划标 **2026-07** |
| 草案 | SG13 TD（如 142-WP3, 2025-07）多为 **TIES 受限**，本仓无全文 |

**定位**：在 bDDN（Big Data Driven Networking）族谱中，规定如何从网络大数据 **构建知识** 的架构与机制。

### 2.2 bDDN 族谱上下文（已公开可核）

| 标准 | 角色 | 状态（公开页） |
|------|------|----------------|
| [Y.3650](https://www.itu.int/rec/T-REC-Y.3650) | bDDN 总框架（大数据 / 网络 / 管理三平面） | In force |
| [Y.3652](https://www.itu.int/rec/T-REC-Y.3652) | 需求 | In force |
| [Y.3653](https://www.itu.int/rec/T-REC-Y.3653) | 功能架构（感知→仓储→分析→智能与服务） | In force |
| [Y.3661](https://www.itu.int/rec/T-REC-Y.3661) | 面向客户的智能运维架构与机制 | In force (2025-08) |
| **Y.3663** | **知识构建**架构与机制 | 工作计划登记，正式公开 PDF【待补充】 |

**【推断】** Y.3663 补强 Y.365x「intelligence」侧：把「数据→知识」生命周期（表示、抽取、融合、推理、存储、更新等）标准化。  
**【注意】** 自治网络另有 [Y.3064 Knowledge management](https://itu.int/rec/recommendation.asp?lang=en&parent=T-REC-Y.3064-202512-I)（基于 Y.3061）；与 Y.3663 同「知识」主题但属 **AN 线**，勿混用编号。

### 2.3 概念映射：bDDN ↔ 本项目网关（类比，非合规声明）

| bDDN / Y.3663 语境（公开族谱） | 本项目对应物 | 映射强度 |
|--------------------------------|--------------|----------|
| 感知层采集异构数据 | KeyFrame / VoxelDiff / 边端语义 | 概念类似 |
| 大数据仓储 / 知识库 | 网关地图库 + Graph 索引 | 概念类似 |
| 知识构建与融合 | 跨机 merge、版本化 SpatialChunk | 概念类似 |
| 知识查询 / 智能服务 | `QueryGraph` + VLN grounding | 概念类似 |
| 管理平面策略闭环 | Folder / ActionGroup / Trigger | 弱类比 |
| 运营商级流量/QoE 运维 | — | **不适用** |

**【事实】** 本仓此前无 ITU / bDDN / Y.3663 引用。  
**【推断】** 对外材料可写「知识生命周期对齐国际网络智能标准族（bDDN）」；**不可**声称产品已符合 Y.3663（全文未核、域不同）。

### 2.4 与本项目关系（借鉴矩阵）

| Y.3663 / bDDN 内容 | 本项目模块 | 可借鉴？ | 优先级 | 备注 |
|--------------------|-----------|----------|--------|------|
| 知识构建生命周期叙事 | 网关架构说明 / 汇报 | 是 | 仅存档→跟踪 | 正式文本出后升「列入调研」 |
| 三平面分层 | 本体前端 / 网关后端 /（可选）云 | 弱 | 仅存档 | 已有前后端分离，无需改栈 |
| 接口能力标准化思路 | Token 协议对外契约 | 间接 | 仅存档 | 学「契约分层」而非抄条款 |
| 机器人 SLAM / VLN 数据面 | 中间件 | 否 | — | 标准对象是电信网络大数据 |

**一句话**：Y.3663 是 **标准与话术层** 参考；工程主线仍以 Swarm-SLAM + KeyFrame/VoxelDiff 为准。

---

## 3. 二者对照与对本项目的统一建议

```text
                    ┌─────────────────────┐
  感知原始流 ──────▶│  知识 / 空间记忆层   │──────▶ 语言导航 / 调度
                    └─────────────────────┘
                              ▲
              ┌───────────────┼───────────────┐
              │               │               │
         SuperMap         本项目网关        Y.3663
         单机 4D          弱网多机          电信 bDDN
         scene graph      Graph+VoxelDiff   知识构建标准
```

| 决策项 | 建议 |
|--------|------|
| P0 工程 | **不**引入 SuperMap 整栈；不阻塞 schema 冻结 |
| Graph 语义扩展 | 跟踪 SuperMap 的实例生命周期与 \(E_t\)（列入调研） |
| 标准引用 | 对外可先引 Y.3650/Y.3653；Y.3663 标「进行中」 |
| 文献闭环 | SuperMap PDF/开源到位后，可另开 `04-文献阅读/notes/` 正式笔记 |
| 专利 | 本文仅概念对标；**不**把未申请独权写入公开 Spec/论文 |

---

## 4. Next actions

- [ ] 跟踪 SuperMap 开源仓库与论文 PDF → 落入 `10-收集箱/papers/` 后补 `04-文献阅读` 四章笔记
- [ ] T-003 冻结 schema 时，人工决定是否纳入 instance 生命周期 / 时间边（本文不预设字段）
- [ ] Y.3663 正式 Recommendation 公开后，补「条款 ↔ 网关模块」对照表（需 TIES/公开 PDF）
- [ ] 若写入汇报材料：SuperMap 作竞品/基线一句；Y.3663 作标准族谱一句，避免过度承诺

---

## 5. 来源清单

| 来源 | 用途 |
|------|------|
| https://superodometry.com/supermap | SuperMap 摘要、架构、指标 |
| https://roboticsconference.org/program/papers/ | RSS 2026 录用与作者 |
| https://www.itu.int/itu-t/workprog/wp_search.aspx?Q=7%2F13 | Y.3663 工作计划登记 |
| ITU-T Y.3650 / Y.3652 / Y.3653 / Y.3661 公开页 | bDDN 族谱上下文 |
| 本仓 `02-架构设计/Go2-VLA-SLAM-Token技术方案.md` 等 | 对照关系 |
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | ANA-EXT-SUPERMAP-Y3663-001 |
| type | analysis |
| stage | analysis |
| status | done |
| canonical | false |
| evidence_level | proposal |
| confidentiality | internal |
| updated | 2026-07-14 |
| next | SuperMap 开源后做模块级对照；Y.3663 正式文本发布后补条款级映射 |
| related | `02-架构设计/Go2-VLA-SLAM-Token技术方案.md`、`02-架构设计/行为树调度架构_BehaviorTree设计.md`、`01-工作计划/多机器人协同_详细技术与科研规划.md` |
| sources | 3 条（见下方列表） |

**sources**

- https://superodometry.com/supermap
- https://roboticsconference.org/program/papers/
- https://www.itu.int/itu-t/workprog/wp_search.aspx?Q=7%2F13
