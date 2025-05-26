from selenium.webdriver.common.by import By
import re

class GetMonitorData:
    # 这个是大的行：css-fpx8k9-LegendRow
    # css-s2uf1z 这个是纯数字
    def __init__(self, driver):
        self.driver = driver

    def get_max_data(self):
        """获取最大监控数据
        """
        data = []
        for i in self.driver.find_elements(By.XPATH, '//*[@class="css-s2uf1z"]'):
            data.append(i.text.replace("\n", " ").split(" "))

        print("data=======", data)
        # data: [['272', 'ms'], ['192', 'ms'], ['46.6', 'ms'], ['38.8', 'ms'], ['29.8', 'ms'], ['24.5', 'ms']]
        # 提取数字
        def extract_number(value):
            match = re.match(r"(\d+(\.\d+)?)", value)  # 匹配整数或浮动数
            return float(match.group(0)) if match else None

        if not data:
            print("没有找到监控数据")
            return None
        else:
            # 获取最大值
            max_value = max(data, key=lambda x: extract_number(x[0]))

            # 输出结果
            max_num = extract_number(max_value[0])
            print(f"最大值: {max_value[0]}，转换为数字: {max_num}")
    

    def get_specified_data(self, text):
        """获取指定的监控数据"""
        usage_list = self.driver.find_elements(By.XPATH, '//*[@class="css-fpx8k9-LegendRow"]')
        for usage in usage_list:
            data = usage.text.replace("\n", " ")
            print(data)
            if text in data:
                print(f"获取到的监控数据：{data}")
                return data
