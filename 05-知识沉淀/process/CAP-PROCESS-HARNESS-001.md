# Agent Harness：工作台 / 验收单 / 返工

## 结论

长时程 Agent 产出取决于环境，不只取决于模型。对本仓：

1. **工作台**：`ProjectState` 短目录 + 分层文档，按需读取  
2. **验收单**：阶段完成条件写成可勾选布尔项  
3. **返工**：生成与核校拆分；错误固化进 rule/模板，而非只改当次对话  

## 适用条件

- 文献闭环、架构文档、验证填表、专利交底等**可重复**任务
- 需要跨会话保持质量、减少「AI 自评很好但不可用」

## 不适用

- 一次性探索闲聊、无验收标准的头脑风暴
- 用 Harness 讨论为名写入 `patent-sensitive` 完整方法或建议公开未申请细节

## 关联

- 笔记：`04-文献阅读/notes/90-行业报告-趋势/2026-OpenAI-Anthropic-Harness-Engineering-阅读笔记.md`
- 缺口：`00-指导AI/motion-Harness缺口清单.md`
- 实践：`00-指导AI/Harness三周实践-文献闭环.md`
- 既有：`WORKFLOW.md`、`00-指导AI/prompt.md`、`.cursor/rules/*`

## 验证 todo

- [ ] 按三周实践跑通 ≥1 篇文献闭环（含核校轮 + 失败固化 1 条）
- [ ] P0 / 专利附录检查点在真实任务上各试用一次

---

## 文档元数据

| 字段 | 值 |
| --- | --- |
| id | CAP-PROCESS-HARNESS-001 |
| type | capability |
| stage | knowledge |
| status | done |
| evidence_level | proposal |
| sources | OpenAI Harness engineering 2026-02-11；Anthropic Harness design 2026-03-24；本仓 WORKFLOW/prompt |
| applies_to | 统筹仓 AI 协作流程；可迁移至 motion_ws 验证闭环 |
| updated | 2026-07-17 |
