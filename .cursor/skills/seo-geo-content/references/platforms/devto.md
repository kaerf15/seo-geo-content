# Dev.to Article

> Hands-on developer article in English.

产出格式 → [formats.md](../formats.md) + [_dev_article.md](./_dev_article.md)

## 约束

- **篇幅**：800–2200 words
- **Title**：≤80 characters
- **语气**：practical, dev-first
- **忌**：marketing copy; no hands-on detail
- **结构**：TL;DR → steps → code/command → gotchas

## Title formulas

- `How I {solved X} with {tool} (step-by-step)`
- `{Tool} vs {Tool} for {use case}: what actually worked`
- `Fixing {error} in {stack}: a minimal repro`

## 分发要点

- **Tags**：4 tags max on Dev.to — pick stack + topic
- **Cover image**：1200×630 optional but helps feed
- **Series**：if multi-part, link part 1 in intro
- **Canonical**：cross-post from own blog with canonical URL if applicable

## 发布 checklist（不写进 output）

- [ ] Title ≤80 chars
- [ ] TL;DR or "先给结论" equivalent at top
- [ ] Runnable code or commands

## Front matter（发布到 Dev.to 时用，可不写入 output）

```yaml
---
title: ...
published: false
tags: tag1, tag2
series:
  name: ...
  position: 1
---
```
