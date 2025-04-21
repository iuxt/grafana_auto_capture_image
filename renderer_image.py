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
    def __init__(self, username, password, uid, date_from, date_to, panel_id, safe_filename):
        self.username = username
        self.password = password
        self.uid = uid
        self.date_from = date_from
        self.date_to = date_to
        self.panel_id = panel_id
        self.safe_filename = safe_filename


    def render_panel(self, max_retries=3, retry_interval=5):

        # 配置Chrome浏览器选项（无界面浏览器）
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        # chrome_options.binary_location = ""
        # chrome_options.add_argument("--headless")  # 无头模式
        # chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速（可选）
        ser = Service()
        ser.executable_path = r'./chromedriver'	# 指定 ChromeDriver 的路径


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


        # 转到某个仪表板页面
        dashboard_url = os.getenv("GF_URL") + f"/d/{self.uid}/?orgId=1&from={self.date_from}&to={self.date_to}&timezone=browser&viewPanel=panel-{self.panel_id}"
        driver.get(dashboard_url)


        # 等待仪表板加载完成，直到某个元素（例如第一个面板）可见
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@class="css-itdw1b-panel-container"]')
            )
        )


        # 检测 Spinner 是否消失（等待最多60秒）
        WebDriverWait(driver, 60).until(
            EC.invisibility_of_element_located(
                (By.XPATH, '//*[@class="css-1p4srcl-Icon"]')
            )
        )
        # 感叹号图标: css-om0k8z-toolbar-button-panel-header-state-button
        retries = 0
        while retries < max_retries:
            try:
                element = driver.find_element(By.XPATH, '//*[@class="css-om0k8z-toolbar-button-panel-header-state-button"]')
                print(f"第 {retries + 1} 次生成图表失败，正在重试...")
                retries += 1
                time.sleep(retry_interval)
                driver.refresh()
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@class="css-itdw1b-panel-container"]')
                    )
                )
                WebDriverWait(driver, 60).until(
                    EC.invisibility_of_element_located(
                        (By.XPATH, '//*[@class="css-1p4srcl-Icon"]')
                    )
                )
            except NoSuchElementException:
                print("生成图表成功")
                break
            except Exception as e:
                print(f"发生其他错误: {str(e)}")
                break

        if retries == max_retries:
            print(f"面板 '{self.panel_title}' 重试 {max_retries} 次仍然失败，跳过该面板。")
            driver.quit()
            return




        # 定位目标 panel 元素
        panel = driver.find_element(By.XPATH, '//*[@class="css-itdw1b-panel-container"]')

        # 对 panel 元素进行截图
        panel.screenshot(self.safe_filename)

        # 退出浏览器
        driver.quit()




if __name__ == "__main__":
    # 示例用法
    username = os.getenv("GF_USER")
    password = os.getenv("GF_PASSWORD")
    uid = "gw-service"
    date_from = "now-30d"
    date_to = "now"
    panel_id = "16"
    panel_title = "系统负载"

    dashboard = GrafanaDashboard(username, password, uid, date_from, date_to, panel_id, panel_title)
    dashboard.render_panel()