# P1 WeakNet Collaborative Bench 指标提纲

> **定位**：OctVox→TokenSequence→x86 VLN 无损闭环通过后的弱网增量尺子（T-010）。先定指标与场景，**禁止**在无实测时填写「实测」列。  
> **叙事对照**：arXiv:2607.09792 证明「无几何 → CR 高」；本 Bench 额外证明「有几何但通信差 → SR/SSR 掉、恢复慢」——motion L4 差异化。  
> **能力卡**：`05-知识沉淀/eval/CAP-EVAL-VLN-REAL-001.md`

## 1. 评测目标

在可控通信损伤下，对比：

- 不同中间件 / 压缩 / 调度策略
- 单机 vs 双机（P1 扩展）
- Map / 任务成功 / 安全 / 恢复时间

老板口径（见 `职业路线规划/学术生态位与三年行动计划.md` §5.2）：

```text
Packet Loss → Latency → Bandwidth → DDS QoS
  → Map Accuracy / SR / SSR / CR / 断连恢复
```

## 2. 四轴指标

### 轴 A — 通信（注入与观测）


| 指标            | 目标/参考              | 实测  | 备注           |
| ------------- | ------------------ | --- | ------------ |
| 丢包率 (%)       | 扫 0 / 5 / 10 / 20… |     | tc / 专用注入    |
| RTT (ms)      | 扫基线与 +50/+100/+200 |     |              |
| RTT jitter (ms) | 扫基线与扫参档位         |     | 对齐 AsyncShield「网络抖动」矛盾；见 CAP-EXEC-ASYNC-SHIELD-ALIGN-001 |
| 推理/指令延迟 (ms) | 扫 0 / 200 / 500 / 1000… |  | 模拟云端 VLA 推理时滞；与 RTT 可叠加 |
| 可用带宽 (Mbps)   | 限速档位               |     |              |
| 断连时长 (s)      | 如 30s              |     | 与 P0 场景对齐    |
| 断网恢复时间 (s)    |                    |     | 地图/任务恢复到可用   |
| DDS/传输 QoS 配置 |                    |     | 记录 profile 名 |


### 轴 B — 任务与安全（对齐真机 VLN 口径）

SR / SSR / OSR / SPL / CR 的基础定义与成功阈值继承 `40-验证/P0-Benchmark-模板.md` 和 `CAP-EVAL-VLN-REAL-001`，本表只记录弱网相对无损基线的变化，避免复制两套定义。

| 指标                    | 目标/参考 | 实测  | 备注          |
| --------------------- | ----- | --- | ----------- |
| SR / SSR 相对基线变化 (pp) |       |     | 同任务、同成功定义 |
| CR 相对基线变化 (pp)       | 趋近 0  |     | 同 episode 终止规则 |
| 危险/无效 waypoint 比例 (%) |       |     |             |
| 意图恢复误差 (m / °)        |       |     | 可选；时滞对齐前后子目标相对当前 ego 的偏移（AsyncShield 对标） |
| 固件避障触发次数              |       |     | 与 CR 分列     |


指令分型建议（可复用综述比例，按规模缩放）：**70%** 逐步 / **20%** 意图模糊 / **10%** 回溯。

### 轴 C — Token 编解码与时效

| 指标 | 目标/参考 | 实测 | 备注 |
|---|---|---|---|
| 事务编码成功率 (%) | | | 输入为可回放 `VoxelTransaction` |
| Token 解码成功率 (%) | | | schema 校验通过且载荷完整 |
| 版本连续率 / gap 率 (%) | | | 按 `session_id + commit_version` |
| Token 新鲜度 p50/p95 (ms) | | | 生成时间到 x86 可消费时间 |
| 过期 Token 比例 (%) | | | 超过 TTL 或关联版本失效 |
| 编码 / 解码延迟 p50/p95 (ms) | | | 两端分别记录 |
| TokenSequence 大小 (KB/transaction) | | | payload 与协议开销分列 |
| x86 VLN Adapter 有效输入率 (%) | | | 解码后能形成模型输入的比例 |
| 断连恢复后版本追平时间 (s) | | | 恢复至可消费连续版本 |

### 轴 D — 中间件、地图与资源

| 指标                               | 目标/参考      | 实测  | 备注     |
| -------------------------------- | ---------- | --- | ------ |
| VoxelDiff/SpatialChunk 带宽 (KB/s) |            |     | 含协议开销 |
| 每成功任务传输量 (MB/success)            |            |     |        |
| 定位 ATE/RPE                       |            |     | 弱网前后对比 |
| Go2 Encoder CPU / 内存              |            |     | 与未接 Token 基线对比 |
| x86 Decoder / Adapter CPU / 内存     |            |     | 分模块记录 |


## 3. 场景矩阵（勾选）

- [ ] 室内同层 + WiFi 基线
- [ ] **无损 Token→VLN→执行闭环**（P0-C 前置 Gate）
- [ ] 限速 / 丢包扫描
- [ ] **延迟 / jitter 扫描**（云端 VLA 异步；对齐 AsyncShield）
- [ ] 断网 30s 恢复
- [ ] （P1）双机：一台探索、一台执行语言目标
- [ ] （可选）户外/动态行人 — 标注传感器盲区

## 4. 与综述 / P0 的关系


| 来源                 | 贡献                     | 本提纲用法       |
| ------------------ | ---------------------- | ----------- |
| EmbodiedVLN Survey | SSR、CR、语义停、sim-to-real | 轴 B 定义      |
| P0-Benchmark 模板    | 单机任务/安全定义与无损基线       | 轴 B 只记相对变化 |
| Token P0-A～P0-C | 事务、编解码、x86 VLN 闭环 | 轴 C/D 前置输入 |
| motion L4 主张       | 通信感知协同                 | 轴 A 为主变量    |


## 5. 首期最低验收（提纲阶段）

- [x] 四轴指标表落盘（含 Token 编解码与时效）
- [ ] P0-C 无损 Token→VLN→执行闭环通过
- [ ] 选定注入工具与复现命令（写入 `reports/`）
- [ ] 与 P0 共用至少 1 套任务脚本与成功定义
- [ ] 首组 measured 后回链 `motion_ws` commit

## 附件与回链


| 项        | 路径                                                                    |
| -------- | --------------------------------------------------------------------- |
| 文献笔记     | `04-文献阅读/notes/01-具身智能-VLA-VLN/2026-arXiv-EmbodiedVLN-Survey-阅读笔记.md` |
| AsyncShield | `04-文献阅读/notes/01-具身智能-VLA-VLN/2026-arXiv-AsyncShield-阅读笔记.md`；CAP-EXEC-ASYNC-SHIELD-ALIGN-001 |
| 实现方向     | `01-工作计划/ForkSpatialLink-实现方向_含AsyncShield对齐.md` |
| P0 模板    | `40-验证/P0-Benchmark-模板.md`                                            |
| bag / 报告 | 【待补充】                                                                 |


---

## 文档元数据


| 字段             | 值                          |
| -------------- | -------------------------- |
| id             | BENCH-P1-WEAKNET-001       |
| type           | benchmark                  |
| stage          | validation                 |
| status         | todo                       |
| canonical      | true                       |
| evidence_level | idea                       |
| stack          | motion_ws                  |
| commit         | 【待补充】                      |
| updated        | 2026-07-22                 |
| next           | P0-C 无损闭环通过后，选定注入工具并逐轴扫描 bandwidth/latency/jitter/loss/disconnect |


