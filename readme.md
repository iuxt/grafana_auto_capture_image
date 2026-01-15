## 自动截图Grafana


## 准备工作

### chromedriver

### chromium浏览器

版本变化了可以根据这篇文章：  <https://zahui.fan/posts/suwpme/> 找一下对应的元素。

兼容的grafana版本：registry.cn-hangzhou.aliyuncs.com/iuxt/grafana-with-render:11.5.3-ubuntu


## 运行

```bash
docker run --platform linux/amd64 --rm \
    --env-file=./.env \
    -v ./output:/tmp/output \
    -v ./:/code \
    grafana_image_renderer:2025-05-13 /venv/bin/python3 -u main.py gw-service now-30d now
```

