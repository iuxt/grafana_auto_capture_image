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

    end_dt = datetime.strptime(end, '%Y-%m-%dT%H:%M:%SZ')
    start_dt = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ')

    # 根据查询时间范围调整 step 参数
    if (end_dt - start_dt).days > 15:
        step = '6h'
    elif (end_dt - start_dt).days > 5:
        step = '1h'
    else:
        step = '5m'

    # 根据时间范围替换range变量
    if '$__range' in expr:
        expr = expr.replace('$__range', f'{(end_dt - start_dt).days}d')

    print(f"查询 Prometheus: {expr}, 开始时间: {start}, 结束时间: {end}, 查询时间范围: {end_dt - start_dt}, step: {step}, 设置 step 参数: {step}")

    params = {
        'query': expr,
        'start': start,
        'end': end,
        'step': step
    }
    response = requests.get(url, params=params)
    return response.json()


def get_max_value_with_labels(data):
    """
    从 prometheus 数据中获取最大值及对应的标签信息
    
    Args:
        data: Prometheus API返回的JSON数据
        
    Returns:
        dict: 包含最大值及对应标签信息的字典，格式如下：
            {
                'value': float,        # 最大值
                'labels': dict,            # 对应的标签信息
                'timestamp': float,        # 最大值出现的时间戳
                'timestamp_formatted': str, # 格式化的时间戳
            }
    """
    # 初始化结果
    result = {
        'value': None,
        'labels': None,
        'timestamp': None,
        'timestamp_formatted': None
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
        labels = item.get('metric', {})
        
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
                        'value': current_value,
                        'labels': labels,
                        'timestamp': timestamp
                    }
                    
            except (ValueError, TypeError) as e:
                print(f"错误：解析值或时间戳失败 - {e}")
                continue
    
    # 如果找到最大值，更新结果
    if max_value_info:
        result.update(max_value_info)
        # 格式化输出
        result['timestamp_formatted'] = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    
    return result


def get_min_value_with_labels(data):
    """
    从 prometheus 数据中获取最小值及对应的标签信息
    
    Args:
        data: Prometheus API返回的JSON数据
        
    Returns:
        dict: 包含最小值及对应标签信息的字典，格式如下：
            {
                'value': float,        # 最小值
                'labels': dict,            # 对应的标签信息
                'timestamp': float,        # 最小值出现的时间戳
                'timestamp_formatted': str, # 格式化的时间戳
            }
    """
    # 初始化结果
    result = {
        'value': None,
        'labels': None,
        'timestamp': None,
        'timestamp_formatted': None
    }
    
    # 数据验证
    if not isinstance(data, dict):
        print("错误：数据不是字典类型")
        return result
        
    if 'data' not in data or 'result' not in data['data']:
        print("错误：数据结构不符合预期")
        return result
    
    min_value = float('inf')
    min_value_info = None
    
    # 遍历所有查询结果
    for item in data['data']['result']:
        # 获取metric信息和标签
        labels = item.get('metric', {})
        
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
                    
                # 更新最小值信息
                if current_value < min_value:
                    min_value = current_value
                    min_value_info = {
                        'value': current_value,
                        'labels': labels,
                        'timestamp': timestamp
                    }
                    
            except (ValueError, TypeError) as e:
                print(f"错误：解析值或时间戳失败 - {e}")
                continue
    
    # 如果找到最小值，更新结果
    if min_value_info:
        result.update(min_value_info)
        # 格式化输出
        result['timestamp_formatted'] = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    
    return result


def get_avg_value_with_labels(data):
    """
    从 prometheus 数据中获取平均值及相关信息
    
    Args:
        data: Prometheus API返回的JSON数据
        
    Returns:
        dict: 包含平均值及相关信息的字典，格式如下：
            {
                'value': float,        # 平均值
                'total_samples': int,      # 有效样本数量
                'labels': list            # 所有labels信息
            }
    """
    # 初始化结果
    result = {
        'value': None,
        'total_samples': 0
    }
    
    # 数据验证
    if not isinstance(data, dict):
        print("错误：数据不是字典类型")
        return result
        
    if 'data' not in data or 'result' not in data['data']:
        print("错误：数据结构不符合预期")
        return result
    
    total_value = 0.0
    sample_count = 0
    
    # 遍历所有查询结果
    for item in data['data']['result']:

        # 遍历时间序列数据
        for value in item.get('values', []):
            if not isinstance(value, list) or len(value) < 2:
                continue
                
            try:
                # 转换值
                current_value = float(value[1])
                
                # 跳过NaN值
                if current_value != current_value:
                    continue
                    
                # 累加值和计数
                total_value += current_value
                sample_count += 1
                    
            except (ValueError, TypeError) as e:
                print(f"错误：解析值或时间戳失败 - {e}")
                continue
    
    # 如果有有效样本，计算平均值
    if sample_count > 0:
        avg_value = total_value / sample_count
        result['value'] = avg_value
        result['total_samples'] = sample_count
    
    return result



if __name__ == '__main__':
    expr = 'sum(increase(http_method_duration_seconds_count{project=~"gw",k8s="gw",service="idk-mob-sdk-server"}[$__range])) by ( service )'
    start = '2025-12-17T00:00:00Z'
    end = '2026-01-01T23:00:00Z'
    
    # 查询数据
    data = query_prometheus(expr, start, end)
    
    # 获取最大值及标签信息
    max_info = get_max_value_with_labels(data)
    
    # 打印结果
    print("\n===== 最大值查询结果 =====")
    if max_info['value'] is not None:
        print(f"最大值: {max_info['value']}")
        print(f"最大值出现时间: {max_info['timestamp_formatted']}")
        print(f"对应的标签信息: {max_info['labels']}")
    else:
        print("未找到有效数据")
    
    # 获取最小值及标签信息
    min_info = get_min_value_with_labels(data)
    
    # 打印结果
    print("\n===== 最小值查询结果 =====")
    if min_info['value'] is not None:
        print(f"最小值: {min_info['value']}")
        print(f"最小值出现时间: {min_info['timestamp_formatted']}")
        print(f"对应的标签信息: {min_info['labels']}")
    else:
        print("未找到有效数据")
    
    # 获取平均值及相关信息
    avg_info = get_avg_value_with_labels(data)
    
    # 打印结果
    print("\n===== 平均值查询结果 =====")
    if avg_info['value'] is not None:
        print(f"平均值: {avg_info['value']}")
        print(f"有效样本数量: {avg_info['total_samples']}")
    else:
        print("未找到有效数据")

    print(max_info)
    print(min_info)
    print(avg_info)