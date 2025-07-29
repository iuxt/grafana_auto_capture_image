class SaveData:
    def __init__(self, filename):
        self.filename = filename

    
    def insert_result_to_file(self, title, data):
        """将结果写入结果文件"""
        print("写入到结果文件---------", self.filename , '---------')
        with open(self.filename, 'a', encoding='utf-8') as f:
            f.write(title + '\t')
            f.write(str(data) + '\n')


    # def get_org_data(self, data_type):
    #     # 获取title legend table类型的原始数据
    #     if data_type == 'legend':
    #         css = '//*[@class="css-5cr14k"]'
    #     elif data_type == 'table':
    #         css = '//*[@class="css-8fjwhi-row"]'
        
    #     for i in self.driver.find_elements(By.XPATH, css):
    #         data = i.text
    #     print("原始table数据=======", data)
    #     return data



    # if 'CPU使用率' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result(panel['title'], data)
    # elif '内存使用率' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result(panel['title'], data)
    # elif '磁盘使用率' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result(panel['title'], data)
    # elif 'SDK内存占用' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result('SDK服务POD内存占用量', data + 'GB')
    # elif '重启次数统计' in panel['title']:
    #     data = Table(data).get_table_max_data()
    #     save_result(panel['title'], str(data[1]))
    # elif 'MySQL连接数百分比' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result(panel['title'], data)  
    # elif '表占用空间概览Top10' in panel['title']:
    #     data, unit = Table(get_org_data('table')).get_table_max_data_and_unit()
    #     save_result(panel['title'], str(data) + unit)
    # elif '每分钟慢查询数量' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result(panel['title'], data)
    # elif 'Kafka消费组延迟' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result(panel['title'], data)
    # elif '每秒操作数' in panel['title']:
    #     data = LegendTable(get_org_data('legend')).get_max()
    #     save_result(panel['title'], data)
    # else:
    #     pass