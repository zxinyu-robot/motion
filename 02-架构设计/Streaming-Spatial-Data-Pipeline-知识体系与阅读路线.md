# Streaming Spatial Data Pipeline —— 知识体系与阅读路线

——机器人底层、高性能地图同步与具身智能

> 整理自技术讨论（2026-07-09，2026-07-14 更新）  
> 视角：SLAM 工程师 / 机器人底层 / 通信 / Spatial Computing  
> 关联文档：`02-架构设计/Go2-VLA-SLAM-Token技术方案.md`、`02-架构设计/SLAM-Token弱网中间件-汇报材料.md`、`01-工作计划/多机器人协同_详细技术与科研规划.md`
> **使用边界**：internal / patent-sensitive 阅读路线，非当前状态或执行排序源；触发阈值与带宽数字仅作历史架构参考，不得作为公开 Spec 或实测结论。

---

## 1. 核心判断

**不要把重心放在单一通信技术（Iceoryx / DDS / ZMQ），而要上升到「Streaming Spatial Data Pipeline」（空间数据流管线）。**

这是当前机器人底层、数字孪生、Spatial Computing 的共同范式。各模块应解耦：

- **算法层**：只负责生成增量更新
- **数据交换层**：使用与内部实现无关的稳定消息格式
- **传输层**：负责高效、可靠地传送
- **空间索引层**：用 Pose Graph / Graph Node 维持全局坐标、版本与数据引用
- **远程建图层**：自由选择最适合稠密重建的数据结构
- **任务编排层**：用 Folder / ActionGroup / Trigger 决定数据服务哪个任务、何时流动

这也是越来越多机器人平台、数字孪生系统和空间计算系统采用的设计思路。

---

## 2. 知识体系总览

| 方向 | 代表工作 | 核心思想 |
|------|----------|----------|
| 增量地图同步 | LECES (2024)、Kimera-Multi、MapAPI | 只同步变化数据（Delta Sync） |
| 高性能本机通信 | Iceoryx、ROS 2 Shared Memory、Cyclone DDS SHM | 零拷贝 IPC，消除 memcpy 和序列化 |
| 高效序列化 | FlatBuffers、Cap'n Proto、SBE（Simple Binary Encoding） | 最小化序列化/反序列化开销 |
| 高性能网络传输 | QUIC、Zenoh、eCAL | 面向低延迟和跨网络的数据分发 |
| 地图表示 | OpenVDB、Voxel Hashing、NanoVDB、TSDF | 稀疏体素、高效存储和流式更新 |
| 稠密重建 | Voxblox、nvblox、BundleSDF、Gaussian Splatting | 从局部更新逐步构建全局稠密地图 |

---

## 3. 先进整体架构

一个比较先进的整体架构可以是：

```
LiDAR
   │
Super-LIO
   │
Local Incremental Map (iVox / Hash，内部实现)
   │
Adapter + Dirty Block / Delta Generator
   │
Canonical SpatialChunk / VoxelDiff
   │
├─ Iceoryx / loaned message（本机）
└─ QUIC / Zenoh（跨机器人或远程 PC）
   │
Remote Map Fusion
   ├─ Pose Graph + Graph Node Index
   ├─ VLN：text → 子图检索 → RGB / Voxel Chunk
   └─ Reconstruction：Occupancy / TSDF → Mesh
```

### 3.1 与 SLAM-Token 方案的对应关系

| 管线阶段 | SLAM-Token 现有实现 |
|----------|---------------------|
| LiDAR + LIO | Livox Mid-360 + Super-LIO（本仓帧耗时【待补充实测】；论文参考见 Super-LIO 阅读笔记） |
| Local Incremental Map | 【待补充】以 `motion_ws` 实际 commit 核对 iVox / OctVox / Hash 实现 |
| Dirty Block / Delta | 运动与几何变化的事件触发（具体阈值由内部 Gate 冻结） |
| 序列化 + 压缩 | Protobuf schema（demo 期） |
| 传输 | ZMQ/WiFi（demo 期） |
| Remote Fusion | 网关版本化 SpatialChunk merge + 轻量 Pose Graph |
| 空间索引 | Graph Node → KeyFrame / RGB / Voxel Chunk / Semantic Patch |
| 下游消费 | x86 VLN Adapter、当前 Nav2 2D；ego/3D planner 与 Occupancy/TSDF/Mesh 为后续候选 |

**架构铁律：协议是不变量，前端是可换件。** 对外只暴露统一 KeyFrame/VoxelDiff 协议；传输载体可替换——**换的是运输车，不是货物格式**。

### 3.2 两条空间链与一个索引

| 链路 | 回答 | 产物 |
|---|---|---|
| 增量体素链 | 空间里有什么、能否通行 | SpatialChunk/VoxelDiff、语义标签、重建块 |
| Pose Graph 链 | 这些内容在哪里、不同机器人如何对齐 | GraphNode/GraphEdge、优化后位姿 |
| Graph 索引 | 当前文本任务应该读取哪些空间内容 | Graph Node 关联的 KeyFrame、RGB、Chunk 与语义引用 |

Pose Graph 不能单独作为 VLN 环境输入，因为节点与约束边不包含足够的物体和可通行几何；全量体素也不应直接输入 VLN。正确路径是按 `text + current_pose + Folder scope + map_version` 检索相关子图，再读取关联空间块完成 grounding。

---

## 4. 传输与序列化方案对比

### 4.1 五种方案速览

| 方案 | 优点 | 缺点 / 适用边界 |
|------|------|-----------------|
| **ROS 2 DDS** | 开发快，生态成熟，QoS/发现完善 | 大量 Voxel 序列化压力大（CDR + 逐消息拷贝） |
| **Iceoryx** | 同机跨进程零拷贝，性能极佳 | **不能跨网络**；Remote 在本机时最佳 |
| **FlatBuffers** | Zero-Copy Deserialize，Voxel 直接访问，无需 new/memcpy/deserialize | 需按固定布局设计 schema |
| **Cap'n Proto** | 同样 Zero-Copy，RPC 一体化 | Google 内部机器人栈常用，学习曲线略陡 |
| **QUIC** | UDP + 可靠 + 多路复用，弱网友好，比 DDS 更易控制 | 需自建应用层语义，生态不如 DDS 完整 |

### 4.2 按场景选型

| 场景 | 推荐 | 原因 |
|------|------|------|
| **边端本机**（LIO → 事务/Token Encoder → Nav2/Recorder） | Iceoryx 或 ROS2 loaned message（候选） | 低拷贝，不涉及跨网；不得宣称端到端零拷贝 |
| **边端 → 同机 PC**（Go2 Orin → 笔记本） | 共享内存 / Unix domain socket + FlatBuffers | 同网段、低延迟，不必上 DDS 全家桶 |
| **边端 → 远程网关**（弱网 WiFi） | **Zenoh 或 QUIC** + FlatBuffers + LZ4 | 断线重连、带宽自适应；弱网主题是差异化 |
| **网关 ↔ 多机调度** | Fast DDS（控制面）+ Zenoh（数据面） | DDS 做 RPC/QoS/发现；大块 spatial data 走 Zenoh pub/sub |
| **Schema 定稿** | FlatBuffers > Protobuf | 体素 diff 是大量同质小记录，FlatBuffers 直接 mmap 访问，避免 deserialize 风暴 |

### 4.3 DDS 的「Voxel 序列化压力」解法

问题不在 DDS 本身，而在 **CDR 序列化 + 逐消息拷贝**。解法：

1. **数据面和控制面分离**（DDS 传 meta，Zenoh/QUIC 传 chunk）
2. **同机段用 Data-sharing / iceoryx 零拷贝**
3. **消息体用 FlatBuffers 预布局**，DDS 只传 loaned buffer 指针

### 4.4 项目阶段建议

| 阶段 | 传输载体 | Schema | 说明 |
|------|----------|--------|------|
| Demo（当前） | ZMQ + WiFi | Protobuf | 快速验证，schema 按 FlatBuffers 思维设计 |
| 产品期 | DDS + 共享内存零拷贝 / Zenoh | FlatBuffers | 换运输车，不换货物格式 |
| 多机网关 | Fast DDS（控制）+ Zenoh（数据） | FlatBuffers + LZ4 | 弱网协同场景 |

---

## 5. 压缩策略

Voxel 数据其实很好压缩。典型三连：

```
Morton 排序 → Delta Encoding → LZ4 / Zstd
```

示例（Delta Encoding）：

```
原始:  111111111, 111111112, 111111113
Delta: 111111111, +1, +1
```

与哈希体素 diff 天然契合：

```
原始: [hash_key, x, y, z, count, intensity] × N
优化: Morton 排序 → 对 hash_key 做 delta → 坐标量化 → LZ4 块压缩
```

| 算法 | 特点 | 适用 |
|------|------|------|
| **LZ4** | 极快，压缩率适中 | 实时流式传输 |
| **Zstd** | 高压缩率，速度尚可 | 带宽极度受限时 |

运动与几何变化的事件触发可进一步限制 N 的大小；具体阈值属于内部待冻结设计。历史带宽估算仅作架构参考，需由 `40-验证/P0-Benchmark-模板.md` 实测确认。

---

## 6. Spatial Computing 前瞻：从 Voxel 到 Chunk

行业趋势不是传整张地图，而是 **Transmit Chunk**：

| 阶段 | 传什么 | 代表 |
|------|--------|------|
| 现在（机器人导航） | Hash voxel diff / submap pose | SLAM-Token、Kimera-Multi |
| 近期（数字孪生） | TSDF block / ESDF slice | nvblox、Voxblox |
| 中期（Spatial Computing） | Gaussian splat chunk / mesh LOD | NVIDIA Omniverse、Apple RoomPlan |
| 远期（共享空间） | Semantic scene graph + anchor | Kimera DSG、AR Cloud |

NVIDIA 很多工作都是 **Chunk Streaming**，类似 Minecraft 加载地图，而不是 Entire Map。

中间件 schema 应设计成 **「Spatial Chunk」抽象**，而不是序列化 iVox/OctVox 的内部指针、桶或节点：

```text
SpatialChunk
├─ chunk_id / robot_id / timestamp
├─ frame_id / pose / covariance
├─ map_version / base_version
├─ voxel_size / chunk_origin / LOD
├─ payload_type / payload
└─ graph_node_id / confidence
```

未来从哈希体素 diff 升级到 TSDF、mesh 或 Gaussian chunk，只需更换 `payload_type` 和编码，不推翻协议。iVox 是生产者，SpatialChunk 才是传输与消费契约。

### 6.1 同一增量事实的两类消费

- **VLN/VLA**：SpatialChunk → BEV/三视图或稀疏体素 Token；与 text、当前 RGB、Graph 子图一起输入。
- **三维重建**：SpatialChunk → Occupancy/TSDF 融合 → Mesh；不要求 VLN 使用同一种内部表示。

两类消费者共享 chunk/version/pose 锚点，但各自维护适合任务的派生表示。

---

## 7. 推荐阅读清单（按优先级）

### Tier 0：立刻建立直觉（1–2 周）

| 方向 | 必读 | 为什么重要 |
|------|------|------------|
| **增量地图同步** | [Kimera-Multi](https://github.com/MIT-SPARK/Kimera-Multi) | 分布式 pose graph + 子图交换，多机网关 merge 直接对标 |
| | LECES (2024) | 只传变化块，论文级论证 Delta Sync 带宽收益；PDF【待补充】见 `papers/04/2024-RAL-LECES-PDF待补充.md` |
| | MapAPI | 地图作为 API/服务的抽象，「协议即产品」参考；PDF ✅ `papers/04/2015-ICRA-MapAPI-Cieslewski.pdf` |
| **稀疏体素/哈希** | [iVox](https://github.com/hku-mars/FAST_LIO)（FAST-LIO2 配套） | 和 OctVox 同族，哈希体素 + 局部更新工程细节 |
| | [Voxel Hashing](https://niessnerlab.org/)（Nießner 2013） | 稀疏体素奠基，理解 block/chunk 粒度设计 |
| **本机零拷贝** | [Iceoryx](https://github.com/eclipse-iceoryx/iceoryx) | 同机 LIO → Tokenizer → planner 消除 memcpy |
| | ROS 2 Intra-process + loaned messages | 最低成本零拷贝入口 |
| | Cyclone DDS + iceoryx 集成 | 多进程 DDS 零拷贝 |

### Tier 1：构建传输层判断力（2–4 周）

| 方向 | 必读 | 要点 |
|------|------|------|
| **序列化** | [FlatBuffers](https://google.github.io/flatbuffers/) | Voxel diff zero-copy 访问 |
| | [Cap'n Proto](https://capnproto.org/) | Zero-copy + RPC 一体化 |
| | [SBE](https://github.com/real-logic/simple-binary-encoding) | 固定布局，体素数组批量传输极快 |
| **跨网络传输** | [Zenoh](https://zenoh.io/) | pub/sub + 存储 + 路由，弱网比纯 DDS 灵活 |
| | [QUIC](https://www.rfc-editor.org/rfc/rfc9000) + [msquic](https://github.com/microsoft/msquic) | 弱网多路复用、0-RTT 重连 |
| | [eCAL](https://github.com/eclipse-ecal/ecal) | 机器人低延迟 pub/sub，和 Zenoh 对比 |
| **压缩** | LZ4、Zstd | Morton + Delta + LZ4 是体素流标准三连 |

### Tier 2：稠密重建与 Spatial Computing 前瞻（1–2 月）

| 方向 | 必读 | 为什么 |
|------|------|--------|
| **TSDF 流式** | [nvblox](https://github.com/nvidia-isaac/nvblox) | NVIDIA chunk streaming，「Minecraft 式加载」 |
| | [Voxblox](https://github.com/ethz-asl/voxblox) | 经典 ESDF/TSDF 增量更新 |
| **OpenVDB 生态** | [OpenVDB](https://www.openvdb.org/) + [NanoVDB](https://developer.nvidia.com/nanovdb) | 远程融合稠密表示，GPU 友好 |
| **Gaussian / 神经表示** | [3D Gaussian Splatting](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/) | Spatial Computing 从 voxel 转向 Gaussian chunk |
| | [BundleSDF](https://bundlesdf.github.io/) | 在线神经隐式重建，「传 submap 不传全图」 |
| **多机 SLAM** | [Swarm-SLAM](https://github.com/MISTLab/Swarm-SLAM) | 多机规划已选定，深入关键帧/子图交换 |
| | [COVINS-G](https://github.com/VIS4ROB-lab/covins) | 研究参考，centralized vs decentralized 融合差异 |

### Tier 3：系统论文（建立「定义者」视野）

这些不是学某个库，而是学**怎么设计一层标准接口**：

- **Kimera** 系列（MIT SPARK）：从 mesh 到 DSG 语义场景图，「几何 → 语义」分层
- **NVIDIA Isaac Perceptor / Nova**：工业级 spatial streaming pipeline
- **Meta Reality Labs** spatial anchor / scene mesh streaming（Spatial Computing 产品化参考）
- **edgeSLAM2** 类前后端分离工作：专利可以、顶会新意不足，但读透有助于写 Spec

---

## 8. 八周阅读路线

```
Week 1–2:  iVox 源码 + Iceoryx examples + FlatBuffers tutorial
           → 建立「本机零拷贝 + zero-copy 反序列化」直觉

Week 3–4:  Kimera-Multi 论文+代码 + Swarm-SLAM 关键帧交换逻辑
           → 理解多机 delta merge 工程细节

Week 5–6:  nvblox chunk streaming + Zenoh pub/sub 教程
           → 理解「Minecraft 式地图加载」+ 弱网传输

Week 7–8:  QUIC 基础 + LZ4/Morton delta 实现 toy benchmark
           → 数据说话：Protobuf vs FlatBuffers × ZMQ vs QUIC 带宽/延迟
```

Week 8 的 benchmark 可直接成为 **SLAM-VLA Benchmark** 中「Token 传输效率」指标的参考实现。

---

## 9. 行动建议（结合 SLAM-Token 项目）

当前最该做的不是换一个通信库，而是：

1. **核对前端事实**：以 `motion_ws` commit 确认实际 iVox/OctVox/Hash Map 接口
2. **把 schema 按 Streaming Spatial Chunk 设计**（类型无关、版本化、LOD 可扩展）
3. **建立 Graph Node 索引**：绑定 KeyFrame、RGB、Voxel Chunk 与语义引用
4. **本机段先上零拷贝**（Iceoryx / loaned message）
5. **跨网段为弱网选 Zenoh 或 QUIC**，而不是默认 DDS 扛所有数据
6. **压缩用 Morton + delta + LZ4**，与 VoxelDiff 结合
7. **先完成 Mapping–Planner–Avoid–Arrival 和 benchmark**；模型量化压缩只在实测成为瓶颈后启动

### 9.1 与标准锚点的对齐

| 锚点 | 本知识体系对应 |
|------|----------------|
| 锚点 1：SLAM 输出规范 | 前端 Adapter → SpatialChunk/VoxelDiff + 双触发 + Morton/LZ4 |
| 锚点 2：VLA 输入规范 | text + Graph 子图 + SpatialChunk → 三视图 / 稀疏体素 Token |
| 锚点 3：交互协议规范 | FlatBuffers schema + Zenoh/QUIC 数据面 + RPC 控制面 |
| 锚点 4：任务编排规范 | Folder + ActionGroup + Trigger |

### 9.2 评测指标关联

| 指标 | 本知识体系支撑 |
|------|----------------|
| Token 带宽（KB/s） | Delta Sync + LZ4 压缩 |
| 关键帧延迟（ms） | 本机零拷贝 + FlatBuffers zero-copy |
| 边端 CPU 占用率 | 避免 deserialize 风暴 |
| 全局空间块一致性（%） | Remote Map Fusion + version/hash merge |
| SR / SPL / Arrival 成功率 | Graph 检索上下文 + 分层规划执行 |
| 每成功任务传输量 | Trigger + Delta Sync + 任务范围检索 |

---

## 10. 一句话总结

知识框架与 SLAM-Token 方案是**同一条路**。核心是 **Streaming Spatial Data Pipeline**：增量体素承载空间事实，Pose Graph 维护全局一致性，Graph Node 索引任务相关上下文，Folder / ActionGroup / Trigger 驱动数据流；前端、传输载体和下游表示均可替换。
