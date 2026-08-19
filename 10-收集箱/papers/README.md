# papers 分领域索引

> 原始 PDF 按**领域**存放，避免 `paper_final2` 式混乱。  
> 笔记镜像目录：`04-文献阅读/notes/<同编号>/`

---

## 目录一览


| 编号       | 目录                | 放什么                                            | 与 motion 主线关系 |
| -------- | ----------------- | ---------------------------------------------- | ------------- |
| `_inbox` | 未定类新进             | 刚下载、还没分类的 PDF                                  | 每周清零          |
| **01**   | `01-具身智能-VLA-VLN` | VLN、VLA、Embodied AI、NaVILA、OpenVLA             | **P0 核心**     |
| **02**   | `02-SLAM-定位-建图`   | LIO、voxel、loop、点云配准、定位                         | **P0 核心**     |
| **03**   | `03-多机协同-Swarm`   | Swarm-SLAM、C-SLAM、多智能体协同                       | **P0 核心**     |
| **04**   | `04-空间数据流-中间件`    | LECES、Delta sync、SLAM-Token、streaming pipeline | **P0 核心**     |
| **05**   | `05-通信-弱网-网络`     | DDS、Zenoh、MANET、5G/O-RAN、语义通信                  | **P1**        |
| **06**   | `06-模型压缩-边缘部署`    | BRCB、量化、INT8、边缘推理                              | **P1**        |
| **07**   | `07-规划-控制-RL`     | ego-planner、MPC、WBC、RL 导航                      | **P1**        |
| **08**   | `08-世界模型-多模态`     | World Model、VLM、3D-LLM、LL3DA                   | **P1 学术**     |
| **09**   | `09-协议-任务编排`      | Folder/ActionGroup、Mission Contract、KMZ        | **P1 产品**     |
| **90**   | `90-行业报告-趋势`      | 算力、大模型趋势、低空经济报告（非 peer-review）                 | 叙事参考          |
| **91**   | `91-航空-旁支`        | 跑道识别、着陆、机载雷达等历史方向                              | **旁支，不进 WBS** |
| **99**   | `99-已处理`          | 已读完且笔记已产出（可选归档 PDF）                            | —             |


---

## 使用规则

### 1. 新进 PDF

```text
下载 → _inbox/ → 判断领域 → 移入 01–09 / 90 / 91
```

不确定时先放 `_inbox`，在 `ProjectState.md` 记一条 todo。

### 2. 读完之后

```text
10-收集箱/papers/<领域>/xxx.pdf
    ↓ 分析（@文献阅读prompt.md）
04-文献阅读/notes/<领域>/<年>-<会>-<简称>-阅读笔记.md
    ↓ 可复用结论
05-知识沉淀/<主题>/CAP-*.md
    ↓（可选）
PDF 移入 99-已处理/ 或保留原位
```

### 3. 笔记命名

```
2025-IJCAI-BRCB-阅读笔记.md
2024-ICRA-SwarmSLAM-阅读笔记.md
```

### 4. 领域判断速查


| 关键词                                       | 目录  |
| ----------------------------------------- | --- |
| VLN, VLA, instruction following, NaVILA   | 01  |
| LIO, iVox, voxel, loop closure, ATE       | 02  |
| Swarm, multi-robot SLAM, C-SLAM           | 03  |
| KeyFrame, VoxelDiff, delta sync, token    | 04  |
| DDS, weak network, semantic comm, MANET   | 05  |
| quantization, BRCB, edge deploy, Orin     | 06  |
| ego-planner, MPC, locomotion, RL policy   | 07  |
| world model, VLM, 3D-LLM, embodied WM     | 08  |
| WPML, ActionGroup, mission, behavior tree | 09  |
| 行业深度、趋势报告、投资研报                            | 90  |
| 航空、跑道、着陆、机载                               | 91  |


---

## 当前库存（2026-07-17 整理）

> 【事实】根目录与 `CoRL/`/`IROS/`/`RSS/` 已清空；产品手册进 `10-收集箱/source/`。

### `_inbox`（待定类 / 非主线）

- `2407.18064v2-ComPeer-HCI.pdf`（HCI，建议丢弃或移出）
- `曾欣宇.pdf`
- `Elements_of_Information_Theory_Elements.pdf`（教材）
- `Hands On Machine Learning ... Geron.pdf`（教材）
- `未确认 525183.crdownload`（未完成下载，可删）

### 01-具身智能-VLA-VLN


| 文件 | 笔记 |
| ---- | ---- |
| `2607.09792.pdf` | `04-文献阅读/notes/01-具身智能-VLA-VLN/2026-arXiv-EmbodiedVLN-Survey-阅读笔记.md` ✅ |
| **AsyncShield** arXiv:2604.24086 | `04-文献阅读/notes/01-具身智能-VLA-VLN/2026-arXiv-AsyncShield-阅读笔记.md`（**PDF 待下载** → 本目录）；CAP-EXEC-ASYNC-SHIELD-ALIGN-001；方向稿 `01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` |
| `2509.19480v1-OmniVLA.pdf` | — |
| `VLA-AN-An Efficient and Onboard.pdf` | — |
| `OpenFly ... Aerial VLN.pdf` / `openuav_datas.pdf` | — |
| `CombatVLA...` / `CoT-VLA...` / `DataPlatter...` | — |
| `Gemini Robotics...` / `GR00T N1...` | — |
| `see_point_fly.pdf` | — |
| `SmartBot-2025-Sheng-...HumanoidRobots.pdf` | — |
| `具身智能：算法到场景...敬巍.pdf` / `通往真实世界的具身智能...王越.pdf` | — |


### 02-SLAM-定位-建图


| 文件 | 笔记 |
| ---- | ---- |
| `2509.05723v2-Super-LIO.pdf` | `04-文献阅读/notes/02-SLAM-定位-建图/2025-RAL-Super-LIO-阅读笔记.md` ✅；CAP-SLAM-SUPER-LIO-PRODUCER-001 |
| `2403.06341v1-RTAB-Map.pdf` | — |


- `DeepPointMap.pdf`
- `GS-PT ... 3DGS ...pdf` / `MapFusion ...pdf`
- `基于RGB信息的激光点云数据配准与分割精简算法.pdf`
- `基于BP神经网络的三维激光扫描点云数据的滤波方法研究.pdf`

### 03-多机协同-Swarm


| 文件 | 笔记 |
| ---- | ---- |
| `2301.06230v3-Swarm-SLAM.pdf` | `04-文献阅读/notes/03-多机协同-Swarm/2024-arXiv-Swarm-SLAM-阅读笔记.md` ✅；CAP-SLAM-SWARM-SLAM-GATE-001 |
| `2106.14386v2-Kimera-Multi.pdf`（+ `.txt`） | `04-文献阅读/notes/03-多机协同-Swarm/2022-TRO-Kimera-Multi-阅读笔记.md` ✅；CAP-SLAM-KIMERA-MULTI-REF-001 |
| `2510.23988v1-Collab-SLAM-3DGS.pdf` | — |
| `2310.11843v2-MultiRobot-Scaling.pdf` | — |
| `AT-Drone.pdf` / `mastering_multi_drone_volleyball.pdf` | — |
| `how_to_coordinate_UAVs_and.pdf` / `A_Cooperative_Bearin-Rate_Approach.pdf` | — |
| `Optimal Complexity in Decentralized Training.pdf` | — |
| `多智能体协同研究进展综述_ 博弈和控制交叉视角.pdf` | — |


### 05-通信-弱网-网络

- `基于AI和O-RAN架构的5G网络容量自适应算法.pdf`

### 06-模型压缩-边缘部署


| 文件 | 笔记 |
| ---- | ---- |
| `0766.pdf`（已恢复） | `04-文献阅读/notes/06-模型压缩-边缘部署/2025-IJCAI-BRCB-阅读笔记.md` ✅ |


### 07-规划-控制-RL

- `2410.03076v1-ResidualPolicy-Quadruped.pdf`
- `RAPID.pdf` / `Demonstrating_ViSafe.pdf` / `flyinghand.pdf`
- `fly_on_the_PC.pdf` / `Perception-aware_Planning_for_Quadrotor.pdf` / `PIWAN.pdf`
- `Automactic_Generation_of_aerobatic.pdf` / `Decentrailzed_aerial_manipulation.pdf`
- `Dynamic_perception_enhanced_motion.pdf` / `Hierarchical_graph-based_terrain-aware.pdf`
- `whole-body-control.pdf` / `无人机避障算法综述.pdf`
- Dai 多旋翼设计/仿真系列 4 篇（旁支偏强，低优先级）

### 08-世界模型-多模态

- `多模态智能处理单元.pdf`

### 04-空间数据流-中间件


| 文件 | 笔记 |
| ---- | ---- |
| `2015-ICRA-MapAPI-Cieslewski.pdf` ✅ | CAP-SPATIAL-MAPAPI-REF-001（Chunk/Trigger 设计参考，非产品底座） |
| `2024-RAL-LECES-PDF待补充.md` | PDF **closed**（DOI 10.1109/LRA.2024.3433200）；无 arXiv；待机构下载 → 建议名 `2024-RAL-LECES-Zhang.pdf` |


工程半篇（非 PDF）：`04-文献阅读/notes/04-空间数据流-中间件/2026-工程-Iceoryx-FlatBuffers-传输半篇.md`；CAP-COMM-TRANSPORT-STACK-001

### 05 / 09 / 99

- 05 工程半篇：`04-文献阅读/notes/05-通信-弱网-网络/2026-工程-Zenoh-弱网传输半篇.md`
- 09 / 99：（空）

### 90-行业报告-趋势

- 大模型趋势/案例集、算力深度、高瓴 Recommend
- NOKOV 动捕/人形论文合集 3 份

### 91-航空-旁支

- 跑道识别、FOD、着陆滑跑等历史资料 + `MUST...` / `Study on Deep Learning in Radar.pdf` / 桥梁数字孪生（默认低优先级）

### `10-收集箱/source/`（非 peer-review）

- `Odin1重定位地图获取手册.pdf` / `Odin重定位操作手册.pdf`
- `odin1 建图 & 重定位 建议调用流程 v0.1.0.pdf`

---

## 与学习计划 / SALM学习 的关系

- `SALM学习/Kx /` 内 PDF：**暂不搬迁**，以 `Kx资料汇总文档.md` 为索引
- 新读机器人论文优先进本目录 `01–09`，不要继续堆在根目录

