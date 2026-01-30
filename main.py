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



# 从配置中读取，截图
with open('gw_panel_config.json', 'r') as f:
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
with open('gw_panel_config.json', 'r') as f:
    panel_config = json.load(f)

    uid = panel_config['uid']
    name = panel_config['name']

    # 厂商里的每个面板
    for panel in panel_config['panels']:
        panel_id = panel['id']
        panel_name = panel['title']
        expr = panel['expr']
        # prometheus 查询这个语句
        data = prometheus_data.query_prometheus(expr, utils.convert_to_prometheus_format(date_from), utils.convert_to_prometheus_format(date_to))
        get_value = panel.get('get_value', 'max')
        if get_value == 'max':
            max_info = prometheus_data.get_max_value_with_labels(data)
            print(f"面板{panel_name}的最大值信息:", max_info)
            if max_info['max_value'] is not None:
                print(max_info)
                print(f"最大值: {max_info['max_value']}")
                print(f"最大值出现时间: {max_info['timestamp_formatted']}")
                max_info = prometheus_data.get_max_value_with_labels(data)
                print(f"面板{panel_name}的最大值信息:", max_info)
        elif get_value == 'min':
            min_info = prometheus_data.get_min_value_with_labels(data)
            print(f"面板{panel_name}的最小值信息:", min_info)
        elif get_value == 'avg':
            avg_info = prometheus_data.get_avg_value_with_labels(data)
            print(f"面板{panel_name}的平均值信息:", avg_info)


# 发邮件
send_mail.send_email_now(name=name)