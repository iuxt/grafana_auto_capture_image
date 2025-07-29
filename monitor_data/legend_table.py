import re

class LegendTable:
    def __init__(self, data):
        self.data = data

    def parse(self):
        """
        input:
        Name Mean Max
        gw_elk1
        79.3% 79.5%
        gw_elk2
        77.8% 78.1%
        
        output:
        [
            {"Name": "gw_elk1", "Mean": "79.3%", "Max": "79.5%"},
            {"Name": "gw_elk2", "Mean": "77.8%", "Max": "78.1%"}
        ]
        """

        if '%' in self.data:
            lines = self.data.strip().split('\n')
            result = []

            # Extract header
            headers = lines[0].strip().split()

            # Process each pair of lines
            for i in range(1, len(lines), 2):
                name = lines[i].strip()
                metrics = lines[i + 1].strip().split()
                result.append({
                    "Name": name,
                    headers[1]: metrics[0],
                    headers[2]: metrics[1]
                })

        elif 'GiB' in self.data or 'GB' in self.data or 'MiB' in self.data or 'MB' in self.data or 'KiB' in self.data or 'KB' in self.data:
            result = []
            lines = self.data.strip().split('\n')
            headers = lines[0].strip().split()

            # Process each pair of lines
            for i in range(1, len(lines), 2):
                name = lines[i].strip()
                metrics = lines[i + 1].strip()
                fixed_s = re.sub(r'\s+(GB|GiB|MB)', r'\1', metrics).split()
                result.append({
                    "Name": name,
                    headers[1]: fixed_s[0],
                    headers[2]: fixed_s[1]
                })

        return result

    def convert_to_comparable(self, value):
        """将不同单位的数值转换为可比较的浮点数"""
        if '%' in value:
            return float(value.replace('%', ''))
        elif 'GiB' in value or 'GB' in value:
            return float(value.replace('GiB', '').replace('GB', '')) * 1024
        elif 'MiB' in value or 'MB' in value:
            return float(value.replace('MiB', '').replace('MB', ''))
        elif 'KiB' in value or 'KB' in value:
            return float(value.replace('KiB', '').replace('KB', '')) / 1024
        elif 's' in value:
            # 处理秒和毫秒
            if 'ms' in value:
                return float(value.replace('ms', '')) / 1000
            return float(value.replace('s', ''))
        else:
            # 默认尝试直接转换为浮点数
            try:
                return float(value)
            except ValueError:
                return 0.0  # 无法转换的情况返回0
            

    def get_max(self):
        """
        获取最大值
        return:
        {'Name': 'gw_elk1', 'Mean': '79.3%', 'Max': '79.5%'}
        """
        parsed_data = self.parse()
        if not parsed_data:
            return None
        
        # 找到Max值最大的元素
        max_value = max(parsed_data, key=lambda x: self.convert_to_comparable(x["Max"]))
        
        return max_value
    

    def get_mean_max(self):
        """
        获取 Mean 的最大值
        return:
        {'Name': 'gw_elk2', 'Mean': '77.8%', 'Max': '78.1%'}
        """
        parsed_data = self.parse()
        if not parsed_data:
            return None
        
        # 找到Max值最大的元素
        max_value = max(parsed_data, key=lambda x: self.convert_to_comparable(x["Mean"]))
        
        return max_value
    
    

if __name__ == "__main__":
    data = f"""Name Max Mean
    idk-mob-sdk-server-69d8dd8d9c-6k94f
    0.99 GB 2.44 GB
    idk-mob-sdk-server-69d8dd8d9c-ck6p2
    2.53 GB 2.52 GB
    idk-mob-sdk-server-69d8dd8d9c-l9n7k
    2.45 GB 9 GB
    idk-mob-sdk-server-69d8dd8d9c-ntw7t
    2.44 GB 10000 MB
    idk-mob-sdk-server-69d8dd8d9c-p6rlv
    2.46 GB 2.45 GB
    idk-mob-sdk-server-69d8dd8d9c-sf4zx
    8.88 GB 2.46 GB
    idk-mob-sdk-server-69d8dd8d9c-w2qp2
    10 GB 2.47 GB"""



    legend_table = LegendTable(data)
    parsed_data = legend_table.parse()
    print(parsed_data)
    print("MAX ====================", legend_table.get_max())
    print("Mean max ===============", legend_table.get_mean_max())
