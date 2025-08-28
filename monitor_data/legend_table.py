import re
from typing import List, Dict, Optional

class LegendTable:
    def __init__(self, data: str):
        self.data = data
        self._unit_patterns = {
            'percentage': r'%',
            'full_units': r'\s+(GiB|GB|MiB|MB|KiB|KB|Mil|K|M|G)',
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

        # 判断数据格式
        is_alternating = False
        if len(lines) > 1 and not any(c.isdigit() or c in '%' for c in lines[1]):
            is_alternating = True

        result = []
        if is_alternating:
            for i in range(1, len(lines), 2):
                if i+1 >= len(lines):
                    break
                entry = {"Name": lines[i]}
                values = lines[i+1].split()
                for j in range(min(len(headers)-1, len(values))):
                    entry[headers[j+1]] = values[j]
                result.append(entry)
        else:
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
        if data_type == 'percentage':
            return metrics.split()
        elif data_type == 'full_units':
            return re.findall(r'[\d.]+(?:\s*[a-zA-Z%]+)?', metrics)
        elif data_type == 'short_units':
            return re.sub(self._unit_patterns['short_units'], r'\1', metrics).split()
        elif data_type == 'time_units':
            return re.findall(r'[\d.]+\s*[a-zA-Z]+', metrics)
        else:
            return metrics.split()

    def convert_to_comparable(self, value: str) -> float:
        if not value:
            return 0.0

        value = value.strip()

        # 百分比
        if '%' in value:
            return float(value.replace('%', ''))

        # 存储单位
        unit_multipliers = {
            'GiB': 1024**3,
            'GB': 1000**3,
            'MiB': 1024**2,
            'MB': 1000**2,
            'KiB': 1024,
            'KB': 1000,
            'Mil': 1_000_000,   # 新增
            'K': 1_000,         # 改成 1000 更符合 "K/Mil" 场景
            'M': 1_000_000,
            'G': 1_000_000_000
        }

        for unit, multiplier in unit_multipliers.items():
            if value.endswith(unit):
                return float(value.replace(unit, '').strip()) * multiplier

        # 时间
        if value.endswith("ms"):
            return float(value.replace("ms", '')) / 1000
        elif value.endswith("s"):
            return float(value.replace("s", ''))

        try:
            return float(value)
        except ValueError:
            return 0.0

    def get_max(self, field: str = "Max") -> Optional[Dict[str, str]]:
        parsed_data = self.parse()
        if not parsed_data or field not in parsed_data[0]:
            return None
        return max(parsed_data, key=lambda x: self.convert_to_comparable(x[field]))

    def get_max_numeric(self, field: str = "Max") -> Optional[float]:
        max_item = self.get_max(field)
        if max_item is None:
            return None
        return round(self.convert_to_comparable(max_item[field]), 4)


if __name__ == "__main__":
    data = """
    Name Max
    graylog2 (topic: nub_prod_client_trace)
    1.12 Mil
    graylog2 (topic: diting_prod_client_trace)
    458 K
    k8s_group (topic: k8s-pod-logs)
    4.71 Mil
    """

    table = LegendTable(data)
    parsed = table.parse()
    print("Parsed Data:", parsed)
    print("Max Value:", table.get_max())
    print("Max Numeric Value:", table.get_max_numeric())
