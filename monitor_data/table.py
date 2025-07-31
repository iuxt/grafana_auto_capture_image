import re
from typing import Union, List, Dict

class Table:
    def __init__(self, title: str, data: str):
        self.title = title
        self.data = data
        headers = [line.strip() for line in self.title.strip().split('\n') if line.strip()]
        self.headers = headers

    def _convert_to_mb(self, value: str) -> float:
        """
        将带单位的数据转换为MB，区分二进制和十进制单位
        
        :param value: 带单位的字符串值，如"1.5 GiB"或"2 GB"
        :return: 转换为MB后的数值
        """
        # 正则匹配数值和单位
        match = re.match(r'^([\d.]+)\s*(KB|KiB|MB|MiB|GB|GiB|TB|TiB)?$', value.strip(), re.IGNORECASE)
        if not match:
            try:
                return float(value)
            except ValueError:
                return 0.0

        number = float(match.group(1))
        unit = (match.group(2) or '').upper()

        # 二进制单位 (基于1024)
        if unit == 'KIB':
            return number / 1024
        elif unit == 'MIB':
            return number
        elif unit == 'GIB':
            return number * 1024
        elif unit == 'TIB':
            return number * 1024 * 1024
        
        # 十进制单位 (基于1000)
        elif unit == 'KB':
            return number / 1000
        elif unit == 'MB':
            return number
        elif unit == 'GB':
            return number * 1000
        elif unit == 'TB':
            return number * 1000 * 1000
        
        # 无单位，默认为MB
        return number

    def parse_table_data(self) -> List[Dict]:
        """
        将表格数据转换为JSON格式，并统一转换为MB
        
        :return: JSON格式的数据列表，所有大小单位已转换为MB
        """
        lines = [line.strip() for line in self.data.strip().split('\n') if line.strip()]
        group_size = len(self.headers)
        if group_size == 0:
            return []
        
        result = []
        for i in range(0, len(lines), group_size):
            if i + group_size - 1 >= len(lines):
                break
                
            item = {}
            for j in range(group_size):
                value = lines[i + j]
                
                # 尝试转换为数值
                try:
                    if any(unit in value.upper() for unit in ['KB', 'KIB', 'MB', 'MIB', 'GB', 'GIB', 'TB', 'TIB']):
                        # 如果是带单位的值，转换为MB
                        item[self.headers[j]] = self._convert_to_mb(value)
                    elif '.' in value:
                        item[self.headers[j]] = float(value)
                    else:
                        item[self.headers[j]] = int(value)
                except ValueError:
                    item[self.headers[j]] = value
            
            result.append(item)
        
        return result

    def get_table_max(self, column_name: str = None) -> float:
        """
        获取表格数据中指定列的最大值(单位MB)
        
        :param column_name: 列名，如果为None则使用最后一列
        :return: 最大值(MB)，保留2位小数
        """
        json_data = self.parse_table_data()
        if not json_data:
            return 0.0
        
        target_column = column_name if column_name else self.headers[-1]
        
        values = []
        for item in json_data:
            if target_column in item and isinstance(item[target_column], (int, float)):
                values.append(item[target_column])
        
        return round(max(values), 2) if values else 0.0


if __name__ == "__main__":
    # 测试数据包含各种单位
    title = """Field
    占用空间
    """

    data = """
    idk_base.ca_cert_info
    100.0 GiB
    idk_base.ca_sign_20240923
    23.7 GB
    idk_base.mobile_device
    18.8 GiB
    idk_base.vehicle_user_key_his
    10.4 GB
    idk_base.virtualkey_user
    4.56 GiB
    idk_base.sys_log
    4550 MiB
    idk_base.bluetooth_device_logs
    1.94 GiB
    idk_base.vehicle_logs
    1610 MiB
    idk_base.bluetooth_device
    1.33 GB
    idk_base.vehicle_user_role
    1.24 GiB
    """
    table = Table(title, data)
    
    # 转换数据并打印
    json_data = table.parse_table_data()
    import json
    print(json.dumps(json_data, indent=2, ensure_ascii=False))
    
    # 获取最大存储空间
    max_space = table.get_table_max("占用空间")
    print(f"\n最大存储空间: {max_space:.2f} MB")