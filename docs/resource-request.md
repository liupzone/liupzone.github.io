# 资源代找留言接口

资源页默认把留言保存为访客浏览器中的本机草稿，适用于静态预览。要让博主在不同设备收到留言，可在 `resources.html` 之前注入接口配置：

```html
<script>
  window.LIUPZONE_REQUEST_ENDPOINT = 'https://your-domain.example/api/resource-request';
</script>
```

页面会向该地址发送匿名 `POST` JSON：

```json
{
  "name": "想找什么资源",
  "contact": "可选联系方式",
  "detail": "版本、年份和用途等线索",
  "createdAt": "2026-10-29T12:00:00.000Z",
  "source": "https://example.com/resources.html"
}
```

服务端应限制提交频率，过滤恶意内容，并只保留完成资源代找所需的信息。
