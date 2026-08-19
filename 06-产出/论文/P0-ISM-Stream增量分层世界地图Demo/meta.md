# 论文 Demo meta：ISM-Stream（增量分层局部世界地图流式）

> 调度入口。正文见同目录 `论文Demo.md`。  
> 申请日前仅 internal；完整方法受 C 族 SLAM-Token 专利分流约束。

## 1. 研究定位

**【设计决策】** 本 Demo 不写成“提出通用世界模型”，而限定为：

> 在端边协同条件下，将主通信内容从像素流升级为版本化局部世界增量，并通过分层加权传输与版本绑定动作，使机器人与上层模型对齐同一几何世界切片。

相对 P1（多机弱网世界模型）：本 Demo 是**单机端边可跑切片**。  
相对 P3（关键帧压缩）：本 Demo 以「传世界增量 vs 传图」为对照主轴，压缩是手段不是唯一主张。

## 2. 摘要指针

完整摘要草案见 `论文Demo.md` §11。效果性结论【待实验】后回填。

## 3. 与主链映射

| Demo 阶段 | P0 主链 | 状态 |
|---|---|---|
| D1 L0 增量通道 | P0-A/B | todo |
| D2 ActionGroup+version | P0-C | todo |
| D3 L1 语义旁路 | 扩展 | todo |
| D4 QoS 加权 + WeakNet | P0-D | 阻塞于 P0-C |

## 4. 已可引用事实

- Go2 纯 Nav2：N4/N5/N6 measured（见 BENCH-P0）  
- Token/QoS/分层传输：proposal，未测  

## 文档元数据

| 字段 | 值 |
|---|---|
| id | PAPER-DEMO-ISM-STREAM-001 |
| type | paper |
| stage | outline |
| status | in-progress |
| priority | ★★★★ |
| confidentiality | internal |
| knowledge_refs | CAP-SLAM-SUPER-LIO-PRODUCER-001；CAP-EVAL-VLN-REAL-001 |
| patent_refs | C族-SLAM-Token |
| benchmark_refs | BENCH-P0-Go2-MotionSLAM；P1-WeakNet-Collab-指标提纲 |
| canonical_body | `论文Demo.md` |
| updated | 2026-07-30 |
| next | D1 最小 L0 通道实验设计落 `40-验证/` 提纲；申请日前不扩写方法伪码 |
