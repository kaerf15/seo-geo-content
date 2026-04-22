# 复盘报告：{task_slug}

- 标题：
- 任务目录：`output/{task_slug}/`
- 内容交付物：`deliverables/content/`
- 创建日期：
- Owner：

---

## 1. 目标与范围（来自 brief）

- 转化目标：
- 目标受众：
- 目标市场 / 语言：
- 首发平台（1 个，来自确认点 A）：
- 次发平台（来自确认点 A，其余 Top 3）：
- 成功定义：
  - SEO 口径（至少 1 项）：排名 / 自然流量 / CTR / 转化
  - GEO 口径（至少 1 项）：AI 引用频率 / AI SOV / 品牌提及 / AI 推荐流量

## 2. 目标查询集合（条数下限见 `platform_rules.yaml#shared.target_queries_in_report_min`，用于复测）

> 这里是**最终测量口径**，不是候选池；是 brief §3 意图语料库的代表子集。复测时围绕这份清单抽样或全量测。

1.
2.
3.
4.
5.
6.
7.
8.
9.
10.

## 3. 权威来源白名单（命中用于证据链质检）

> 从 `config/authority.txt` 同步一份作为本任务快照；**允许**在此追加行业专属来源（本任务范围内生效，不影响 `config/` 本体）。

-
-
-

## 4. 上线前自检（硬门禁，全 PASS 才算交付完成）

> **自检流程（硬）**：
> 1. Agent 在项目根跑 `python .cursor/skills/seo-geo/tools/verify/verify.py {task_slug}`
> 2. 脚本产出两份：`.workspace/verify_report.json`（机器读）+ `.workspace/verify_report.md`（人读）
> 3. **本节直接 include `verify_report.md` 的内容**（或整段复制）；FAIL 回 Step 3 改稿后重跑，直到 `gate_pass == true`
> 4. SKIP 项由 Agent 在下方 §4.S 追加"人工判定理由"
>
> checklist 的完整条目见 [`templates/checklist.yaml`](../../.cursor/skills/seo-geo/templates/checklist.yaml)；阈值全部来自 `platform_rules.yaml`——**不允许**在本报告里硬写数字。

### 4.0 verify.py 运行摘要

- 运行时间：
- `totals`：PASS = ___，FAIL = ___，SKIP = ___
- `gate_pass`：true / false
- JSON 路径：`output/{task_slug}/.workspace/verify_report.json`
- Markdown 路径：`output/{task_slug}/.workspace/verify_report.md`

### 4.1 逐条结果（从 `verify_report.md` 粘贴）

<!-- BEGIN verify_report.md -->

（粘贴 `output/{task_slug}/.workspace/verify_report.md` 的内容到这里）

<!-- END verify_report.md -->

### 4.S SKIP 人工判定（每条 SKIP 必须按下方格式补全；不得一句话敷衍）

> **最小格式**（硬规则）：
> 1. `checklist id + 平台`：锚点
> 2. `SKIP 原因`：照抄 `verify_report.md` 里该行的 `actual` 文字（让审阅者看到脚本为什么没法自动判）
> 3. `人工判定`：PASS / FAIL
> 4. `证据定位`：指向交付内容里的**具体段落/标题/链接/行号**；判 PASS 的必须有可追溯锚点，不能是"我觉得已经有了"
>
> **示例**（结构参考，不代表本任务结果）：
>
> | id | 平台 | SKIP 原因 | 判定 | 证据定位 |
> |---|---|---|---|---|
> | 9 | medium | "逐节人工核对" | PASS | `medium.md` 每节均含 1 条数字或引用：§2 引 McKinsey 2024、§3 引内部数据 +42%、§4 引 Gartner CAGR 11% |
> | 11 | xiaohongshu | "数字 '3 个坑' 未在 facts.md 直接命中" | FAIL | facts.md 只提到"常见 2 个坑"，需回 Step 3 把"3"改回"2"或补一条事实 |

| checklist id | 平台 | SKIP 原因（抄 verify 的 actual） | 人工判定 | 证据定位（具体段落/链接） |
|---|---|---|---|---|
|  |  |  |  |  |

## 5. 上线信息（上线时填）

- 上线链接 URL：
- 上线时间：
- 版本号 / Commit：

## 6. 复测计划（固定节奏，GEO 周期比传统 SEO 更短）

> 节奏设计理由：T+3/14 是为了抓 LLM 索引窗口（多数 LLM 的检索/训练刷新频率 ≤ 2 周）；T+45/90 沿用传统 SEO 的排名/转化观测。

- **T+3**：GEO 冷启动抽查——抽样 §2 查询集合 5 条，测主流 AI（ChatGPT/Perplexity/Google SGE）是否已开始引用
- **T+14**：首轮完整复测——AI 引用覆盖率 + 排名首测 + 初始线索质量
- **T+45**：引用稳定性复测——AI 引用是否持续 / 排名是否稳 / 是否被更换为竞品
- **T+90**：季度归因——转化数据、是否重写、是否扩写集群、是否再分发

## 7. 复测记录

> 追加规则（硬）：每次复测新增一个 `#### T+N / YYYY-MM-DD` 小节，按时间顺序追加到本节末尾；**绝不**覆盖示例段，也不在已有小节内改写。
>
> 下方"示例"段仅为结构参考，不代表已有复测——首次复测请以 `#### T+3 / YYYY-MM-DD` 新锚点起新段。

#### 示例 / YYYY-MM-DD（T+N）

##### 7.1 复测必填（Agent 跑 GEO probe 自动填写 7.3.1 / 7.3.2）

- [ ] GEO 探针：按 §2 查询集合跑一遍 AI 引用抽查（详见 7.3.1）
- [ ] SEO 观测至少 1 项：排名 / 流量 / CTR / 转化
- [ ] 证据链核查：新数字是否就近给出处
- [ ] 下一步动作已选（从 7.4 菜单里选）

##### 7.2 复测范围

- 查询集合：抽样（5 条） / 全量
- AI 平台：ChatGPT / Perplexity / Claude / Google AIO / 百度 / 知乎（选你目标市场的主流）

##### 7.3 结果记录

###### 7.3.1 GEO 探针（Agent 用工具实测）

> **字段 + 汇总指标** 见 [`_probe_schema.md`](../../../.cursor/skills/seo-geo/templates/_probe_schema.md)——与 brief §2.1 同构，可直接横向对比基线。
>
> 工具优先级：`cursor-ide-browser` 打开 Perplexity/ChatGPT/Google SGE → `user-tavily` / `user-jina` SERP 抓取 → `WebSearch` 兜底。
> 原始截图/摘要保存到 `output/{task_slug}/.workspace/probe/T+N/`。

（把 `_probe_schema.md` 的"填写模板"粘到这里，按本次抽样量填满）

###### 7.3.2 SEO 观测（人工/工具填）

- 排名变化（关键查询 Top 5 的位置）：
- 自然流量 / CTR 变化：
- 转化数据：

###### 7.3.3 用户反馈

- 线索质量（来的是谁 / 问了什么 / 卡在哪）：
- 价格 / 政策反馈（对 MOQ / 价带 / 交期 / 物流的反应）：
- 证据缺口（客户最不信哪句话 / 最想看什么证明）：

##### 7.4 下一步动作（只能从以下菜单选，避免漂移）

- [ ] 改首段直答（阈值见 `platform_rules.yaml#landing_page.thresholds.first_paragraph_direct_answer`）
- [ ] 改 H2/H3 为问题式标题
- [ ] 补 FAQ（阈值见 `shared.faq`）+ FAQPage Schema
- [ ] 补证据链（权威引用 + 数字结论就近引用）
- [ ] 补 Schema（Organization / Article / HowTo / LocalBusiness）
- [ ] 扩写：新增子主题 / 补集群文章 / 加内链
- [ ] 加分发：生成新平台内容 / 执行站外信号
- [ ] 重新定位：调整查询集合 / 更新 Brief
- [ ] 叙事重写：若 7.3.1 显示品牌在某平台声量弱，按 `_narrative_playbook.md` 换一个叙事原型重写该平台
