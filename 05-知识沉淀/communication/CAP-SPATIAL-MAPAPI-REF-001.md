# ETH Map API：去中心化地图数据后端（设计参考，非产品底座）

## 结论

**【事实】** Map API 指 ETH Zurich Cieslewski 等 ICRA 2015 工作 *Map API - Scalable Decentralized Map Building for Robots*（非 Google/高德式地图瓦片 API）。它提供 **Table / Chunk / Item** 对象模型，以及 **Trigger（变更订阅）**、**事务 + 乐观并发**、**Chord DHT 查找** 的去中心化地图数据后端思想。

**【设计决策·motion】** Map API 可启发本项目的 **SpatialChunk 粒度、按需订阅、增量同步与带宽记账**，但**不能**直接等同于：

- 当前 **VoxelDiff / KeyFrame** 协议（产品契约层）
- **Swarm-SLAM** 多机协同底座（P0 已选定）
- **弱网安全 / 拜占庭容错** 机制（本文未覆盖）

**【推断】** 产品路线为「本体→网关」金字塔 + 增量体素契约；Map API 的 **全 P2P 去中心化** 与中心化网关 hash merge **拓扑不同**，宜作对照与 Reading Group 素材，不宜整栈替换。

## 论文机制边界（避免误读）

| 常见说法 | 论文实际【事实】 |
|----------|------------------|
| 「完全无锁」 | 乐观并发 + **提交阶段 chunk 读写锁**；非长事务全局锁 |
| 「系统内置冲突合并规则」 | commit 失败时返回冲突项；**由应用层**实现 resolution |
| 「核心载体是位姿图」 | 通用 Table/Chunk 后端；proof-of-concept 偏视觉地图，非唯一定义 Pose Graph |
| 「保证最终一致性」 | chunk 复制 + 逻辑时钟；断连/节点离开边界见后续扩展工作，非本文主承诺 |

## 适用条件

- 设计 **SpatialChunk / VoxelDiff** 的订阅、触发与分片粒度
- WeakNet Bench：**按需拉取 / 变更推送** 的通信记账类比
- 与 Kimera-Multi（P2P 稠密）、Swarm-SLAM（去中心稀疏）做 **拓扑对照**
- 阅读 `ethz-asl/map_api` 或 ICRA'15 PDF 前的 **30 秒口径**

## 不适用

- 作为 motion P0 **协同 SLAM 产品底座**（已选 Swarm-SLAM）
- 替代 **网关增量 merge** 或 SLAM-Token 独权叙事
- 把区块链 / 拜占庭 / 联邦学习等 **后续研究** 当作 Map API 已实现能力
- 在 `patent.stage < filed` 前把完整双触发/Token 细节写入对外材料

## 关联

- PDF：`10-收集箱/papers/04-空间数据流-中间件/2015-ICRA-MapAPI-Cieslewski.pdf`
- 代码：https://github.com/ethz-asl/map_api
- 架构：`02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` §7 Tier0
- 对照：`02-架构设计/大疆上云API参考-ActionGroup与Folder分层.md` §MapAPI
- 多机对标：`CAP-SLAM-SWARM-SLAM-GATE-001`、`CAP-SLAM-KIMERA-MULTI-REF-001`
- 传输分层：`CAP-COMM-TRANSPORT-STACK-001`（Map API = 数据组织；ZMQ/Zenoh = 运输车）

## 验证 todo

- [ ] （可选）开正式阅读笔记 → `04-文献阅读/notes/04-空间数据流-中间件/`
- [ ] Schema v0.1 冻结时显式写清：哪些思想来自 Chunk/Trigger，哪些来自自有 VoxelDiff
- [ ] T-012 Reading Group：MapAPI vs 网关金字塔 vs Swarm 一页对照

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-SPATIAL-MAPAPI-REF-001 |
| type | capability |
| stage | knowledge |
| status | done |
| evidence_level | literature |
| sources | `2015-ICRA-MapAPI-Cieslewski.pdf`；`ethz-asl/map_api` README |
| applies_to | SpatialChunk 设计、增量同步、多机拓扑对照、L4 弱网网关叙事 |
| related_tasks | T-001, T-003, T-012 |
| updated | 2026-07-21 |
