from dotenv import load_dotenv
import grafana_api
import prometheus_data
import renderer_image
import utils
import os
import json


load_dotenv()

url = os.getenv("GF_URL")
api_key = os.getenv("GF_API_KEY")
date_from = "2026-01-02T00:00:00.000Z"
date_to = "2026-01-03T00:00:00.000Z"
username = os.getenv("GF_USER")
password = os.getenv("GF_PASSWORD")



# 遍历面板信息，自动获取全部数据
# grafana_api = grafana_api.GrafanaApi(url, api_key, uid)
# extract_panel_info = grafana_api.extract_panel_info()
# print(extract_panel_info)
# for panel in extract_panel_info:
#     for expr in panel['expr']:
#         print(expr)
#         # prometheus 查询这个语句
#         print(utils.convert_time_format(date_from), utils.convert_time_format(date_to))
#         data = prometheus_data.query_prometheus(expr, utils.convert_time_format(date_from), utils.convert_time_format(date_to))
#         max_info = prometheus_data.get_max_value_with_labels(data)
#         if max_info['max_value'] is not None:
#             print(max_info)
#             print(f"最大值: {max_info['max_value_formatted']}")
#             print(f"最大值出现时间: {max_info['timestamp_formatted']}")
#     chrome_obj.render_panel(date_from=date_from, date_to=date_to, panel_id=panel['id'], panel_name=panel['title'])


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
        print(expr)
        # prometheus 查询这个语句
        data = prometheus_data.query_prometheus(expr, utils.convert_time_format(date_from), utils.convert_time_format(date_to))
        max_info = prometheus_data.get_max_value_with_labels(data)
        print(f"面板{panel_name}的最大值信息:", max_info)
        if max_info['max_value'] is not None:
            print(max_info)
            print(f"最大值: {max_info['max_value_formatted']}")
            print(f"最大值出现时间: {max_info['timestamp_formatted']}")
