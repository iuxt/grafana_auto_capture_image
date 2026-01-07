from dotenv import load_dotenv
import grafana_api
import prometheus_data
import renderer_image
import utils
import os


load_dotenv()

url = os.getenv("GF_URL")
api_key = os.getenv("GF_API_KEY")
uid = 'df9c7ijyb55vke'
date_from = "2025-12-02T00:00:00.000Z"
date_to = "2026-01-03T00:00:00.000Z"
username = os.getenv("GF_USER")
password = os.getenv("GF_PASSWORD")


grafana_api = grafana_api.GrafanaApi(url, api_key, uid)

extract_panel_info = grafana_api.extract_panel_info()
print(extract_panel_info)



# 截图操作
dashboard = renderer_image.GrafanaDashboard(url, username, password, uid )
dashboard.init_chromium(debug=os.getenv("CHROME_DEBUG"))

# 遍历面板信息
for panel in extract_panel_info:
    for expr in panel['expr']:
        print(expr)
        # prometheus 查询这个语句
        pass
    dashboard.render_panel(date_from=date_from, date_to=date_to, panel_id=panel['id'], panel_name=panel['title'])

dashboard.driver.quit()