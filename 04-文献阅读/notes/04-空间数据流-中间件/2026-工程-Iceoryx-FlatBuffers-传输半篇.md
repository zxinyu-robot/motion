# 2026-工程-Iceoryx-FlatBuffers 传输半篇

> **类型**：工程技术半篇（非 peer-review 论文四章精读）  
> **依据**：`02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md` §4；`03-技术分析/联网外部参考资料索引.md` §4；官方入口见文末  
> **保密**：只谈传输载体与 schema 形态；不写未 filed 的双触发/Token 独权伪码。

---

## 1. 是什么（一句话 + 边界）

| 对象 | 一句话 | 边界 |
|------|--------|------|
| **Iceoryx** | Eclipse 同机跨进程 **共享内存零拷贝** pub/sub（常与 ROS 2 / Cyclone DDS data-sharing 联用） | **不能跨网络**【事实·Streaming §4.1】 |
| **FlatBuffers** | Google 序列化格式：缓冲区可 **zero-copy 随机访问**，不必先整包反序列化成对象图 | 需固定布局 schema；演进要管兼容 |
| **ROS 2 loaned messages** | 本机最低成本零拷贝入口（借缓冲、少一次拷贝） | 仍受 DDS/进程模型约束；跨机无效 |

---

## 2. 与本项目关系

本项目铁律：**协议（KeyFrame / SpatialChunk·VoxelDiff）是不变量；传输是可换运输车**（汇报材料 / Streaming §4）。

| 场景 | 角色 | 优先级 |
|------|------|--------|
| Go2 本机：LIO → Tokenizer → Nav/Planner | Iceoryx **或** loaned message | **立即跟进**（直觉 + 后续 bench） |
| Demo 期跨机 | ZMQ + WiFi + **Protobuf**（架构现状） | 已定；schema 按 FlatBuffers 思维设计 |
| 产品期体素/大块 payload | FlatBuffers（+ LZ4）作数据面布局 | **列入调研** → schema 冻结前对比 |
| 把 Iceoryx 当跨 WiFi 方案 | — | **仅存档/禁止** |

### 借鉴矩阵（精简）

| 内容 | 对应模块 | 可借鉴？ | 优先级 | 备注 |
|------|----------|----------|--------|------|
| 本机零拷贝 SHM | Producer→契约消费者同机路径 | 是 | 立即跟进 | 端侧约束：跨网传输**不**保证端到端零拷贝 |
| FlatBuffers 直接读体素字段 | VoxelDiff / FST 编码缓冲 | 是 | 列入调研 | Demo 可用 Protobuf，布局思维对齐 |
| Cap'n Proto / SBE | 同上 | 部分 | 仅存档 | Streaming Tier1；非本半篇展开 |
| 独权伪码写进传输笔记 | 专利 | 否 | — | — |

**一句话**：先把「同机零拷贝 + 可 mmap 的 payload 布局」想清楚；跨网交给 Zenoh/QUIC 半篇，勿用 Iceoryx 解决弱网。

---

## 3. 设计参数 / 对标建议（无可编造的库版本实测）

| 项 | 仓内口径【事实·架构】 | 本仓必须另测 |
|----|----------------------|--------------|
| Demo schema | Protobuf | 消息大小、序列化 CPU、端到端延迟 |
| 产品倾向 | FlatBuffers > Protobuf（大量同质小记录） | 同 payload 下 Proto vs FB 对比 |
| 本机 | Iceoryx / loaned | 相对普通 topic 的 CPU/延迟差 |
| 压缩三连 | Morton → Delta → LZ4/Zstd（Streaming §5） | 与 VoxelDiff 结合的带宽 |

**【事实·扫描】** 2026-07-21：`motion_ws` **无** iceoryx / flatbuffers 包依赖（见 `motion_ws/docs/传输依赖扫描-2026-07-21.md`）。版本号 N/A。

---

## 4. next

- [x] `motion_ws` 扫描：iceoryx / flatbuffers → **未引入**
- [ ] Schema v0.1 冻结前做一次 Proto vs FlatBuffers toy bench（可挂 WeakNet / Token 传输效率）
- [x] 姊妹篇：`notes/05-通信-弱网-网络/2026-工程-Zenoh-弱网传输半篇.md`
- [x] 能力卡：`CAP-COMM-TRANSPORT-STACK-001`

---

## 附录：来源核校（硬门）

| 核项 | 说法 | 来源 | 判定 |
|------|------|------|------|
| Iceoryx 不能跨网络 | Streaming §4.1 | L2 文档 | 【事实·仓内】 |
| Demo=Protobuf / 产品倾向 FB | Streaming §4.2–4.4 | L2 | 【事实·仓内设计决策】 |
| 官方入口 | github.com/eclipse-iceoryx/iceoryx；google.github.io/flatbuffers | L3 索引 | 【事实·外链】 |
| 延迟数字 | — | 无本仓实测 | 【待补充】禁止填实测列 |

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | NOTE-2026-ENG-ICEORYX-FLATBUFFERS |
| type | tech-note |
| stage | analysis |
| status | done |
| priority | 立即跟进（本机）/ 列入调研（FB 产品期） |
| related_capability | CAP-COMM-TRANSPORT-STACK-001 |
| related_docs | Streaming-Spatial-Data-Pipeline；Go2-VLA-SLAM-Token §3.3 |
| updated | 2026-07-21 |
