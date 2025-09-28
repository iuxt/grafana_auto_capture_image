import os
import requests
import json
import re


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
        """提取面板信息，排除行类型的面板，并正确处理展开和折叠的行
        return: [{'id': 23763571997, 'title': '域名状态明细', 'description': '', 'type': 'table', 'row': 'DK数字钥匙域名监控'}, {'id': 68, 'title': 'HTTP总访问量', 'description': None, 'type': 'stat', 'row': 'DK数字钥匙域名监控'}]
        """
        if dashboard_json is None:
            dashboard_json = self.get_dashboard_json()
        os.makedirs('/tmp', exist_ok=True)
        json.dump(dashboard_json, open('/tmp/dashboard.json', 'w', encoding='utf-8'), indent=2)
        panels_info = []
        current_row = None

        def process_panel(panel, parent_row):
            nonlocal current_row
            print('=============================', panel.get('description'))
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
                        'description': panel.get('description'),
                        'type': panel.get('type'),
                        'row': parent_row['title'] if parent_row else None
                    })

        if 'dashboard' in dashboard_json and 'panels' in dashboard_json['dashboard']:
            for panel in dashboard_json['dashboard']['panels']:
                process_panel(panel, current_row)

        return panels_info

