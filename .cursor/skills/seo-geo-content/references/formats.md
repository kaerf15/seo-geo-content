# 产出结构（`output/<name>.md`）

写满实词，无占位。约束以 [platforms/INDEX.md](./platforms/INDEX.md) 对应平台文件为准。

**短帖** `xiaohongshu`

```text
{标题}

{正文}

#标签1 #标签2 …
```

**线程** `twitter`

```text
1/ …

2/ …
```

**长文** `zhihu` `quora` — `# 标题` → 结论段 → `##` 小节 → 参考链接

**长文** `wechat` `toutiao` — `# 标题` → 开头 → `##` 小节 → 行动清单 → CTA

**长文** `baijiahao` — `# 标题` → 首段直答（40–80 字）→ `##` 小节 → `## 常见问题`（3–8 条，每条 30–120 字）→ CTA

**长文 EN** `medium` `substack` `hackernoon` `linkedin` — `# Title` → Hook / TL;DR → `##` → CTA

**开发者** `juejin` `csdn` `cnblogs` `devto` — 见 [_dev_article.md](./platforms/_dev_article.md)

**短视频** `douyin` `tiktok` `wechat_video` — 口播全文 + 分镜表（模板如下）

**中长视频** `bilibili` `youtube` — `# 标题` + 简介 + 口播 + 分镜表

### 分镜表模板（视频类必填）

```markdown
## 口播

{可照读全文，标注 (0–2s)(2–10s) 等时间段}

## 分镜表

| 镜号 | 时长 | 画面 | 口播/字幕 | 字幕要点 | BGM/音效 | 备注 |
|------|------|------|-----------|----------|----------|------|
| 1 | 0–2s | … | … | ≤15字 | … | 钩子 |
| 2 | 2–10s | … | … | … | … | 结论 |
| 3 | … | … | … | … | … | … |
```

**站内** `landing_page`

```markdown
# {标题}

{首段直答 40–80 字}

## …

## 常见问题

### Q1 …
…

## {CTA}

---

## 发布元数据

- **meta description**：…（≤160 字，含主查询）
- **canonical**：…（已有 URL 则填，无则留空不编造）
```

**站内** `own_blog`

```markdown
---
title: "{标题}"
description: "{≤160 字，含主查询}"
date: YYYY-MM-DD
updated: YYYY-MM-DD
tags: […]
---

# {标题}

{首段直答 40–80 字}

## …

## 延伸阅读

- […](url)

---

## 发布元数据

- **og:title** / **og:description**：与 title/description 一致
- **schema**：Article（title、datePublished、author 有则填）
```
