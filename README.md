# sky-demand-prd-builder-skill

A Codex skill for turning product demands into structured PRD drafts (with data/metrics, events, and TODOs).

## What this skill does

- **Input**  
  - 直接接收一段产品需求/场景描述；或  
  - 接收 `sky-demand-evaluator` 已判定为「真需求 + 推荐实施」的结构化结果。

- **Output：生成结构化的 PRD 草稿，包括**：
  - PRD 元信息（需求名、Owner、版本、TODO 等）；
  - 背景、问题陈述与关键假设（假设明确可验证/证伪）；
  - 用户与使用场景（用户角色、Job story、关键用户路径）；
  - 需求范围与分层（Must/Should/Could + MVP 建议）；
  - 方案设计概要（功能架构、流程、页面/模块）；  
  - 数据 / 埋点 / 报表 / 监控设计；
  - 灰度发布 / 实验设计与上线后复盘计划；
  - 验收标准与用例示例；
  - 风险、依赖与 TODO 汇总（按角色+优先级）。

- **自检模式**  
  - 当输入是一份已有 PRD 文档时，不重写 PRD，而是按自身结构输出一份「自检报告」，指出缺失或薄弱的部分并给出补充建议。

## Layout

- `skill/SKILL.md`  
  核心 skill 定义与使用说明（PRD 结构、数据设计等）。

## Typical workflow

1. **需求判断（可选）**  
   - 使用 `sky-demand-evaluator` 判断某条用户/业务需求是否属于真需求，并给出实施推荐度评分。  
   - 对于「真需求 + 推荐度 > 50%」的条目，可直接作为本 skill 的输入。

2. **生成 PRD 草稿**  
   - 将需求描述或 `sky-demand-evaluator` 的结构化输出输入给 `sky-demand-prd-builder-skill`。  
   - 本 skill 生成结构化 PRD 文本（通常会另存为一个 `.md` 文件，默认目录如 `output/prd/xxx-prd.md`），你在此基础上补完 TODO、对齐团队口径即可用于评审/跟进。

3. **PRD 自检（可选）**  
   - 如已有人手工写好 PRD，也可以让本 skill 以自检模式对该 PRD 做结构化检查，给出需要补充的模块、风险与 TODO 清单。
