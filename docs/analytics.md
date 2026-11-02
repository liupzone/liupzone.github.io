# 访问统计接入说明

首页默认使用 `localStorage` 做本机回退统计，按自然日去重，并根据浏览器时区显示大致地区。静态 GitHub Pages 无法直接汇总所有访客，因此需要配置一个外部统计接口，才能显示全站数据。

在部署前注入配置即可：

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

## 每日反问人数

首页的“每日反问人数”记录用户在站内搜索中输入问题的匿名人数。同一浏览器在同一自然日只计 1 人；页面默认显示本机统计，不会伪造全站数字。

若配置汇总接口，页面会显示全站匿名人数：

```html
<script>
  window.LIUPZONE_QUESTION_ENDPOINT = 'https://your-domain.example/api/question';
  window.LIUPZONE_QUESTION_SUMMARY_URL = 'https://your-domain.example/api/question/summary';
</script>
```

记录接口接收：

```json
{
  "day": "2026-11-02",
  "at": "2026-11-02T08:00:00.000Z",
  "source": "site-search",
  "query": "用户搜索词"
}
```

汇总接口返回：

```json
{
  "todayQuestions": 12
}
```

服务端应按每日匿名浏览器标识去重，并只保存聚合人数。不要保存 IP、姓名或精确位置。
