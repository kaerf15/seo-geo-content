<!--
叙事层（Agent 必读）
原型：#9 Hook-Cut-Cue（钩子-切-行动）
手册：`_narrative_playbook.md`
差异化检验：0–3s 必须制造反差/冲突；画面指引与口播对齐；禁止超长 intro / 纯口播无画面。
-->

# 短视频脚本

> 时长区间：`platform_rules.yaml#short_video.duration_sec`。
> 分段：`platform_rules.yaml#short_video.thresholds.segments`（hook / core / explain / cta 的起止秒数）。
> **注意**：短视频不走字数口径，checklist #8 以"时长命中 duration_sec"为判定标准。

## 核心主张（一句话）

>

## 结构（秒数以 thresholds.segments 为准）

- 钩子段（问题 / 冲突 / 数据 / 反共识）
- 核心结论段（≤ `segments.core.max_points` 条）
- 解释段（用例 / 数据 / 类比）
- 行动段（关注 / 评论 / 私信 / 链接）

## 分镜表

> **硬对齐**：时段必须完全由 `platform_rules.yaml#short_video.thresholds.segments` 决定——
> - `0` 到 `segments.hook.end` s ⇒ hook（钩子）
> - `segments.core.start` 到 `segments.core.end` s ⇒ core（核心结论，条数 ≤ `core.max_points`）
> - `segments.explain.start` 到 `segments.explain.end` s ⇒ explanation（例证）
> - `segments.cta.start` 到 `segments.cta.end` s ⇒ CTA
>
> Agent 动笔时**按 rules 实际秒数填充下表，不要套用下面的示例秒数**。若 rules 调整了总时长或段落分配，必须跟着改。
>
> 下表仅为"示例格式"——四行一行一大段，**实际行数可增删**，但每行必须落在 rules 的某一段里。

| 时间（依 rules） | 阶段 | 画面 | 口播 | 字幕 |
|---|---|---|---|---|
| 0–`segments.hook.end`s | hook |  |  |  |
| `segments.core.start`–`segments.core.end`s | core |  |  |  |
| `segments.explain.start`–`segments.explain.end`s | explain |  |  |  |
| `segments.cta.start`–`segments.cta.end`s | cta |  |  |  |

## 封面 / 首帧建议

- 版式：
- 主色：
- 上封面的文字：
