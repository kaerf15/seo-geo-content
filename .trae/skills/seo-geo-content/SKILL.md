---
name: seo-geo-content
description: 面向 SEO / GEO 场景的极简内容生产 skill。对外只交付内容与报告；对内只保留内容、规则与底线校验。
---

# SKILL: SEO + GEO Content Skill

## 目标

这个 skill 只做两件事：

- 产出可直接发布的内容
- 产出一份可执行的发布与跟进报告

默认不要生成中间文件，不要堆流程说明，不要把复杂思考落盘给用户。

## 核心文件

- `intake.md`
- `report.md`
- `content/core.md`
- `content/platforms/*.md`
- `rules/channels.yaml`

## 可选工具

- `tools/verify/verify.py`
- `tools/admin/update_registry.py`

## 工作流

### Step 1：收集最少必要信息

先读 `intake.md`。

只收这些：

- 目标
- 市场 / 语言
- 目标受众
- 产品 / 服务 / 核心卖点
- 可公开证据
- CTA 与禁区

缺少 `目标`、`目标受众`、`可公开证据` 时必须追问。

把整理结果写入：`output/<task_slug>/.workspace/facts.md`

### Step 2：决定内容组合

1. 按目标先定核心资产类型：
   - 偏获客 / 询盘 / 承接：优先 `landing_page`
   - 偏 SEO / 教育 / 对比 / 方法论：优先 `own_blog`
2. 再读 `rules/channels.yaml`，选 1 到 2 个最适合的分发平台
3. `rule_key: null` 的平台只进报告建议，不默认生成
4. 能否直接生成由 3 类资产自动决定：
   - `content/platforms/*.md`
   - `rules/platform_rules.yaml`
   - `rules/eval_rubric.yaml`
5. 若用户提出新增平台，先用 `tools/admin/update_registry.py` 更新渠道；只有要直接生成时，才补上面 3 类资产

### Step 3：生成内容

每篇内容都这样做：

1. 读 `content/core.md`
2. 读对应平台卡 `content/platforms/<rule_key>.md`
3. 读 `rules/platform_rules.yaml`
4. 先出标题候选
5. 再出开头候选
6. 再写正文
7. 落盘到 `output/<task_slug>/deliverables/content/<slug>.md`

### Step 4：自评与校验

1. 用 `rules/eval_rubric.yaml` 自评
2. 自评不过就先改稿
3. 需要时再运行 `tools/verify/verify.py`

`verify` 只负责底线，不代表内容已经足够强。
如果用户提出新增行业权威来源或补白名单，优先调用 `tools/admin/update_registry.py`。

### Step 5：写报告

先读 `report.md`。

写入：`output/<task_slug>/deliverables/report.md`

报告必须包含：

- 本次目标与受众
- 推荐平台 Top 3
- 首发 / 次发建议
- 已交付内容清单
- 标题 / 摘要 / CTA 建议
- T+7 / T+30 / T+60 的 SEO / GEO 跟进计划
- 风险与待补证据

## 输出契约

```text
output/<task_slug>/
├── .workspace/
│   ├── facts.md
│   └── verify_report.*      # 按需出现
└── deliverables/
    ├── content/
    │   ├── landing_page.md / own_blog.md
    │   ├── xiaohongshu.md / zhihu.md / linkedin.md / ...
    │   └── ...
    └── report.md
```

默认不生成：

- 额外模板副本
- 中间思考文件
- 面向用户的流程说明

## 红线

1. 不得编造数字、案例、认证、媒体引用或客户评价
2. 不得在交付目录放中间产物
3. 不得默认全平台铺内容
4. 不得跳过标题候选和开头候选直接定稿
5. 不得把不同平台写成同一篇文章换壳
6. 不得把 `verify PASS` 当作写得好
7. 不得把“让用户手动维护平台或白名单”当作默认处理方式
