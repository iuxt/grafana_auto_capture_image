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
from datetime import datetime
from zoneinfo import ZoneInfo



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


class Utils:
    @staticmethod
    def get_title(dashboard_id, datetime):
        """
        获取邮件标题
        """
        date_str = datetime.strftime('%Y年%m月')
        if dashboard_id == 'w-service':
            return '达布溜运维巡检报告 - ' + date_str
        elif dashboard_id == 'c-service':
            return '吃运维巡检报告 - ' + date_str
        else:
            return '巡检报告' + date_str
        

    @staticmethod
    def get_html_content(filename,title):
        """
        从结果文件中生成HTML内容
        """
        with open(filename, 'r') as f:
            body = f.read()
            tmp_dict = {}
            list = body.strip().split('\n')
            for i in list:
                key, value = i.split('\t')
                tmp_dict[key] = value
        # 构建HTML内容
        html_content = f"""<!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ background-color: #2c3e50; color: white; padding: 15px; border-radius: 5px; }}
                .timestamp {{ font-size: 0.9em; color: #666; text-align: right; }}
                
                /* 表格样式 */
                .monitor-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                .monitor-table th, .monitor-table td {{
                    padding: 10px 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                .monitor-table th {{
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-weight: 600;
                }}
                
                /* 进度条样式 */
                .progress-container {{
                    background-color: #f3f3f3;
                    border-radius: 3px;
                    height: 20px;
                    width: 100%;
                    margin-top: 2px;
                }}
                .progress-bar {{
                    border-radius: 3px;
                    height: 100%;
                    color: white;
                    text-align: center;
                    line-height: 20px;
                    font-size: 0.9em;
                }}
                .low-risk {{ background-color: #28a745; }}    /* 绿色 */
                .medium-risk {{ background-color: #ffc107; }} /* 黄色 */
                .high-risk {{ background-color: #dc3545; }}   /* 红色 */
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{title}</h2>
                    <p class="timestamp">生成时间: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <table class="monitor-table">
                    <thead>
                        <tr>
                            <th>监控指标</th>
                            <th>最大值</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 格式化数据并添加到HTML表格
        for key, value in tmp_dict.items():
            # 检查是否为百分比值
            is_percentage = False
            value_str = str(value)
            if isinstance(value, (int, float)):
                value_str = f"{value:.2f}"
            if value_str.endswith('%'):
                is_percentage = True
                percent = float(value_str.replace('%', ''))
                # 确定进度条颜色
                if percent < 50:
                    risk_class = "low-risk"
                elif percent < 80:
                    risk_class = "medium-risk"
                else:
                    risk_class = "high-risk"
            
            # 添加表格行
            html_content += f"                <tr>\n"
            html_content += f"                    <td>{key}</td>\n"
            html_content += f"                    <td>{value_str}</td>\n"
            html_content += f"                    <td>\n"
            
            if is_percentage:
                html_content += f"                        <div class=\"progress-container\">\n"
                html_content += f"                            <div class=\"progress-bar {risk_class}\" style=\"width: {percent}%\">{value_str}</div>\n"
                html_content += f"                        </div>\n"
            else:
                html_content += f"                        -"
            
            html_content += f"                    </td>\n"
            html_content += f"                </tr>\n"
        
        # 完成HTML内容
        html_content += f"""            </tbody>
                </table>
            </div>
        </body>
        </html>
        """
        return html_content


    def insert_result_to_file(driver, panel, filename):
        """将结果写入结果文件"""
        def save_result(title, data):
            print("写入到结果文件---------", title, data, '---------')
            with open(filename, 'a') as f:
                f.write(title + '\t')
                f.write(str(data) + '\n')
    
        if 'CPU使用率' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result(panel['title'], data)
        elif '内存使用率' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result(panel['title'], data)
        elif '磁盘使用率' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result(panel['title'], data)
        elif 'SDK内存占用' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result('SDK服务POD内存占用量', data + 'GB')
        elif '重启次数统计' in panel['title']:
            data = GetMonitorData(driver).get_table_max_data()
            save_result(panel['title'], str(data[1]))
        elif 'MySQL连接数百分比' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result(panel['title'], data)  
        elif '表占用空间概览Top10' in panel['title']:
            data, unit = GetMonitorData(driver).get_table_max_data_and_unit()
            save_result(panel['title'], str(data) + unit)
        elif '每分钟慢查询数量' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result(panel['title'], data)
        elif 'Kafka消费组延迟' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result(panel['title'], data)
        elif '每秒操作数' in panel['title']:
            data = GetMonitorData(driver).get_max_data()
            save_result(panel['title'], data)
        else:
            pass





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
        print(f"Processing panel: {panel}")
        row_value = panel.get('row', None)
        row_value = '' if row_value is None else str(row_value)
        os.makedirs('/tmp/output/' + row_value + '/', exist_ok=True)
        safe_filename = '/tmp/output/' + row_value + '/' + re.sub(r'[\\/*?:"<>|]', '_', panel['title']) + '.png'
        if os.path.exists(safe_filename):
            print(f"File {safe_filename} already exists, skipping...")
            continue
        else:
            # 渲染面板并保存为图片
            dashboard.render_panel(date_from=grafana.date_from, date_to=grafana.date_to, panel_id=panel['id'], safe_filename=safe_filename)
            # 将结果写入文件
            Utils.insert_result_to_file(driver=dashboard.driver, panel=panel, filename=result_file)


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
    send_mail.send_email(zip_filename, to_email, subject=title, body=Utils.get_html_content(filename=result_file, title=title), from_email=from_email, password=password, smtp_server=smtp_server, smtp_port=smtp_port)
