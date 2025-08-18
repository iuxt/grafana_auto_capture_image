from dotenv import load_dotenv
import os
import json
from datetime import datetime

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
    def read_result_file(filename):
        """读取结果文件并返回字典"""
        metrics = {}
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    key, value = line.strip().split('\t')
                    metrics[key.strip()] = float(value.strip())
        return metrics
    
    @staticmethod
    def get_risk_level(metric_name, value):
        """根据指标名称和值返回风险等级"""
        thresholds = {
            'MySQL连接数百分比': (80, 90),
            '每分钟慢查询数量': (5, 10),
            'CPU使用率': (80, 90),
            '磁盘使用率': (80, 90),
            '内存使用率': (80, 90),
            '重启次数统计': (1, 3),
            '每秒操作数': (1000, 2000),
            'Kafka消费组延迟': (5000, 10000),
            'SDK服务响应延迟水位线': (0.5, 1.0),
            '表占用空间概览Top10': (51200, 102400)
        }
        
        if metric_name not in thresholds:
            return 'normal'
        
        warn, critical = thresholds[metric_name]
        if value >= critical:
            return 'critical'
        elif value >= warn:
            return 'warning'
        else:
            return 'normal'
    
    @staticmethod
    def get_html_content(filename, title):
        """
        生成极简HTML监控报告
        """
        metrics = Utils.read_result_file(filename)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.5;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        .timestamp {{
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background-color: #f5f5f5;
        }}
        .normal {{ color: #27ae60; }}
        .warning {{ color: #f39c12; }}
        .critical {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <div class="timestamp">报告时间: {current_time}</div>
    
    <table>
        <thead>
            <tr>
                <th>监控指标</th>
                <th>当前值</th>
                <th>状态</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for metric, value in metrics.items():
            risk_level = Utils.get_risk_level(metric, value)
            
            if '百分比' in metric or '率' in metric:
                display_value = f"{value}%"
            else:
                display_value = str(value)
            
            risk_label = {
                'normal': '正常',
                'warning': '警告',
                'critical': '危险'
            }.get(risk_level, '正常')
            
            html_content += f"""
            <tr>
                <td>{metric}</td>
                <td>{display_value}</td>
                <td class="{risk_level}">{risk_label}</td>
            </tr>
            """
        
        html_content += """
        </tbody>
    </table>
    
    <div style="text-align: center; color: #95a5a6; margin-top: 30px;">
        自动生成报告 · © 2025 系统监控
    </div>
</body>
</html>
"""
        return html_content

if __name__ == "__main__":
    utils = Utils()
    html = utils.get_html_content("result.txt", "系统监控报告")
    
    # 将HTML写入文件
    with open("monitor_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("HTML报告已生成: monitor_report.html")