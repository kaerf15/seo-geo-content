# seo-geo：一人驱动 Agent 做 SEO+GEO 内容生产、机械化门禁与复盘

一个人通过自然语言对话，让 Agent 完成"事实收集 → AI 认知探针 → 叙事转译 → 多平台内容生产 → 机械化门禁 → 上线后 AI 复测"全流程。

**最终交付只有两样东西**：

- `output/<task>/deliverables/content/*.md`：各选定平台的内容文档
- `output/<task>/deliverables/report.md`：复盘报告（上线前自检 + T+3/14/45/90）

其他一切都是中间产物，藏在 `.workspace/` 里。

> 详细流程、禁令、步骤细则、产物契约全部在 [`.cursor/skills/seo-geo/SKILL.md`](./.cursor/skills/seo-geo/SKILL.md)——Agent 读那一份，人类想了解细节也去读那一份。本 README 只管"怎么启动"和"骨架在哪"。

## 一次性准备（5 分钟）

```bash
pip install -r .cursor/skills/seo-geo/tools/verify/requirements.txt        # 只有 PyYAML
python .cursor/skills/seo-geo/tools/verify/verify.py --self-check           # 验证脚本能跑
```

`--self-check` 能跑出自检报告即环境就绪。

## 启动任务（一句话）

对 Agent 说：

> 按 seo-geo skill 的流程帮我做一个内容任务，主题是 XXX，task_slug 叫 YYY。先按 facts 模板问我。

Agent 会加载 `SKILL.md`，之后它会：

- 在【确认点 A】让你选 Top 3 分发平台 + 指定 1 个首发
- 在【确认点 B】从项目根跑 `python .cursor/skills/seo-geo/tools/verify/verify.py <slug>`，全 PASS 才算交付完成
- 上线后你回来说"该跑 T+3 复测了"，它用工具链自动跑 GEO 引用抽查

> `task_slug` 硬规则：小写字母开头、只允许 `[a-z0-9-]`、3–41 位（正则 `^[a-z][a-z0-9-]{2,40}$`）。

## 架构分层（只看一眼就够）

```
seo-geo/
├── README.md                                       # 你读这个（怎么启动 + 骨架在哪）
├── .cursor/skills/
│   ├── seo-geo/                                    # skill 自包含，整个目录可直接拷贝/分享
│   │   ├── SKILL.md                                # Agent 读这个（完整流程 + 禁令）
│   │   ├── config/                                 # 跨任务共识；宜结合真实场景维护（见下文）
│   │   │   ├── channels.yaml                       # 渠道矩阵（slug / rule_key 桥接 platform_rules）
│   │   │   └── authority.txt                       # 权威域名白名单
│   │   ├── tools/verify/                           # 判定型脚本（非生成型）
│   │   │   ├── verify.py / rules_loader.py / checks/
│   │   │   └── README.md
│   │   └── templates/
│   │       ├── facts.md / brief.md / report.md
│   │       ├── platform_rules.yaml                 # SSOT #1：硬数字
│   │       ├── checklist.yaml                      # SSOT #2：11 条自检元数据
│   │       ├── _probe_schema.md                    # SSOT #3：AI/GEO 探针字段
│   │       └── platforms/
│   │           ├── _narrative_playbook.md          # 9 种叙事原型 + 差异化 3 问
│   │           └── <rule_key>.md                   # landing_page / own_blog / xiaohongshu / ...
│   └── gemini-image-gen/                           # 辅助：配图（可选，要 302.AI Key）
└── output/<task>/                                  # Agent 工作目录（不进 skill）
    ├── .workspace/                                 # facts / brief / verify_report / probe
    └── deliverables/                               # content/*.md + report.md（最终交付）
```

> **路径约定 / 落盘文件名 / 产物契约 / SSOT 细则**全部在 [`SKILL.md §0`](./.cursor/skills/seo-geo/SKILL.md) 和 §5 调用速查表里统一定义，本 README 不再复刻，避免同步疲劳。

## `config/` 维护小抄（低频）

**建议优先这样维护**：动手改 [`.cursor/skills/seo-geo/config/`](./.cursor/skills/seo-geo/config/) 之前，**先对齐真实任务场景**——例如行业与可引用的权威来源、目标区域/语言、实际会发的平台清单、是否有落地页/博客等。`channels.yaml` 与 `authority.txt` 是「团队共识 + 门禁依据」，脱离场景堆条目容易和后续任务、verify 判定脱节；有了一两类典型任务再收敛配置，比先铺大而全的矩阵更稳。改完后可跑 `python .cursor/skills/seo-geo/tools/verify/verify.py --self-check` 确认桥接与规则未断。

| 文件 | 作用 | 改动场景 | Agent 权限 |
|---|---|---|---|
| `config/channels.yaml` | 渠道矩阵；每平台 `slug`（落盘文件名）+ `rule_key`（挂到 platform_rules.yaml） | 新开/放弃平台；无骨架先填 `rule_key: null` | 只读；追加须与用户对齐 |
| `config/authority.txt` | 权威域名白名单，供 `verify.py` checklist #4 判定（会自动合并 `report.md §3` 行业追加） | 新行业加来源；删失效域名 | 只读；行业专属来源请改 report §3，不必碰本文件 |

## 分享 skill

整个 `.cursor/skills/seo-geo/` 目录是**自包含**的：

- 拷贝它到另一个项目的 `.cursor/skills/` 下即可立即使用
- 依赖只有 PyYAML，用 `requirements.txt` 装
- 新项目只需在根目录建一个 `output/` 就开始跑任务

## 可选：图片生成

如需给 landing_page / own_blog 配信息图、对比图、流程图或题图，让 Agent 调用独立 skill `gemini-image-gen`。**不配置也不影响 seo-geo 主流程**。

- 需要 302.AI API Key
- 一次性：`export AI_302AI_API_KEY=...` 写进 `~/.zshrc`
- 触发：对 Agent 说"用 gemini-image-gen 给 X 生成图"

## 设计原则（详情见 SKILL.md §0）

1. **只守两份交付**：`deliverables/content/*.md` + `report.md`，其他全是中间态
2. **判定型脚本 + 叙事层 + 实测探针**：不写"替 Agent 生成内容"的脚本；写内容前先写叙事转译牌；探针必须用工具实测
3. **三份 SSOT + 一张桥接表**：`platform_rules.yaml` / `checklist.yaml` / `_probe_schema.md` 管内容硬约束；`channels.yaml` 的 `slug ↔ rule_key` 是"平台（文件名） ↔ 规则段"桥接。verify.py 的 `--self-check` 会做元校验防止桥断
4. **skill 自包含**：`.cursor/skills/seo-geo/` 整个目录即全部资产，便于跨项目复用
