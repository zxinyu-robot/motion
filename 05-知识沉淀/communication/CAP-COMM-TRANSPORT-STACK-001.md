# 传输栈分层：本机零拷贝 / Schema / 弱网数据面

## 结论

**【设计决策·仓内】** 空间契约（KeyFrame / VoxelDiff 等）与传输实现解耦：**换运输车，不换货物格式**。  
**【事实·Streaming】** 分层推荐口径：

| 层 | 候选 | 用途 |
|----|------|------|
| 本机 | Iceoryx / ROS 2 loaned | LIO→Tokenizer→Planner，消除同机 memcpy |
| Schema | Demo Protobuf；产品倾向 FlatBuffers（+ LZ4） | 大块同质体素可 zero-copy 访问 |
| 跨机弱网 | Demo ZMQ；产品期 Zenoh 或 QUIC 作数据面，DDS 可留控制面 | 边端↔网关、多机大块 |

**【推断】** P0 证据飞轮未出传输 bench 前，不得宣布「已选定 Zenoh/Iceoryx 量产」。  
**【事实】** 跨网路径不提供端到端零拷贝保证（见 Go2 端侧约束表述）。  
**【事实·2026-07-21 扫描】** `motion_ws` 树内**无** Iceoryx / FlatBuffers / Zenoh / 业务 ZMQ·Protobuf 源码依赖；Go2 探测为 CycloneDDS + 自研 `ShmStaticLayer`（非 Iceoryx）。详见 `motion_ws/docs/传输依赖扫描-2026-07-21.md`。

## 适用条件

- 讨论中间件集成、网关数据面、Token 传输效率指标时
- WeakNet / Streaming Week 1–2 / 5–6 阅读与选型

## 不适用

- 用传输选型替代 Swarm-SLAM Gate 或 Super-LIO Producer 验收
- 把官网延迟数字或他文（如 Kimera 70%）填进本仓实测列
- 申请前公开完整 schema 独权细节

## 关联

- 半篇：`04-文献阅读/notes/04-空间数据流-中间件/2026-工程-Iceoryx-FlatBuffers-传输半篇.md`
- 半篇：`04-文献阅读/notes/05-通信-弱网-网络/2026-工程-Zenoh-弱网传输半篇.md`
- 架构：`02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` §4
- 对标记账：`CAP-SLAM-KIMERA-MULTI-REF-001`（PR/GV/DPGO 分账思想）
- 地图 chunk：`CAP-SPATIAL-MAPAPI-REF-001`（Table/Chunk/Trigger；非 VoxelDiff 等价物）
- 验证：`40-验证/P1-WeakNet-Collab-指标提纲.md`

## 验证 todo

- [x] `motion_ws` 依赖扫描：iceoryx / flatbuffers / zenoh 是否已引入 → **均未引入**（2026-07-21）
- [ ] （可选）扫 Go2 `MotionSLAM_ws` 源码 `#include` / `package.xml` 补 ZMQ/Protobuf 使用痕迹
- [ ] 同 schema 下 ZMQ vs（DDS|Zenoh）首组带宽/延迟 → `40-验证/`
- [ ] Schema v0.1：Protobuf demo 与 FlatBuffers 布局对齐说明（不含独权伪码）
---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | CAP-COMM-TRANSPORT-STACK-001 |
| type | capability |
| stage | knowledge |
| status | done |
| evidence_level | proposal + scan（motion_ws 树） |
| sources | Streaming §4；两篇 2026 工程传输半篇；`motion_ws/docs/传输依赖扫描-2026-07-21.md` |
| applies_to | 本机 IPC、序列化、弱网数据面选型 |
| related_tasks | T-001, T-003, T-010 |
| updated | 2026-07-21 |
