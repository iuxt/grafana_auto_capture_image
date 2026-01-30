from datetime import datetime, timedelta
import pytz
import re

# 当前的UTC时间
utc_now = datetime.now(pytz.UTC)


def convert_time_format(time_str):
    """
    convert_time_format 的 Docstring
    将类似 "now/M", "now", "now-7d" 等格式的时间字符串转换为具体的 UTC 时间字符串。给Grafana使用
    如果输入的时间字符串不符合上述格式，则直接返回原字符串。
    :param time_str: 说明
    """
    if time_str == "now/M":
        # 计算本月第一天（UTC时间 00:00:00.000）
        date = utc_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    elif time_str == "now": 
        # 当前时间格式化（毫秒固定为000，与示例格式一致）
        date = utc_now.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return date
    elif re.match(r"now-(\d+)d", time_str):
        # 提取数字并转为整数（动态获取偏移天数）
        match = re.match(r"now-(\d+)d", time_str)
        days = int(match.group(1))
        # 计算偏移后的时间 + 格式化（保留原格式：YYYY-MM-DDTHH:mm:ss.000Z）
        offset_date = (utc_now - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        return offset_date
    else:
        return time_str
    

def get_year_month(time_str):
    """
    get_year_month 的 Docstring
    从时间字符串中提取年月部分（YYYY-MM）
    :param time_str: 时间字符串，格式为 "2025-12-02T00:00:00.000Z"
    :return: 年月字符串，格式为 "2025-12"
    """
    if not time_str:
        return ""
    
    # 使用 datetime 解析时间字符串，提取年月部分
    date = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.000Z")
    return date.strftime("%Y-%m")



def convert_to_prometheus_format(time_str):
    """
    将带毫秒的ISO 8601时间格式转换为不带毫秒的格式
    Grafana需要使用 带 ms 的格式
    Prometheus使用不带 ms 的格式
    
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
    time_without_ms = convert_to_prometheus_format(time_with_ms)
    print(f"转换前: {time_with_ms}")
    print(f"转换后: {time_without_ms}")

    print(convert_time_format("now/M"))  # 本月第一天
    print(convert_time_format("now"))     # 当前时间
    print(convert_time_format("now-7d"))  # 7天前的时间
    print(convert_time_format("2023-10-01T00:00:00.000Z"))  # 原样返回
    print(type(convert_time_format("now/M")))
