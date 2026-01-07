def custom_yes_data_now_data(days=1):
    """
    专门给 prometheus 使用
    获取前几天的时间 days=2 默认生产2天前 2022-10-09T00:00:00.781Z
    获取当天时间 2022-10-11T12:59:59.781Z

    """
    import datetime
    now = datetime.datetime.now()
    now_data = now.strftime('%Y-%m-%dT%H:%M:00.781Z')
    yes_data = now + datetime.timedelta(days=-days)
    yes_data = yes_data.strftime('%Y-%m-%dT%H:%M:00.781Z')
    return yes_data, now_data
