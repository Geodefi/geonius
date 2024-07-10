# -*- coding: utf-8 -*-

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from src.globals import get_env, get_config, get_logger


def get_log_attachment():
    return (
        os.getcwd().join(get_config().directory).join(get_config().logger.directory).join("log"),
        "log.txt",
    )


def send_email(
    subject, body, attachments: list[tuple[str, str]] = None, send_attachments: str = True
):
    env = get_env()
    if send_attachments and not attachments:
        attachments: list[tuple[str, str]] = [get_log_attachment()]

    msg: MIMEMultipart = MIMEMultipart()
    msg['From'] = env.SENDER_EMAIL
    msg['To'] = env.RECEIVER_EMAIL if env.RECEIVER_EMAIL else env.SENDER_EMAIL
    msg['Subject'] = f"GEONIUS - {env.OPERATOR_ID}: {subject}"
    if get_config().email.notify_geode:
        msg['Cc'] = get_config().email.admin_email

    msg.attach(MIMEText(body, 'plain'))

    if attachments:
        for file_path, new_filename in attachments:
            try:
                with open(file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {new_filename}')
                msg.attach(part)
            except Exception as e:
                get_logger().error(f"Failed to attach file {file_path}: {e}")
                raise e

    try:
        server = smtplib.SMTP(get_config().email.smtp_server, get_config().email.smtp_port)
        server.starttls()
        server.login(env.SENDER_EMAIL, env.SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        get_logger().error(f"Failed to send email: {e}")
        raise e
