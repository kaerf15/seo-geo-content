# 内部 Brief（Agent 自用，不交付）

> Agent 基于 `.workspace/facts.md` 填充本文件，目的是让自己想清楚再动手。写得快而准即可，不要花哨。写完放到 `output/<task>/.workspace/brief.md`。
>
> 本文件里涉及字数/比例/数量的阈值，一律引用 `platform_rules.yaml` 的 `shared` 与各平台 `thresholds`——不再在本模板里写硬数字。

---

- 主题：
- 日期：
- 行业：
- 地区 / 语言：
- 目标客户：

## 1. 目标与范围

- 业务目标（从 facts Q1 带过来）：
- 要在哪些平台上影响心智（待确认点 A 后补）：
- 需要影响的核心语义范围（3–5 个语义簇）：
- 关键实体（品牌/产品/人/地点/概念/专属 IP）：

## 2. AI 认知探针（Agent 必须抽样实测，不允许纯推测）

> **硬规则**：本节不是"拍脑袋推测"，Agent 必须用自带的网页/搜索工具实测 ≥ 5 个样本查询。
>
> **字段与汇总指标统一走** [`_probe_schema.md`](./_probe_schema.md)——本节与 `report.md §7.3.1` 共用同一张表结构，这样上线前基线与上线后复测能直接对照。
>
> **工具优先级**（按可用性选，不强制用某一家）：
> - 首选：MCP `user-tavily.search` / `user-jina.web_search` / `user-firecrawl.search`（语义搜索 + 摘要）
> - 兜底：`WebSearch` / `WebFetch`（逐条抓 SERP + People Also Ask）
> - 测 LLM 是否引用：`cursor-ide-browser` 打开 Perplexity / ChatGPT / Google SGE，提问相同 query 并截屏/抓答案
>
> **抽样量**：从 §3 意图语料库里挑 5 条最具代表性的（1 信息类、1 实操类、1 对比类、1 本地类、1 长尾）。

### 2.1 基线抽样表

> **表结构与填法见** [`_probe_schema.md`](./_probe_schema.md)。直接复制那里的"填写模板"到本节。

（把 probe schema 模板粘到这里并填满 ≥ 5 行）

### 2.2 机会缺口（从 2.1 的表与汇总指标推出）

- 哪些高频问题**需求强但品牌声量弱**（AI 答里没人提你）：
  -
- 哪些问题**竞品占优但叙事角度单一**（你可以从另一个原型切入）：
  -
- 哪些**权威域名**最常被引用（`config/authority.txt` 里有没有？不在就考虑本任务追加）：
  -

## 3. 意图语料库（问题清单）

> 条数下限见 `platform_rules.yaml#shared.intent_corpus_in_brief_min`。
> **与 report §2 的关系**：本节是**全集**；从中挑选最有代表性的 `shared.target_queries_in_report_min` 条作为**代表子集**，进入 `report.md` §2 作为复测口径。本节的条数下限 > report 的条数下限，两者不是同义重复。

### 信息类（是什么 / 为什么）

-
-

### 实操类（如何做 / 步骤）

-
-

### 对比类（A vs B / 选型）

-
-

### 本地 / 场景类（如适用）

-
-

## 4. 支柱-集群结构

### 支柱页面（Pillar / 即 landing_page）

- 标题候选：
- 目标关键词（SEO）：
- 目标问题（GEO）：
- 长度区间：见 `platform_rules.yaml#landing_page.word_count`

### 集群主题（Cluster，每条可对应一个子平台内容）

| 子主题 | 适合平台 | 搜索意图 | 需要的证据 | 建议 Schema |
|---|---|---|---|---|
|  |  |  |  |  |

## 5. 证据索引（引用 facts.md Q11，不复制正文）

> 本节是**索引**不是正文：左列写主张，右列指向 `.workspace/facts.md` 里 Q11 的具体条目（如 `Q11.认证` / `Q11.案例`），而**不要**把 facts 原文重抄一遍。
>
> 缺证据时标"暂无"——"暂无"必须是用户亲口确认（见 SKILL.md Step 1 第 4 条）。
>
> 目的：写内容时快速回查"这句话靠哪条事实撑着"；facts.md 一处改，brief 这里自动生效。

| 主张 | 对应 facts Q11 条目 | 可公开 | 权威域 | 备注 |
|---|---|---|---|---|
|  | facts.md#Q11.<字段> |  |  |  |

## 6. 写作指令（Agent 给自己的自律清单）

> 所有硬数字一律走 `platform_rules.yaml`；本节只写"做什么"，不写"具体多少"。

### SEO 基础（landing_page 必做）

- Title：命中 `landing_page.title.max`
- Meta Description：命中 `landing_page.meta_description.max`
- URL 建议：
- 内链：数量见 `shared.internal_links`（至少 1 条回链 landing_page 集群）
- 外链：权威来源数量见 `shared.external_authority_links`

### GEO 增量（landing_page 必做）

- 首段直答：命中 `landing_page.thresholds.first_paragraph_direct_answer`
- H2/H3 问题式占比：≥ `shared.question_style_headings_ratio_landing`
- FAQ：条数与单条字数命中 `shared.faq`
- 数字/事实就近链接：比例 ≥ `shared.numeric_citation_ratio`
- 确定性语言（避免"可能/大概/一些人认为"）
- 实体密度（品牌/产品/术语一致出现）

## 7. KPI 与监测口径（进 report.md §1 成功定义）

> 口径的"项目"留在此，"阈值"由数据决定；两者在 report 中才合并为最终测量口径。

- 目标查询集合（≥ `shared.target_queries_in_report_min` 条）：从本 brief §3 意图语料库中挑代表子集
  -
  -
- SEO 口径（至少 1 项）：排名 / 自然流量 / CTR / 转化
- GEO 口径（至少 1 项）：AI 引用频率 / AI SOV / 品牌提及 / AI 推荐流量

## 8. 站外信号建议（可在 Step 2 写完，不依赖确认点 A）

> 注意：首发平台 / 次发平台属于**确认点 A 之后**才确定的字段，**不写在 brief**，直接进入 `report.md` §1。本节只写"除 Top 3 之外还能用什么站外信号助推"。

- 站外信号：PR / 社区 / 目录 / 评论平台（按行业选择）：
