from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from get_monitor_data import GetMonitorData



chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-extensions")

# 指定 ChromeDriver 的路径
chrome_driver_path = "C:/Data/chromedriver-win64/chromedriver.exe"

# 创建 Service 对象并禁用自动更新
service = Service(executable_path=chrome_driver_path)


# 初始化浏览器
driver = webdriver.Chrome(options=chrome_options, service=service)
driver.set_window_size(1920, 1080)


# 打开 Grafana 登录页面
grafana_url = f"https://sre-grafana.ingeek.com/login"
driver.get(grafana_url)

# 等待登录页面加载完成，直到用户名输入框可见
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.NAME, "user"))
)

# 填写用户名和密码并登录
username_input = driver.find_element(By.NAME, "user")
password_input = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')
username_input.send_keys("admin")
password_input.send_keys("oPToNfQ859qpOV")
login_button.click()

# 等待登录完成，第一个面板可见
WebDriverWait(driver, 60).until(
    EC.presence_of_element_located(
        (By.XPATH, '//*[@class="css-itdw1b-panel-container"]')
    )
)
