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

        # 提取数字并判断单位
        for item in data:
            if len(item) < 2:
                continue
            else:
                value, unit = item
                if unit == 'ms':
                    value = float(value)  # 转换为浮动数字
                elif unit == 's':
                    value = float(value) * 1000  # 秒转换为毫秒
                elif unit == 'K':
                    value = float(value) * 1000
                elif unit == 'M':
                    value = float(value) * 1000000
                item[0] = str(value)  # 将转换后的值赋回数据中
        


        def extract_number(value):
            match = re.match(r"(\d+(\.\d+)?)", value)  # 匹配整数或浮动数
            return float(match.group(0)) if match else None

        if not data:
            print("没有找到监控数据")
            return None
        else:
            # 获取最大值
            max_value = max(data, key=lambda x: extract_number(x[0]))
            print(f"最大值: {max_value[0]}")
            return max_value[0]
    

    def get_table_max_data(self):
        data = []
        for i in self.driver.find_elements(By.XPATH, '//*[@class="css-1yrzrqq-cellContainerOverflow"]'):
            data.append(i.text.replace("\n", " ").split(" "))
        print("data=======", data)
        # data: [['idk-mob-sdk-server-67847b6fdc-2rd4k'], ['0'], ['idk-mob-sdk-server-67847b6fdc-4ck49'], ['0'], ['idk-mob-sdk-server-67847b6fdc-flr6h'], ['0'], ['idk-mob-sdk-server-67847b6fdc-knbnr'], ['0'], ['idk-mob-sdk-server-67847b6fdc-knmnc'], ['0'], ['idk-mob-sdk-server-67847b6fdc-shzqr'], ['0'], ['idk-mob-sdk-server-67847b6fdc-z6jzn'], ['0'], ['idk-mob-sdk-server-67847b6fdc-zz69r'], ['0'], ['idk-oms-server-748d45cb44-ngzdh'], ['0'], ['idk-oms-wfe-5cbb694975-ndvmd'], ['0'], ['idk-oms-wfe-5cbb694975-pgrmx'], ['0'], ['idk-supplier-server-77c9c59dfb-c6tct'], ['0'], ['idk-supplier-server-77c9c59dfb-s4s64'], ['0'], ['idk-supplier-wfe-77f49cbbf7-wmqdt'], ['0'], ['idk-supplier-wfe-77f49cbbf7-z7d7v'], ['0'], ['idk-tsp-server-777699864f-75n9d'], ['0']]
        numbers = [int(item[0]) for item in data if item[0].isdigit()]  # 提取所有数字并转换为整数
        max_value = max(numbers) if numbers else None  # 获取最大值，防止空列表
        return max_value


    def get_specified_data(self, text):
        """获取指定的监控数据"""
        usage_list = self.driver.find_elements(By.XPATH, '//*[@class="css-fpx8k9-LegendRow"]')
        for usage in usage_list:
            data = usage.text.replace("\n", " ")
            print(data)
            if text in data:
                print(f"获取到的监控数据：{data}")
                return data
