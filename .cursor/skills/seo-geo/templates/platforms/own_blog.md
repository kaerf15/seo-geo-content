<!--
叙事层（Agent 必读，**填骨架前**先完成叙事转译牌）
原型：#2 Pillar Explainer（支柱讲解）
手册：`_narrative_playbook.md`
差异化检验：与 landing_page 要**错位**——本篇是作者第一人称、有立场、给边界判断（"X 情况不适用"）。
-->

# {文章标题，长度见 `platform_rules.yaml#own_blog.title.max`}

> 副标题 / Meta Description（长度见 `platform_rules.yaml#own_blog.meta_description.max`，一句话概括本文要解决的问题）

- 发布日期：YYYY-MM-DD
- 最近更新：YYYY-MM-DD
- 作者：
- 所属集群（回链 landing_page 或支柱页）：[支柱页标题]()
- 目标查询：（列 3–5 条本文主攻的查询）

---

## 首段直答

> 字数阈值：`platform_rules.yaml#own_blog.thresholds.first_paragraph_direct_answer`（与 landing_page 同一 `shared.first_paragraph_direct_answer`）
>
> 直接回答本文核心问题，不做铺垫。

---

## 为什么这件事值得写（1 段，含 1 个权威数据 + 出处）

> 数字就近给链接，域名命中 `config/authority.txt`。本段建立"为什么现在读"的紧迫感。

---

## H2：问题式小标题 1

> 问题式标题占比要求：≥ `platform_rules.yaml#shared.question_style_headings_ratio_blog`（略低于 landing_page）

（核心论点 + 证据）

- 证据 1（数字 + 出处链接）
- 证据 2
- 证据 3

## H2：问题式小标题 2（展开 / 方法 / 步骤）

### H3：子问题或步骤 1

### H3：子问题或步骤 2

### H3：子问题或步骤 3

## H2：问题式小标题 3（对比 / 案例 / 行业观察）

> 博客相比 landing_page 的差异点在此——加入观点、案例、行业对比，而不是只做 FAQ 汇总。

| 维度 | 方案 A | 方案 B | 方案 C |
|---|---|---|---|
|  |  |  |  |

## H2：我的判断 / 给读者的建议

> 博客可以有观点。写清楚你主张什么、边界在哪、什么情况不适用。

---

## 延伸阅读（站内链接）

> 数量要求：`platform_rules.yaml#shared.internal_links`。必须回链一次支柱页 / landing_page，并链 1–2 条同主题集群内的其他博客文。

- [支柱页标题]()
- [相关博客文 1]()
- [相关博客文 2]()

## 参考来源

> 权威引用要求：至少 `platform_rules.yaml#shared.authority_citations_min` 条命中 `config/authority.txt`；总权威来源数量建议见 `shared.external_authority_links`。

- [来源 1]()
- [来源 2]()
- [来源 3]()

---

## 作者简介（E-E-A-T 信号）

（1–2 句：作者是谁、为什么有资格写这篇、相关背景或成果。）

---

## 附：结构化数据建议

在 `<head>` 中注入以下 JSON-LD（必含类型见 `platform_rules.yaml#shared.schema_blog_required`；可选类型见 `shared.schema_blog_optional`，含步骤时加 HowTo，正文内有 FAQ 块时加 FAQPage）：

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{文章标题}",
  "description": "{Meta Description}",
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "author": {
    "@type": "Person",
    "name": "{作者}",
    "url": "{作者主页}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "{品牌名}",
    "logo": { "@type": "ImageObject", "url": "{logo URL}" }
  },
  "mainEntityOfPage": "{本文 URL}"
}
</script>
```
