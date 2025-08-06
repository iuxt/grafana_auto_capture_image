import re
from typing import List, Dict, Optional, Union

class LegendTable:
    def __init__(self, data: str):
        self.data = data
        self._unit_patterns = {
            'percentage': r'%',
            'full_units': r'\s+(GiB|GB|MiB|MB|KiB|KB)',
            'short_units': r'\s+([KMG])',
            'time_units': r'\s*(ms|s)'
        }

    def parse(self) -> List[Dict[str, str]]:
        """解析表格数据为结构化格式"""
        if not self.data.strip():
            return []

        lines = [line.strip() for line in self.data.strip().split('\n') if line.strip()]
        if not lines:
            return []
            
        headers = lines[0].split()
        
        # Handle special case where we have probability-time pairs
        if len(headers) == 2 and headers[1] == "Max":
            result = []
            for i in range(1, len(lines), 2):
                if i + 1 >= len(lines):
                    break
                probability = lines[i]
                time_value = lines[i+1]
                result.append({
                    headers[0]: probability,
                    headers[1]: time_value
                })
            return result
        
        # Original format handling
        data_type = self._detect_data_type(lines)
        result = []
        for i in range(1, len(lines), 2):
            if i + 1 >= len(lines):
                break
                
            name = lines[i]
            metrics = lines[i + 1]
            
            processed_metrics = self._process_metrics(metrics, data_type)
            
            if len(headers) == 3 and len(processed_metrics) >= 2:
                result.append({
                    "Name": name,
                    headers[1]: processed_metrics[0],
                    headers[2]: processed_metrics[1]
                })
        
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
            return re.sub(self._unit_patterns['full_units'], r'\1', metrics).split()
        elif data_type == 'short_units':
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
            'KB': 1000
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
        return self.convert_to_comparable(max_item[field])

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
    
    table = LegendTable(data)
    parsed = table.parse()
    print("Parsed Data:", parsed)
    print("Max Value:", table.get_max())
    print("Max Numeric Value:", table.get_max_numeric())