
from datetime import datetime
import os
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
from grafana_api import GrafanaApi


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

result_file = '/tmp/result.txt'
for panel in panels:
    row_value = panel.get('row', None)
    row_value = '' if row_value is None else str(row_value)
    manufacturer = Utils.get_name(sys.argv[1])
    dashboard.render_panel(date_from=grafana.date_from, date_to=grafana.date_to, panel_id=panel['id'], 
                           row_value=row_value, panel_name=panel['title'], manufacturer=manufacturer, 
                           panel_description=panel.get('description') or '', panel_type=panel['type'])


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
title = Utils.get_name(sys.argv[1]) + ' ' + beijing_time.strftime('%Y-%m-%d') + '巡检报告'
zip_filename = "/tmp/" + Utils.get_name(sys.argv[1]) + '_' + beijing_time.strftime('%Y-%m-%d') +  ".zip"
print(zip_filename)
send_mail.zip_files(source_dir, zip_filename)
send_mail.send_email(zip_filename, to_email, subject=title, body=Utils.get_html_content(filename=result_file, title=title), from_email=from_email, password=password, smtp_server=smtp_server, smtp_port=smtp_port)
