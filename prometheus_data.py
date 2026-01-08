from dotenv import load_dotenv
import requests
from datetime import datetime
import os


load_dotenv()

def query_prometheus(expr, start, end):
    """
    查询 prometheus 数据
    """
    url = os.getenv('PROMETHEUS_URL') + '/api/v1/query_range'
    params = {
        'query': expr,
        'start': start,
        'end': end,
        'step': '1m'
    }
    response = requests.get(url, params=params)
    print(response.url)
    return response.json()


def get_max_value_with_labels(data):
    """
    从 prometheus 数据中获取最大值及对应的标签信息
    
    Args:
        data: Prometheus API返回的JSON数据
        
    Returns:
        dict: 包含最大值及对应标签信息的字典，格式如下：
            {
                'max_value': float,        # 最大值
                'max_value_formatted': str, # 格式化的最大值
                'labels': dict,            # 对应的标签信息
                'timestamp': float,        # 最大值出现的时间戳
                'timestamp_formatted': str, # 格式化的时间戳
                'metric': dict             # 完整的metric信息
            }
    """
    # 初始化结果
    result = {
        'max_value': None,
        'max_value_formatted': None,
        'labels': None,
        'timestamp': None,
        'timestamp_formatted': None,
        'metric': None
    }
    
    # 数据验证
    if not isinstance(data, dict):
        print("错误：数据不是字典类型")
        return result
        
    if 'data' not in data or 'result' not in data['data']:
        print("错误：数据结构不符合预期")
        return result
    
    max_value = float('-inf')
    max_value_info = None
    
    # 遍历所有查询结果
    for item in data['data']['result']:
        # 获取metric信息和标签
        metric = item.get('metric', {})
        labels = metric.copy()
        
        # 遍历时间序列数据
        for value in item.get('values', []):
            if not isinstance(value, list) or len(value) < 2:
                continue
                
            try:
                # 转换值和时间戳
                current_value = float(value[1])
                timestamp = float(value[0])
                
                # 跳过NaN值
                if current_value != current_value:
                    continue
                    
                # 更新最大值信息
                if current_value > max_value:
                    max_value = current_value
                    max_value_info = {
                        'max_value': current_value,
                        'labels': labels,
                        'timestamp': timestamp,
                        'metric': metric
                    }
                    
            except (ValueError, TypeError) as e:
                print(f"错误：解析值或时间戳失败 - {e}")
                continue
    
    # 如果找到最大值，更新结果
    if max_value_info:
        result.update(max_value_info)
        # 格式化输出
        result['max_value_formatted'] = f"{result['max_value']:.6f}"
        result['timestamp_formatted'] = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    
    return result


if __name__ == '__main__':
    expr = 'sum(increase(http_method_duration_seconds_count{project=~"gw",k8s="gw",service="idk-mob-sdk-server"}[1m])) by ( service )'
    start = '2026-01-01T00:00:00Z'
    end = '2026-01-01T23:00:00Z'
    
    # 查询数据
    data = query_prometheus(expr, start, end)
    
    # 获取最大值及标签信息
    max_info = get_max_value_with_labels(data)
    
    # 打印结果
    print("\n===== 查询结果 =====")
    if max_info['max_value'] is not None:
        print(max_info)
        print(f"最大值: {max_info['max_value_formatted']}")
        print(f"最大值出现时间: {max_info['timestamp_formatted']}")
        print(f"对应的标签信息: {max_info['labels']}")
        print(f"完整的metric信息: {max_info['metric']}")
    else:
        print("未找到有效数据")