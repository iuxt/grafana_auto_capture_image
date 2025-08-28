import re
from typing import List, Dict, Optional


class LegendTable:
    UNIT_MULTIPLIERS = {
        'GiB': 1024**3, 'GB': 1000**3,
        'MiB': 1024**2, 'MB': 1000**2,
        'KiB': 1024,    'KB': 1000,
        'Mil': 1000000, 'K': 1000,
        'M': 1000000,   'G': 1000000000,
    }

    UNIT_PATTERNS = {
        'percentage': r'%',
        'full_units': r'[\d.]+\s*(?:' + '|'.join(UNIT_MULTIPLIERS.keys()) + r')',
        'time_units': r'[\d.]+\s*(?:ms|s)',
        'plain': r'[\d.]+'
    }

    def __init__(self, data: str):
        self.data = data

    def parse(self) -> List[Dict[str, str]]:
        """解析表格数据为结构化格式"""
        lines = [line.strip() for line in self.data.strip().splitlines() if line.strip()]
        if len(lines) < 2:
            return []

        headers = self._parse_headers(lines[0])
        data_type = self._detect_data_type(lines)

        result = []
        # 每两行一个 entry（名称 + 指标）
        for i in range(1, len(lines), 2):
            if i + 1 >= len(lines):
                break
            entry = {"Name": lines[i]}
            values = self._process_metrics(lines[i + 1], data_type)
            for j, val in enumerate(values[:len(headers) - 1], start=1):
                entry[headers[j]] = val
            result.append(entry)
        return result

    def _parse_headers(self, header_line: str) -> List[str]:
        """解析表头"""
        raw = header_line.split()
        headers = []
        i = 0
        while i < len(raw):
            if i + 1 < len(raw) and raw[i] == "Last" and raw[i + 1] == "*":
                headers.append("Last *")
                i += 2
            else:
                headers.append(raw[i])
                i += 1
        return headers

    def _detect_data_type(self, lines: List[str]) -> str:
        """检测数据类型"""
        sample = ' '.join(lines[1:3])
        for dtype, pattern in self.UNIT_PATTERNS.items():
            if re.search(pattern, sample):
                return dtype
        return 'plain'

    def _process_metrics(self, metrics: str, data_type: str) -> List[str]:
        """按数据类型解析数值"""
        pattern = self.UNIT_PATTERNS.get(data_type, r'\S+')
        return re.findall(pattern, metrics)

    def convert_to_comparable(self, value: str) -> float:
        """统一数值转换为 float"""
        if not value:
            return 0.0
        value = value.strip()

        # 百分比
        if value.endswith('%'):
            return float(value.replace('%', ''))

        # 单位数值
        for unit, multiplier in self.UNIT_MULTIPLIERS.items():
            if value.endswith(unit):
                return float(value.replace(unit, '').strip()) * multiplier

        # 时间
        if value.endswith("ms"):
            return float(value.replace("ms", '')) / 1000
        if value.endswith("s"):
            return float(value.replace("s", ''))

        # 纯数字
        try:
            return float(value)
        except ValueError:
            return 0.0

    def get_max(self, field: str = "Max") -> Optional[Dict[str, str]]:
        parsed = self.parse()
        if not parsed or field not in parsed[0]:
            return None
        return max(parsed, key=lambda x: self.convert_to_comparable(x[field]))

    def get_max_numeric(self, field: str = "Max") -> Optional[float]:
        max_item = self.get_max(field)
        return round(self.convert_to_comparable(max_item[field]), 4) if max_item else None


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
    print("Parsed Data:", table.parse())
    print("Max Value:", table.get_max())
    print("Max Numeric Value:", table.get_max_numeric())
