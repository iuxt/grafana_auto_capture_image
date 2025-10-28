## 自动截图Grafana

![](/images/run.gif)


## 准备工作

### chromedriver

### chromium浏览器

版本变化了可以根据这篇文章：  <https://zahui.fan/posts/suwpme/> 找一下对应的元素。

兼容的grafana版本：registry.cn-hangzhou.aliyuncs.com/iuxt/grafana-with-render:11.5.3-ubuntu

### 注意

取数据需要是table类型
legend 类型的数据不要有 last *

## 运行

```bash
docker run --platform linux/amd64 --rm \
    --env-file=./.env \
    -v ./output:/tmp/output \
    -v ./:/code \
    grafana_image_renderer:2025-05-13 /venv/bin/python3 -u main.py gw-service now-30d now
```


面板增加注释
默认截图，如果指定了 
```bash
# 默认全部截图，跳过截图
screenshot: false

# 解析并保存数据
save_data: true
```