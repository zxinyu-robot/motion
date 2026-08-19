# ONEPAGER：具身 VLN 真机评测告诉我们什么

> **用途**：internal Reading Group / 月度分享大纲  
> **confidentiality**：`internal` — 外发前再审查；**不含**专利独权、协议伪码、未冻结 Spec  
> **文献**：Tongji et al., arXiv:2607.09792（Embodied VLN Survey + Real-World Eval）

## 一页结论

语言导航要从「仿真榜单 SR」转向「真机语义完成 + 安全」。在论文测试配置下：带地图/LiDAR 的层级系统更稳；仅 RGB 的端到端系统 sim→real 掉点大、碰撞高。对 motion：**不抢 L3 大脑，做 L4 几何与弱网下的可送达上下文**。

## 问题

真实指令是「去水槽旁 / 带我到床边」，不是坐标点。VLN = 第一视角视觉 + 语言 + 记忆 + 动作；传统 SR（停在 3 m 内）掩盖语义停错误。

## 方法地图（一句话）


| 维   | 两极                   |
| --- | -------------------- |
| 动作  | 层级 waypoint ↔ 单体低层动作 |
| 模型  | 判别式选动作 ↔ 生成式出计划/动作   |


趋势：任务专家判别模型 → LLM/LVLM 生成式；仿真 → 真机部署。

## 真机数字（论文配置，勿外推为「层级永远赢」）


|                                | SR      | SSR | OSR | CR      |
| ------------------------------ | ------- | --- | --- | ------- |
| 单体 RGB（JanusVLN 配置）            | 22%     | 17% | 27% | **51%** |
| 层级 + 全景 + SLAM/LiDAR（CLASH 配置） | **51%** | 37% | 67% | **7%**  |


- 单体仿真 SR 约 **61%** → 真机 **22%**
- 10 场景 × 100 ep/系统；指令约 70% 逐步 / 20% 意图 / 10% 回溯
- 差距混有传感器与地图栈，论文自行提醒勿过度归因架构

## 失败模式

1. 动作方向错 / 泛化不足
2. 碰撞（RGB 视野与无显式几何；LiDAR 也有扫描平面下盲区）
3. 经过正确区域却不停（OSR≫SR；意图/回溯尤甚）

## 对本线含义（对外口径）

```text
L3 具身大脑（他方/合作）     ← 理解指令、出 waypoint
        ↑ 需要可靠几何与上下文
L4 motion：弱网多机空间智能基础设施
        ↑ KeyFrame / 增量空间块 / 通信感知调度（细节 internal）
L1 前端 SLAM
```

- **立即做**：评测报 SSR + CR；WeakNet Bench 加通信轴  
- **不做**：另起炉灶卷端到端 VLN 刷仿真榜  
- **差异化尺子**：有几何时，通信变差是否拖垮 SR/SSR/恢复时间

## 建议幻灯 5 页（标题级）

1. 从坐标导航到语言导航：问题重述
2. 二维分类：层级/单体 × 判别/生成
3. 真机表：SR/SSR/CR 与 sim-to-real
4. 失败：碰撞、语义停、传感器盲区
5. 我们的位置：L4 尺子与下一步（P0 实测 / WeakNet 提纲）

## 禁止写入本材料的内容

- 双触发伪码、VoxelDiff 完整 schema、未 filed 方法细节  
- 「已验证 / 已量产」类表述（当前 evidence 多为 proposal）  
- 建议把统筹仓全文公开到可检索渠道

---

## 文档元数据


| 字段              | 值                                   |
| --------------- | ----------------------------------- |
| id              | ONEPAGER-2026-EmbodiedVLN-Survey    |
| type            | influence                           |
| stage           | output                              |
| status          | done                                |
| confidentiality | internal                            |
| knowledge_refs  | CAP-EVAL-VLN-REAL-001               |
| paper_refs      | arXiv:2607.09792                    |
| updated         | 2026-07-16                          |
| next            | Reading Group 第二期宣讲；可作 T-011 月度分享素材 |


