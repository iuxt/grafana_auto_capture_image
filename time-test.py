from datetime import datetime
from zoneinfo import ZoneInfo

# 获取当前 UTC 时间
utc_now = datetime.now(ZoneInfo("UTC"))
# 将 UTC 时间转换为北京时间
beijing_time = utc_now.astimezone(ZoneInfo("Asia/Shanghai"))

print("当前北京时间:", beijing_time.strftime('%Y-%m-%d %H:%M:%S'))