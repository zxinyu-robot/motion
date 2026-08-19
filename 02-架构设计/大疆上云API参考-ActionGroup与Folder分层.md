# 大疆上云 API 参考 —— ActionGroup 与 Folder 分层

——无人机协议如何下沉到机器人边端，以及 SLAM-Token 任务编排规范

> 整理自技术讨论（2026-07-09，2026-07-14 更新）  
> 视角：协议产品化 / 弱网中间件 / 多机协同调度  
> 关联文档：《Go2-VLA-SLAM-Token 技术方案》《SLAM-Token 弱网中间件-汇报材料》《行为树调度架构_BehaviorTree设计》《Streaming-Spatial-Data-Pipeline-知识体系与阅读路线》  
> 官方参考：[DJI Cloud API Doc](https://github.com/dji-sdk/Cloud-API-Doc)
> **保密与状态**：`patent-sensitive`；本文是大疆分层到机器人任务契约的内部参考草案，`canonical: false`。MissionSpec、Trigger 与阈值相关内容不得在申请日前作为公开 Spec；当前执行口径以 ForkSpatialLink 方向稿 §2.4、§4.3 为准。

---

## 1. 核心关注点

**参考大疆上云 API，不是因为 MQTT 或物模型本身，而是因为它的 ActionGroup + Folder 分层任务编排模型。**

无人机和地面机器人在「边端 Agent → 网关 → 远程大脑」链路上存在可借鉴的任务分层。大疆上云协议不能原样照搬，应抽取 Folder / ActionGroup / Trigger 语义并经过机器人安全、坐标系和弱网 Gate。

真正值得借鉴的三层：

| 层级 | 大疆概念 | 管什么 |
|------|----------|--------|
| 全局策略 | `missionConfig` | 失控怎么办、超时返航、机型适配 |
| 子任务路径 | **Folder** | 去哪：一条可执行航线 / 子任务 |
| 触发式动作 | **ActionGroup** | 到了 / 走的过程中干什么：拍照、录点云、悬停 |

以及地图侧的 **element-group**（图层分组），用于战术标注与多终端同步。

---

## 2. 先澄清：三样不同的「地图 API」

| 名称 | 是什么 | 和你的关系 |
|------|--------|------------|
| **大疆地图元素（Map Elements）** | HTTPS + WebSocket 同步 GeoJSON 点线面 | 学图层分组与 CRUD+推送模式；不是体素流 |
| **大疆 WPML 航线（Folder + ActionGroup）** | 任务编排：路径 + 触发式动作 | **重点参考**，对齐行为树 SubTree |
| **ETHZ MapAPI**（[ethz-asl/map_api](https://github.com/ethz-asl/map_api)） | 学术 P2P 分布式 chunk 同步（像 git for maps） | 学 Chunk/Trigger 思想；与中心化网关路线不同 |

大疆「地图元素」≠ OctVox diff。大疆不传稠密 3D 体素，传的是**战术标注层**。你的壁垒在几何流层（voxel diff），壳子学大疆，货物自己定义。

---

## 3. 大疆协议整体架构（可下沉边端）

### 3.1 端-边-云三层

```
无人机 ──→ 网关（遥控器/机场/Pilot2）──→ 第三方云平台
Go2   ──→ 边端 Agent（Orin + Tokenizer）──→ x86 协同网关 / PC VLA
```

飞机不直连云，必须经网关——你的 Tokenizer 就是这个网关 Agent。

### 3.2 三协议铁三角

| 协议 | 用途 | 边端映射 |
|------|------|----------|
| **MQTT** | 物模型：定频状态 + 事件 + 服务调用 | odom 定频、关键帧事件、SetWaypoint |
| **HTTPS** | 大块 CRUD、首次全量拉取 | 关键帧列表、子图元数据、任务文件 |
| **WebSocket** | 实时变更推送 | 「B 机有新关键帧」通知 Web/其他机器人 |
| **对象存储** | 媒体/航线文件 | FlatBuffers + LZ4 体素块、RGB JPEG |

协议不绑公有云。MQTT Broker + HTTPS + WS 跑在**本地 x86 网关**上，就是边云一体。

### 3.3 物模型 pushMode 分流

| pushMode | 含义 | MQTT Topic | SLAM-Token 映射 |
|----------|------|------------|-----------------|
| 0 | 定频推送 | `thing/product/{sn}/osd` | odom、电量、ego 状态 |
| 1 | 变化才推 | `thing/product/{sn}/state` | 体素 diff 超阈值、回环、定位丢失 |
| — | 云端调用 | `thing/product/{sn}/services` | UploadKeyFrame、SetWaypoint、RequestPeerView |

这和「运动 + 几何」双触发关键帧天然对齐。

### 3.4 Workspace 容器

大疆用 `workspace_id` 隔离任务空间下的设备、航线、地图元素。多机网关可直接映射：

```
workspace_id  →  任务组 / 厂房区域
gateway_sn    →  Go2 #1 / Go2 #2
device_sn     →  本体传感器模组
```

---

## 4. Folder + ActionGroup：重点分层模型

### 4.1 WPML 文件结构

来源：[waylines.wpml 说明](https://developer.dji.com/doc/cloud-api-tutorial/cn/api-reference/dji-wpml/waylines-wpml.html)

```
Document
├── missionConfig              ← 全局任务配置（返航、失控、机型、速度…）
└── Folder                     ← 一条可执行航线（子任务）
    ├── templateId / waylineId
    ├── autoFlightSpeed
    ├── startActionGroup       ← 航线开始前动作（断点恢复也先跑这个）
    └── Placemark × N          ← 航点 0, 1, 2…
        ├── Point (lat, lon, height)
        ├── executeHeight / waypointSpeed / turnParam
        └── actionGroup        ← 该航点段上的触发式动作
```

要点：

- **一个 Folder = 一条完整可执行航线**（wayline）
- 一个 KMZ 可有**多个 Folder**（如倾斜摄影生成 5 条航线）
- `missionConfig` 管全局，`Folder` 管局部执行

### 4.2 ActionGroup 结构

来源：[共用元素 actionGroup](https://developer.dji.com/doc/cloud-api-tutorial/cn/api-reference/dji-wpml/common-element.html)

```xml
<wpml:actionGroup>
  <wpml:actionGroupId>0</wpml:actionGroupId>
  <wpml:actionGroupStartIndex>1</wpml:actionGroupStartIndex>
  <wpml:actionGroupEndIndex>1</wpml:actionGroupEndIndex>
  <wpml:actionGroupMode>sequence</wpml:actionGroupMode>
  <wpml:actionTrigger>
    <wpml:actionTriggerType>reachPoint</wpml:actionTriggerType>
  </wpml:actionTrigger>
  <wpml:action> gimbalRotate </wpml:action>
  <wpml:action> takePhoto </wpml:action>
</wpml:actionGroup>
```

#### 四个关键设计

**① 区间生效（StartIndex ~ EndIndex）**

- `start == end`：只在单个航点触发
- `start < end`：覆盖一段路径（如航点 3→7 之间等距拍照）

**② 触发器与动作分离**

| actionTriggerType | 含义 | 典型配合动作 |
|-----------------|------|-------------|
| `reachPoint` | 到达航点时 | takePhoto、gimbalRotate |
| `betweenAdjacentPoints` | 航段飞行过程中 | gimbalEvenlyRotate |
| `multipleTiming` | 等时间间隔 | takePhoto（等时拍照） |
| `multipleDistance` | 等距离间隔 | takePhoto（等距拍照） |

路径怎么走 和 什么时候触发感知动作 是两套逻辑。

**③ 动作串行（sequence）**

一个 ActionGroup 内多个 action 按序执行。

**④ 航线级 startActionGroup**

Folder 级别可在开始前执行初始化动作；断点恢复时**先跑 startActionGroup，再跑航点动作**。

### 4.3 大疆 action 类型（负载级）

| action | 含义 |
|--------|------|
| `takePhoto` | 单拍 |
| `startRecord` / `stopRecord` | 录像 |
| `gimbalRotate` | 转云台 |
| `hover` | 悬停等待 |
| `recordPointCloud` | 点云录制 |
| `orientedShoot` | 定向精准拍照 |
| `customDirName` | 创建媒体文件夹 |

---

## 5. 地图侧 element-group（另一套分组）

来源：[地图元素功能集](https://developer.dji.com/doc/cloud-api-tutorial/cn/feature-set/pilot-feature-set/map-elements.html)

```
Workspace
└── element-group（图层）
    ├── type: CUSTOM / DEFAULT / SHARED
    └── elements[]（点线面 GeoJSON）
```

| 图层类型 | 用途 |
|----------|------|
| `SHARED`（Pilot Share Layer） | 飞手端共享标注，必须存在否则无法同步 |
| `DEFAULT` | 系统默认（如禁飞区） |
| `CUSTOM` | 用户自定义 |

同步机制：HTTPS CRUD + WebSocket 推送变更。A 机标注可同步给 B 机和 Web 端。

与 WPML Folder **不是同一层**，但分层思想一致：Workspace → Group → Element。

---

## 6. 与 SLAM-Token / 行为树的映射

### 6.1 分层对照表

| 大疆 | SLAM-Token / 行为树 | 说明 |
|------|---------------------|------|
| `workspace` | group-A 编队 / 任务空间 | 多机隔离容器 |
| `missionConfig` | 组级 BT 全局参数 | 弱网降级、断网切 L1+L2、超时策略 |
| **Folder** | **group-B SubTree** | 一条语义子任务（"探索区域 A"） |
| `Placemark` | coarse waypoint | VLA 输出，~10s/步，odom 系 |
| **ActionGroup** | **触发式 Action 序列** | 何时推关键帧、何时等 VLA、何时请求协同 |
| `actionTrigger` | 双触发关键帧 | reachPoint=运动触发，multipleDistance=行进中推 diff |
| `startActionGroup` | 任务初始化 | SLAM 对齐、坐标系初始化 |
| element-group | spatialLayers | 禁区、战术标注（GeoJSON） |
| `takePhoto` | `uploadKeyFrame` | RGB + voxel diff |
| `recordPointCloud` | `uploadVoxelChunk` | OctVox diff 流 |
| （无） | `requestPeerView` | 多机协同，B 视角共享给 A |
| （无） | `waitForVLA` | 等 PC 端推理完成 |
| （无） | `updateGraphNode` | 绑定 pose、KeyFrame、RGB、Voxel Chunk 与语义引用 |
| （无） | `queryGraph` | 按 text、当前位置、Folder 范围和地图版本检索子图 |

### 6.2 Graph Node 是任务编排与空间数据的连接点

Folder / ActionGroup / Trigger 不负责生成或优化 Pose Graph，而是负责何时采集、绑定、上传、检索和消费 Graph Node：

```text
Folder：SearchCupInOfficeA（任务语义 + 区域/子图范围）
  ↓
ActionGroup：captureKeyFrame → uploadVoxelChunk → updateGraphNode
  ↓
Trigger：reachPoint / voxelDiff / semanticLowConfidence / networkRecovered
  ↓
Graph Node：pose + KeyFrame/RGB + SpatialChunk + Semantic Patch
  ↓
queryGraph(text, current_pose, folder_scope, map_version)
  ↓
VLN grounding → 下一 coarse waypoint / Folder
```

Graph Node 是空间记忆索引，不是把所有 payload 内嵌到图中；大块 RGB/体素数据保存在数据面或对象存储，节点只保存稳定引用与版本。

### 6.3 当前 SLAM-Token 管线 vs 大疆分层后

**当前 P0（路径与感知动作尚未完全分层）：**

```
空间增量 → VLA 出 waypoint/ActionGroup → Nav2 2D + L1 安全链执行
```

**后续分层目标（路径与动作解耦）：**

```
VLA 出 Folder + waypoint（去哪）
     ↓
边端按 ActionGroup + Trigger 执行（到了/走着干什么）
     ↓
可替换本地规划器执行路径 + 固件 L1 兜底
```

### 6.4 机器人版 ActionGroup 示例

```yaml
# Folder: "SearchCupInOffice"
folderId: 0
graphScope: {region_id: office_a, map_version: latest}
waypoints:
  - index: 0, pose: {x: 1.2, y: 3.4, theta: 0.0}
  - index: 1, pose: {x: 5.6, y: 7.8, theta: 1.57}

startActionGroup:
  - type: initSLAM
    params: { frame: odom, align_world: true }

actionGroups:
  - id: 0
    startIndex: 0
    endIndex: 0
    trigger: reachPoint
    actions:
      - type: uploadKeyFrame
        params: { trigger_mode: motion }
      - type: updateGraphNode
        params: {bind: [pose, keyframe, rgb, voxel_chunk]}

  - id: 1
    startIndex: 0
    endIndex: 1
    trigger: multipleDistance
    triggerParam: 2.0          # 每走 2m
    actions:
      - type: uploadKeyFrame
        params: { trigger_mode: voxel_diff, threshold: 200 }
      - type: requestPeerView
        params: { peer_id: go2_b }

  - id: 2
    startIndex: 1
    endIndex: 1
    trigger: reachPoint
    actions:
      - type: semanticObserve
        params: { target: cup, views: three_view }
      - type: queryGraph
        params: {text: "find the cup", scope: current_folder, top_k: 8}
      - type: waitForVLA
        params: { timeout_s: 15 }

  - id: 3
    startIndex: 0
    endIndex: 1
    trigger: semanticLowConfidence
    triggerParam: 0.6
    actions:
      - type: requestPeerView
        params: {scope: current_folder}
      - type: queryGraph
        params: {include_peer_nodes: true}
```

---

## 7. SLAM-Token MissionSpec v0.1（草案）

建议定义的协议结构，壳子学大疆，payload 自研：

```
MissionSpec
├── missionConfig
│   ├── coordinateFrame          # odom / map / world
│   ├── finishAction             # goHome / holdPosition / requestHelp
│   ├── weakNetPolicy            # 断网切 L1+L2 / 降频关键帧
│   ├── timeout_s
│   └── robotProfile             # 机型、传感器、SLAM 前端类型
│
├── folders[]                    # 子任务列表（对应 Folder）
│   ├── folderId
│   ├── name
│   ├── graphScope              # region/node filters + map_version
│   ├── waypoints[]              # coarse waypoint（odom 系）
│   │   ├── index
│   │   ├── pose {x, y, theta}
│   │   └── speed
│   ├── startActionGroup[]       # 任务开始前动作
│   └── actionGroups[]           # 航点段触发式动作
│       ├── actionGroupId
│       ├── startIndex
│       ├── endIndex
│       ├── mode                 # sequence（串行）
│       ├── trigger
│       │   ├── type             # reachPoint / voxelDiff / semanticLowConfidence / networkRecovered / graphOptimized
│       │   └── param
│       └── actions[]
│           ├── actionId
│           ├── type             # 见 §7.1 枚举
│           └── params
│
└── spatialLayers[]              # element-group：战术标注
    ├── groupId
    ├── type                       # CUSTOM / DEFAULT / SHARED
    └── elements[]                 # GeoJSON 点线面
```

### 7.1 机器人 action 枚举（差异化）

| action type | 含义 | 对应大疆 |
|-------------|------|----------|
| `uploadKeyFrame` | 推 RGB + OctVox diff | takePhoto + recordPointCloud |
| `uploadVoxelChunk` | 纯体素 diff 流 | recordPointCloud |
| `semanticObserve` | 三视图 / Minkowski 编码观测 | orientedShoot |
| `waitForVLA` | 等待 PC 端推理 | hover |
| `requestPeerView` | 请求 B 机关键帧/视角 | （无，多机独有） |
| `updateGraphNode` | 绑定/更新 Pose、KeyFrame、Chunk、RGB、语义引用 | （无） |
| `queryGraph` | 按文本、位置、Folder 范围和版本检索相关子图 | （无） |
| `refreshSemanticLabel` | 对指定节点/Chunk 重新做边侧语义分割 | （无） |
| `detectObject` | 本地/远程目标检测 | （无） |
| `initSLAM` | 初始化/对齐坐标系 | startActionGroup 语义 |
| `navigateTo` | 执行到 waypoint | 隐含在 Placemark 路径中 |

### 7.2 传输分工

| 数据类型 | 传输通道 | 格式 |
|----------|----------|------|
| MissionSpec 元数据 | MQTT Service / HTTPS | JSON 或 FlatBuffers |
| waypoint / action 指令 | MQTT `services` | 物模型 Service |
| voxel diff payload | HTTPS 上传 / Zenoh 数据面 | FlatBuffers + LZ4 |
| Graph Node / Edge 元数据 | DDS/MQTT 事件 + HTTPS CRUD | JSON/FlatBuffers；大块 payload 仅存引用 |
| 图层变更通知 | WebSocket | 同大疆地图元素 |
| odom / 状态 | MQTT `osd` / `state` | 物模型 Property |

**换的是运输车，不是货物语义**——MissionSpec 仍为内部草案；稳定语义与具体 schema 均须经过实现、兼容性和专利 Gate 后冻结，传输载体可独立评估。

---

## 8. 借鉴与不借鉴

### 8.1 借鉴

| 项 | 原因 |
|----|------|
| Folder / ActionGroup / Trigger 三层 | 路径与感知动作解耦，直接对齐行为树 SubTree |
| missionConfig 全局策略 | 弱网降级、断点恢复语义 |
| element-group 图层分组 | 战术标注、多机共享 |
| startActionGroup | 任务初始化与断点恢复 |
| Workspace 多租户容器 | 多机任务隔离 |
| HTTPS CRUD + WS 推送 | 地图/任务元数据同步模式 |
| 物模型 osd/state/services 分流 | 定频小数据 vs 事件大数据 |

### 8.2 不借鉴

| 项 | 原因 |
|----|------|
| WPML XML 格式 | 用 JSON/FlatBuffers + 自有 MissionSpec |
| WGS84 航点坐标 | 机器人用 odom/map 系 |
| 只传 GeoJSON 点线面 | 必须加 voxel diff 几何流层 |
| 无人机负载 action（gimbal 等） | 换成认知级/协同级 action |
| ETHZ MapAPI 去中心化 P2P | 与中心化网关 hash merge 路线不符 |

---

## 9. 与标准锚点的关系

| 锚点 | 本规范对应 |
|------|------------|
| 锚点 1：SLAM 输出规范 | `uploadKeyFrame` / `uploadVoxelChunk` + SpatialChunk/VoxelDiff |
| 锚点 2：VLA 输入规范 | text + `graphScope/queryGraph` + RGB/SpatialChunk |
| 锚点 3：交互协议规范 | MissionSpec + MQTT Service + 数据面分离 |

ActionGroup 的 `trigger` 可承载事件触发语义【内部草案】：

- `reachPoint` / 运动阈值 → 运动触发
- `multipleDistance` + `voxelDiff` → 几何变化触发（具体阈值不在本文公开口径中冻结）
- `semanticLowConfidence` → 目标未确认时补视角、查询同机节点
- `networkRecovered` → 续传缺失 diff 并恢复等待中的 ActionGroup
- `graphOptimized` → 位姿图更新后刷新节点空间锚点，不重复上传 payload

---

## 10. 推荐阅读顺序

### 针对 ActionGroup + Folder（优先）

1. [waylines.wpml 说明](https://developer.dji.com/doc/cloud-api-tutorial/cn/api-reference/dji-wpml/waylines-wpml.html) — Folder 结构
2. [共用元素 actionGroup](https://developer.dji.com/doc/cloud-api-tutorial/cn/api-reference/dji-wpml/common-element.html) — trigger 类型全集
3. [地图 element-groups API](https://developer.dji.com/doc/cloud-api-tutorial/cn/api-reference/pilot-to-cloud/https/map-elements/create.html) — 图层分组
4. 本仓库 `02-架构设计/行为树调度架构_BehaviorTree设计.md` §3.2 group-B SubTree — 行为树对齐

### 针对协议整体（次之）

5. [产品架构](https://developer.dji.com/doc/cloud-api-tutorial/cn/overview/product-architecture.html) — 端边云分层
6. [物模型概念](https://developer.dji.com/doc/cloud-api-tutorial/cn/overview/basic-concept/thing-model.html) — Property/Service/Event
7. [MQTT Topic 定义](https://developer.dji.com/doc/cloud-api-tutorial/cn/api-reference/dock-to-cloud/mqtt/topic-definition.html) — osd/state/services
8. GitHub：[Cloud-API-Doc](https://github.com/dji-sdk/Cloud-API-Doc) — 物模型 JSON 与 Demo

### 学术参考（MapAPI，不必上手）

9. [ETHZ MapAPI](https://github.com/ethz-asl/map_api) — Chunk/Trigger 思想
10. [ICRA 2015 论文](http://rpg.ifi.uzh.ch/docs/ICRA15_Cieslewski.pdf) — 分布式地图版本控制

---

## 11. 一句话总结

大疆最值得学的不是通信协议，而是 **Folder（子任务路径）+ ActionGroup（触发式动作序列）+ Trigger（何时推数据）** 这套任务编排分层。Graph Node 补上中间的空间记忆索引：任务编排决定何时生产、绑定、查询和消费节点，SpatialChunk/VoxelDiff 负责承载几何事实，Pose Graph 负责全局一致性。协议壳子学大疆，空间数据契约自己定义。

---

## 文档元数据

| 字段 | 值 |
|---|---|
| id | ARCH-ACTIONGROUP-FOLDER-REF-001 |
| type | architecture-reference |
| stage | design |
| status | in-progress |
| canonical | false |
| evidence_level | proposal |
| confidentiality | patent-sensitive |
| updated | 2026-07-23 |
| next | 仅作为 P0-C ActionGroup 适配参考；字段与 Trigger 语义在实现、兼容性与专利 Gate 后冻结 |
