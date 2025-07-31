from pathlib import Path
from dotenv import load_dotenv
import pymysql
from datetime import datetime
import os


class SaveData:
    def __init__(self):
        env_path = Path(__file__).resolve().parent.parent / '.env'
        load_dotenv(env_path)


    def insert_result_to_file(self, title, data, filename='result.txt'):
        """将结果写入结果文件"""
        print("写入到结果文件---------", filename , '---------')
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(title + '\t')
            f.write(str(data) + '\n')


    def pymysql_write(self, manufacturer, name, max_value, mean_max=None):
        create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            connection = pymysql.connect(
                host=os.getenv('MYSQL_HOST'),
                user=os.getenv('MYSQL_USER'),
                password=os.getenv('MYSQL_PASSWORD'),
                database=os.getenv('MYSQL_DATABASE'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            with connection.cursor() as cursor:
                # 插入数据
                sql = "INSERT INTO `usage` (manufacturer, name, max, mean_max, create_time) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(sql, (manufacturer, name, max_value, mean_max, create_time))
                result = cursor.fetchall()
                print(result)
            connection.commit()
            print("MySQL写入成功")
        finally:
            connection.close()


if __name__ == "__main__":
    save_data = SaveData()
    save_data.pymysql_write("Test Manufacturer", 100, 50)