import requests
import json
import re
from datetime import datetime
import os
import time
from renderer_image import GrafanaDashboard
from dotenv import load_dotenv


class GrafanaApi:
    def __init__(self, api_key, uid, date_from, date_to):
        self.api_key = api_key
        self.uid = uid
        self.date_from = date_from
        self.date_to = date_to
        load_dotenv()

    def get_dashboard_json(self):
        """获取仪表板 JSON 数据"""
        response = requests.get(
            os.getenv("GF_URL") + f"/api/dashboards/uid/{self.uid}",
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
    grafana = GrafanaApi(
        uid="gw-service",
        api_key=os.getenv("GF_API_KEY"),
        date_from="2025-03-01T00:00:00.000Z",
        date_to="2025-03-30T00:00:00.000Z"
    )
    
    # 获取并保存仪表板JSON
    dashboard_json = grafana.get_dashboard_json()
    # with open('dashboard.json', 'w') as f:
    #     f.write(json.dumps(dashboard_json))
    
    # 遍历所有面板进行下载
    panels = grafana.extract_panel_info(dashboard_json)
    for panel in panels:
        print(f"Processing panel: {panel}")
        username = os.getenv("GF_USER")
        password = os.getenv("GF_PASSWORD")
        safe_filename = re.sub(r'[\\/*?:"<>|]', '_', panel['title']) + '.png'
        dashboard = GrafanaDashboard(username, password, grafana.uid, grafana.date_from, grafana.date_to, panel['id'], safe_filename)
        dashboard.render_panel()
        # //todo 文件存在就不下载了。
