---
name: gemini-image-gen
description: "调用 Gemini 生图模型（通过 302.AI OpenAI 兼容接口）把 Markdown 内容生成可引用配图：信息图/对比图/框架图/流程图/题图。"
---

# Gemini Image Generation via 302.AI

Generate images from Markdown content files with Gemini image generation models through 302.AI's OpenAI-compatible chat relay.

## API Configuration

- **API Key**: 通过环境变量统一注入（不要写进文档或提交到仓库）
  - `AI_302AI_API_KEY`
- **Default Model**: `gemini-3-pro-image-preview`
- **Optional Model**: `gemini-3.1-flash-image-preview`
- **Endpoint**: `https://api.302.ai/v1/chat/completions`
- **Format**: OpenAI-compatible chat API
- **Model Rule**: Keep using `gemini-3-pro-image-preview` by default. Only switch to `gemini-3.1-flash-image-preview` when the user explicitly asks for that model.

## Prompt

本 skill 接受 system prompt 作为唯一“版式/风格/约束”入口。建议由 Agent 生成最终 prompt，再通过参数传给脚本。

- `--system-prompt-text "..."`：直接传入提示词
- `--system-prompt-file "path/to/prompt.md"`：从文件读取提示词（推荐用于可复盘与可协作）

Agent 可按需求自行组织提示词结构（例如：画幅比例、是否允许文字、信息层级、卡片数量、配色风格、禁用项、输出要求等）。

为保证本 skill 可独立运行，仓库内提供了一组基础 prompt 文件（可直接用，也可作为起点再改）：

- `prompts/one_pager_cn.md`
- `prompts/one_pager_en.md`
- `prompts/compare.md`
- `prompts/framework.md`
- `prompts/flow.md`
- `prompts/cover.md`

`--include-images` 使用规则：

- 源内容包含图片引用（本地路径或URL），或你希望输出遵循参考图风格 → 开启 `--include-images`

| 场景 | 提示词来源 | 说明 | 推荐设置 |
|------|-----------|------|----------|
| 信息图 / one pager | （Agent生成） | 适合正文插图与分发 | 建议开启 `--include-images` 发送参考图 |
| 对比图 | （Agent生成） | A/B、旧/新、对/错等对照关系 | 有参考图建议开 `--include-images` |
| 框架图 | （Agent生成） | 体系/模型/结构/模块关系 | 有参考样式建议开 `--include-images` |
| 流程图 | （Agent生成） | SOP、步骤、判断分支 | 必要时开 `--include-images` 对齐参考样式 |
| 题图/封面图 | （Agent生成） | 16:9 题图/头图 | 通常不启用 `--include-images` |

## Workflow

### Step 1: Prepare Content File

这里的用法以“仓库里的 Markdown 文件”为准。

脚本的图片提取（`--include-images`）会解析内容文件里的图片引用，并把图片随请求一起发送给模型。支持：

- 标准 Markdown 图片：`![alt](path/to/image.png)`、`![alt](https://...)`
- 兼容 `![[image.png]]`（可选）

为保证引用图片能被正确读取，优先使用 `--content-file`（而不是 `--content-text`），并把 `--project-root` 当作“项目根目录”来用。

常见方式：

- 直接对某个文件生图：使用 `--content-file "path/to/file.md"`
- 对一段文本生图：使用 `--content-text "..."`（不支持本地图片引用）

注意：如果你使用 `--include-images`，不要删除内容里的图片引用行；脚本需要据此读取图片文件。

### Step 2: Decide Image Type (Prompt)

If user doesn't specify, ask. Heuristics:
- "信息图/one pager/总结图" → 选用 one_pager_cn/en 的 prompt（或让 Agent 编写更严格的 prompt）
- "对比/PK/vs/前后变化/优劣比较" → compare
- "框架/模型/体系/结构图" → framework
- "流程/SOP/步骤/工作流/路径图" → flow
- "题图/封面/头图" → cover
- "画图/生成图" generic → ask expected chart type and ratio

### Step 3: Execute

**Model selection rule:**
- Default: `gemini-3-pro-image-preview`
- If the user explicitly asks for `gemini-3.1-flash-image-preview`, use that exact model
- Do not switch models proactively

示例（对一个 Markdown 文件生图）：

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/generate_image.py" \
  --model "gemini-3-pro-image-preview" \
  --content-file "path/to/content.md" \
  --system-prompt-file "${CLAUDE_SKILL_DIR}/prompts/one_pager_cn.md" \
  --project-root "." \
  --include-images \
  --output-dir "output" \
  --task-dir "your_topic" \
  --output-name "descriptive_name"
```

**Important**: 
- Set `timeout=120000` for Bash calls. Generation typically takes 30-60s.
- Script prints `SUCCESS:<relative_path>` on success.
- 不要把 API Key 写进文档或提交到仓库；用环境变量注入即可。

### Step 4: Present Result

1. Parse `SUCCESS:` line from stdout → get image relative path
2. Read the image with Read tool to verify visually
3. Embed in response: use the returned relative file path
4. If unsatisfied, offer to regenerate with adjusted params

## Parameters

| Param | Options | Default |
|-------|---------|---------|
| `--model` | `gemini-3-pro-image-preview`, `gemini-3.1-flash-image-preview` | `gemini-3-pro-image-preview` |
| `--system-prompt-file` | path | unset |
| `--system-prompt-text` | text | unset |
| `--include-images` | flag | off（有参考图或源内容含图片时建议开启） |
| `--max-images` | 1-14 | 14 |
| `--dry-run` | flag | off |

## Error Handling

- **429 rate limit**: Wait 10s, retry once
- **401 unauthorized**: The 302.AI relay API key is invalid or expired. Ask user to check the 302.AI account
- **400 bad request**: Model name or prompt format invalid. Try with default model `gemini-3-pro-image-preview`
- **No image URL in response**: The Gemini image model response did not include image markdown. Try simplifying content or prompt
- **Download failed**: Generated image URL is unreachable. This is rare; ask user to retry
- **Timeout**: Generation takes 30-60s; always use `timeout=120000`

## Technical Notes

### API Flow
1. Send chat request to the Gemini image model through the 302.AI relay endpoint
2. Receive markdown-formatted response containing image URL (e.g., `![](https://...)`)
3. Extract URL from response
4. Download image and convert to base64
5. Save to output directory
6. Return relative path to saved image

### Response Format
The relay response returns markdown text with an embedded image link:
```markdown
![Generated Image](https://302.ai/images/...)
```

Script extracts the URL and downloads the image to your configured output directory.
