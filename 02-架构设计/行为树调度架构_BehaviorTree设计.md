# 多机器人协同调度 —— 行为树（BehaviorTree.CPP + Groot2）架构设计

> 本文档承接 `01-工作计划/多机器人协同_详细技术与科研规划.md`（下称《主规划》）§5.1 边端金字塔与「多机协同调度（自研 + 群体智能）」一节，把**调度层的实现机制**具体化。
> 严格遵循 `00-指导AI/prompt.md` 的四条铁律：凡事实附来源，凡推断/待补充显式标注，**不编造** SDK 函数名、版本号与调用链。
> 定位：本文件是**设计文档（design doc）**，不是对已有代码的扫描报告——因为**【事实】截至编写时，仓库内不存在任何行为树 / 调度相关源码**（全库扫描仅 13 个文件，均为文档与环境脚本）。
> 更新：2026-07-14（对齐 Graph 检索式 VLN 与 Folder / ActionGroup / Trigger）

---

## 0. 一句话结论

**调度层统一采用行为树（BehaviorTree.CPP v4 + Groot2）作为唯一的任务协调机制；不再单独维护一套顶层有限状态机（FSM）。状态机仅在「把各平台机器人 SDK 封装成行为树叶子节点」时，作为该叶子节点的内部实现细节存在（SDK-as-Leaf）。**

---

## 1. 选型决策与理由

### 1.1 决策

| 项 | 选型 | 标注 |
|---|---|---|
| 行为树框架 | **BehaviorTree.CPP v4**（`BTCPP_format="4"`） | 【推断/待锁定】版本需在引入时以实际编译通过的 tag 锁定 |
| 可视化 / 调试 | **Groot2**（配套 GUI，实时监视 + 编辑 XML） | 【推断/待锁定】 |
| 顶层 FSM | **不引入**独立顶层状态机 | 【决策】本次需求明确 |
| SDK 接入方式 | **SDK 作为行为树叶子节点**（Action/Condition），其内部可含小型 FSM | 【决策】本次需求明确 |
| 运行时 | ROS 2 Jazzy | 【事实】《主规划》§3.4 已确认开发环境为 Ubuntu 24.04 + ROS 2 Jazzy |

### 1.2 为什么是行为树而不是顶层 FSM

对应《主规划》以及前序讨论中确认的**范式定位**（从「调度已知世界」转向「协同探索未知世界」）：

1. **搜索型任务需要可组合的重规划**：第 27 行「A 指导 B 找杯子」场景里，目标位姿未知、需多轮「观测–规划–行动」。FSM 的状态爆炸（每加一种失败恢复就要连边）在这种场景难以维护；行为树用 `Fallback + Retry + Decorator` 天然表达「失败就换策略」。
2. **子树可复用**：`SearchObject`、`NavigateTo`、`DeliverTo` 可作为子树在不同任务间复用，契合「任务组」概念。
3. **生态对齐**：Nav2（ROS 2 官方导航栈）本身即用 BehaviorTree.CPP 做任务编排。【推断】这降低了与导航栈集成的阻抗，但**是否直接复用 Nav2 的 BT 节点库需在集成时验证**【待补充】。
4. **可视化可运维**：Groot2 可实时看到每个节点 RUNNING/SUCCESS/FAILURE，便于弱网/边缘现场排障。

### 1.3 为什么「SDK 作为子节点，而不是 SDK 之上再套 FSM」

- 各本体 SDK（Go2 底层 API、宇树 SDK、Booster SDK 等）本身已提供底层动作原语，其内部往往**已有状态时序**（如 站立→行走→到位）。
- 若在 BT 之外再维护一套 FSM 去驱动 SDK，会出现**两套控制真相**（BT 与 FSM 争夺谁是任务主控），难以调试。
- 因此约定：**SDK 的底层状态时序被封装进单个 BT 叶子节点内部**，对上层只暴露三态（RUNNING / SUCCESS / FAILURE）。上层永远只有行为树一个「大脑」。

---

## 2. 与边端金字塔的映射（分层行为树）

《主规划》§5.1 已确立**边端分层金字塔**（本体前端 → 边缘网关 → 可选云）。行为树按此分两层部署：

```
网关端（后端 · 调度大脑）                         本体端（前端 · 在线执行）
─────────────────────────────                    ──────────────────────────────
【组级行为树 Group-BT】                            【个体级行为树 Agent-BT】
· 编组 / 分工 / 协同仲裁                            · 局部导航闭环
· 任务分解: FetchCup → 谁搜/谁待命                  · 感知-移动-检测循环
· Graph Node 索引 / 子图检索 / 语义 grounding           · SDK 叶子节点（运控/抓取）
· 组级黑板 (group blackboard)                      · 个体黑板 (agent blackboard)
        │                                                   ▲
        └────────── DDS 话题 / 服务（子目标下发·状态回传）──────┘
```

- **组级 BT** 跑在网关：只做「谁去做什么」的粗粒度协同，不直接调 SDK。
- **个体级 BT** 跑在每台机器人：把子目标翻译成 SDK 调用，SDK 即叶子节点。
- 两层通过 DDS 通信（《主规划》§5.2，今年用 Fast DDS + WiFi，非 TSN）。

【推断】两层是否都用 BehaviorTree.CPP，还是组级用轻量自研协调器 + 个体级用 BT，需在 M2/M3 阶段按算力与实时性验证【待补充】。

---

## 3. 「group」的三层定义

前序讨论区分了 group 的三种含义，此处给出各自在本架构中的落地定义。

### 3.1 group-A：编队 / 机器人组（协同单元）

**行为树不原生提供，由网关调度层定义。** 一个协同组 = 一棵组级 BT 实例 + 一份组级黑板。

建议的组描述（配置态，YAML 草案，字段命名遵循 `prompt.md` §2.2「小驼峰」约定）：

```yaml
# 【草案 · 待补充】group 静态定义示例，字段名待评审
groupId: "office-floor1"
members:
  - robotId: "go2_a"
    line: "A"          # 传感器线，见主规划§3.2（A=激光/FAST-LIO2）
    role: "searcher"
  - robotId: "go2_b"
    line: "A"
    role: "standby"
sharedResources:
  mapHandle: "gw://fused_map/office-floor1"   # 网关融合地图句柄
  bandwidthBudgetMbps: 0                       # 【待补充】弱网带宽预算
formation: "none"      # MVP 同层办公不做严格编队
```

- **静态编组**：YAML 预定义（MVP 推荐，简单可控）。
- **动态编组**：网关运行时按任务把空闲机器人编入组（后期能力，对应群体智能，《主规划》§8.1）。【待补充】动态编组策略未定。

### 3.2 group-B：任务组（可复用子树 SubTree）

一段可复用行为逻辑打包成一棵子树，用 `<SubTree ID="...">` 引用。这是 BT 层面最主要的「组」。示例见 §6。

### 3.3 group-C：控制节点分组（框架语义）

BehaviorTree.CPP 的组合节点：`Sequence` / `Fallback`(Selector) / `Parallel` / `ReactiveSequence` 等，把子节点「成组」执行。属于框架已有语义，不需自定义。

---

## 4. 节点库设计（自定义节点清单）

> 命名遵循 `prompt.md` §2.2；每个节点须有 Google Style 注释说明参数/返回/功能/示例（§2.2）。
> **【重要】下表中的 SDK 具体函数名一律标【待补充】**——真实 API 须在引入对应 SDK、看到头文件后填写，不得编造（铁律一）。

### 4.1 SDK 叶子节点（Action，含内部 FSM）

| 节点 | 类型 | 输入端口 | 输出端口 | 底层 SDK | 内部是否含 FSM |
|---|---|---|---|---|---|
| `NavigateTo` | StatefulAction | `goal`(Pose) | `result` | 本体导航 / Nav2 桥【待补充】 | 是（趋近→到位→超时） |
| `Pick` | StatefulAction | `object`(Pose/id) | `grasped` | 本体机械/抓取 SDK【待补充】 | 是（对准→合爪→确认） |
| `StandUp` / `Locomote` | StatefulAction | `mode` | — | 宇树/各厂运控 SDK【待补充】 | 是（SDK 内部时序） |
| `HandOver` | StatefulAction | `targetRobotId` | `done` | 交接逻辑【待补充】 | 是 |

**内部 FSM 封装规范（SDK-as-Leaf）：**

```cpp
// 【示意 · 非真实API】StatefulActionNode 内部用小型状态机驱动 SDK，
// 对外只暴露三态。真实 SDK 调用处标 TODO 待补充。
class NavigateTo : public BT::StatefulActionNode {
  enum class Phase { kInit, kMoving, kArrived, kFailed };  // SDK 内部状态机
  Phase phase_ = Phase::kInit;

  BT::NodeStatus onStart() override {
    // TODO(SDK): 调用本体导航 SDK 下发目标（真实函数名待补充）
    phase_ = Phase::kMoving;
    return BT::NodeStatus::RUNNING;
  }
  BT::NodeStatus onRunning() override {
    // TODO(SDK): 轮询 SDK 反馈，推进内部状态机
    // if reached -> return SUCCESS; if error -> return FAILURE;
    return BT::NodeStatus::RUNNING;
  }
  void onHalted() override {
    // TODO(SDK): 取消 SDK 当前动作，保证可被上层 BT 抢占
  }
};
```

### 4.2 感知 / 条件节点（Condition）

| 节点 | 类型 | 说明 |
|---|---|---|
| `IsLocalized` | Condition | SLAM 前端是否已收敛（对接 FAST-LIO2 状态）【待补充】接口 |
| `DetectObject` | Condition/Action | 目标（如 cup）是否被检出；可消费边侧语义标签或 VLN grounding 结果 |
| `IsBatteryOK` | Condition | 电量护栏 |

### 4.3 装饰器 / 协同节点

| 节点 | 类型 | 说明 |
|---|---|---|
| `RetryUntilSuccessful` | Decorator（框架自带） | 搜索失败重试 |
| `Timeout` | Decorator（框架自带） | 单步超时护栏 |
| `RequestPeerView` | Action（自定义） | 组级：请求把 B 视角/关键帧共享给 A（对接 DDS 关键帧话题） |
| `AssignRole` | Action（自定义） | 组级：给成员分配 searcher/standby 角色 |
| `UpdateGraphNode` | Action（自定义） | 绑定/更新 pose、KeyFrame、RGB、SpatialChunk 与语义引用 |
| `QueryGraph` | Action（自定义） | 按 text、当前位置、Folder scope 和 map version 检索相关子图 |
| `WaitForVLN` | StatefulAction（自定义） | 等待网关 grounding；超时按弱网策略返回 FAILURE 或降级 |

---

## 5. 黑板（Blackboard）与数据流

- **个体黑板**：机器人本地状态（位姿、目标、检测结果）。
- **组级黑板**：组成员表、融合地图句柄、Graph 查询结果引用、任务进度、共享语义。
- 跨机数据**不走黑板直接共享**，而是经 DDS 话题/服务同步后写入各自黑板（避免把 DDS 通信藏进黑板造成隐式耦合）。

```
B视角(关键帧/位姿) ──DDS──▶ 网关融合 ──▶ 组级黑板{sharedMap, bViewSummary}
                                          │
                        组级BT读取 → 生成子目标 ──DDS──▶ 个体黑板{goal}
                                                              │
                                                      个体BT: NavigateTo(goal) → SDK
```

---

## 6. 端到端示例：同层 MVP 版「找杯子」

> 对应第 27 行愿景，但**去掉跨楼层**（跨楼层是《主规划》§8 研究攻关点，不进 MVP）。此处为**同层办公场景**：网关组级 BT 协调，B 执行搜索，A 作为协作者可注入 hint。

### 6.1 组级 BT（网关，Group-BT）

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="FetchCupMission_Group">
    <Sequence>
      <AssignRole group="{groupId}" searcher="go2_b" standby="go2_a"/>
      <RequestPeerView from="go2_b" to="go2_a"/>        <!-- B视角共享给A -->
      <SubTree ID="SearchObject_Group" target="cup" agent="go2_b"/>
      <DispatchGoal agent="go2_b" task="DeliverTo" arg="{handoverPose}"/>
    </Sequence>
  </BehaviorTree>
</root>
```

### 6.2 个体级 BT（本体 go2_b，Agent-BT）

```xml
<root BTCPP_format="4">
  <BehaviorTree ID="SearchObject_Agent">
    <Sequence>
      <IsLocalized/>
      <RetryUntilSuccessful num_attempts="10">
        <Fallback>
          <DetectObject object="cup" output="{cupPose}"/>   <!-- 找到即成功 -->
          <Sequence>
            <ExploreNext output="{nextViewpoint}"/>          <!-- 乱房间里换搜索点 -->
            <NavigateTo goal="{nextViewpoint}"/>             <!-- 叶子：内部FSM驱动SDK -->
          </Sequence>
        </Fallback>
      </RetryUntilSuccessful>
      <Pick object="{cupPose}"/>                             <!-- 叶子：内部FSM驱动SDK -->
    </Sequence>
  </BehaviorTree>
</root>
```

要点：`NavigateTo` / `Pick` 是 SDK 叶子节点，其内部小 FSM 对上层不可见；上层只看三态并据此重试/换策略。

---

## 7. Groot2 使用约定

- **XML 单一真相源**：行为树结构以 `.xml` 存于版本库（见 §9 目录），Groot2 读/写同一 XML；禁止在 Groot2 里改完不回写仓库。
- **实时监视**：运行期通过 BehaviorTree.CPP 的日志/发布接口连接 Groot2 观察节点状态。【推断】具体端口/连接方式需按所锁定的 BТ.CPP 版本文档确认【待补充】。
- **节点模型（palette）**：自定义节点需导出节点模型供 Groot2 识别。【待补充】导出流程按版本文档执行。

---

## 8. 依赖与版本（须在引入时锁定，禁止编造）

| 依赖 | 用途 | 版本 | 标注 |
|---|---|---|---|
| BehaviorTree.CPP | 行为树运行时 | v4.x（`BTCPP_format="4"`），**具体 tag 待锁定** | 【待补充】 |
| Groot2 | 可视化/调试 | 待锁定 | 【待补充】 |
| ROS 2 | 运行时 | Jazzy | 【事实】主规划§3.4 |
| 各本体 SDK | 叶子节点底层 | — | 【待补充】Go2「底层 API + ROS 兼容」、Booster「Booster SDK」等来自主规划§3.1，但**具体函数签名待看到 SDK 后填写** |

> 【事实来源】平台/SDK 描述引自《主规划》§3.1 平台总表；ROS 2 Jazzy 引自《主规划》§3.4。
> 版本号一律**待编译验证后回填**，符合铁律一「不能编」。

---

## 9. 建议工程目录（草案）

> 遵循 `prompt.md` §2.2「目录结构参照 C++/Python 标准模板」——此处为**建议**，真实结构以代码入库为准【待补充】。

```
scheduler_bt/                 # 【草案】行为树调度模块（ROS 2 package）
├─ include/scheduler_bt/
│  └─ nodes/                  # 自定义节点头文件（Google Style 注释）
├─ src/
│  ├─ nodes/                  # NavigateTo/Pick/DetectObject/... 实现
│  ├─ group_bt_node.cpp       # 组级BT（网关）执行器
│  └─ agent_bt_node.cpp       # 个体BT（本体）执行器
├─ trees/                     # ★ 行为树 XML（Groot2 单一真相源）
│  ├─ group/FetchCupMission_Group.xml
│  └─ agent/SearchObject_Agent.xml
├─ config/
│  └─ groups/office-floor1.yaml   # group-A 静态编组定义
└─ CMakeLists.txt
```

---

## 10. 与《主规划》WBS 的对齐

| 主规划里程碑 | 本调度层对应交付 |
|---|---|
| M2 仿真验证 B（Gazebo 双 Go2 + Swarm-SLAM） | 个体 BT：`IsLocalized` + `NavigateTo` 叶子跑通（SDK/Nav2 桥） |
| M3 真机迁移（双 Go2 + x86 网关 + WiFi） | 组级 BT 上网关，DDS 下发子目标 / 回传状态 |
| M5 上层智能（Graph 检索式 VLN） | `QueryGraph` 检索任务相关节点，`DetectObject` 消费语义结果，`ExploreNext` 由 Folder / coarse waypoint 引导；压缩按实测瓶颈后置 |
| M6 异构攻关（跨楼层） | group-A 扩展跨楼层拓扑（研究攻关，非本文档范围） |

---

## 11. 待确认事项（TODO）

- [ ] 锁定 BehaviorTree.CPP 具体版本 tag 与 Groot2 版本，回填 §8。
- [ ] 确认是否直接复用 Nav2 的 BT 节点库，还是自建 `NavigateTo`（§1.2）。
- [ ] 组级是否也用 BehaviorTree.CPP，还是自研轻量协调器（§2）。
- [ ] 各本体 SDK 头文件到手后，回填 §4 叶子节点的真实函数签名（铁律一）。
- [ ] `DetectObject` 在 M5 前的临时实现（几何/颜色检测 or 数据集标注）。
- [ ] 动态编组（group-A）策略是否纳入，与《主规划》§8.1 群体智能对齐。
- [ ] group / 节点端口字段命名评审（§3.1 草案 → 定稿）。
