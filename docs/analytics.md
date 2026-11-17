# 访问统计接入说明

网站使用 GoatCounter 统计所有页面的匿名访问，首页读取当天全站访问数。GoatCounter 失败时，首页会回退到 `localStorage` 的本机统计，但回退值不代表全站数据。

当前站点配置为：

```html
<script data-goatcounter="https://liupzone.goatcounter.com/count"
        async src="https://gc.zgo.at/count.js"></script>
```

如需更换统计站点，修改 `assets/site-analytics.js` 中的 `endpoint` 和 `site`，并同步更新页面生成器。

旧版自建接口配置示例：

```html
<script>
  window.LIUPZONE_ANALYTICS_ENDPOINT = 'https://your-domain.example/api/visit';
  window.LIUPZONE_ANALYTICS_SUMMARY_URL = 'https://your-domain.example/api/visit/summary';
</script>
```

记录接口接收 `POST` JSON：

```json
{
  "visitorId": "anonymous-browser-id",
  "day": "2026-10-29",
  "region": "中国大陆",
  "timezone": "Asia/Shanghai",
  "language": "zh-CN",
  "device": "mobile",
  "referrer": "direct",
  "path": "/"
}
```

汇总接口返回：

```json
{
  "todayVisits": 128,
  "regions": {
    "中国大陆": 92,
    "中国香港": 12,
    "日本": 8
  }
}
```

建议服务端只保留聚合后的每日计数，不保存 IP、姓名或精确位置，并在隐私政策中说明统计用途。

## 每日访问人数

首页的“每日访问人数”显示 GoatCounter 返回的当天全站访客数；同一访客在 GoatCounter 的会话规则内不会被重复计为新访客。接口暂时不可用时，页面显示本机回退值，并保持“本机统计”标记。

若配置汇总接口，页面会显示全站匿名人数：

```html
<script>
  window.LIUPZONE_ANALYTICS_ENDPOINT = 'https://your-domain.example/api/visit';
  window.LIUPZONE_ANALYTICS_SUMMARY_URL = 'https://your-domain.example/api/visit/summary';
</script>
```

记录接口接收：

```json
{
  "day": "2026-11-02",
  "at": "2026-11-02T08:00:00.000Z",
  "path": "/"
}
```

汇总接口返回：

```json
{
  "todayVisits": 12
}
```

服务端应按每日匿名浏览器标识去重，并只保存聚合人数。不要保存 IP、姓名或精确位置。
