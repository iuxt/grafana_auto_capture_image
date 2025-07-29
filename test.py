from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementNotInteractableException
from monitor_data import table, legend_table
import time


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




def wait_for_element(xpath, timeout=60):
    """等待元素可见，直到超时"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except Exception as e:
        print(f"等待元素失败: {str(e)}")
        return None


def wait_for_element_disappear(xpath, timeout=60):
    """等待元素消失，直到超时"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located((By.XPATH, xpath))
        )
    except Exception as e:
        print(f"等待元素消失失败: {str(e)}")
        return None


def check_text_element(text):
    """检查指定文本是否存在，存在返回True，不存在返回False"""
    try:
        driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
        print(f"指定文本{text}存在")
        return True
    except Exception as e:
        print(f"不存在指定文本:{text}")
        return False


def check_xpath_element(xpath):
    """检查指定的xpath是否存在，存在返回True，不存在返回False"""
    try:
        driver.find_element(By.XPATH, f"'{xpath}'")
        print(f"xpath存在：{xpath}")
        return True
    except Exception as e:
        print(f"xpath不存在：{xpath}")
        return False


# 等待登录完成，第一个面板可见
wait_for_element('//*[@class="css-itdw1b-panel-container"]')    


url = f"https://sre-grafana.ingeek.com/d/gw-service/e4b89a-e58aa1-e79b91-e68ea7-e5a4a7-e79b98?orgId=1&from=now-24h&to=now&timezone=Asia%2FShanghai&refresh=0&viewPanel=panel-2103" # CPU使用率%
# url = f"https://sre-grafana.ingeek.com/d/gw-service/e4b89a-e58aa1-e79b91-e68ea7-e5a4a7-e79b98?orgId=1&from=now-24h&to=now&timezone=Asia%2FShanghai&refresh=0&viewPanel=panel-2102" # SDK内存 GB
driver.get(url)

wait_for_element('//*[@class="css-itdw1b-panel-container"]')
wait_for_element_disappear('//*[@class="css-1p4srcl-Icon"]', timeout=600)

driver.save_screenshot("screenshot.png")


# # 获取title legend table类型的原始数据
# for i in driver.find_elements(By.XPATH,   '//*[@class="css-5cr14k"]'):
#     data = i.text
# print("data=======", data)

# # 初始化数据成json格式
# legend_table = legend_table.LegendTable(data)
# print("Parsed Data:", legend_table.parse())
# print(legend_table.get_max())


# 获取title table类型的原始数据
# for i in driver.find_elements(By.XPATH, '//*[@class="css-1d40qib"]'):
for i in driver.find_elements(By.XPATH, '//*[@class="css-rzpihd"]'): # 数据不带标题
# for i in driver.find_elements(By.XPATH, '//*[@class="css-1y4sadw-row"]'): # 标题
    data = i.text
print("data=======", data)
