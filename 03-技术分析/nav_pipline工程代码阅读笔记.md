# nav_pipline 工程代码阅读笔记

——大疆 WPML/KMZ 三维航线规划工程与 SLAM-Token 的对应关系

> 整理自代码阅读（2026-07-09）  
> 工程路径：`/home/ubuntu/nav_pipline`  
> 关联文档：`02-架构设计/大疆上云API参考-ActionGroup与Folder分层.md`、`02-架构设计/Go2-VLA-SLAM-Token技术方案.md`、`02-架构设计/Streaming-Spatial-Data-Pipeline-知识体系与阅读路线.md`

---

## 1. 项目定位

README 写明：基于 **Vue 3 + Cesium** 的三维无人机航线规划系统，配套 **Flask** 后端，支持 Docker 交付。

| 层级 | 技术栈 |
|------|--------|
| 前端 | Vue 3、Cesium、Ant Design Vue、Pinia、Vite、Gaussian Splat 可视化 |
| 后端 | Flask、SQLAlchemy、MySQL、MinIO 存储 |
| 算法 | path_editor（几何规划）、path_planner（DSM 碰撞/GA 优化）、voxelizer |
| 交付 | Docker 全量/分离打包、Python 代码加密编译（pyecli） |

### 1.1 已具备能力（README §1）

- 3D 航线规划前端（航点 CRUD、航线库、测量、键盘控机）
- 航线业务 API（列表/导入/导出/KMZ 下载/提交）
- 覆盖路径生成流水线（boustrophedon、oblique、spiral、viewpoint_optimized 等）
- 点云体素化、B3DM 模型处理
- KMZ 编辑 → 生成 → 导出闭环

### 1.2 待完善

- `workspace_id` 绑定与外部无人机系统适配
- KMZ 与对象存储（MinIO）同步链路
- 多机型真机场景调参验证

---

## 2. 整体架构

```
frontend/          Vue3 + Cesium 3D 地图、航线编辑、Gaussian 预览
backend/app/
  views/           Flask Blueprint API
  utils/
    kmz/           WPML/KML 同构树解析（dji_tree.py）
    path_editor/   五层航线流水线 + KMZ 导出 + 动作库
    path_planner/  DSM 碰撞、GA 优化、任务生成
  models/          Wayline、WaylineGroup、WaylineJob
wpmz/              根目录 WPML/KML 样例
docker/            Nginx + MySQL + 后端容器编排
work_dir/          waylines、autopath、坐标合同样例
test/              KMZ roundtrip、路径规划单测
```

### 2.1 后端 Blueprint 路由

| 路由前缀 | 模块 | 职责 |
|----------|------|------|
| `/api/v1/waylines` | `waylines.py` | 航线 CRUD、规划、KMZ 导出（核心，2400+ 行） |
| `/api/v1/wayline_groups` | `wayline_group.py` | 航线文件夹分组管理 |
| `/path/editor` | `path_editor.py` | 几何编辑 API |
| `/path/kmz` | `path_kmz.py` | KMZ 读写 |
| `/task/fly` | `path_planner.py` | 异步飞行规划任务 |
| `/api/v1/task/voxelize` | `voxelizer.py` | 点云体素化 |

---

## 3. 核心关注：Folder + ActionGroup 在代码里的实现

### 3.1 大疆标准三层（WPML）

工程完整实现了大疆 WPML 分层：

```
Document
├── wpml:missionConfig     ← MissionConfig 数据类
└── Folder                  ← 可执行航线（一条或多条）
    ├── Placemark (航点)
    └── wpml:actionGroup    ← 触发式动作序列
```

#### missionConfig

文件：`backend/app/utils/path_editor/params/mission_config.py`

```python
@dataclass
class MissionConfig:
    """任务配置：对应 wpml:missionConfig 子元素，兼容司空解析。"""
    fly_to_wayline_mode: str = "safely"       # safely | pointToPoint
    finish_action: str = "goHome"            # goHome | autoLand | hover | noAction
    exit_on_rc_lost: str = "goContinue"      # goContinue | executeLostAction
    execute_rc_lost_action: str = "goBack"   # goBack | hover | landing
    take_off_security_height: float = 120.0
    global_transitional_speed: float = 15.0
    global_rth_height: float = 100.0
    ...
```

#### actionGroup

文件：`backend/app/utils/path_editor/output/action_library.py`

`ActionTemplate` 数据类 + `build_wpml_action_group()` 方法，构建标准 WPML actionGroup：

- `actionGroupId` / `actionGroupStartIndex` / `actionGroupEndIndex`
- `actionGroupMode` = `sequence`（串行执行）
- `actionTrigger`（reachPoint / multipleTiming / multipleDistance 等）
- `action` 列表（takePhoto、gimbalRotate 等）

#### 前端导出

文件：`frontend/src/gaussianUtils/wayline/djiWayLine.js`

`formatToDJIWayline()` 将内部航线数据转换为大疆标准 WPML，生成 `missionConfig`、`folder`、`actionGroup` XML。

### 3.2 工程自研扩展：「动作库 Folder」

除大疆标准 Folder 外，项目增加了**编辑器内部的「动作库 Folder」**：

- KMZ 内放置名为 `动作库` / `ActionLibrary` / `动作模板库` 的 KML Folder
- 通过 `ExtendedData/Data[name=actionTemplate]` 存储 JSON 动作模板
- 规划导出时通过 `actionTemplateId` 选用模板
- **最终 KMZ 会删除动作库 Folder**（不发给飞手）

关键逻辑：`backend/app/utils/path_editor/output/kmz.py`

```python
def _is_action_library_folder(folder_elem):
    # 识别 name 为「动作库」「ActionLibrary」「动作模板库」的 Folder

def _remove_action_library_folders(parent):
    """最终 KMZ 不回写编辑器内部动作模板库 Folder。"""
```

内置模板示例：

| 模板 ID | 触发器 | 动作 |
|---------|--------|------|
| `photo_only` | reachPoint | takePhoto |
| `photo_45` | multipleTiming (2s) | takePhoto |

这与「可复用 ActionTemplate 库」思路一致，可平移为 SLAM-Token 的 Robot Action 模板库。

### 3.3 业务层 Folder：WaylineGroup

数据库模型 `WaylineGroup`（`t_wayline_group`）是**航线库文件夹**：

| 字段 | 含义 |
|------|------|
| `name` | 文件夹名称 |
| `type` | 0=custom, 1=default, 2=app shared |

对应大疆 `element-group` 的 CUSTOM / DEFAULT / SHARED 分层。代码中 `workspace_id` 已标注「不再使用」，与 README「待完善 workspace 绑定」一致。

---

## 4. 航线规划流水线（path_editor 五层）

文件：`backend/app/utils/path_editor/pipeline.py`

```
几何输入 → 规划参数 → 算法 → 后处理 → 输出(KMZ)
```

| 类型 | 算法 | 入口函数 |
|------|------|----------|
| 面状航线 | boustrophedon 扫掠 | `edit_route()` |
| 走廊/带状 | corridor | `edit_corridor_route()` |
| 圆柱/立体 | surface_sweep / spiral | `edit_cylinder_route()` |
| 斜面/倾斜 | oblique 多 Folder | 模板 `oblique_standard` |
| 贴近摄影 | close photography | `calculate_area` 合同 |

KMZ 导出核心：`export_waypoints_to_kmz()`（`output/kmz.py`），将航点序列 + `mission_config` + `action_template_id` + `action_library` 写成标准 KMZ。

---

## 5. WPML 解析基础设施（dji_tree）

文件：`backend/app/utils/kmz/dji_tree.py`

实现 **WPML/KML XML ↔ JSON 同构树**双向转换。金样 roundtrip 测试：`test/test_dji_tree_roundtrip.py`，验证与真实大疆 KMZ（斜面航线、面状航线）语义一致。

这是整个工程的**协议底座**，相当于一套可运行的「大疆 WPML 参考实现」。

---

## 6. 前端关键模块

| 模块 | 路径 | 作用 |
|------|------|------|
| 地图主视图 | `views/MapView.vue` | Cesium 初始化、航线可视化 |
| 航点编辑 | `components/drawing/WaypointEditModal.vue` | 经纬度/偏航/动作编辑 |
| 飞行器动作 | `components/drawing/AircraftActionForm.vue` | takePhoto 等 |
| 云台动作 | `components/drawing/GimbalActionForm.vue` | pitch/roll/yaw |
| 航线导出 | `utils/djiWaylineFormatter.js` + `gaussianUtils/wayline/djiWayLine.js` | → 大疆 WPML |
| 状态管理 | `stores/routeStore.js` | 航线/航点 Pinia |
| Gaussian 预览 | `components/gaussian/` | 3D Gaussian Splat |

---

## 7. 与 SLAM-Token / 大疆参考文档的对应关系

本工程几乎是《大疆上云API参考-ActionGroup与Folder分层.md》的**可运行版本**，差异在领域：

| 维度 | nav_pipline（本工程） | SLAM-Token |
|------|----------------------|------------|
| 坐标系 | WGS84 / ENU / 起飞点相对高 | odom / world / OctVox hash |
| Folder 内容 | 飞行航点 Placemark | coarse waypoint 序列 |
| ActionGroup 动作 | takePhoto、gimbalRotate、recordPointCloud | uploadKeyFrame、requestPeerView、waitForVLA |
| 动作库 | ActionTemplate 可复用模板 | Robot Action 模板库 |
| missionConfig | 返航/失控/安全高度 | 弱网降级/断网策略 |
| 传输 | HTTP API + KMZ 文件 | MQTT/Zenoh + FlatBuffers 流 |
| 地图层 | 无稠密体素 | OctVox diff 核心壁垒 |

### 7.1 可直接复用

| 本工程模块 | 平移到 SLAM-Token |
|-----------|-------------------|
| `MissionConfig` + `ActionTemplate` + `build_wpml_action_group()` | → `RobotMissionSpec` |
| 「动作库 Folder」模板机制 | → Robot Action 模板库 |
| `dji_tree.py` XML↔JSON 双向转换 | → 协议 schema 工具链 |
| `WaylineGroup` 分组模型 | → 多机任务/协同 workspace |
| path_editor 五层流水线思想 | → Streaming Spatial Data Pipeline |

### 7.2 需要替换

- 航点坐标：LLH → odom
- action 类型：负载级 → 认知级/协同级
- 增加 voxel diff payload 数据通道（KMZ 里没有）

---

## 8. 建议代码阅读顺序

### 第一优先（Folder + ActionGroup）

1. `backend/app/utils/path_editor/output/action_library.py` — ActionTemplate 全流程
2. `backend/app/utils/path_editor/params/mission_config.py` — missionConfig
3. `backend/app/utils/path_editor/output/kmz.py` — KMZ 导出如何挂 actionGroup
4. `frontend/src/gaussianUtils/wayline/djiWayLine.js` — 前端如何组 Folder/ActionGroup

### 第二优先（协议底座）

5. `backend/app/utils/kmz/dji_tree.py` — WPML 同构树
6. `test/test_dji_tree_roundtrip.py` — 金样验证

### 第三优先（规划能力）

7. `backend/app/utils/path_editor/pipeline.py` — 五层流水线
8. `backend/app/views/waylines.py` — 业务 API 总入口（可按 `actionTemplateId`、`calculate_area` 检索）

---

## 9. 一句话总结

`nav_pipline` 不是泛泛的导航 demo，而是**已经实现大疆 Folder + ActionGroup + missionConfig + 动作库模板**的完整航线规划产品。对 SLAM-Token 而言，最适合作为 **MissionSpec 的参考实现**：壳子和分层直接借，把航点换成 coarse waypoint、把 takePhoto 换成 uploadKeyFrame，再补上体素 diff 数据面即可。
