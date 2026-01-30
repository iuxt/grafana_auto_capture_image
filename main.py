from dotenv import load_dotenv
import prometheus_data
import renderer_image
import utils
import os
import json
import tempfile
import send_mail


load_dotenv()

url = os.getenv("GF_URL")
api_key = os.getenv("GF_API_KEY")
date_from = utils.convert_time_format(os.getenv("DATE_FROM"))
date_to = utils.convert_time_format(os.getenv("DATE_TO"))
username = os.getenv("GF_USER")
password = os.getenv("GF_PASSWORD")
grafana_config = "grafana_config/config.json"


# 从配置中读取，截图
with open(grafana_config, 'r') as f:
    panel_config = json.load(f)

    uid = panel_config['uid']
    name = panel_config['name']

    # 打开浏览器
    chrome_obj = renderer_image.GrafanaDashboard(url, username, password, uid )
    chrome_obj.init_chromium(debug=os.getenv("CHROME_DEBUG"))

    # 厂商里的每个面板
    for panel in panel_config['panels']:
        panel_id = panel['id']
        panel_name = panel['title']
        chrome_obj.render_panel(date_from=date_from, date_to=date_to, panel_id=panel_id, panel_name=panel_name)
    # 关闭浏览器
    chrome_obj.driver.quit()


# 从配置中读取，取监控数据
with open(grafana_config, 'r') as f:
    panel_config = json.load(f)

    uid = panel_config['uid']
    name = panel_config['name']
    all_data = []

    # 厂商里的每个面板
    for panel in panel_config['panels']:
        panel_id = panel['id']
        panel_name = panel['title']
        expr = panel['expr']
        # prometheus 查询这个语句
        data = prometheus_data.query_prometheus(expr, utils.convert_to_prometheus_format(date_from), utils.convert_to_prometheus_format(date_to))
        get_value = panel.get('get_value', 'max')
        if get_value == 'max':
            monitor_value = prometheus_data.get_max_value_with_labels(data)
        elif get_value == 'min':
            monitor_value = prometheus_data.get_min_value_with_labels(data)
        elif get_value == 'avg':
            monitor_value = prometheus_data.get_avg_value_with_labels(data)
        else:
            monitor_value = None
        
        if monitor_value is not None:
            monitor_value['panel_name'] = panel_name
            all_data.append(monitor_value)

    # 一次性写入所有数据到文件，移出循环
    with open(f'monitor_data.json', 'w', encoding="utf-8") as mf:
        json.dump(all_data, mf, indent=4, ensure_ascii=False)


# 发邮件
send_mail.send_email_now(name=name)