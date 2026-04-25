# seo-geo-content

一个极简内容生产仓库。

它只做两件事：

- 产出可直接发布的内容
- 产出一份发布与后续 SEO / GEO 跟进报告

最终交付只有两类文件：

- `output/<task_slug>/deliverables/content/*.md`
- `output/<task_slug>/deliverables/report.md`

其他内容都属于中间态，默认不面向用户展开。

详细规则在 [SKILL.md](./.trae/skills/seo-geo-content/SKILL.md)。

## 快速开始

一次性安装：

```bash
pip install -r .trae/skills/seo-geo-content/tools/verify/requirements.txt
python3 .trae/skills/seo-geo-content/tools/verify/verify.py --self-check
```

发起任务时，对 Agent 直接说白话即可，例如：

> 用 `seo-geo-content` 做一个内容任务，主题是 XXX，`task_slug` 是 yyy，先按 intake 问我。

## 仓库结构

```text
seo-geo/
├── README.md
├── .trae/skills/seo-geo-content/
│   ├── SKILL.md
│   ├── intake.md
│   ├── report.md
│   ├── content/
│   │   ├── core.md
│   │   └── platforms/
│   ├── rules/
│   │   ├── channels.yaml
│   │   ├── platform_rules.yaml
│   │   ├── eval_rubric.yaml
│   │   ├── checklist.yaml
│   │   ├── authority.txt
│   │   └── authority_aliases.yaml
│   └── tools/
│       ├── admin/update_registry.py
│       └── verify/
└── output/<task_slug>/
    ├── .workspace/
    └── deliverables/
```

## 核心原则

- 主路径只围绕 `intake.md`、`content/*`、`report.md`
- 渠道属于配置，不属于代码逻辑
- 平台能否直接生成，由模板、平台规则、评估规则三类资产共同决定
- `verify.py` 只做底线检查，不负责判断内容是否足够强
- 用户说白话时，优先由 `tools/admin/update_registry.py` 维护渠道和白名单

## 热插拔维护

日常只需要维护数据和资产：

- 调整渠道：改 `rules/channels.yaml`
- 调整白名单：改 `rules/authority.txt`
- 调整权威别名：改 `rules/authority_aliases.yaml`
- 新增可直接生成的平台：补 `content/platforms/<rule_key>.md`、`rules/platform_rules.yaml`、`rules/eval_rubric.yaml`

通常不需要改 Python 代码。

## 可选工具

- `tools/verify/verify.py`：任务底线检查
- `tools/admin/update_registry.py`：白话维护渠道和白名单
- `gemini-image-gen`：可选配图，不影响主流程
