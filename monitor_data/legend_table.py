import re
from typing import List, Dict, Optional, Union

class LegendTable:
    def __init__(self, data: str):
        self.data = data
        self._unit_patterns = {
            'percentage': r'%',
            'full_units': r'\s+(GiB|GB|MiB|MB|KiB|KB|Mil)',
            'short_units': r'\s+([KMG])',
            'time_units': r'\s*(ms|s)'
        }

    def parse(self) -> List[Dict[str, str]]:
        """解析表格数据为结构化格式"""
        if not self.data.strip():
            return []

        lines = [line.strip() for line in self.data.strip().split('\n') if line.strip()]
        if len(lines) < 2:
            return []

        # 处理表头，保留"Last *"作为整体
        headers = []
        raw_headers = lines[0].split()
        i = 0
        while i < len(raw_headers):
            if i+1 < len(raw_headers) and raw_headers[i] == "Last" and raw_headers[i+1] == "*":
                headers.append("Last *")
                i += 2
            else:
                headers.append(raw_headers[i])
                i += 1

        result = []
        i = 1
        while i < len(lines):
            # 当前行是名称
            name_line = lines[i]
            
            # 检查下一行是否存在，并根据下一行内容判断数据类型
            if i + 1 < len(lines):
                value_line = lines[i + 1]
                
                # 根据下一行的内容检测数据类型
                data_type = self._detect_data_type_by_line(value_line)
                
                entry = {"Name": name_line}
                processed = self._process_metrics(value_line, data_type)
                
                # 确保处理后的数据列数与表头匹配
                for j in range(min(len(headers)-1, len(processed))):
                    entry[headers[j+1]] = processed[j]
                
                # 如果处理后的数据列数不足，用空字符串填充
                for j in range(len(processed), len(headers)-1):
                    entry[headers[j+1]] = ""
                    
                result.append(entry)
                i += 2  # 前进两行
            else:
                # 只有名称没有数值的情况
                entry = {"Name": name_line}
                # 为缺失的数值字段设置空值
                for j in range(1, len(headers)):
                    entry[headers[j]] = ""
                result.append(entry)
                i += 1

        return result

    def _detect_data_type_by_line(self, line: str) -> str:
        """根据单行内容检测数据类型"""
        if '%' in line:
            return 'percentage'
        elif re.search(self._unit_patterns['time_units'], line):
            return 'time_units'
        elif re.search(self._unit_patterns['full_units'], line):
            return 'full_units'
        elif re.search(self._unit_patterns['short_units'], line):
            return 'short_units'
        else:
            return 'plain'

    def _process_metrics(self, metrics: str, data_type: str) -> List[str]:
        """根据数据类型处理指标字符串"""
        if data_type == 'percentage':
            return metrics.split()
        elif data_type == 'time_units':
            # 专门处理时间单位：匹配数字+时间单位（如 81.7 ms, 5.03 s）
            # 使用正则表达式确保单位和数值保持在一起
            time_pattern = r'[\d.]+\s*(?:ms|s)'
            matches = re.findall(time_pattern, metrics)
            return matches
        elif data_type == 'full_units':
            # 匹配数字+完整单位（如 1.2GiB）
            return re.findall(r'[\d.]+(?:\s*[a-zA-Z%]+)?', metrics)
        elif data_type == 'short_units':
            # 简写单位处理（如 1.2G -> 1.2）
            return re.sub(self._unit_patterns['short_units'], r'\1', metrics).split()
        else:
            return metrics.split()

    def convert_to_comparable(self, value: str) -> float:
        """将不同单位的数值转换为可比较的浮点数"""
        if not value:
            return 0.0
            
        value = value.strip()
        
        # 处理百分比
        if '%' in value:
            return float(value.replace('%', ''))
        
        # 处理存储单位
        unit_multipliers = {
            'GiB': 1024**3,
            'GB': 1000**3,
            'MiB': 1024**2,
            'MB': 1000**2,
            'KiB': 1024,
            'KB': 1000,
            'Mil': 1000000
        }
        
        for unit, multiplier in unit_multipliers.items():
            if unit in value:
                return float(value.replace(unit, '')) * multiplier
        
        # 处理简写单位
        short_units = {
            'G': 1024**3,
            'M': 1024**2,
            'K': 1024
        }
        
        for unit, multiplier in short_units.items():
            if unit in value:
                return float(value.replace(unit, '')) * multiplier
        
        # 处理时间单位 - 这是重点
        if 'ms' in value:
            # 提取数字部分，处理可能有空格的情况
            num_str = re.search(r'[\d.]+', value)
            if num_str:
                return float(num_str.group()) / 1000
        elif 's' in value and 'ms' not in value:
            # 确保不是ms的情况
            num_str = re.search(r'[\d.]+', value)
            if num_str:
                return float(num_str.group())
        
        # 默认尝试转换为浮点数
        try:
            return float(value)
        except ValueError:
            return 0.0

    def get_max(self, field: str = "Max") -> Optional[Dict[str, str]]:
        """获取指定字段的最大值"""
        parsed_data = self.parse()
        if not parsed_data or field not in parsed_data[0]:
            return None
            
        return max(parsed_data, key=lambda x: self.convert_to_comparable(x[field]))

    def get_max_numeric(self, field: str = "Max") -> Optional[float]:
        """获取指定字段的最大值（纯数字）"""
        max_item = self.get_max(field)
        if max_item is None:
            return None
        return round(self.convert_to_comparable(max_item[field]), 4)

    def get_mean_max(self) -> Optional[Dict[str, str]]:
        """获取Mean字段的最大值"""
        return self.get_max("Mean")

    def get_mean_max_numeric(self) -> Optional[float]:
        """获取Mean字段的最大值（纯数字）"""
        return self.get_max_numeric("Mean")



if __name__ == "__main__":
    data = """Name Max
    0.99
    187 ms
    0.95
    21.7 ms
    0.90
    15.2 ms
    """
    data = """Name Mean Last * Max
    172.26.9.9_Total
    2.24% 2.52% 2.96%"""
    data = """
    Name Max
    app6 (topic: diting_prod_client_trace)
    1.81 K
    canal_group_nub_prod_SDK_front_v2 (topic: nub_prod_client_trace)
    3.35 K
    canal_group_nub_prod_Vehicle_front_v2 (topic: nub_prod_vehicle_trace)
    5
    flink_data_ao2 (topic: event_track_preProcess_A02)
    159 K
    graylog2 (topic: client_trace)
    0
    graylog2 (topic: diting_prod_client_trace)
    458 K
    graylog2 (topic: nub_prod_client_trace)
    1.12 Mil
    graylog2_client_trace_log (topic: client_trace)
    0
    graylog2_client_trace_log (topic: diting_prod_client_trace)
    741
    graylog2_client_trace_log (topic: nub_prod_client_trace)
    1.08 K
    graylog2_client_userevent_group (topic: event_track_preProcess_A02)
    437 K
    graylog2_client_userevent_log_group (topic: event_track_preProcess_log_A02)
    92.1 K
    graylog2_cloud_trace_log (topic: k8s-pod-logs)
    16.5 Mil
    k8s_group (topic: ingress-logs)
    2.53 K
    k8s_group (topic: k8s-pod-logs)
    4.71 Mil
    k8s_pod_group (topic: k8s-pod-logs)
    9.94 K
    vehicle2 (topic: diting_prod_vehicle_trace)
    42
    """
    data = """
    Name Mean Max
    请求耗时
    81.7 ms 5.03 s
    """
    table = LegendTable(data)
    parsed = table.parse()
    print("Parsed Data:", parsed)
    print("Max Value:", table.get_max())
    print("Max Numeric Value:", table.get_max_numeric())