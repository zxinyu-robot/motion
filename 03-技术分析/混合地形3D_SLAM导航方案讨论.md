# 楼梯等混合地形场景下四足机器人 3D SLAM 导航方案讨论

> 本文档整理了关于「楼梯等混合地形场景下足式机器人 3D SLAM 导航方案」的讨论，包含原始提问与方案分析、相关工作梳理。

---

## 一、原始提问

### 提问 1：方案构想

> 楼梯等混合地形场景下的具足机器人 3D SLAM 导航方案，我思考的是里程计估计 t 时刻的相对高度位姿，一部分用于抑制机体 IMU 飘逸，一部分用于肢体姿态驱动，由姿态状态稳定地持续输出驱动伺服减速器和电机状态偏移量；然而这个方案就有点类似于一拖多，主要工作在于系统内部姿态的向量通信协议及相关编解码器设计。

### 提问 2

> 这方面相关的工作有哪些？

---

## 二、方案分析与建议

方向是对的：在楼梯、坡面、碎石这类混合地形里，**仅靠平面 2D 导航不够**，必须让机器人持续理解「机体相对地形的高度、姿态、接触状态和可落脚区域」。

但建议把方案从「一份里程计结果拖多个下游」改成 **状态估计中心化 + 下游语义解耦**。

**核心判断**：相对高度位姿不应该直接同时驱动 IMU 抑漂和肢体姿态伺服。它更适合作为状态估计器的一类观测量或约束，融合后输出统一可信的 `BaseState / TerrainState / ContactState`，再分别服务导航、控制、步态和安全模块。

### 2.1 推荐系统链路

```text
IMU + 关节编码器 + 足端接触 + LiDAR/Depth
        |
        v
多源状态估计器
Leg Odom + IMU Preintegration + Contact Constraint + LiDAR/Inertial SLAM
        |
        v
统一状态输出
BasePose3D / BaseVelocity / IMU Bias / Contact State / Covariance
        |
        +--> 3D SLAM / 局部高程地图 / 可通行性评估
        |
        +--> 步态调度 / 落脚点规划 / 机体高度规划
        |
        +--> WBC/MPC/PD 控制器
        |
        v
JointCommand / TorqueCommand / Safety Limit
```

「估计 t 时刻相对高度位姿，一部分用于抑制 IMU 飘逸，一部分用于肢体姿态驱动」，更合理的表达应该是：

> 相对高度、接触约束和视觉/激光匹配结果作为观测输入，用于修正状态估计器中的机体位姿、速度和 IMU bias；控制器只消费融合后的状态和地形模型，不直接消费原始里程计高度。

这样可以避免一个模块既像定位器，又像控制源，又像协议中心，后面系统会更稳。

### 2.2 关于「一拖多」的问题

「一拖多」是很真实的工程风险。典型问题有：

- 一个高度估计异常，会同时污染导航、姿态控制和腿部补偿。
- 下游模块对同一个字段有不同语义理解，例如 `z` 到底是世界系高度、相对地面高度，还是机体质心到支撑平面的距离。
- 多频率模块耦合：SLAM 10-30Hz，状态估计 200-500Hz，控制 400-1000Hz，不能用同一套消息节奏硬拖。
- 编解码器越复杂，越容易把「算法问题」伪装成「协议问题」。

所以协议应该是边界，不是核心。核心应该是 **状态语义定义 + 时间同步 + 协方差 + 坐标系契约**。

### 2.3 关键接口建议

建议至少拆 4 类消息，而不是一个大姿态向量包打天下：

```cpp
struct BaseState {
  TimeStamp stamp;
  Pose3d pose_world_base;
  Vector3d linear_velocity_world;
  Vector3d angular_velocity_base;
  Vector3d imu_accel_bias;
  Vector3d imu_gyro_bias;
  Matrix<double, 15, 15> covariance;
};

struct TerrainState {
  TimeStamp stamp;
  double body_height_to_support_plane;
  Vector3d terrain_normal_world;
  double slope;
  double roughness;
  double traversability_score;
};

struct ContactState {
  TimeStamp stamp;
  std::array<bool, 4> in_contact;
  std::array<double, 4> contact_confidence;
  std::array<Vector3d, 4> foot_position_world;
};

struct LocomotionCommand {
  TimeStamp stamp;
  Vector3d desired_base_velocity;
  double desired_yaw_rate;
  double desired_body_height;
  GaitType gait_type;
};
```

其中 `BaseState` 是估计器输出，`TerrainState` 是地形理解输出，`ContactState` 是腿部约束输出，`LocomotionCommand` 是导航/任务层给运动控制层的目标。**不要让 SLAM 直接输出电机偏移量。**

### 2.4 楼梯场景的重点

楼梯不是普通 3D SLAM 问题，而是 **SLAM + 高程建图 + 落脚规划 + 机体姿态控制** 的组合问题。

需要重点处理：

- **高度突变**：楼梯边缘会让局部平面假设失效。
- **足端接触不连续**：上台阶时某些腿提前接触或悬空。
- **IMU 短时冲击**：落脚冲击会污染加速度积分。
- **LiDAR/Depth 遮挡**：近距离台阶、腿部遮挡、低矮结构容易建图不完整。
- **控制延迟**：地形估计慢，控制环快，必须做预测和缓存。

对于楼梯，导航层不应该只输出 `vx/vy/wz`，还应该输出：

```text
desired_body_height
terrain_normal
foothold_region
step_height_estimate
risk_level
```

否则运动控制层只能「盲走」。

### 2.5 通信协议怎么设计

协议/编解码器工作确实重要，但建议按「实时等级」分层：

```text
实时控制链路：固定结构体 / lock-free ring buffer / shared memory
中频状态链路：ROS2 msg / DDS QoS / protobuf 可选
低频日志回放：protobuf / flatbuffers / rosbag2
```

控制环内不建议频繁做复杂序列化/反序列化。比如 1000Hz 关节控制，不要依赖动态分配、JSON、复杂 protobuf 解析。高频链路尽量固定内存、固定字段、固定大小。

协议字段一定要包含：

- `stamp`
- `frame_id`
- `sequence_id`
- `source`
- `valid`
- `covariance` 或 `confidence`
- `latency_ms`
- `fault_flags`

否则后面排查漂移、延迟、跳变会很痛苦。

### 2.6 方案的一句话定义

> 面向楼梯等混合地形，系统以 IMU、腿部运动学、足端接触和 3D 感知构建融合状态估计，输出带协方差的机体 6DoF 状态、相对支撑面高度和地形可通行语义；导航层基于高程地图生成速度与落脚约束，运动控制层基于融合状态和地形约束生成关节位置/速度/力矩命令，通信协议仅负责跨模块状态契约、时间同步和故障隔离。

这样比「一套里程计一拖多」更清晰，也更适合后续扩展到 MPC、WBC 或 RL residual。

---

## 三、相关工作梳理

这个想法落在 **腿式机器人状态估计 + 3D SLAM + 地形理解 + 运动控制接口协议** 的交叉区，不是单一方向。

### 3.1 腿式里程计与接触辅助状态估计

最接近「用相对高度/位姿抑制 IMU 漂移」的方向。

关键词：`legged odometry`、`contact-aided inertial navigation`、`legged robot state estimation`、`contact-aided invariant EKF`、`kinematic-inertial fusion`

代表性工作：

- **Bloesch et al., State Estimation for Legged Robots**
  ETH Zurich / ANYmal 系列经典工作，用 IMU、关节编码器、足端接触约束融合估计机体状态。
- **Contact-aided Invariant EKF**
  常用于四足/双足机器人，把足端接触点当作短时间静止约束，修正 IMU 积分漂移。
- **Pronto: A Multi-Sensor State Estimator for Legged Robots**
  MIT 相关工作，融合 IMU、腿部运动学、视觉/激光等传感器，面向动态腿式机器人状态估计。

核心思想：**腿不是只负责运动，也可以成为状态估计传感器**。

### 3.2 LiDAR / Visual-Inertial SLAM 与腿式平台融合

对应 3D SLAM、楼梯环境建图、全局定位。

关键词：`LiDAR-inertial odometry`、`visual-inertial odometry`、`legged robot SLAM`、`LiDAR SLAM for quadruped robots`、`multi-sensor fusion SLAM`

常见基础系统：

- **LOAM / LeGO-LOAM**：经典 LiDAR odometry 与 mapping。LeGO-LOAM 对地面分割更友好，但原始设计偏地面车辆。
- **LIO-SAM**：LiDAR + IMU + 因子图优化，工程常用，适合做 3D SLAM 基线。
- **FAST-LIO / FAST-LIO2**：高速 LiDAR-inertial odometry，实时性强。
- **VINS-Fusion / OpenVINS**：视觉惯性里程计方向，相机方案参考。

四足难点不在「能不能跑 SLAM」，而在 **机体抖动、足端冲击、视角快速变化、楼梯边缘稀疏结构、近距离遮挡**。

### 3.3 高程地图与可通行性评估

把环境转成控制可用的地形语义。

关键词：`elevation mapping`、`traversability analysis`、`terrain mapping for legged robots`、`foothold planning`、`grid map`

代表性工作：

- **Elevation Mapping for Locomotion and Navigation (GPU / Grid Map)**
  ETH Zurich 系列高程地图方案，把点云融合成局部高度图，估计坡度、粗糙度、法向、可通行代价。
- **ANYmal rough terrain navigation**
  ANYmal 在复杂地形、自主巡检、楼梯/碎石/工业场景的导航工作。
- **Grid Map library**
  ROS 生态常见的二维栅格多层地图表示，可存储 elevation、slope、roughness、traversability 等层。

### 3.4 楼梯与复杂地形运动控制

更靠近「肢体姿态驱动、伺服减速器、电机状态偏移量」。

关键词：`quadruped stair climbing`、`MPC legged locomotion`、`whole-body control`、`foothold adaptation`、`terrain-aware locomotion`、`blind locomotion vs perceptive locomotion`

代表方向：

- **MIT Cheetah / Mini Cheetah MPC**：凸 MPC + 低层关节控制，很多四足控制框架的基线。
- **ANYmal Perceptive Locomotion**：把地形感知输入到运动控制，根据高程地图调整落脚点和机体姿态。
- **Whole-Body Control (WBC)**：用全身动力学约束统一求解机体姿态、足端力、关节力矩。
- **RL-based perceptive locomotion**：用深度强化学习处理复杂地形，输入包括高度扫描、历史状态、目标速度、IMU、关节状态等。

「由姿态状态稳定持续输出驱动伺服减速器和电机状态偏移量」，在现有体系里更接近：

```text
State Estimation -> Locomotion Controller -> Joint Command
```

而不是：

```text
Odometry -> Motor Offset
```

电机偏移量应该由控制器根据状态误差、地形约束和动力学模型算出来。

### 3.5 系统通信与接口协议相关工作

「系统内部姿态向量通信协议及编解码器设计」更像机器人中间件和实时系统设计方向。

关键词：`ROS2 real-time communication`、`DDS QoS robotics`、`robot interface definition`、`shared memory transport`、`protobuf robotics`、`FlatBuffers real-time`、`LCM robotics`

相关技术：

- **ROS2 + DDS**：模块化系统，支持 QoS、时间戳、生命周期管理，高频控制环要小心延迟和抖动。
- **LCM**：MIT 系常用，轻量、低延迟、适合机器人消息通信。
- **Protobuf / FlatBuffers**：适合跨进程、日志、回放和跨语言接口。FlatBuffers 对零拷贝和实时性更友好。
- **Shared Memory / Lock-free Ring Buffer**：高频控制链路常用，适合 400-1000Hz 控制环。

重点不是「编码器多复杂」，而是协议是否清楚表达：

```text
时间戳、坐标系、状态来源、有效性、协方差、延迟、故障标志
```

---

## 四、推荐重点阅读方向（按方案优先级）

1. **Legged State Estimation**：先理解 IMU + 腿部运动学 + 接触约束如何融合。
2. **Contact-aided Invariant EKF**：和「抑制 IMU 漂移」最直接相关。
3. **Elevation Mapping / Traversability Mapping**：解决楼梯、坡面、碎石的地形表达问题。
4. **ANYmal perceptive locomotion**：看工业级四足如何把感知、地图、状态估计、控制连接起来。
5. **MPC / WBC for quadruped locomotion**：理解状态估计输出如何真正变成关节命令。

**一句话总结**：方向最接近 **「接触辅助状态估计 + 地形感知 SLAM + 感知驱动运动控制」**，协议设计是工程落地的重要部分，但算法主线应该围绕状态估计和控制接口解耦展开。
