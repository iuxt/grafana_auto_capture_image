import requests


def query_prometheus(expr, start, end):
    """
    查询 prometheus 数据
    """
    url = 'https://prometheus.example.com/api/v1/query_range'
    params = {
        'query': expr,
        'start': start,
        'end': end,
        'step': '6h'
    }
    response = requests.get(url, params=params)
    print(response.url)
    return response.json()


def get_max_value(data):
    """
    从 prometheus 数据中获取最大值
    """
    max_value = float('-inf')
    for item in data['data']['result']:
        for value in item['values']:
            max_value = max(max_value, float(value[1]))
    return max_value


if __name__ == '__main__':
    expr = '1 - avg(irate(node_cpu_seconds_total{project="gw",k8s="gw",mode="idle"}[3m])) by (instance)'
    start = '2026-01-01T00:00:00Z'
    end = '2026-01-01T23:00:00Z'
    data = query_prometheus(expr, start, end)
    print(data)
    max_value = get_max_value(data)
    print(max_value)