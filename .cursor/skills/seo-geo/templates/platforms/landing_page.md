<!--
叙事层（Agent 必读，**填骨架前**先完成叙事转译牌）
原型：#1 Authority Declaration（权威声明）
手册：`_narrative_playbook.md`
差异化检验：开头 3 段不能与 own_blog 撞——本篇必须**第三人称、结论前置、陈述为主**。
-->

# {主标题，长度见 `platform_rules.yaml#landing_page.title.max`}

> 副标题（一句话利益点，长度见 `platform_rules.yaml#landing_page.meta_description.max`）

- 发布日期：YYYY-MM-DD
- 最近更新：YYYY-MM-DD
- 作者：
- 目标查询：（列 3–5 条本页主攻的查询）

---

## 首段直答

> 字数阈值：`platform_rules.yaml#landing_page.thresholds.first_paragraph_direct_answer`
>
> 直接回答本页核心问题，不做铺垫。此段是 AI 引用的首选抽取区，必须一段话可独立理解。

---

## 为什么这件事重要（1 段，含 1 个权威数据 + 出处）

> 数字就近给链接，域名命中 `config/authority.txt`。

---

## H2：用户会问的问题 1（问题式标题）

（核心论点）

- 证据 1（数字 + 出处链接）
- 证据 2
- 证据 3

## H2：用户会问的问题 2

### H3：具体怎么做（分步骤）

1. 步骤 1
2. 步骤 2
3. 步骤 3

## H2：用户会问的问题 3（对比/选型/避坑）

| 维度 | 方案 A | 方案 B | 方案 C |
|---|---|---|---|
|  |  |  |  |

## H2：真实案例 / 交付数据（如可公开）

> 尽量给具体数字、时间、客户类型。不可公开的写"案例详情请联系"，不要编。

---

## FAQ

> 条数下限与单条字数阈值：`platform_rules.yaml#shared.faq`（`count_min` / `per_item`）。
> 每条 Q&A 都必须可独立理解（脱离上下文也能看懂）。

### Q1. （客户常见问题 1）

A.

### Q2. （客户常见问题 2）

A.

### Q3.

A.

### Q4.

A.

### Q5.

A.

---

## 下一步 / 询盘入口

- 联系方式（来自 facts Q12）：
- 统一对外话术：
- 可索取的资料：

---

## 附：结构化数据建议（开发同学部署）

在 `<head>` 中注入以下 JSON-LD（三段可合并为数组，类型见 `platform_rules.yaml#shared.schema_landing`）：

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "{品牌名}",
  "url": "{官网}",
  "logo": "{logo URL}",
  "sameAs": ["{社媒链接}"]
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{主标题}",
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "author": { "@type": "Person", "name": "{作者}" },
  "publisher": { "@type": "Organization", "name": "{品牌名}" },
  "mainEntityOfPage": "{本页 URL}"
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "Q1", "acceptedAnswer": { "@type": "Answer", "text": "A1" } },
    { "@type": "Question", "name": "Q2", "acceptedAnswer": { "@type": "Answer", "text": "A2" } }
  ]
}
</script>
```
