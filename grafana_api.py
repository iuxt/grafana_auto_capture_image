import os
from dotenv import load_dotenv
import requests
import json
import re


class GrafanaApi:
    def __init__(self, url, api_key, uid):
        self.url = url
        self.api_key = api_key
        self.uid = uid

        """获取仪表板 JSON 数据"""
        response = requests.get(
            url = f"{self.url}" + f"/api/dashboards/uid/{self.uid}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        self.dashboard_json = response.json()



    def get_grafana_variables(self):
        """
        从Grafana JSON中提取所有变量
        
        Args:
            dashboard_json: Grafana Dashboard JSON数据
        
        Returns:
            变量字典，键为变量名，值为当前值
        """
        variables = {}
        for template_var in self.dashboard_json.get('dashboard', {}).get('templating', {}).get('list', []):
            var_name = template_var.get('name')
            current_value = template_var.get('current', {}).get('value')
            
            if var_name:
                # 处理多选值
                if isinstance(current_value, list):
                    variables[var_name] = '|'.join([str(v) for v in current_value])
                else:
                    variables[var_name] = str(current_value)
        
        return variables



    def replace_variables_in_query(self, query):
        """
        从Grafana JSON中提取并替换变量
        
        Args:
            dashboard_json: Grafana Dashboard JSON数据
            variable_values: 可选的变量值字典，用于覆盖当前值
        
        Returns:
            替换后的查询列表
        """
        variables = self.get_grafana_variables()

        """替换查询中的变量占位符"""
        # Grafana变量格式: $variable 或 ${variable:format}
        pattern = r'\$(\w+)(?::[^}]*)?|\$\{(\w+)(?::[^}]*)?\}'
        
        def replace_match(match):
            var_name = match.group(1) or match.group(2)
            if var_name in variables:
                return variables[var_name]
            return match.group(0)  # 未找到变量，保持原样
        
        return re.sub(pattern, replace_match, query)






    def extract_panel_info(self):
        """提取面板信息，排除行类型的面板，并正确处理展开和折叠的行
        return: [{'id': 23763571997, 'title': '域名状态明细', 'description': '', 'type': 'table', 'row': 'DK数字钥匙域名监控'}, {'id': 68, 'title': 'HTTP总访问量', 'description': None, 'type': 'stat', 'row': 'DK数字钥匙域名监控'}]
        """
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
                        'description': panel.get('description'),
                        'type': panel.get('type'),
                        'expr': [] if 'targets' not in panel else [self.replace_variables_in_query(target['expr']) for target in panel['targets']],
                        'row': parent_row['title'] if parent_row else None
                    })

        if 'dashboard' in self.dashboard_json and 'panels' in self.dashboard_json['dashboard']:
            for panel in self.dashboard_json['dashboard']['panels']:
                process_panel(panel, current_row)

        return panels_info



if __name__ == '__main__':
    load_dotenv()
    grafana_api = GrafanaApi(
        url = os.getenv("GF_URL"),
        api_key = os.getenv("GF_API_KEY"),
        uid = os.getenv("GF_UID")
    )
    
    extract_panel_info = grafana_api.extract_panel_info()
    print(extract_panel_info)