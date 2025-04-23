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


class GrafanaDashboard:
    def __init__(self, username, password, uid):
        self.username = username
        self.password = password
        self.uid = uid

    def init_chromium(self):

        # 配置Chrome浏览器选项（无界面浏览器）
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.binary_location = ""
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")

        # 设置ChromeDriver的路径
        ser = Service()
        # ser.executable_path = r'./chromedriver'


        # 初始化浏览器
        driver = webdriver.Chrome(options=chrome_options, service=ser)
        driver.set_window_size(1920, 1080)

        # 打开 Grafana 登录页面
        grafana_url = os.getenv("GF_URL") + "/login"
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
        

    def render_panel(self, date_from, date_to, panel_id, safe_filename, max_retries=3, retry_interval=5):

        # 转到某个仪表板页面
        dashboard_url = os.getenv("GF_URL") + f"/d/{self.uid}/?orgId=1&from={date_from}&to={date_to}&timezone=browser&viewPanel=panel-{panel_id}"
        self.driver.get(dashboard_url)

        # 等待仪表板加载完成，直到某个元素（例如第一个面板）可见
        self.wait_for_element('//*[@class="css-itdw1b-panel-container"]')    

        # 检测 Spinner 是否消失（等待最多60秒）
        self.wait_for_element_disappear('//*[@class="css-1p4srcl-Icon"]')

        # 检查面板是否成功加载，如果没有加载成功，则重试
        retries = 0
        while retries < max_retries:
            try:
                element = self.driver.find_element(By.XPATH, '//*[@class="css-om0k8z-toolbar-button-panel-header-state-button"]')
                print(f"第 {retries + 1} 次生成图表失败，正在重试...")
                retries += 1
                time.sleep(retry_interval)
                self.driver.refresh()
                # 等待仪表板加载完成，直到某个元素（例如第一个面板）可见
                self.wait_for_element('//*[@class="css-itdw1b-panel-container"]')    

                # 检测 Spinner 是否消失（等待最多60秒）
                self.wait_for_element_disappear('//*[@class="css-1p4srcl-Icon"]')
                
            except NoSuchElementException:
                print("生成图表成功")
                break
            except Exception as e:
                print(f"发生其他错误: {str(e)}")
                break

        if retries == max_retries:
            print(f"面板 '{safe_filename}' 重试 {max_retries} 次仍然失败，跳过该面板。")
            return




        # 定位目标 panel 元素
        panel = self.driver.find_element(By.XPATH, '//*[@class="css-itdw1b-panel-container"]')

        # 对 panel 元素进行截图
        panel.screenshot(safe_filename)





if __name__ == "__main__":
    # 示例用法
    username = os.getenv("GF_USER")
    password = os.getenv("GF_PASSWORD")
    uid = "gw-service"
    date_from = "now-30d"
    date_to = "now"
    panel_id = "16"
    safe_filename = "系统负载.png"

    
    dashboard = GrafanaDashboard(username, password, uid )
    dashboard.init_chromium()
    dashboard.render_panel(date_from, date_to, panel_id, safe_filename)
    dashboard.driver.quit()