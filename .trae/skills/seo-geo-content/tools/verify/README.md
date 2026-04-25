# tools/verify

内部质检脚本，只负责底线检查，不负责判断内容是否足够强。

## 用法

所有命令都从项目根执行。

### 一次性安装依赖

```bash
pip install -r .trae/skills/seo-geo-content/tools/verify/requirements.txt
```

依赖只有 PyYAML。

### 对任务跑自检

```bash
python .trae/skills/seo-geo-content/tools/verify/verify.py <task_slug>
```

- 读：`output/<task>/deliverables/content/*.md` + `deliverables/report.md` + `.workspace/facts.md`
- 写：
  - `output/<task>/.workspace/verify_report.json`（结构化，机器读）
  - `output/<task>/.workspace/verify_report.md`（人类读，可按需贴进报告或工作记录）
- 退出码：0 = 通过；2 = 存在 FAIL；其他非 0 = 运行错误

### 脚本本身自检（不依赖任务）

```bash
python .trae/skills/seo-geo-content/tools/verify/verify.py --self-check
```

开发或改规则时用。

## 建议使用场景

- `landing_page` 或 `own_blog`
- 内容里有较多数字、引用、FAQ、Schema
- 用户明确要求严格检查

## 覆盖范围

checklist 的 SSOT 是 [`../../rules/checklist.yaml`](../../rules/checklist.yaml)。

自动化程度：

- `auto`：直接 PASS / FAIL
- `semi`：启发式检查，必要时 SKIP
- `manual`：脚本不处理
