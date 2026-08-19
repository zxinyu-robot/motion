# BENCH-P0：Swarm-SLAM GrAco bag Gate（M1）

> T-008 / CAP-SLAM-SWARM-SLAM-GATE-001  
> 执行范围：**选项 A（仅 M1 bag）** — 见 `motion_ws/docs/仿真Gate范围选型.md`

---

## 1. 环境

| 字段 | 值 |
|------|-----|
| stack | motion_ws |
| commit | 【待补充】 |
| 平台 | x86 主机（Ubuntu 24.04） |
| ROS 2 | Humble（Docker `swarmslam-gate`） |
| 数据集 | GrAco Ground：Graco-0/1/2 ← ground-01/02/03 ROS2 |
| launch | `ros2 launch cslam_experiments graco_lidar.launch.py rate:=0.5 enable_simulated_rendezvous:=false` |
| 实测日期 | 【待补充】 |

---

## 2. Gate 验收项（布尔）

| 项 | 目标 | 实测 | 备注 |
|----|------|------|------|
| 三机 bag 就绪 | `check-data.sh` → DATA_READY | ❌ **0/3**（2026-07-20 自动下载失败） | 见 `motion_ws/docs/T-008-GrAco-下载清单.md` |
| 容器编译通过 | `docker build` 成功 | ✅ `swarmslam-gate:latest`（10.5GB，2026-07-17；跳过 TEASER Python 绑定） | `motion_ws/logs/docker-build-13-humble.log` |
| Docker 冒烟 | `cslam_experiments` + launch 可解析 | ✅ 2026-07-20 | `motion_ws/logs/gate-docker-smoke-*.log` |
| 三机节点启动 | r0/r1/r2 cslam 无 fatal | 【待补充】 | 日志 `motion_ws/logs/` |
| 跨机回环 | inter-robot loop closure 出现 | 【待补充】 | |
| 优化位姿输出 | `/r*/cslam/optimized_estimates` 有消息 | 【待补充】 | `check-gate-output.sh` |
| 参考系收敛 | 三机轨迹同全局系【推断】 | 【待补充】 | 可选 evo + GT |
| 纳入结论 | 纳入 / 有条件纳入 / 不纳入真机 P0 | 【待补充】 | |

---

## 3. 指标（实测列仅填真实值）

| 指标 | 目标/参考（论文 Table III） | 实测 | 工具 |
|------|---------------------------|------|------|
| 回放速率 | 0.5（算力不足再降） | 【待补充】 | launch `rate` |
| 总通信量 | ~95 MB / 3 机 / 475 m | 【待补充】 | 【待补充】 |
| 机间回环数 | 67（真机参考） | 【待补充】 | 日志 |
| 优化耗时 | 5.52±7.11 s（真机参考） | 【待补充】 | 日志 |
| ATE vs GPS | GrAco Ground ~6.19 m（论文 Table II） | 【待补充】 | evo【待补充】 |

---

## 4. 复现命令

**宿主机 ROS 2（Jazzy/Humble）：**

```bash
cd /home/ubuntu/Downloads/motion_ws
source /opt/ros/jazzy/setup.bash   # 或 humble
./scripts/bootstrap-swarm-slam-host.sh
./scripts/check-data.sh
GATE_MODE=host ./scripts/run-graco-gate.sh
./scripts/check-gate-output.sh
```

**Docker（无需宿主机 ROS）：**

```bash
cd /home/ubuntu/Downloads/motion_ws
./scripts/check-data.sh
GATE_MODE=docker ./scripts/run-graco-gate.sh
GATE_MODE=docker ./scripts/check-gate-output.sh
```

详见 `motion_ws/docs/宿主机ROS2-Gate路径.md`。

---

## 5. 纳入结论（模板）

**【待补充】** 填写日期与结论：

- 结论：`纳入` / `有条件纳入` / `不纳入`
- 理由：
- 与产品拓扑差异（P2P rendezvous vs 网关金字塔）：
- 下一步：M2 Gazebo / 真机 Go2 / FAST-LIO 替换 RTAB-Map 里程计

---

## 文档元数据

| 字段 | 值 |
|------|-----|
| id | BENCH-P0-SwarmSLAM-GrAco-Gate |
| type | benchmark |
| stage | validation |
| status | in-progress |
| canonical | true |
| evidence_level | proposal（Docker 冒烟 ✅；Gate 实测待 bag） |
| stack | motion_ws |
| commit | 【待补充】 |
| updated | 2026-07-20 |
| next | 手动下载 GrAco 三机 ROS2 bag → `run-graco-gate.sh` → 填实测列 |
