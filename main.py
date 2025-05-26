import requests
import json
import re
from datetime import datetime
import os
import time
import sys
from renderer_image import GrafanaDashboard
from dotenv import load_dotenv
from get_monitor_data import GetMonitorData
import send_mail

class GrafanaApi:
    def __init__(self, url, api_key, uid, date_from, date_to):
        self.url = url
        self.api_key = api_key
        self.uid = uid
        self.date_from = date_from
        self.date_to = date_to

    def get_dashboard_json(self):
        """获取仪表板 JSON 数据"""
        response = requests.get(
            url = f"{self.url}" + f"/api/dashboards/uid/{self.uid}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

    def extract_panel_info(self, dashboard_json=None):
        """提取面板信息，排除行类型的面板，并正确处理展开和折叠的行"""
        if dashboard_json is None:
            dashboard_json = self.get_dashboard_json()

        panels_info = []
        current_row = None

        def process_panel(panel, parent_row):
            nonlocal current_row
            panel_type = panel.get('type')

            if panel_type == 'row':
                current_row = panel
                if panel.get('collapsed', False):
                    for sub_panel in panel.get('panels', []):
                        process_panel(sub_panel, current_row)
            else:
                if 'id' in panel and 'title' in panel:
                    panels_info.append({
                        'id': panel['id'],
                        'title': panel['title'],
                        'row': parent_row['title'] if parent_row else None
                    })

        if 'dashboard' in dashboard_json and 'panels' in dashboard_json['dashboard']:
            for panel in dashboard_json['dashboard']['panels']:
                process_panel(panel, current_row)

        return panels_info



if __name__ == "__main__":
    load_dotenv()

    grafana = GrafanaApi(
        uid=sys.argv[1],
        api_key=os.getenv("GF_API_KEY"),
        url=os.getenv("GF_URL"),
        # date_from="2025-03-01T00:00:00.000Z",
        date_from=sys.argv[2] if len(sys.argv) > 2 else "now-1d",
        date_to=sys.argv[3] if len(sys.argv) > 3 else "now"
    )
    
    # 初始化浏览器，打开并登录Grafana
    dashboard = GrafanaDashboard(
        url = grafana.url,
        username = os.getenv("GF_USER"), 
        password = os.getenv("GF_PASSWORD"), 
        uid = grafana.uid
        )
    dashboard.init_chromium(debug=os.getenv("CHROME_DEBUG"))

    # 遍历所有面板进行下载
    dashboard_json = grafana.get_dashboard_json()
    panels = grafana.extract_panel_info(dashboard_json)
    for panel in panels:
        print(f"Processing panel: {panel}")
        os.makedirs('/tmp/output/', exist_ok=True)
        safe_filename = '/tmp/output/' + re.sub(r'[\\/*?:"<>|]', '_', panel['title']) + '.png'
        if os.path.exists(safe_filename):
            print(f"File {safe_filename} already exists, skipping...")
            continue
        else:
            dashboard.render_panel(date_from=grafana.date_from, date_to=grafana.date_to, panel_id=panel['id'], safe_filename=safe_filename)
            
            def save_result(title, data):
                print(panel['title'], data, '---------')
                with open('/tmp/' + sys.argv[1] + '-result.txt', 'a') as f:
                    f.write(title + '\t')
                    f.write(str(data) + '\n')
            
            if '节点CPU使用率' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            elif '节点内存使用率' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            elif '节点磁盘使用率' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            elif 'SDK内存占用率' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            elif '重启次数统计' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_table_max_data()
                save_result(panel['title'], data)
            elif 'MySQL连接数百分比' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            elif '每分钟慢查询数量' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            elif 'Kafka消费组延迟' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            elif 'Redis每秒操作数' in panel['title']:
                data = GetMonitorData(dashboard.driver).get_max_data()
                save_result(panel['title'], data)
            else:
                pass


    dashboard.driver.quit()

    # 打包，发邮件
    load_dotenv('.env')
    to_email = os.getenv('MAIL_RECEIVERS')
    from_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 465))
    source_dir = "/tmp/output"
    zip_filename = "/tmp/" + sys.argv[1] +  ".zip"
    with open('/tmp/' + sys.argv[1] + '-result.txt', 'r') as f:
        body = f.read()
    send_mail.zip_files(source_dir, zip_filename)
    send_mail.send_email(zip_filename, to_email, subject='巡检报告', body=body, from_email=from_email, password=password, smtp_server=smtp_server, smtp_port=smtp_port)
    