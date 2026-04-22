# tools/verify —— seo-geo 上线前自检

这是 seo-geo skill 的**门禁脚本集合**，位于 `.cursor/skills/seo-geo/tools/verify/`。它把 `SKILL.md §确认点 B` 的 11 条 checklist 里的 9 条自动化掉（剩余 2 条因为涉及语义/意图仍需 Agent 肉眼判断）。

> 原 SKILL.md 禁令第 7 条说"主流程不写/运行脚本"。本 tools/ 目录是它的**唯一例外**，且只做"判定"不做"生成"——生成仍由 Agent 按模板手写。

## 用法

所有命令一律从**项目根**（包含 `.cursor/` 的目录）执行。脚本内部会自己算 skill 根与项目根，不需要传参。

### 一次性安装依赖

```bash
pip install -r .cursor/skills/seo-geo/tools/verify/requirements.txt
```

依赖只有 PyYAML，没别的；轻到可以直接在 Agent 会话里用 Shell 工具装。

### 对任务跑自检

```bash
python .cursor/skills/seo-geo/tools/verify/verify.py <task_slug>
```

- 读：`output/<task>/deliverables/content/*.md` + `deliverables/report.md` + `.workspace/facts.md`
- 写：
  - `output/<task>/.workspace/verify_report.json`（结构化，机器读）
  - `output/<task>/.workspace/verify_report.md`（人类读 + 给 `report.md §4.1` 直接 include）
- 退出码：0 = 全 PASS 或只有 SKIP；2 = 存在 FAIL；非 0/2 = 运行错误

### 脚本本身自检（不依赖任务）

```bash
python .cursor/skills/seo-geo/tools/verify/verify.py --self-check
```

开发/升级脚本时用，快速验证规则解析与各 check 模块能跑通。

## 覆盖的 checklist 条目

checklist 的 SSOT 是 [`../../templates/checklist.yaml`](../../templates/checklist.yaml)——本脚本每一个 check 模块都对应那里的某个 `id` + `verifier` 字段。改 checklist 去改那个 yaml，不在本文件复述表格。

> 自动化程度映射：`automation: auto` → 全自动 PASS/FAIL；`automation: semi` → 启发式 + SKIP（未知项交给 Agent 人工判断）；`automation: manual` → 脚本不处理。

## Agent 的用法约定

SKILL.md §2 的确认点 B：

1. Agent 跑 `python tools/verify/verify.py <slug>`
2. 产出两份：`.workspace/verify_report.json`（机器读）+ `.workspace/verify_report.md`（人类读）
3. `report.md §4.1` **直接 include** `verify_report.md` 的内容，不再手工搬表
4. 对 `status=SKIP` 的条目，Agent 在 `report.md §4.S` 用一行文字说明人工判定理由
5. 存在 `FAIL` 时 `gate_pass=false`，**不得**宣告交付完成；回 Step 3 改稿重跑

## 判定口径的设计取舍

1. **字数统计用 "中文字符数 / 英文词数 取较大值"**：自适应中英混合文档，避免把英文稿用汉字数硬判 FAIL。
2. **FAQ 单条字数按 effective length**：与字数统计一致。
3. **数字回溯用字符串包含**：会有误报（段落里的`5 个步骤`也会被判为需回溯），宁可让 Agent 复核也不让事实飞掉。
4. **must_include 未知 id 一律 SKIP**：避免启发式误判把合规内容打成 FAIL。
