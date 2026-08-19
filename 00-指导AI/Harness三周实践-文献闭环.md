# Harness 三周实践：文献闭环打样

> 主线：文献闭环（PDF → 笔记 → CAP → ProjectState）。  
> 目标：用最小成本验证「工作台 / 验收单 / 返工」三问，而非一次搭完美 Harness。  
> 对照：`00-指导AI/motion-Harness缺口清单.md`  
> 方法来源：`04-文献阅读/notes/90-行业报告-趋势/2026-OpenAI-Anthropic-Harness-Engineering-阅读笔记.md`

## 开场固定 `@` 清单（W1 起强制）

每次文献任务开场只带：

1. `@ProjectState.md`
2. `@00-指导AI/prompt.md`
3. `@04-文献阅读/文献阅读prompt.md`
4. `@10-收集箱/papers/<域>/<文件>.pdf`（或已有笔记）
5. 对照材料之一：`@02-架构设计/Go2-VLA-SLAM-Token技术方案.md`（或同级 L2）

禁止开场一次塞入全部 L2/L3。需要时再按路径下钻。

---

## 第 1 周：工作台（AI 知道去哪找）

### 动作

- [ ] 确认 PDF 落在 `10-收集箱/papers/<域编号>-<域名>/`
- [ ] 确认笔记将写入 `04-文献阅读/notes/<同域>/`
- [ ] 命名：`<年>-<会或来源>-<简称>-阅读笔记.md`
- [ ] 对照缺口清单，勾掉「找得到路径」相关项的心理预期（G2 本周只做路径纪律）

### 验收（布尔）

- [ ] PDF 路径与 `notes/` 领域编号一致
- [ ] 笔记不落在 `notes/` 根目录
- [ ] 开场 `@` 未超出上方清单（额外材料仅在后续轮次引入）

**本周完成定义**：任选 1 篇，路径与命名正确，可开始写笔记（笔记本身可到 W2 完成）。

---

## 第 2 周：验收单（什么叫做完）

### 文献闭环 6 步勾选（来自 WORKFLOW）

- [ ] 1. PDF → `10-收集箱/papers/`
- [ ] 2. 分析笔记 → `04-文献阅读/notes/<域>/*-阅读笔记.md`
- [ ] 3. 能力卡 → `05-知识沉淀/<主题>/CAP-*.md` **或** 文内写明「无需 CAP」理由
- [ ] 4. 若影响架构 → 更新 L2 与/或 `ProjectState.md` 任务
- [ ] 5. 若可专利 → 仅登记到 `06-产出/专利/` 索引意图（**不**在笔记写未 filed 独权细节）
- [ ] 6. 若可论文 → 申请日后；本周最多记 `next` 指针

### 质量门（四章 + 元数据）

- [ ] 四章齐全：是什么 / 作者方 / 与本项目关系 / 参数指标
- [ ] 借鉴矩阵含优先级：立即跟进 / 列入调研 / 仅存档
- [ ] 【事实】/【推断】/【待补充】已区分
- [ ] 文末「文档元数据」表完整（至少 id、type、stage、status、updated）
- [ ] CAP（若有）含：结论、适用、不适用、关联

### 验收（布尔）

- [ ] 笔记 `status=done`
- [ ] CAP 已落盘 **或** 有「无需 CAP」一句理由
- [ ] `ProjectState` 相关任务状态已更新（或注明无任务可改）

**本周完成定义**：单篇闭环质量门全勾选。

---

## 第 3 周：返工机制（看见错并改环境）

### 两轮流程

1. **生成轮**：按 `文献阅读prompt.md` 写出笔记初稿  
2. **核校轮**（换提示或新会话）：对照 PDF/原文，填「粘贴/生成核校表」（模式见 EmbodiedVLN 笔记附录 A）

核校表示意：

| 核项 | 初稿说法 | 原文位置 | 判定 |
| --- | --- | --- | --- |
| … | … | … | 【事实】一致 / 需改正 |

### 错误固化（必做 ≥1 次）

发现一类可复现错误时：

1. 记入 `motion-Harness缺口清单.md` §3 失败固化日志  
2. 改环境：`文献阅读prompt.md` 或 `.cursor/rules/paper-analysis.mdc` 补 1 条防再犯  
3. 用同篇或同结构任务回归一次

### 验收（布尔）

- [x] 存在核校表（附录或独立节）且至少核过 3 个硬事实点（Super-LIO 附录 A）
- [x] 失败固化日志有 ≥1 条完整记录（缺口清单 §3，2026-07-21）
- [x] 对应 rule/prompt 已改（`文献阅读prompt.md` venue/LICENSE 硬门）
- [x] `ProjectState` 中本实践相关任务已勾选或更新 next（T-015）

**三周总完成定义**：W1–W3 验收项全部勾选；缺口清单 G2–G4 可勾。✅ 2026-07-21

---

## 附录 A：P0 验证可迁移检查点

> 同一三问；主线仍是文献。P0 有 `motion_ws` 证据后再单独开三周。

| 三问 | 检查点（布尔） |
| --- | --- |
| 在哪 | `@40-验证/P0-Benchmark-模板.md` + `@01-工作计划/技术栈索引.md`；实测细节回链 `motion_ws` |
| 用什么 | 复现命令、bag/日志路径写入验证文档；evo 等工具名如实 |
| 对不对 | 环境表关键字段齐全；`stack`+`commit` 已填；定位 ATE/RPE 或等价 ≥1；关键帧或频率 ≥1；≥1 场景勾选+附件；**实测列无参考值冒充** |
| 完成定义 | `benchmark-validation.mdc`「P0 首组最低验收」全勾；相关 CAP/`evidence_level` 回链 |

---

## 附录 B：专利交底可迁移检查点

> 不在本实践展开独权细节；只迁移 Harness 纪律。

| 三问 | 检查点（布尔） |
| --- | --- |
| 在哪 | `@06-产出/专利/` + `@06-产出/专利/专利族谱映射.md` + `@.cursor/rules/patent-disclosure.mdc` |
| 用什么 | 交底书结构：问题 / 方案 / 效果 / 权利要求骨架；上位概括，不绑死具体实现名 |
| 对不对 | `confidentiality: patent-sensitive` 已标；`meta.md` 的 `stage`/`next` 已更新；申请前无「建议公开完整 Spec/方法」 |
| 完成定义 | 代理人可读的一版交底落盘；族谱无重复独权冲突说明 |

---

## 进度记录（执行时填写）

| 周 | 选用文献/任务 | 完成日 | 备注 |
| --- | --- | --- | --- |
| W1 | Swarm-SLAM（`papers/03/.../2301.06230v3-Swarm-SLAM.pdf`） | 2026-07-17 | 路径/命名正确；笔记落 `notes/03-...` |
| W2 | 同上：笔记 + CAP + ProjectState T-016 | 2026-07-17 | 质量门四章+元数据+核校表；CAP-SLAM-SWARM-SLAM-GATE-001 |
| W3 | venue/LICENSE/图轴硬门固化；Super-LIO 核校表回归 | 2026-07-21 | 改 `文献阅读prompt.md`；缺口清单 G4 ✅；登记失败日志首条 |

---

## 文档元数据

| 字段 | 值 |
| --- | --- |
| id | GUIDE-HARNESS-PRACTICE-LIT-001 |
| type | plan |
| stage | design |
| status | done |
| canonical | true |
| evidence_level | proposal |
| confidentiality | internal |
| related | GUIDE-HARNESS-GAP-001；NOTE-2026-OpenAI-Anthropic-Harness-Engineering；CAP-PROCESS-HARNESS-001；NOTE-2024-arXiv-Swarm-SLAM；NOTE-2025-RAL-Super-LIO |
| updated | 2026-07-21 |
| next | 工程侧推进 T-008 / T-004；文献下一篇 Kimera-Multi |
