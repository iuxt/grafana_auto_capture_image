import requests
import json
import re
from datetime import datetime
import os
import time
import sys
from renderer_image import GrafanaDashboard
from dotenv import load_dotenv
import send_mail
from datetime import datetime
from zoneinfo import ZoneInfo
from monitor_data.legend_table import LegendTable
from monitor_data.table import Table
from monitor_data.save_data import SaveData
from utils import Utils


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
    load_dotenv('.env')

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
    result_file = '/tmp/' + sys.argv[1] + '-result.txt'
    for panel in panels:
        row_value = panel.get('row', None)
        row_value = '' if row_value is None else str(row_value)
        manufacturer = Utils.get_name(sys.argv[1])
        dashboard.render_panel(date_from=grafana.date_from, date_to=grafana.date_to, panel_id=panel['id'], row_value=row_value, panel_name=panel['title'], manufacturer=manufacturer)


    dashboard.driver.quit()


    # 打包，发邮件
    to_email = os.getenv('MAIL_RECEIVERS')
    from_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 465))
    source_dir = "/tmp/output"
    
    # 获取当前 UTC 时间
    utc_now = datetime.now(ZoneInfo("UTC"))
    # 将 UTC 时间转换为北京时间
    beijing_time = utc_now.astimezone(ZoneInfo("Asia/Shanghai"))
    
    zip_filename = "/tmp/" + beijing_time.strftime('%Y-%m-%d') + '_' + sys.argv[1] +  ".zip"
    title = Utils.get_title(sys.argv[1], beijing_time)
    send_mail.zip_files(source_dir, zip_filename)
    send_mail.send_email(zip_filename, to_email, subject=title, body=Utils.get_html_content(filename=result_file, title=title, time=beijing_time.strftime('%Y-%m-%d %H:%M:%S')), from_email=from_email, password=password, smtp_server=smtp_server, smtp_port=smtp_port)
