class Table:
    def __init__(self, title, data):
        self.title = title
        self.data = data


    def parse_table_data(self) -> list:
        """
        将表格数据转换为JSON格式
        
        :param title: 标题行，包含列名
        :param data: 数据内容
        :return: JSON格式的数据列表
        """
        # 提取列名
        headers = [line.strip() for line in self.title.strip().split('\n') if line.strip()]
        
        # 处理数据行
        lines = [line.strip() for line in self.data.strip().split('\n') if line.strip()]

        # 计算每组数据的行数 (列数)
        group_size = len(headers)
        if group_size == 0:
            return []
        
        result = []
        for i in range(0, len(lines), group_size):
            # 确保有足够的数据行
            if i + group_size - 1 >= len(lines):
                break
                
            # 创建每个数据项
            item = {}
            for j in range(group_size):
                # 尝试将数字转换为int/float
                value = lines[i + j]
                if value.isdigit():
                    value = int(value)
                else:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                
                item[headers[j]] = value
            
            result.append(item)
        
        return result


if __name__ == "__main__":
    # 示例数据
    title = """Time
    Pod名
    时间范围内重启次数111
    """

    data = """
    2025-07-29 23:32:09.486
    idk-mob-sdk-server-69d8dd8d9c-6k94f
    0
    2025-07-29 23:32:09.486
    idk-mob-sdk-server-69d8dd8d9c-ck6p2
    0
    2025-07-29 23:32:09.486
    idk-mob-sdk-server-69d8dd8d9c-l9n7k
    0
    2025-07-29 23:32:09.486
    idk-mob-sdk-server-69d8dd8d9c-ntw7t
    0
    2025-07-29 23:32:09.486
    mysql-exporter-76c6cc6b49-ddts4
    0
    """
    table = Table(title, data)
    # 转换数据
    json_data = table.parse_table_data()
    import json
    # 输出结果
    print(json.dumps(json_data, indent=2, ensure_ascii=False))

