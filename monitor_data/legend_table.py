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

        # 判断数据格式：交替格式(名称+数值)还是标准格式
        is_alternating = False
        if len(lines) > 1 and not any(c.isdigit() or c in '%' for c in lines[1]):
            is_alternating = True

        result = []
        if is_alternating:
            # 处理交替格式(名称+数值)
            for i in range(1, len(lines), 2):
                if i+1 >= len(lines):
                    break
                entry = {"Name": lines[i]}
                # 使用split()处理可能的多列数值
                values = lines[i+1].split()
                for j in range(min(len(headers)-1, len(values))):
                    entry[headers[j+1]] = values[j]
                result.append(entry)
        else:
            # 处理标准格式(名称+多列数值)
            data_type = self._detect_data_type(lines)
            for i in range(1, len(lines), 2):
                if i+1 >= len(lines):
                    break
                entry = {"Name": lines[i]}
                processed = self._process_metrics(lines[i+1], data_type)
                for j in range(min(len(headers)-1, len(processed))):
                    entry[headers[j+1]] = processed[j]
                result.append(entry)

        return result


    def _detect_data_type(self, lines: List[str]) -> str:
        """检测数据类型"""
        sample_line = ' '.join(lines[1:3]) if len(lines) >= 3 else ''
        
        if '%' in sample_line:
            return 'percentage'
        elif re.search(self._unit_patterns['full_units'], sample_line):
            return 'full_units'
        elif re.search(self._unit_patterns['short_units'], sample_line):
            return 'short_units'
        elif re.search(self._unit_patterns['time_units'], sample_line):
            return 'time_units'
        else:
            return 'plain'


    def _process_metrics(self, metrics: str, data_type: str) -> List[str]:
        """根据数据类型处理指标字符串"""
        if data_type == 'percentage':
            return metrics.split()
        elif data_type == 'full_units':
            # 匹配数字+单位（如 1.2GiB）
            return re.findall(r'[\d.]+(?:\s*[a-zA-Z%]+)?', metrics)
        elif data_type == 'short_units':
            # 简写单位处理（如 1.2G -> 1.2）
            return re.sub(self._unit_patterns['short_units'], r'\1', metrics).split()
        elif data_type == 'time_units':
            # 匹配时间值（如 62.2 ms）
            return re.findall(r'[\d.]+\s*[a-zA-Z]+', metrics)
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
        
        # 处理存储单位 - 添加Mil单位处理
        unit_multipliers = {
            'GiB': 1024**3,
            'GB': 1000**3,
            'MiB': 1024**2,
            'MB': 1000**2,
            'KiB': 1024,
            'KB': 1000,
            'Mil': 1000000  # 添加百万单位
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
        
        # 处理时间单位
        if 'ms' in value:
            return float(value.replace('ms', '')) / 1000
        elif 's' in value:
            return float(value.replace('s', ''))
        
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
    # data = """Name Max
    # 0.99
    # 187 ms
    # 0.95
    # 21.7 ms
    # 0.90
    # 15.2 ms
    # """
    # data = """Name Mean Last * Max
    # 172.26.9.9_Total
    # 2.24% 2.52% 2.96%"""


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
    table = LegendTable(data)
    parsed = table.parse()
    print("Parsed Data:", parsed)
    print("Max Value:", table.get_max())
    print("Max Numeric Value:", table.get_max_numeric())