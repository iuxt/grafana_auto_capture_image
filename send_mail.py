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


def get_email_content():
    return "巡检报告详见附件，请查收。"


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
