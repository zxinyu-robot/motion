# P0 Benchmark 模板（Go2 单机 SLAM-Token）

> 首组数据填好后，`evidence_level` 升为 `measured`，并回链 `motion_ws` commit。

## 环境


| 项              | 值                                        |
| -------------- | ---------------------------------------- |
| 平台             | 填具体本体与版本 |
| 边端             | 填型号、RAM 与功耗模式 |
| 网关             | 填 x86/其他硬件与资源 |
| 网络             | 填接口、拓扑、基线 RTT/带宽 |
| SLAM Producer   | 填实现、版本与配置 |
| Local Map / Planner | 填当前实际消费者与规划器 |
| Avoid / Arrival | 填安全链、到达阈值与判定工具 |
| 空间契约           | 填 VoxelTransaction / TokenSequence schema 版本与接入状态 |
| VLN Adapter / 模型 | 填 x86 Adapter 与实际模型版本 |
| stack commit   | 填与本次实验一致的 commit / dirty 状态 |
| 日期             | YYYY-MM-DD |

> **首组 measured 实例**：[`BENCH-P0-Go2-MotionSLAM-基线.md`](BENCH-P0-Go2-MotionSLAM-基线.md)


## 指标


| 指标                               | 目标/参考      | 实测  | 备注                                                    |
| -------------------------------- | ---------- | --- | ----------------------------------------------------- |
| 定位 ATE (m)                       | 【待补充】      |     | evo；首组未录 bag                                         |
| 定位 RPE (m)                       | 【待补充】      |     | evo；F2 3m 回测 0.087 m（非 evo）                          |
| 关键帧大小 (KB)                       | ~200KB 级   |     | 双触发后                                                  |
| 关键帧发送频率 (Hz)                     |            |     |                                                       |
| VoxelDiff/SpatialChunk 带宽 (KB/s) |            |     | 记录 payload 与协议开销                                      |
| 每成功任务传输量 (MB/success)            |            |     | 总传输量 / 成功任务数                                          |
| 边端 SLAM 延迟 (ms)                  |            |     | 工具、统计口径与论文参考分列 |
| Token 编码/解码成功率 (%)             |            |     | schema 校验 + payload 完整 |
| 版本连续率 / gap 率 (%)                |            |     | `session_id + commit_version` |
| Token 新鲜度 p50/p95 (ms)             |            |     | 生成至 x86 可消费 |
| 编码/解码延迟 p50/p95 (ms)             |            |     | 两端分列 |
| x86 VLN Adapter 有效输入率 (%)         |            |     | 解码后成功形成模型输入 |
| 端到端 waypoint 延迟 (ms)              |            |     | Token 生成至目标返回 |
| 任务成功率 SR (%)                     |            |     | 实测只填实例文件 |
| 严格成功率 SSR (%)                    |            |     | SR ∧ 语义正确停止（人工/规则标注 `sem_i`）；对齐 CAP-EVAL-VLN-REAL-001 |
| Oracle 成功率 OSR (%)               |            |     | 轨迹曾进入成功半径即可；与 SR 落差诊断「不会停」；不测则【待补充】                   |
| 路径长度加权成功率 SPL                    |            |     | 与对应 VLN 场景一致                                          |
| Arrival 成功率 (%)                  |            |     | 位置/朝向/规划稳定；**语义确认与 SSR 对齐**（有语言目标时必填语义项）              |
| 任务完成时间 (s)                       |            |     | 成功任务统计                                                |
| 危险/无效 waypoint 比例 (%)            |            |     | 不可达或触发安全拒绝                                            |
| 碰撞次数                             | 0          |     | 与固件避障触发分开统计                                           |
| 碰撞率 CR (%)                       | 0          |     | episode 级：发生碰撞计 1；评测中碰撞即终止（参考 arXiv:2607.09792）       |
| 弱网丢包率下成功率 (%)                    |            |     | 模拟丢包                                                  |
| 断网恢复时间 (s)                       |            |     |                                                       |
| 边端 CPU (%)                       |            |     |                                                       |
| 边端 GPU 显存 (MB)                   |            |     |                                                       |
| 固件避障触发次数                         |            |     | L1 兜底                                                 |
| Graph 查询命中率 (%)                  |            |     | P0 可选；命中节点含所需空间块                                      |
| 三维重建完整度/误差                       |            |     | P0 可选；注明 Occupancy/TSDF/Mesh 与工具                      |


## 测试场景

- [ ] 室内办公同层
- [ ] WiFi 弱网（限速/丢包）
- [ ] 断网 30s 恢复

## 闭环与失败状态

- [ ] Mapping：输出 Pose + KeyFrame + SpatialChunk/VoxelDiff
- [ ] Planner：coarse waypoint 可转换为本地轨迹
- [ ] Avoid：弱网/断网时 L1/L2 独立工作
- [ ] Arrival：按位置、可选朝向、规划器状态判定；有语言目标时语义确认与 SSR 对齐


| 状态            | 次数  | 证据/日志 |
| ------------- | --- | ----- |
| `SUCCESS`     |     |       |
| `UNREACHABLE` |     |       |
| `LOST`        |     |       |
| `NOT_FOUND`   |     |       |
| `TIMEOUT`     |     |       |


## 附件与回链


| 项    | 路径    |
| ---- | ----- |
| bag  | 【待补充】 |
| 报告   | 【待补充】 |
| 复现命令 | 【待补充】 |


---

## 文档元数据


| 字段             | 值                                                  |
| -------------- | -------------------------------------------------- |
| id             | BENCH-P0-001                                       |
| type           | benchmark                                          |
| stage          | validation                                         |
| status         | done                                              |
| canonical      | true                                               |
| evidence_level | proposal（模板；实测见 BENCH-P0-Go2-MotionSLAM-基线） |
| stack          | motion_ws / Go2 MotionSLAM_ws（按实例填写）         |
| commit         | 【实例必填】                                        |
| updated        | 2026-07-22                                         |
| next           | 实例化 P0-A～P0-C 报告；模板本身不保存实测值            |


