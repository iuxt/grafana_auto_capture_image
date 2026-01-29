
# 转换时间格式
from datetime import datetime, timedelta
import pytz
import re

# 当前的UTC时间
utc_now = datetime.now(pytz.UTC)


def convert_time_format(time_str):
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
    

# 示例用法
if __name__ == "__main__":
    print(convert_time_format("now/M"))  # 本月第一天
    print(convert_time_format("now"))     # 当前时间
    print(convert_time_format("now-7d"))  # 7天前的时间
    print(convert_time_format("2023-10-01T00:00:00.000Z"))  # 原样返回

    print(type(convert_time_format("now/M")))