from selenium.webdriver.common.by import By
import re

class GetMonitorData:
    # 这个是大的行：css-fpx8k9-LegendRow
    # css-s2uf1z 这个是纯数字
    def __init__(self, driver):
        self.driver = driver

    def get_max_data(self):
        """
        获取最大监控数据,折线图需要有table类型的数据展示出来
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
                    value = float(value)
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
        """
        针对表格数据，并且数据不带单位的情况
        """
        data = []
        for i in self.driver.find_elements(By.XPATH, '//*[@class="css-8fjwhi-row"]'):
            data.append(i.text.replace("\n", " ").split(" "))
        print("data=======", data)
        max_value = max(data, key=lambda x: x[1])
        return max_value


    def get_table_max_data_and_unit(self):
        """
        针对表格数据，并且数据带单位的情况
        """
        data = []
        for i in self.driver.find_elements(By.XPATH, '//*[@class="css-8fjwhi-row"]'):
            data.append(i.text.replace("\n", " ").split(" "))
        """
        data======= [['idk_base.ca_cert_info', '73.4', 'GiB'], ['idk_base.ca_sign_20240923', '23.7', 'GiB'], ['idk_base.mobile_device', '18.2', 'GiB'], ['idk_base.vehicle_user_key_his', '8.53', 'GiB'], ['idk_base.sys_log', '4.55', 'GiB'], ['idk_base.virtualkey_user', '4.31', 'GiB'], ['idk_base.bluetooth_device_logs', '1.94', 'GiB'], ['idk_base.vehicle_logs', '1.61', 'GiB'], ['idk_base.bluetooth_device', '1.25', 'GiB'], ['idk_base.vehicle_user_role', '1.20', 'GiB']]
        """
        list = []
        for i in data:
            if len(i) < 3:
                continue
            else:
                title, value, unit = i[0], i[1], i[2]
                if unit == 'GiB':
                    value = float(value) * 1024
                elif unit == 'MiB':
                    value = float(value)
                elif unit == 'KiB':
                    value = float(value) / 1024
            data[data.index(i)] = [title, value, 'MiB']  # 将转换后的值赋回数据中
        print("data=======", data)
        max_value = max(data, key=lambda x: x[1])
        return max_value[1], max_value[2]



    def get_specified_data(self, text):
        """获取指定的监控数据"""
        usage_list = self.driver.find_elements(By.XPATH, '//*[@class="css-fpx8k9-LegendRow"]')
        for usage in usage_list:
            data = usage.text.replace("\n", " ")
            print(data)
            if text in data:
                print(f"获取到的监控数据：{data}")
                return data
