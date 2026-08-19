# BENCH-P0：Go2 单机 MotionSLAM 基线（T-004）

> 首组 **measured** 数据来自 Go2 `MotionSLAM_ws/docs/测试记录.md`（2026-07-23 前的 Nav2 主线记录）。  
> 真机栈在 Go2 远端，**非**本机 `motion_ws` commit。
>
> **基线边界**：本 Benchmark 当前记录的是纯 Nav2 主线；Go2 最新 `2abc6e4` 已加入 Nav2 全局 + SCAN-Planner 局部 hybrid，但该 hybrid 尚无对应 PASS 记录，不并入本表已验证结论。

---

## 1. 环境

| 字段 | 值 |
|------|-----|
| id | BENCH-P0-Go2-MotionSLAM |
| 平台 | Unitree Go2 EDU |
| 边端 | NVIDIA **Orin NX** Developer Kit，8 核，15 GiB RAM |
| 网络 | WiFi `192.168.110.61/22`（探测日 RTT 【待补充】） |
| SLAM 前端 | Super-LIO（子模块 `42a6137`，ROS2 分支） |
| Local Map | SHM 静态层 → Nav2 costmap（`ShmStaticLayer`）【事实】 |
| Planner | Nav2 2D（MPPI） |
| Avoid | Unitree Sport / 固件 + `estop_go2`（C++） |
| 运行方式 | Humble Docker `motionslam:humble`（host 网络 + CycloneDDS 域 0） |
| 远端 git | `gitlab-go2:zengxinyu/go2_slam.git`，分支 `dev` @ `2abc6e4`（相对 `origin/dev` ahead 1；工作树 dirty，2026-07-27 SSH） |
| 子模块 | Super-LIO `42a6137` · livox `13eb05e` · unitree_ros2 `668d1ec` |
| 实测日期 | 2026-07-13（F 系列）/ 2026-07-20～2026-07-23（Nav2 N 系列） |
| 探测记录 | `motion_ws/docs/go2-host-probe-2026-07-20.md`；`motion_ws/docs/双边事实-motion与Go2-2026-07-27.md` |

---

## 2. 首组指标（来自测试记录，非 evo bag）

| 指标 | 目标/参考 | 实测 | 备注 |
|------|-----------|------|------|
| LIO 姿态（F1 pitch 差） | < 3° | **0.44°** | 2026-07-13，ego 时代脚本 |
| 定位漂移 60s（F2） | < 0.05 m | **0.01 m** | 部分通过 |
| 定位漂移 3m 回测（F2） | < 0.15 m | **0.087 m** | 5m 待测 |
| Nav2 栈自检 N1 | `check_nav_stack.py` 全 PASS | **PASS** | 2026-07-23；odom ~200 Hz；costmap 498×640 |
| H5 到达 2m（N4） | 误差 < 0.3 m | **通过** | 误差 **0.253 m**；行走 1.75 m；7.3 s；2026-07-21 R5 |
| 停栈后静止（N5） | estop 后不再走 | **通过** | 行走中 estop 后 3 s 位移 **0.011 m**；2026-07-21 |
| H5 到达 3m（N6） | 误差 < 0.3 m | **通过** | 误差 **0.283 m**；行走 2.72 m；11.6 s；2026-07-23 |
| 任务成功率 SR（NAV-1 单点 2m） | — | **不形成统一 SR** | 当前有 N4 通过轮次，也保留历史失败轮次；需按预先定义的重复试验集重测 |
| 碰撞次数 | 0 | **0** | 该轮未报碰撞 |
| ATE / RPE | — | 【待补充】 | 需 bag + evo |
| 关键帧 / VoxelDiff 带宽 | — | 【待补充】 | SLAM-Token 未接入 |

---

## 3. 闭环状态（2026-07-20）

| 链路 | 状态 | 证据 |
|------|------|------|
| Mapping（Super-LIO + SHM 地图） | ✅ 自检通过 | N1 |
| Planner（Nav2 ComputePathToPose） | ✅ 干跑通过 | N3 |
| Avoid（estop / 固件） | ✅ | N5 行走中急停通过 |
| Arrival（H5 2m / 3m 真机） | ✅（纯 Nav2） | N4 误差 0.253 m；N6 误差 0.283 m |
| 静态障碍专项 | 【待补充】 | NAV-2 仍待复测 |
| WiFi 中断专项 | 【待补充】 | NAV-4 仍待复测 |

---

## 4. 失败状态统计（Nav2 主线，首扫）

| 状态 | 次数 | 证据 |
|------|------|------|
| `SUCCESS` | ≥2 | N4、N6 通过记录 |
| `TIMEOUT` / 提前结束 | ≥1 | 历史 N4 失败轮次；详见狗端测试记录 |
| `UNREACHABLE` | 0 | — |
| `LOST` | 0 | — |

---

## 5. 系统工程证据 Gate（首个样板）

> 依据 `00-指导AI/项目宪章-无人协同系统工程.md`、`02-架构设计/Go2端侧-可闭环易解释系统工程.md` 与 `02-架构设计/数据飞轮-实施清单与架构.md` §7.1。本表只登记已有证据和阻塞项，不把设计要求写成已通过。

| Gate | 当前结论 | 证据 / 阻塞 |
|---|---|---|
| 运动闭环：N4/N6 到达 | **纯 Nav2 已通过** | N4 2 m 误差 0.253 m；N6 3 m 误差 0.283 m；证据来自狗端 `docs/测试记录.md` |
| 安全闭环：N5 停栈 | **已通过** | 行走中 estop 后 3 s 位移 0.011 m；狗端 bag 名称已登记，尚未确认回传开发机 |
| 证据闭环：版本 + bag + 定位量化 | **部分通过** | `2abc6e4` 与子模块已确认；bag 在狗端；ATE/RPE 与开发机回传【待补充】 |
| 增量事件闭环 | **未开始** | Token 未接入；`ADD/UPDATE/EVICT/RESET` 事务语义尚属设计草案 |
| 弱网安全闭环 | **未开始** | 尚未注入延迟、断网或验证 L1/L2 独立降级 |

**核校清单（本轮）**：

- [x] 未将 Nav2 栈自检 PASS 表述为真机到达通过。
- [x] 未将 LRU `EVICT` 表述为现实空间 `REMOVE`。
- [x] 未将“零中间大对象拷贝”表述为端到端零拷贝。
- [ ] hybrid、bag/ATE、增量事务与弱网场景完成后，按同一 Gate 复核。

---

## 6. 复现与回链

**Go2 上（需容器 + mid360 在线）：**

```bash
ssh go2-robot
cd ~/MotionSLAM_ws
./docker/run_container.sh          # 容器名 motionslam
# 容器内
source install/setup.bash
python3 /ws/scripts/check_nav_stack.py
ros2 launch motionslam_bringup nav2_nav_viz.launch.py with_reloc:=true with_forwarder:=true
python3 /ws/scripts/verify_h5_arrival.py --distance 2
```

**本机拉快照（git + 测试记录）：**

```bash
cd /home/ubuntu/Downloads/motion_ws
./scripts/pull-go2-benchmark.sh
```

| 项 | 路径 |
|----|------|
| 测试记录（canonical） | Go2 `~/MotionSLAM_ws/docs/测试记录.md` |
| 流程 | Go2 `~/MotionSLAM_ws/docs/GO2_Nav2完整流程.md` |
| 快照日志 | `motion_ws/logs/go2-benchmark-*.txt` |
| bag | 狗端 `~/MotionSLAM_ws/bags/` 已有 N4/N5 等目录；回传开发机【待补充】 |

---

## 7. 结论（首组）

**【事实】** 纯 Nav2 单机 LIO、栈自检、真机 2 m / 3 m 到达和行走中急停均已有狗端通过记录。  
**【事实】** Go2 最新 `2abc6e4` 已加入 Nav2 全局 + SCAN-Planner 局部 hybrid，但测试记录尚无 hybrid PASS。  
**【待补充】** bag 回传、ATE/RPE、NAV-2/NAV-4 与 Token/带宽指标仍缺。SLAM-Token、双机和 WeakNet 不是本 Benchmark 已完成能力。

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| type | benchmark |
| stage | validation |
| status | in-progress |
| canonical | true |
| evidence_level | **measured**（部分指标；ATE/bag 仍缺） |
| stack | Go2 `MotionSLAM_ws`（非 motion_ws） |
| commit | `2abc6e4` + dirty working tree（dev，ahead 1）；该 commit 含 SCAN-Planner hybrid 实现方向 |
| updated | 2026-07-27 |
| next | 回传狗端 bag、填 ATE/RPE；补 NAV-2/NAV-4；单独验收 hybrid 后再更新其结论；接入增量事务后补事件/带宽列 |
