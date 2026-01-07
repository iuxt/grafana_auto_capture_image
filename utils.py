import datetime
import re

def custom_yes_data_now_data(days=1):
    """
    专门给 prometheus 使用
    获取前几天的时间 days=2 默认生产2天前 2022-10-09T00:00:00.781Z
    获取当天时间 2022-10-11T12:59:59.781Z

    """
    now = datetime.datetime.now()
    now_data = now.strftime('%Y-%m-%dT%H:%M:00.781Z')
    yes_data = now + datetime.timedelta(days=-days)
    yes_data = yes_data.strftime('%Y-%m-%dT%H:%M:00.781Z')
    return yes_data, now_data


def convert_time_format(time_str):
    """
    将带毫秒的ISO 8601时间格式转换为不带毫秒的格式
    输入: 2025-12-02T00:00:00.000Z
    输出: 2025-12-02T00:00:00Z
    """
    if not time_str:
        return time_str
    
    # 使用正则表达式匹配并移除毫秒部分
    # 匹配模式: 2025-12-02T00:00:00.000Z -> 2025-12-02T00:00:00Z
    pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\.\d+Z$'
    match = re.match(pattern, time_str)
    
    if match:
        return f"{match.group(1)}Z"
    
    # 如果输入格式已经是不带毫秒的，则直接返回
    return time_str


# 使用示例
if __name__ == "__main__":
    time_with_ms = "2025-12-02T00:00:00.000Z"
    time_without_ms = convert_time_format(time_with_ms)
    print(f"转换前: {time_with_ms}")
    print(f"转换后: {time_without_ms}")