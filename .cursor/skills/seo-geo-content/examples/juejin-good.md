> **示例说明**（仅供 skill 校准语气；真实 `output/*.md` 只含可直发正文）  
> 好稿特征：结论 30 秒可见、代码可复制、坑点来自真实失败、标题即搜索问题。  
> 坏稿特征：产品宣传腔、代码缺版本、坑点写「暂无」、无参考来源。

---

# 飞书妙记 Webhook 接入：把会议待办自动推到飞书任务

> 帮已在用飞书妙记的小团队，把「会后待办同步」从手动复制改成 Webhook 自动化。

## 先给结论

- **场景**：妙记开完会，待办要进飞书任务 / 多维表格，不想每次复制粘贴
- **推荐**：妙记导出 JSON + 自建 Webhook 解析 + 飞书开放平台任务 API
- **不适用**：未开通妙记 API 权限；待办格式不固定、每次字段都不同

## 环境 / 前置

- 飞书企业版，妙记 + 开放平台应用（`im:message`、`task:task` 等 scope）
- Node.js 18+ 或任意能跑 HTTP 的服务
- 公网 HTTPS 回调地址（内网调试可用 ngrok）

## 做法：Webhook 接收妙记回调

妙记会议结束后会向你的 URL POST 事件体。最小可用 handler：

```javascript
// webhook.js — Node 18+
import express from "express";

const app = express();
app.use(express.json());

app.post("/feishu/minutes", async (req, res) => {
  const { event } = req.body;
  if (event?.type !== "minutes.transcript_ready") {
    return res.sendStatus(200);
  }

  const actionItems = event.action_items ?? [];
  for (const item of actionItems) {
    await createFeishuTask({
      title: item.content,
      due: item.due_time,
      assignee: item.owner_id,
    });
  }
  res.sendStatus(200);
});

app.listen(3000);
```

`createFeishuTask` 调用 [飞书任务创建 API](https://open.feishu.cn/document/)，需先用 tenant_access_token。

## 坑点与边界

1. **重复推送** — 妙记可能重试 Webhook；用 `event_id` 做幂等，避免重复建任务
2. **owner_id 为空** — 说话人分离不准时 assignee 缺失；降级为「未分配」任务而非丢弃
3. **Token 过期** — tenant_token 约 2 小时；生产环境要缓存 + 自动刷新
4. **字段映射** — 妙记 `action_items` 结构随版本变；上线前用真实会议 JSON 测一遍

## 参考来源

- [飞书开放平台 — 事件订阅](https://open.feishu.cn/document/)
- [飞书妙记 — 产品文档](https://www.feishu.cn/product/minutes)（API 字段以当前版本为准）
