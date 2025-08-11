from dotenv import load_dotenv
import os
import json

# 在模块加载时初始化环境变量
load_dotenv('.env')

class Utils:
    @staticmethod
    def get_name(uid):
        name_mapping_str = os.getenv("NAME_MAPPING")
        if name_mapping_str is None:
            raise ValueError("NAME_MAPPING environment variable not found")
        
        try:
            name_mapping = json.loads(name_mapping_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in NAME_MAPPING: {e}")
        
        return name_mapping.get(uid)  # 返回对应uid的值
    

    @staticmethod
    def get_title(dashboard_id, datetime):
        """
        获取邮件标题
        """
        date_str = datetime.strftime('%Y年%m月')
        if dashboard_id == 'w-service':
            return '达布溜运维巡检报告 - ' + date_str
        elif dashboard_id == 'c-service':
            return '吃运维巡检报告 - ' + date_str
        else:
            return '巡检报告' + date_str
        

    @staticmethod
    def get_html_content(filename,title,time):
        """
        从结果文件中生成HTML内容
        """

        html_content = f"""<!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ background-color: #2c3e50; color: white; padding: 15px; border-radius: 5px; }}
                .timestamp {{ font-size: 0.9em; color: #666; text-align: right; }}
                
                /* 表格样式 */
                .monitor-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 15px;
                }}
                .monitor-table th, .monitor-table td {{
                    padding: 10px 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                .monitor-table th {{
                    background-color: #f8f9fa;
                    color: #2c3e50;
                    font-weight: 600;
                }}
                
                /* 进度条样式 */
                .progress-container {{
                    background-color: #f3f3f3;
                    border-radius: 3px;
                    height: 20px;
                    width: 100%;
                    margin-top: 2px;
                }}
                .progress-bar {{
                    border-radius: 3px;
                    height: 100%;
                    color: white;
                    text-align: center;
                    line-height: 20px;
                    font-size: 0.9em;
                }}
                .low-risk {{ background-color: #28a745; }}    /* 绿色 */
                .medium-risk {{ background-color: #ffc107; }} /* 黄色 */
                .high-risk {{ background-color: #dc3545; }}   /* 红色 */
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{title}</h2>
                    <p class="timestamp">生成时间: {time}</p>
                </div>
                
                <table class="monitor-table">
                    <thead>
                        <tr>
                            <th>监控指标</th>
                            <th>最大值</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        return html_content



if __name__ == "__main__":
    utils = Utils()
    print(utils.get_name("3"))