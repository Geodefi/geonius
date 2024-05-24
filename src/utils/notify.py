# -*- coding: utf-8 -*-

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from src.globals import CONFIG, OPERATOR_ID, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL
from src.logger import log


def get_log_attachment():
    return (os.getcwd().join(CONFIG.directory).join(CONFIG.logger.directory).join("log"), "log.txt")


def send_email(
    subject, body, attachments: list[tuple[str, str]] = None, send_attachments: str = True
):

    if send_attachments and not attachments:
        attachments: list[tuple[str, str]] = [get_log_attachment()]

    msg: MIMEMultipart = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL if RECEIVER_EMAIL else SENDER_EMAIL
    msg['Subject'] = f"GEONIUS - {OPERATOR_ID}: {subject}"
    if CONFIG.email.notify_geode:
        msg['Cc'] = CONFIG.email.admin_email

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
                log.error(f"Failed to attach file {file_path}: {e}")
                raise e

    try:
        server = smtplib.SMTP(CONFIG.email.smtp_server, CONFIG.email.smtp_port)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        log.error(f"Failed to send email: {e}")
        raise e
