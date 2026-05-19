---
name: seo-geo-content
description: 多平台营销文案与 SEO/GEO。营销优先，产出项目根 output/<name>.md。触发：种草、长文、短视频脚本、landing page、GEO、SEO 文案、转化文案、一稿多发、canonical。
---

# SEO / GEO 写作

**目标**：信念 → 行动（钩子 → 判断 → CTA）。SEO/GEO 放大传播，不替代营销。

写前内心过三问（不写进 output）：① 3 秒内读者知道「跟我有关」？② 至少 1 条可带走的判断？③ CTA 与转化目标、平台能力一致？

## 写前

用户未说明时，**只问缺项**（勿写进 output）：

| 项 | 可推断则不问 |
|----|-------------|
| 主题 | 用户已描述意图 |
| 平台 | [platforms/INDEX.md](references/platforms/INDEX.md)；已点名或 URL 暗示 |
| 受众 / 转化 / CTA | 可从主题/平台默认；**有强转化或链接时必须问 CTA** |
| 禁区 | — |
| 事实依据 | 无则正文不写具体数字与具名案例 |
| 主查询 | 主题清晰时可从主题推断 |

**事实**：用户给了资料 → 只用资料；要求行业数据但未给来源 → 先问或检索，搜不到则弱化；禁止无 URL 的「据 XX 报告」。

标题×3、开头×2 内心择优，正文只留一版。语气可参考 [examples/](examples/)（自检不过时再读）。

## 产出

路径：**项目根** `output/<name>.md`（默认 `{主题}-{platform}.md`）。

**只写可直发结果**：读者/运营复制进发布后台即可，不附带写作过程或发布配置。

| 允许 | 禁止写进 output |
|------|----------------|
| 该平台正文（标题、段落、`##`、FAQ、CTA 文案、口播、分镜表、标签行等） | YAML frontmatter（含 platform / topic / cta / facts 等） |
| 文内自然链接（延伸阅读写进正文，不单开「链接清单」节） | `## 发布元数据`、meta / og / schema / canonical 提示块 |
| 各平台规定的结构节名（如 `## 常见问题`、`## 口播`） | **短答**、**结论**、**边界** 等写作标签；候选标题；checklist；TBD；`---` 分隔辅文 |

平台、主查询、CTA、事实依据、canonical 关系 — **只在对话或内心自检中维护**，不进 output 文件。

**禁止**：候选标题、过程 checklist、空占位、TBD。

多平台：每平台一文件；**先读** [adaptation.md](references/adaptation.md)，顺序 canonical → 长文 → 短形态。

## 流程

1. **问缺项**（上表；可推断则跳过）
2. **读平台卡**：`references/platforms/{platform}.md` → 其 **archetype** 文件 → GEO 平台再读 [geo.md](references/geo.md)
3. **写入** `output/{主题}-{platform}.md`（仅可直发正文，见「产出」），过平台文末 **自检**；回复文件路径（不贴过程稿）

**数值约束真源**：[rules/platform_rules.json](rules/platform_rules.json)（篇幅、标题长度、FAQ 条数等）

## 修订

| 用户要求 | 做法 |
|----------|------|
| 改语气 / 缩短 / 加强钩子 | 重读平台卡 + 原 output，改后重过自检 |
| 改事实 / 数据 / 案例 | 先确认事实依据，禁止擅自补数 |
| 换平台 | 新文件、完整流程，禁止同文件换壳 |

## 红线

不编造事实 · 一平台一文件 · 禁止跨平台换壳 · output 只含可直发结果（无 YAML / 元数据块 / 写作标签）· 主查询在标题或首段 · 实体名一致 · 有 CTA · 不像别的平台剪过来的
