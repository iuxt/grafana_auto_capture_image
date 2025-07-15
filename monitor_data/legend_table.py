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
        gw_elk3
        77.8% 78.0%
        gw_k8s_node_4
        75.3% 75.7%
        gw_k8s_node_8
        41.5% 47.4%
        gw_k8s_node_7
        46.5% 46.8%
        gw_k8s_node_1
        41.5% 41.8%
        gw_k8s_node_3
        39.1% 40.0%
        gw_kafka2
        39.0% 39.2%
        gw_k8s_node_2
        34.5% 35.0%
        gw_kafka1
        27.7% 27.9%
        gw_k8s_node_5
        24.9% 25.2%
        gw_k8s_node_6
        24.6% 25.0%
        gw_kafka3
        24.4% 24.6%

        
        output:
        [
            {"Name": "gw_elk1", "Mean": "79.3%", "Max": "79.5%"},
            {"Name": "gw_elk2", "Mean": "77.8%", "Max": "78.1%"},
            {"Name": "gw_k8s_node_4", "Mean": "75.3%", "Max": "75.7%"}
        ]
        """
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

        return result


    def get_max_value(self):
        """
        获取最大值
        return:
        {'Name': 'gw_elk1', 'Mean': '79.3%', 'Max': '79.5%'}
        """
        parsed_data = self.parse()
        if not parsed_data:
            return None
        max_value = max(parsed_data, key=lambda x: float(x["Max"].replace('%', '')))
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
        max_value = max(parsed_data, key=lambda x: float(x["Mean"].replace('%', '')))
        return max_value
    
    

if __name__ == "__main__":
    data = f"""Name Mean Max
    gw_elk1
    79.3% 79.5%
    gw_elk2
    77.8% 78.1%
    gw_elk3
    77.8% 78.0%
    gw_k8s_node_4
    75.3% 75.7%
    gw_k8s_node_8
    41.5% 47.4%
    gw_k8s_node_7
    46.5% 46.8%
    gw_k8s_node_1
    41.5% 41.8%
    gw_k8s_node_3
    39.1% 40.0%
    gw_kafka2
    39.0% 39.2%
    gw_k8s_node_2
    34.5% 35.0%
    gw_kafka1
    27.7% 27.9%
    gw_k8s_node_5
    24.9% 25.2%
    gw_k8s_node_6
    24.6% 25.0%
    gw_kafka3
    24.4% 24.6%"""



    legend_table = LegendTable(data)
    parsed_data = legend_table.parse()
    print(parsed_data)


    """
    [
        {"Name": "gw_elk1", "Mean": "79.3%", "Max": "79.5%"},
        {"Name": "gw_elk2", "Mean": "77.8%", "Max": "78.1%"},
        {"Name": "gw_k8s_node_4", "Mean": "75.3%", "Max": "75.7%"}
    ]
    """
