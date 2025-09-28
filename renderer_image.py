from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
import re
import os
import time
from monitor_data.legend_table import LegendTable
from monitor_data.table import Table
from monitor_data.save_data import SaveData
import ast


class GrafanaDashboard:
    def __init__(self, url, username, password, uid):
        self.url = url
        self.username = username
        self.password = password
        self.uid = uid

    def init_chromium(self, debug):
        # 配置Chrome浏览器选项（无界面浏览器）
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.binary_location = ""

        if debug == "False":
            print("debug: false")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
        else:
            print("debug: true")


        # 指定 ChromeDriver 的路径，就不会自动更新了
        chrome_driver_path = os.getenv("CHROME_DRIVER")
        service = Service(executable_path=chrome_driver_path)


        # 初始化浏览器
        driver = webdriver.Chrome(options=chrome_options, service=service)
        driver.set_window_size(1920, 1080)

        # 打开 Grafana 登录页面
        grafana_url = f"{self.url}" + "/login"
        driver.get(grafana_url)

        # 等待登录页面加载完成，直到用户名输入框可见
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.NAME, "user"))
        )

        # 填写用户名和密码并登录
        username_input = driver.find_element(By.NAME, "user")
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        login_button.click()

        # 等待登录完成，第一个面板可见
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@class="css-itdw1b-panel-container"]')
            )
        )

        self.driver = driver


    def wait_for_element(self, xpath, timeout=60):
        """等待元素可见，直到超时"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except Exception as e:
            print(f"等待元素失败: {str(e)}")
            return None


    def wait_for_element_disappear(self, xpath, timeout=60):
        """等待元素消失，直到超时"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located((By.XPATH, xpath))
            )
        except Exception as e:
            print(f"等待元素消失失败: {str(e)}")
            return None


    def check_text_element(self, text):
        """检查指定文本是否存在，存在返回True，不存在返回False"""
        try:
            self.driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
            print(f"指定文本{text}存在")
            return True
        except Exception as e:
            print(f"不存在指定文本:{text}")
            return False


    def check_xpath_element(self, xpath):
        """检查指定的xpath是否存在，存在返回True，不存在返回False"""
        try:
            self.driver.find_element(By.XPATH, f"'{xpath}'")
            print(f"xpath存在：{xpath}")
            return True
        except Exception as e:
            print(f"xpath不存在：{xpath}")
            return False


    def render_panel(self, date_from, date_to, panel_id, row_value, panel_name, manufacturer, max_retries=3, retry_interval=5):
        print(f"Processing panel: {panel_name}")
        os.makedirs('/tmp/output/' + row_value + '/', exist_ok=True)
        safe_filename = '/tmp/output/' + row_value + '/' + re.sub(r'[\\/*?:"<>|]', '_', panel_name) + '.png'
        if os.path.exists(safe_filename):
            print(f"File {safe_filename} already exists, skipping...")
            return

        # 转到某个仪表板页面
        dashboard_url = self.url + f"/d/{self.uid}/?orgId=1&from={date_from}&to={date_to}&timezone=browser&viewPanel=panel-{panel_id}"
        self.driver.get(dashboard_url)

        # 等待仪表板加载完成，直到某个元素（例如第一个面板）可见
        self.wait_for_element('//*[@class="css-itdw1b-panel-container"]')    

        # 检测 Spinner 是否消失
        self.wait_for_element_disappear('//*[@class="css-1p4srcl-Icon"]', timeout=600)

        # 检查面板是否成功加载，如果没有加载成功，则重试
        retries = 0
        while retries < max_retries:
            # 检查是否存在感叹号 或 存在 No data
            if self.check_xpath_element(xpath='//*[@class="css-om0k8z-toolbar-button-panel-header-state-button"]') or self.check_text_element("No data"):
                print(f"第 {retries + 1} 次生成图表失败，正在重试...")
                retries += 1
                time.sleep(retry_interval)
                self.driver.refresh()
                # 等待仪表板加载完成，直到某个元素（例如第一个面板）可见
                self.wait_for_element('//*[@class="css-itdw1b-panel-container"]')    
                # 检测 Spinner 是否消失
                self.wait_for_element_disappear('//*[@class="css-1p4srcl-Icon"]', timeout=600)
            else:
                print("图表正常展示")
                break

        if retries == max_retries:
            print(f"面板 '{safe_filename}' 重试 {max_retries} 次仍然失败，跳过该面板。")
            return

        # 定位目标 panel 元素
        panel = self.driver.find_element(By.XPATH, '//*[@class="css-itdw1b-panel-container"]')
        # 对 panel 元素进行截图
        panel.screenshot(safe_filename)
        print(f"截图保存到：{safe_filename}")

        # 保存数据到数据库
        if panel_name in ast.literal_eval(os.getenv("LEGEND_TABLE_NAME")):
            # 获取title legend table类型的原始数据
            for i in self.driver.find_elements(By.XPATH, '//*[@class="css-5cr14k"]'):
                org_data = i.text
            print("原始数据=======", org_data)
            print("legend table 类型  -------------", panel_name)

            # 初始化数据成json格式
            legend_table = LegendTable(org_data)
            parsed_data = legend_table.parse()
            legend_max = legend_table.get_max_numeric()
            legend_mean_max = legend_table.get_mean_max_numeric()
            print("Parsed Data:", parsed_data)
            print("最大值   ============",legend_max)
            print("平均最大值============",legend_mean_max)

            # 保存数据到结果
            save_data = SaveData()
            print("写入数据库的数据：", legend_max, legend_mean_max)
            save_data.pymysql_write(manufacturer=manufacturer,name=panel_name, max_value=legend_max, mean_max=legend_mean_max)
            save_data.insert_result_to_file(title=panel_name, data=legend_max, filename='/tmp/result.txt')


        elif panel_name in ast.literal_eval(os.getenv("TABLE_NAME")):
            print("table 类型  -------------", panel_name)
            # 获取title table类型的原始数据
            for i in self.driver.find_elements(By.XPATH, '//*[@class="css-rzpihd"]'): # 数据不带标题
                data = i.text
            for i in self.driver.find_elements(By.XPATH, '//*[@class="css-1y4sadw-row"]'): # 标题
                title = i.text
            print("data=======", data)
            print("title=======", title)
            table = Table(title, data)
            table_json_data = table.parse_table_data()
            table_max = table.get_table_max()
            print("Parsed Data:", table_json_data)

            # 保存数据到结果文件
            save_data = SaveData()
            print("写入数据库的数据：", panel_name, table_max)
            save_data.pymysql_write(manufacturer=manufacturer,name=panel_name, max_value=table_max)
            save_data.insert_result_to_file(title=panel_name, data=table_max, filename='/tmp/result.txt')



if __name__ == "__main__":
    # 示例用法
    from dotenv import load_dotenv
    load_dotenv(".env")
    url = os.getenv("GF_URL")
    username = os.getenv("GF_USER")
    password = os.getenv("GF_PASSWORD")
    uid = "gw-service"
    # date_from="2025-03-01T00:00:00.000Z",
    date_from = "now-1d"
    date_to = "now"
    panel_id = "23763571999"
    safe_filename = "系统负载.png"

    dashboard = GrafanaDashboard(url, username, password, uid )
    print(os.getenv("CHROME_DEBUG"))
    dashboard.init_chromium(debug=os.getenv("CHROME_DEBUG"))
    dashboard.render_panel(date_from, date_to, panel_id, panel_name="测试面板", row_value="测试行")

    dashboard.driver.quit()