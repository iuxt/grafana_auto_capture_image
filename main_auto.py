from dotenv import load_dotenv
import grafana_api
import prometheus_data
import renderer_image
import utils
import os
import json
import send_mail, tempfile


load_dotenv()
url = os.getenv("GF_URL")
api_key = os.getenv("GF_API_KEY")
date_from = str(utils.convert_time_format(os.getenv("DATE_FROM")))
date_to = str(utils.convert_time_format(os.getenv("DATE_TO")))
username = os.getenv("GF_USER")
password = os.getenv("GF_PASSWORD")
uid = os.getenv("UID")


# 打开浏览器
chrome_obj = renderer_image.GrafanaDashboard(url, username, password, uid )
chrome_obj.init_chromium(debug=os.getenv("CHROME_DEBUG"))

# 遍历面板信息，自动获取全部数据
grafana_obj = grafana_api.GrafanaApi(url, api_key, uid)
extract_panel_info = grafana_obj.extract_panel_info()
print(extract_panel_info)
for panel in extract_panel_info:
    for expr in panel['expr']:
        print(expr)
        # prometheus 查询这个语句
        print(utils.convert_to_prometheus_format(date_from), utils.convert_to_prometheus_format(date_to))
        data = prometheus_data.query_prometheus(expr, utils.convert_to_prometheus_format(date_from), utils.convert_to_prometheus_format(date_to))

        max_info = prometheus_data.get_max_value_with_labels(data)
        if max_info['max_value'] is not None:
            print(max_info)

            with open(f"1.log", "a", encoding="utf-8") as f:
                max_info['panel_title'] = panel['title']
                json.dump(max_info, f, indent=4, ensure_ascii=False)

            print(f"最大值: {max_info['max_value']}")
            print(f"最大值出现时间: {max_info['timestamp_formatted']}")
    chrome_obj.render_panel(date_from=date_from, date_to=date_to, panel_id=panel['id'], panel_name=panel['title'])

# 关闭浏览器
chrome_obj.driver.quit()

# 发送邮件
source_dir = "./screenshots"
temp_dir = tempfile.mkdtemp()
zip_filename = os.path.join(temp_dir, "output.zip")
print(f"Temporary zip file will be created at: {zip_filename}")

# 加载环境变量
load_dotenv('.env')
to_email = os.getenv('MAIL_RECEIVERS')
from_email = os.getenv('EMAIL_USER')
password = os.getenv('EMAIL_PASSWORD')
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT', 465))

# 打包文件
send_mail.zip_files(source_dir, zip_filename)

body = send_mail.get_email_content()

# 发送邮件
send_mail.send_email(zip_filename=zip_filename, to_email=to_email, subject='巡检报告', body=body, 
            from_email=from_email, password=password, smtp_server=smtp_server, smtp_port=smtp_port)
