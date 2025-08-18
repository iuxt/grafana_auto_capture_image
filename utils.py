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
            '每分钟慢查询数量': (10, 20),
            'CPU使用率': (80, 90),
            '磁盘使用率': (80, 90),
            '内存使用率': (80, 90),
            '重启次数统计': (1, 3),
            '每秒操作数': (1000, 2000),
            'Kafka消费组延迟': (5000, 10000),
            'SDK服务响应延迟水位线': (0.5, 1.0)
        }
        
        if metric_name not in thresholds:
            return 'low-risk'
        
        warn, critical = thresholds[metric_name]
        if value >= critical:
            return 'high-risk'
        elif value >= warn:
            return 'medium-risk'
        else:
            return 'low-risk'
    
    @staticmethod
    def get_html_content(filename, title):
        """
        从结果文件中生成HTML内容
        """
        # 读取指标数据
        metrics = Utils.read_result_file(filename)
        
        # 获取当前时间
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 开始构建HTML
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary-color: #3498db;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --light-color: #ecf0f1;
            --dark-color: #2c3e50;
            --text-color: #34495e;
            --border-color: #bdc3c7;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            color: var(--text-color);
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 30px auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, var(--dark-color), var(--primary-color));
            color: white;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 25px;
            position: relative;
            overflow: hidden;
        }}
        
        .header::after {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            transform: translate(30%, -30%);
        }}
        
        .header h2 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        
        .timestamp {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        .status-card {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }}
        
        .card {{
            background-color: white;
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
            flex: 1;
            min-width: 200px;
            margin: 0 10px 15px 10px;
            border-left: 4px solid var(--primary-color);
        }}
        
        .card-title {{
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        
        .card-value {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }}
        
        .card.low-risk {{ border-left-color: var(--success-color); }}
        .card.medium-risk {{ border-left-color: var(--warning-color); }}
        .card.high-risk {{ border-left-color: var(--danger-color); }}
        
        .monitor-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border-radius: 6px;
            overflow: hidden;
        }}
        
        .monitor-table th, .monitor-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .monitor-table th {{
            background-color: var(--dark-color);
            color: white;
            font-weight: 500;
        }}
        
        .monitor-table tr:nth-child(even) {{
            background-color: var(--light-color);
        }}
        
        .monitor-table tr:hover {{
            background-color: rgba(52, 152, 219, 0.1);
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            color: white;
        }}
        
        .low-risk {{ background-color: var(--success-color); }}
        .medium-risk {{ background-color: var(--warning-color); }}
        .high-risk {{ background-color: var(--danger-color); }}
        
        .progress-container {{
            background-color: #e0e0e0;
            border-radius: 10px;
            height: 10px;
            width: 100%;
            margin-top: 8px;
            overflow: hidden;
        }}
        
        .progress-bar {{
            height: 100%;
            border-radius: 10px;
        }}
        
        .summary {{
            margin-top: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid var(--primary-color);
        }}
        
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: #95a5a6;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                padding: 15px;
            }}
            
            .card {{
                min-width: 100%;
                margin: 0 0 15px 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{title}</h2>
            <p class="timestamp">报告生成时间: {current_time}</p>
        </div>
        
        <div class="status-card">
            <!-- 关键指标卡片 -->
            <div class="card {Utils.get_risk_level('CPU使用率', metrics.get('CPU使用率', 0))}">
                <div class="card-title">CPU使用率</div>
                <div class="card-value">{metrics.get('CPU使用率', 0)}%</div>
            </div>
            
            <div class="card {Utils.get_risk_level('内存使用率', metrics.get('内存使用率', 0))}">
                <div class="card-title">内存使用率</div>
                <div class="card-value">{metrics.get('内存使用率', 0)}%</div>
            </div>
            
            <div class="card {Utils.get_risk_level('磁盘使用率', metrics.get('磁盘使用率', 0))}">
                <div class="card-title">磁盘使用率</div>
                <div class="card-value">{metrics.get('磁盘使用率', 0)}%</div>
            </div>
            
            <div class="card {Utils.get_risk_level('MySQL连接数百分比', metrics.get('MySQL连接数百分比', 0))}">
                <div class="card-title">MySQL连接数</div>
                <div class="card-value">{metrics.get('MySQL连接数百分比', 0)}%</div>
            </div>
        </div>
        
        <table class="monitor-table">
            <thead>
                <tr>
                    <th>监控指标</th>
                    <th>当前值</th>
                    <th>状态</th>
                    <th>可视化</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 添加表格行
        for metric, value in metrics.items():
            risk_level = Utils.get_risk_level(metric, value)
            
            # 根据指标类型格式化值
            if '百分比' in metric or '率' in metric:
                display_value = f"{value}%"
                progress_width = min(value, 100)
            else:
                display_value = str(value)
                progress_width = 0  # 非百分比指标不显示进度条
            
            # 风险等级标签
            risk_label = {
                'low-risk': '正常',
                'medium-risk': '警告',
                'high-risk': '危险'
            }.get(risk_level, '正常')
            
            html_content += f"""
                <tr>
                    <td>{metric}</td>
                    <td>{display_value}</td>
                    <td><span class="status-badge {risk_level}">{risk_label}</span></td>
                    <td>
                        <div class="progress-container">
                            <div class="progress-bar {risk_level}" style="width: {progress_width}%"></div>
                        </div>
                    </td>
                </tr>
            """
        
        # 结束HTML
        html_content += """
            </tbody>
        </table>
        
        <div class="summary">
            <h3>系统健康状态概览</h3>
            <p>本次监控共检查了 {} 项指标，其中：</p>
            <ul>
                <li><span class="status-badge low-risk">正常</span> 指标: {} 项</li>
                <li><span class="status-badge medium-risk">警告</span> 指标: {} 项</li>
                <li><span class="status-badge high-risk">危险</span> 指标: {} 项</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>© 2023 系统监控平台 | 本报告自动生成，数据仅供参考</p>
        </div>
    </div>
</body>
</html>
""".format(len(metrics), 
           sum(1 for m in metrics if Utils.get_risk_level(m, metrics[m]) == 'low-risk'),
           sum(1 for m in metrics if Utils.get_risk_level(m, metrics[m]) == 'medium-risk'),
           sum(1 for m in metrics if Utils.get_risk_level(m, metrics[m]) == 'high-risk'))
        
        return html_content


if __name__ == "__main__":
    utils = Utils()
    html = utils.get_html_content("result.txt", "系统监控报告")
    
    # 将HTML写入文件
    with open("monitor_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("HTML报告已生成: monitor_report.html")