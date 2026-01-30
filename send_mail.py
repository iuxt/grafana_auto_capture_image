#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import os
from dotenv import load_dotenv 
import tempfile
from email import encoders
import zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import utils
import json
from datetime import datetime


# 打包文件
def zip_files(source_dir, zip_filename):
    """
    zip_files 的 Docstring
    
    :param source_dir: 要打包的目录
    :param zip_filename: 打包后的文件名
    """
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(source_dir):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                zipf.write(filepath, os.path.relpath(filepath, source_dir))


# 发送邮件
def send_email(zip_filename, to_email, subject=None, body=None, from_email=None, password=None, smtp_server=None, smtp_port=465):
    # 设置邮件内容
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    # 添加附件
    part = MIMEBase('application', 'octet-stream')
    with open(zip_filename, "rb") as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        'attachment',
        filename=os.path.basename(zip_filename)  # 使用filename参数自动处理引号
    )
    print(os.path.basename(zip_filename))
    msg.attach(part)

    # 连接邮件服务器并发送邮件
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, msg['To'].split(','), text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def get_email_content(json_file='monitor_data.json'):
    """
    生成邮件内容的HTML报告
    
    Args:
        json_file: 包含监控数据的JSON文件路径
    Returns:
        HTML内容字符串
    """
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)


    # 按panel_name分组数据
    grouped_data = {}
    for item in json_data:
        panel_name = item.get('panel_name', '未知面板')
        if panel_name not in grouped_data:
            grouped_data[panel_name] = []
        grouped_data[panel_name].append(item)
    
    # 获取报告生成时间
    report_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # HTML模板
    html_template = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>系统监控报告</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f5f5f5;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 10px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                font-weight: 300;
            }}
            
            .header .subtitle {{
                font-size: 1.1rem;
                opacity: 0.9;
                margin-bottom: 5px;
            }}
            
            .summary {{
                padding: 25px;
                background: #f8f9fa;
                border-bottom: 1px solid #eaeaea;
            }}
            
            .summary-stats {{
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                gap: 20px;
            }}
            
            .stat-box {{
                flex: 1;
                min-width: 200px;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                text-align: center;
            }}
            
            .stat-box h3 {{
                color: #1a237e;
                margin-bottom: 10px;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            .stat-value {{
                font-size: 1.8rem;
                font-weight: bold;
                color: #333;
            }}
            
            .panels {{
                padding: 25px;
            }}
            
            .panel-group {{
                margin-bottom: 40px;
            }}
            
            .panel-title {{
                font-size: 1.4rem;
                color: #1a237e;
                padding-bottom: 10px;
                margin-bottom: 20px;
                border-bottom: 2px solid #eaeaea;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .panel-title i {{
                font-size: 1.2rem;
            }}
            
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }}
            
            .metric-card {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.08);
                border-left: 4px solid #1a237e;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .metric-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            
            .metric-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            
            .metric-name {{
                font-weight: 600;
                color: #333;
                font-size: 1.1rem;
            }}
            
            .metric-value {{
                font-size: 1.5rem;
                font-weight: bold;
                margin: 15px 0;
                color: #1a237e;
            }}
            
            .labels {{
                background: #f8f9fa;
                padding: 12px;
                border-radius: 6px;
                margin-top: 15px;
                font-size: 0.9rem;
            }}
            
            .label-item {{
                margin-bottom: 5px;
                display: flex;
            }}
            
            .label-key {{
                font-weight: 600;
                color: #555;
                min-width: 100px;
            }}
            
            .label-value {{
                color: #333;
            }}
            
            .timestamp {{
                color: #666;
                font-size: 0.9rem;
                margin-top: 10px;
                padding-top: 10px;
                border-top: 1px solid #eee;
            }}
            
            .severity-normal {{
                border-left-color: #4CAF50;
            }}
            
            .severity-warning {{
                border-left-color: #FF9800;
            }}
            
            .severity-critical {{
                border-left-color: #F44336;
            }}
            
            .footer {{
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                color: #666;
                font-size: 0.9rem;
                border-top: 1px solid #eaeaea;
            }}
            
            .report-info {{
                display: flex;
                justify-content: space-between;
                margin-top: 15px;
                font-size: 0.85rem;
                color: #888;
            }}
            
            @media (max-width: 768px) {{
                .metrics-grid {{
                    grid-template-columns: 1fr;
                }}
                
                .summary-stats {{
                    flex-direction: column;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 系统监控报告</h1>
                <div class="subtitle">系统健康状态与性能指标分析</div>
                <div class="subtitle">报告生成时间: {report_time}</div>
            </div>
            
            <div class="summary">
                <h2 style="color: #1a237e; margin-bottom: 20px;">📈 概览统计</h2>
                <div class="summary-stats">
                    <div class="stat-box">
                        <h3>监控指标总数</h3>
                        <div class="stat-value">{len(json_data)}</div>
                    </div>
                    <div class="stat-box">
                        <h3>监控面板数量</h3>
                        <div class="stat-value">{len(grouped_data)}</div>
                    </div>
                    <div class="stat-box">
                        <h3>数据时间范围</h3>
                        <div class="stat-value">
                            {min([item.get('timestamp_formatted', '') for item in json_data if item.get('timestamp_formatted')], default='N/A')}<br>
                            ~<br>
                            {max([item.get('timestamp_formatted', '') for item in json_data if item.get('timestamp_formatted')], default='N/A')}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="panels">
    """
    
    # 为每个面板组添加内容
    for panel_name, items in grouped_data.items():
        # 根据面板名称选择图标
        icon = "📊"
        if "MySQL" in panel_name:
            icon = "🗄️"
        elif "CPU" in panel_name or "内存" in panel_name:
            icon = "⚡"
        elif "磁盘" in panel_name:
            icon = "💾"
        elif "Redis" in panel_name:
            icon = "🔴"
        elif "负载" in panel_name:
            icon = "📈"
        elif "重启" in panel_name:
            icon = "🔄"
        
        html_template += f"""
                <div class="panel-group">
                    <div class="panel-title">
                        <span>{icon}</span>
                        <span>{panel_name}</span>
                    </div>
                    <div class="metrics-grid">
        """
        
        for item in items:
            value = item.get('value', 0)
            labels = item.get('labels', {})
            timestamp = item.get('timestamp_formatted', '')
            
            # 根据数值确定严重程度
            severity_class = "severity-normal"
            if panel_name == "节点磁盘使用率" and value > 0.8:
                severity_class = "severity-critical"
            elif panel_name == "节点内存使用率" and value > 0.8:
                severity_class = "severity-warning"
            elif panel_name == "节点CPU使用率" and value > 0.7:
                severity_class = "severity-warning"
            
            # 格式化值
            formatted_value = str(value)
            if isinstance(value, float):
                if value < 1:
                    formatted_value = f"{value:.2%}" if "使用率" in panel_name or "百分比" in panel_name else f"{value:.3f}"
                else:
                    formatted_value = f"{value:,.2f}"
            
            # 创建标签HTML
            labels_html = ""
            if labels:
                labels_html += '<div class="labels">'
                for key, val in labels.items():
                    labels_html += f'''
                    <div class="label-item">
                        <span class="label-key">{key}:</span>
                        <span class="label-value">{val}</span>
                    </div>
                    '''
                labels_html += '</div>'
            
            html_template += f'''
                        <div class="metric-card {severity_class}">
                            <div class="metric-header">
                                <div class="metric-name">{panel_name}</div>
                            </div>
                            <div class="metric-value">{formatted_value}</div>
                            {labels_html}
                            <div class="timestamp">
                                📅 数据时间: {timestamp}
                            </div>
                        </div>
            '''
        
        html_template += """
                    </div>
                </div>
        """
    
    # HTML结尾
    html_template += f"""
            </div>
            
            <div class="footer">
                <p>本报告由系统监控平台自动生成</p>
                <p>如有任何异常指标，请及时联系相关技术人员处理</p>
                <div class="report-info">
                    <div>数据源: Prometheus监控系统</div>
                    <div>生成工具: Python HTML报告生成器</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template


def send_email_now(name=""):
    source_dir = "./screenshots"
    temp_dir = tempfile.mkdtemp()
    zip_filename = os.path.join(temp_dir, name + "_巡检报告_" + utils.get_year_month(os.getenv("DATE_FROM")) + ".zip")
    print(f"Temporary zip file will be created at: {zip_filename}")

    # 加载环境变量
    load_dotenv('.env')
    to_email = os.getenv('MAIL_RECEIVERS')
    from_email = os.getenv('EMAIL_USER')
    password = os.getenv('EMAIL_PASSWORD')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 465))

    # 打包文件
    zip_files(source_dir, zip_filename)

    body = get_email_content()

    # 发送邮件
    send_email(zip_filename=zip_filename, to_email=to_email, subject='巡检报告', body=body, 
               from_email=from_email, password=password, smtp_server=smtp_server, smtp_port=smtp_port)


if __name__ == "__main__":
    send_email_now()
