# 2026-工程-Zenoh 弱网传输半篇

> **类型**：工程技术半篇（非 peer-review 论文四章精读）  
> **依据**：`02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` §4；汇报材料传输选型；`03-技术分析/联网外部参考资料索引.md` §4  
> **姊妹篇**：`04-文献阅读/notes/04-空间数据流-中间件/2026-工程-Iceoryx-FlatBuffers-传输半篇.md`  
> **保密**：不写未 filed 独权伪码；不主张某一传输栈已 measured。

---

## 1. 是什么（一句话 + 边界）

| 对象 | 一句话 | 边界 |
|------|--------|------|
| **Zenoh** | 统一数据空间上的 pub/sub、查询与路由；面向动态拓扑与带宽受限场景，常作相对「纯 DDS 大块数据」的数据面候选 | **不是**本机零拷贝替代品；也不自动等于已选定产品栈 |
| **Fast DDS / ROS 2 DDS** | 控制面：发现、QoS、RPC/服务生态成熟 | 大块 Voxel 易撞 CDR+拷贝压力（Streaming §4.3） |
| **QUIC / msquic** | UDP 上可靠多路复用、0-RTT 重连等弱网能力 | 需自建应用层语义；生态完整度不如 DDS【仓内口径】 |
| **eCAL** | 机器人低延迟 pub/sub 对照 | Streaming Tier1；本半篇不展开 |

官方入口【事实·L3】：https://zenoh.io/ ；QUIC RFC 9000；msquic GitHub（见联网索引）。

---

## 2. 与本项目关系

仓内阶段建议【事实·Streaming §4.4】：

| 阶段 | 传输 | Schema |
|------|------|--------|
| Demo（当前） | ZMQ + WiFi | Protobuf |
| 产品期 | DDS + 本机 SHM / **Zenoh** | FlatBuffers |
| 多机网关 | Fast DDS（控制）+ **Zenoh**（数据） | FlatBuffers + LZ4 |

| 维度 | 分析 |
|------|------|
| **直接相关** | 边端→远程网关弱网 WiFi；多机大块 spatial data 与控制面分离 |
| **间接启发** | 与 Kimera-Multi「PR/GV/DPGO 分账」同理：应对 **meta / 关键帧 / 体素块** 分通道记账（WeakNet） |
| **正交** | 不解决 LIO 精度或 VLA 语义 |
| **风险** | ① 未 bench 前锁定 Zenoh=过早；② 换运输车时误改货物 schema；③ 把 Zenoh 当本机 Iceoryx |
| **优先级** | **列入调研**（P0 以 x86+WiFi benchmark 选型，见汇报材料） |

### 借鉴矩阵（精简）

| 内容 | 对应模块 | 可借鉴？ | 优先级 | 备注 |
|------|----------|----------|--------|------|
| 控制面 DDS + 数据面 Zenoh | 网关 / 多机 | 是 | 列入调研 | Streaming §4.2 |
| Zenoh 断线重连 / 路由 | WeakNet Bench | 是 | 列入调研 | 指标：恢复时间、带宽档 |
| 纯 DDS 传全量体素 | 数据面 | 慎用 | — | 先测序列化压力 |
| Demo 直接上 Zenoh 全家桶 | P0 闭环 | 否 | 仅存档 | 先 ZMQ 验证契约 |
| QUIC 替代一切 | 传输 | 部分 | 仅存档 | Week 7–8 toy；非阻塞 |

**一句话**：Zenoh 是弱网/跨机 **数据面候选**；选型结论只能来自 `40-验证/`，不能来自官网宣传。

---

## 3. 应对齐的指标（写入 WeakNet，勿填假实测）

| 轴 | 建议观测 | 说明 |
|----|----------|------|
| 通信 | 丢包 / RTT / 带宽档 / 断连恢复 | 已有 `P1-WeakNet-Collab-指标提纲.md` |
| 载荷分账 | meta vs 关键帧 vs 体素块（类比 Kimera PR/GV/DPGO） | CAP-SLAM-KIMERA-MULTI-REF-001 |
| 栈对比 | ZMQ（基线）vs DDS vs Zenoh（同 schema） | 换车不换货 |
| 序列化 | Protobuf vs FlatBuffers（同语义 payload） | 见 04 半篇 |

**【事实·扫描】** 2026-07-21：`motion_ws` 与 Go2 探测均 **未安装 Zenoh**；`platforms/go2|edge` 仅规划占位。版本号 N/A。详见 `motion_ws/docs/传输依赖扫描-2026-07-21.md`。

---

## 4. next

- [ ] P0/P1：同 WiFi 场景 ZMQ vs Zenoh（或 DDS 数据面）首扫，结果进 `40-验证/`
- [ ] T-010 提纲可选加「传输栈」列
- [x] 能力卡汇总三层栈：`CAP-COMM-TRANSPORT-STACK-001`
- [x] motion_ws 依赖扫描（Zenoh 未引入）

---

## 附录：来源核校

| 核项 | 说法 | 来源 | 判定 |
|------|------|------|------|
| 弱网推荐 Zenoh 或 QUIC + FB + LZ4 | Streaming §4.2 | L2 | 【事实·仓内设计】 |
| Demo 仍为 ZMQ+Protobuf | Streaming §4.4 | L2 | 【事实·仓内设计】 |
| 70% 等论文通信降幅 | — | 属 Kimera-Multi，非 Zenoh | **禁止**挪到本笔记实测 |
| zenoh.io | L3 索引 | 外链 | 【事实】 |

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | NOTE-2026-ENG-ZENOH-WEAKNET |
| type | tech-note |
| stage | analysis |
| status | done |
| priority | 列入调研 |
| related_capability | CAP-COMM-TRANSPORT-STACK-001 |
| related_notes | NOTE-2026-ENG-ICEORYX-FLATBUFFERS；NOTE-2022-TRO-Kimera-Multi |
| updated | 2026-07-21 |
