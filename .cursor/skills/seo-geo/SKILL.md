---
name: seo-geo
description: 围绕一个主题生产多平台内容并做上线复盘的全流程 Agent。使用时机：用户要做 SEO/GEO 内容、多平台分发、或针对某主题做内容生产与复盘时。
---

# SKILL: SEO+GEO 多平台内容生产与复盘

> **路径约定**（贯穿本 skill）：
> - **skill 内部资源**（`config/` / `tools/` / `templates/`）一律以 **skill 根** `.cursor/skills/seo-geo/` 为基准。本文档里写 `config/authority.txt` 时，实际路径是 `.cursor/skills/seo-geo/config/authority.txt`。
> - **用户工作区**（`output/<task>/`）以**项目根**（包含 `.cursor/` 的目录）为基准。output 不进 skill——skill 是跨任务复用品，output 是任务专属。
> - **在终端执行脚本**时一律从项目根跑：`python .cursor/skills/seo-geo/tools/verify/verify.py <task_slug>`（脚本自己会算 skill 根与项目根，无需传参）。

## 0. 第一性原理（Agent 心智）

本 skill 最终只产出两件东西：

- `output/<task>/deliverables/content/*.md`：各选定平台的内容文档
- `output/<task>/deliverables/report.md`：复盘报告（含上线前自检 + T+3/14/45/90）

**其他一切都是中间产物**，必须放 `output/<task>/.workspace/`，不允许污染 `deliverables/`。

**硬数字的唯一真相源（SSOT）**：所有字数、比例、数量等阈值都在 `.cursor/skills/seo-geo/templates/platform_rules.yaml` 里（`shared` 与各平台的 `thresholds` 段）。本 SKILL 与其他模板只引用字段名，不重复写数字。要调阈值只改这一个文件。

**`landing_page` 的身份（特殊约定）**：它是"页型"不是"平台"——所以 `config/channels.yaml` 不把它列为候选（见 Step 2 确认点 A）；但在 `platform_rules.yaml`、`checklist.yaml`、`verify.py` 这三处工程视角里，它**被当作 platform 处理**（有自己的 `landing_page:` 规则段、参与 checklist "启用平台" 定义、落盘 `landing_page.md` 走正常门禁）。这是项目里唯一的"页型-平台"双身份例外，不会再扩展。

**脚本边界**（原"零脚本"原则的细化）：本 skill 主流程**允许**调用 `tools/` 下的判定型脚本（不允许写新的生成型脚本）。`tools/verify/` 是门禁脚本，把确认点 B 的 checklist 自动化；`tools/` 下不允许出现"替 Agent 写内容"的脚本。AI 认知探针（Step 2.5）与 GEO 复测探针（Step 5）**不写脚本**——Agent 直接用自带的网页/搜索/浏览器工具（`WebSearch` / `WebFetch` / MCP `user-tavily` / `user-jina` / `user-firecrawl` / `cursor-ide-browser`）实测。

可选的配图能力由独立 skill `gemini-image-gen` 提供，跟本主流程相互独立。

## 1. 流程总览（4 步 + 2 个人类确认点）

```
事实(facts) ─▶ AI认知探针(brief §2) ─▶ 内部brief ─▶ [确认点A:选Top3渠道 + 指定首发/次发]
                                                      │
                                                      ▼
             叙事转译(_narrative_playbook) ─▶ 多平台内容生成（每篇按 platform_rules 自检）
                                                      │
                                                      ▼
                      跑 verify.py ─▶ 写 report.md §4 ─▶ [确认点B:verify 门禁全PASS]
                                                      │
                                                      ▼
                                              deliverables/ 宣告完成
```

上线后：按 T+3/14/45/90 复测反馈回来时，Agent 用 MCP/浏览器工具跑 GEO 探针，把结果追加到 `report.md §7`。

## 2. 步骤细则

### Step 0：建任务目录

1. 让用户给一个 `<task_slug>`。**硬规则**：必须匹配正则 `^[a-z][a-z0-9-]{2,40}$`（小写字母开头、3–41 位、只允许小写字母/数字/短横线）。不满足就让用户改到满足。
2. 用常规文件写入创建：
   - `output/<task>/.workspace/`
   - `output/<task>/deliverables/content/`

### Step 1：收集事实

1. 读 `.cursor/skills/seo-geo/templates/facts.md`，把 12 个问题用自然语言逐条问用户（或用户一次贴完也行）
2. 把用户回答整理写入 `output/<task>/.workspace/facts.md`
3. **禁区**：任何关键项缺失（转化目标 / 目标客户 / 可公开证据材料）时**停下来追问**，不得凭空编造
4. **"暂无"规则**：只有在用户亲口确认"这一项没有/不便公开"后，才能在 facts.md 里写"暂无"。Agent 不得自行判断为"暂无"来绕过追问。Q11 证据材料里每出现一条"暂无"，Agent 都要在对话中明确确认一次

### Step 2：写内部 Brief（Agent 自用，不交付）

1. 读 `.cursor/skills/seo-geo/templates/brief.md`
2. 基于 facts.md 填充：语义范围 / 关键实体 / 证据清单 / 支柱-集群结构 / KPI 口径
3. 写入 `output/<task>/.workspace/brief.md`
4. **AI 认知探针（硬规则，brief §2 必做）**：从 §3 意图语料库中挑 ≥ 5 条代表性查询，用自带工具实测——填满 brief §2.1 / 2.2 / 2.3。工具选择优先级（按可用性）：
   - MCP `user-tavily.search` / `user-jina.web_search` / `user-firecrawl.search`（语义搜索 + 摘要）
   - 如需测 LLM 引用，用 `cursor-ide-browser` 打开 Perplexity / ChatGPT / Google SGE 提问
   - 兜底：`WebSearch` + `WebFetch` 抓 SERP + People Also Ask
   - **不允许**：用"拍脑袋推测"代替实测。这是 brief §2 的硬门槛
5. Brief §3 意图语料库 ≥ `shared.intent_corpus_in_brief_min` 条；其中最有代表性的 `shared.target_queries_in_report_min` 条将在 Step 4 进入 `report.md` §2 作为复测口径（两者是"全集—代表子集"关系，不是同义重复）
6. Brief 的目的是让 Agent 自己想清楚，不是交付——写得快而准即可

### 【人类确认点 A】渠道选择 + 首发分配

1. 读 `config/channels.yaml`，按 facts.md 中的 region/language/goal/content_type 过滤出候选
2. 在对话中列出 Top 5–8 候选（带简要理由），请用户选 **Top 3**
3. **紧接着**请用户在 Top 3 内指定：**首发平台（1 个）** 与 **次发平台（其余）**；这份分配**只**进入 `report.md` §1 对应字段（不写进 brief，以避免"brief 在确认点 A 之前写"的次序矛盾）
4. 不落盘任何渠道文件，确认结果直接进入 Step 3

> 说明：`landing_page` 不在 `channels.yaml` 候选里（那是页面/文档类型而非平台）。它作为"证据链主承载"在 Step 3 中无条件生产。

### Step 3：多平台内容生成

**对 Top 3 中每一个平台 + landing_page**，依次：

1. **叙事转译（硬规则，填骨架前必做）**：读 `.cursor/skills/seo-geo/templates/platforms/_narrative_playbook.md`，按对应原型（由骨架文件开头的 `<!-- 叙事层 -->` 注释指定）输出一段"叙事转译牌"——在对话或 `.workspace/narrative_<platform>.md` 里写明：原型名、视角与情感、事实块的转译前后对照、本篇的独特锋点。**不允许**直接用同一组事实在多个平台间机械改写
2. 读 `.cursor/skills/seo-geo/templates/platforms/<rule_key>.md` 作为写作骨架（`rule_key` 来自 `config/channels.yaml` 该平台的 `rule_key` 字段）
3. 读 `.cursor/skills/seo-geo/templates/platform_rules.yaml` 中对应 `rule_key` 段作为硬约束（`word_count`/`duration_sec`、`must_include`、`thresholds`、`tone`）
4. 基于 `.workspace/brief.md` + `.workspace/facts.md` + 叙事转译牌，生成内容
5. **落盘文件名硬规则**：`output/<task>/deliverables/content/<slug>.md`，其中 `<slug>` 来自 `config/channels.yaml` 该平台的 `slug` 字段；`landing_page` 固定落 `landing_page.md`。
   - 同 `rule_key`、不同 `slug` 的平台（如 B 站 `bilibili.md` / 抖音 `douyin.md` 都用 `short_video` 规则）**可共存**在一个任务内，verify.py 自动按 `channels.yaml` 的 `slug → rule_key` 映射找规则
   - `rule_key: null` 的平台（Reddit / Product Hunt）**不得**套模板；Agent 必须停下与用户共写，或本轮跳过该平台
6. **立即按 rules 自检**：字数（或时长）命中区间？`must_include` 逐项齐全？`thresholds` 命中？`tone` 一致？不满足则当场修改，不留给最后

**Landing Page 是特殊必选项**：即便用户没把官网/落地页选进 Top 3，也必须生成 `landing_page.md`，因为它是证据链与 Schema 的主承载，也是其他平台引流的最终页。

**差异化检验**：每篇交付前按 [`_narrative_playbook.md §差异化检验`](./templates/platforms/_narrative_playbook.md) 的 3 问自检，任意一问答"否"就重写。该 3 问只在 playbook 保留一份，这里不再复述。

### Step 4：写复盘报告 + 跑 verify 门禁

1. 读 `.cursor/skills/seo-geo/templates/report.md`
2. 填写：
   - §1 目标、成功口径、首发/次发（后者来自确认点 A）
   - §2 目标查询集合：从 `.workspace/brief.md` §3 挑最有代表性的条目，条数 ≥ `shared.target_queries_in_report_min`
   - §3 权威白名单：`config/authority.txt` 的内容复制一份，允许按本任务行业在本节追加（不动 `config/` 本体）
   - §6 保持 T+3/14/45/90 节奏描述
3. 写入 `output/<task>/deliverables/report.md`
4. **跑门禁脚本**：在项目根执行 `python .cursor/skills/seo-geo/tools/verify/verify.py <task_slug>`
5. 读回 `output/<task>/.workspace/verify_report.json`
6. 按 `report.md §4` 填表：§4.0 填 `totals` + `gate_pass`；§4.1 直接 include `.workspace/verify_report.md` 的内容（verify.py 已自动生成 Markdown 片段）；SKIP 项在 §4.S 补一行人工判定理由

### 【人类确认点 B】上线前自检（以 verify.py 为准）

**口径从"Agent 自报"改为"verify.py 跑 + Agent 补 SKIP 证据"**：

- `gate_pass == true`（无 FAIL）→ 可宣告交付
- 存在 FAIL → **必须**回 Step 3 修改对应平台内容，然后**重跑** verify.py，直到 PASS
- SKIP 项 Agent 必须在 `report.md §4.S` 补人工判定理由，不能留空

**FAIL 熔断（硬规则）**：同一任务内连续 **3 轮** verify FAIL 仍未 PASS → **停下**，不得继续盲目改稿。Agent 必须回到对话，把"反复失败的 checklist id + 现在的实测值 + 阈值"列出来，和用户对齐：是改内容、改阈值（改 `platform_rules.yaml`）、还是承认现实（如某证据真的找不到）。这堵住"无限重试直到撞运气 PASS"的漂移。

**SKIP 判定理由的最小格式**（`report.md §4.S` 必须按此写，不得一句话敷衍）：
- **平台 + checklist id**：锚点
- **为什么 verify 判了 SKIP**：引用 verify_report 的 actual 文字
- **Agent 的人工判定**：PASS / FAIL；判为 PASS 的理由必须指向内容里的**具体段落/标题/链接**，不能是"我觉得已经有了"

**11 条 checklist 的完整定义（id / 适用平台 / 判定口径 / 自动化程度 / 覆盖的 must_include）是 SSOT**：见 [`templates/checklist.yaml`](./templates/checklist.yaml)。SKILL / verify README / report 都只引用此文件，不再另抄表。

"启用平台" = Top 3 + landing_page（后者无条件启用，即便没进 Top 3）。

**report.md §3 追加的行业白名单会被门禁采纳**：verify.py 在跑 checklist #4 前，自动把 `config/authority.txt` 与 `report.md §3` 的行业白名单合并。所以你在 §3 加的行业来源**真的会生效**，不是摆设——但只限本任务，不影响 `config/authority.txt` 本体。

### Step 5：上线后追加复测（独立触发）

只有用户带着 T+3 / T+14 / T+45 / T+90 反馈回来时才执行：

1. 读当前 `output/<task>/deliverables/report.md`
2. 在 §7「复测记录」**追加**一个新小节（物理锚点：`#### T+3 / YYYY-MM-DD` 或 `#### T+14 / YYYY-MM-DD` 或 `#### T+45 / YYYY-MM-DD` 或 `#### T+90 / YYYY-MM-DD`），**绝不替换示例段或历史段**
3. **跑 GEO 探针（硬规则）**：按 report §2 的查询集合抽样（T+3 时抽样 5 条；T+14/45/90 抽样 ≥ 8 条或全量），用工具链实测——
   - 首选 `cursor-ide-browser` 打开 Perplexity / ChatGPT / Google SGE，逐条提问并抓答案里的引用 URL
   - 次选 MCP `user-tavily` / `user-jina` / `user-firecrawl` 抓 SERP 和摘要
   - 记录原始截图/摘要到 `output/<task>/.workspace/probe/T+N/`
   - 把数据填进 report §7.3.1 的表格；算出 AI 引用覆盖率和 SOV
4. 按 §7.4「下一步动作菜单」让用户从固定选项里选（改首段直答 / 改标题 / 补 FAQ / 补证据 / 补 Schema / 扩写 / 加分发 / 重新定位 / 叙事重写）
5. 若选择触发再生产，回到 Step 3 生成对应平台的新版本（新版本必须重新跑 verify.py）

## 3. 产物契约（终态）

```
output/<task>/
├── .workspace/
│   ├── facts.md                   # Step 1
│   ├── brief.md                   # Step 2
│   ├── narrative_<platform>.md    # Step 3（可选，不强制落盘）
│   ├── verify_report.json         # Step 4 verify.py 产出
│   └── probe/T+N/                 # Step 5 复测原始材料
└── deliverables/
    ├── content/                   # Step 3（用户选的 Top 3 + 必选的 landing_page）
    │   ├── landing_page.md
    │   ├── xiaohongshu.md
    │   └── ...
    └── report.md                  # Step 4 + Step 5 追加
```

## 4. 禁令（硬性约束）

1. 不得在 `deliverables/` 外产出交付文件，也不得在 `deliverables/` 内放中间产物
2. 不得写任何旧框架文件：`channels_*.md` / `audit_*.md` / `brief_*.md`（注意：`.workspace/brief.md` 不是这里说的旧文件，无下划线后缀即合规）/ `repurpose_*/` / `status_*.md`
3. 不得编造数字、认证、案例或引用链接——没有就先追问用户，确认真无则标"暂无"（见 Step 1 第 4 条）
4. 不得跳过确认点 A（渠道选择 + 首发/次发分配由人决定）
5. 不得在 verify.py 显示 FAIL 的情况下宣告交付完成；SKIP 项必须由 Agent 补人工判定理由
6. 不得修改 `config/` 下的文件（那是团队共识）。**边界区分**：
   - `output/<task>/deliverables/report.md` §3 的白名单是本任务快照，Agent **可**直接追加行业专属来源
   - `config/authority.txt` / `config/channels.yaml` 本体，Agent **只能读**；如需追加条目必须先与用户对齐并拿到明确同意
7. **脚本边界**：
   - **允许**调用 `tools/verify/verify.py`（判定型脚本，Step 4/5 用）
   - **允许**在 brief §2 和 report §7.3.1 里用 `WebSearch` / `WebFetch` / MCP（`user-tavily` / `user-jina` / `user-firecrawl` / `cursor-ide-browser`）做"实测"
   - **不允许**在 `tools/` 下新增"替 Agent 写内容"的生成型脚本
   - **不允许**为了跳过 AI 探针 / GEO 探针而用"Agent 推测"替代实测
   - 可选配图走独立 skill `gemini-image-gen`，且仅在用户明确要求"用 gemini-image-gen 给 X 生成图"时才触发
8. 不得在任何 `.md` / `.yaml` / 代码文件里写 API Key、密码、手机号等机密；Key 一律走环境变量
9. 不得跳过 Step 3 的叙事转译环节——骨架填充前必须产出一张"叙事转译牌"
10. **不得在连续 3 轮 verify FAIL 后仍自行继续改稿**——必须停下来与用户对齐（见确认点 B 的"FAIL 熔断"）
11. **不得以非规范文件名落盘交付内容**：文件名必须是 `config/channels.yaml` 某个平台的 `slug`（或 `landing_page`）。用别的名字 → verify 判 "未知平台 → SKIP"，门禁会认为该文件没被审计

## 5. 路径 + 调用速查表（唯一一张）

> 本表所有路径以**文档顶部的路径约定**为准：`config/` / `tools/` / `templates/` → skill 根；`output/<task>/` → 项目根。

| Agent 要做的事 | 读 | 写 / 执行 |
|---|---|---|
| 问事实 | `templates/facts.md` | `output/<task>/.workspace/facts.md` |
| 想清楚 + AI 探针 | `templates/brief.md` + `templates/_probe_schema.md` + `templates/platform_rules.yaml#shared` + **MCP/WebSearch** 实测 | `.workspace/brief.md`（§2 必含实测数据） |
| 选渠道 + 首/次发 | `config/channels.yaml`（读 `slug` 确定落盘文件名；读 `rule_key` 确认有骨架/硬规则） | 仅对话，不落盘；结果进 `report.md §1` |
| 叙事转译 | `templates/platforms/_narrative_playbook.md` + 平台骨架顶部注释 | 对话内输出"叙事转译牌"，可选写 `.workspace/narrative_<platform>.md` |
| 写 landing_page（无条件） | `templates/platforms/landing_page.md` + `platform_rules.yaml#landing_page` | `deliverables/content/landing_page.md` |
| 写 Top 3 平台内容 | `templates/platforms/<rule_key>.md` + `platform_rules.yaml#<rule_key>` | `deliverables/content/<slug>.md`（文件名用 channels.yaml 的 `slug`；同 `rule_key` 不同 `slug` 的平台可共存） |
| 写复盘报告 | `templates/report.md` + `config/authority.txt` + `platform_rules.yaml#shared` + `templates/checklist.yaml` + `templates/_probe_schema.md` | `deliverables/report.md` |
| 跑门禁 | `tools/verify/verify.py` | 从项目根跑 `python .cursor/skills/seo-geo/tools/verify/verify.py <task_slug>`；读 `.workspace/verify_report.json` + `verify_report.md`，include 到 `report.md §4.1` |
| 复测探针 | `report.md §2` + `templates/_probe_schema.md` + **`cursor-ide-browser` / MCP** | `.workspace/probe/T+N/` 原始数据 + `report.md §7` 追加锚点段 |

**三份 SSOT**（改这三份文件下游全部跟着生效，别处只引用）：

| SSOT 文件（相对 skill 根） | 管什么 |
|---|---|
| `templates/platform_rules.yaml` | 所有硬数字（字数/比例/数量/时长） |
| `templates/checklist.yaml` | 11 条上线前自检 checklist 的元数据；`covered_must_include` 字段决定 must_include 的跳过表 |
| `templates/_probe_schema.md` | AI/GEO 探针的字段与汇总指标 |

**桥接文件**：`config/channels.yaml` 的 `slug` ↔ `rule_key` ↔ `templates/platforms/<rule_key>.md` ↔ `platform_rules.yaml#<rule_key>` 是四者的桥接约束，verify.py `--self-check` 会做元校验（slug 指向的 rule_key 必须真存在）。
