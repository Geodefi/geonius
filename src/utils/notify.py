# -*- coding: utf-8 -*-

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.exceptions import EmailError
from src.globals import get_env, get_config, get_logger

from src.helpers.portal import get_name


def send_email(
    subject,
    body,
    attachments: list[tuple[str, str]] = None,
    send_attachments: str = True,
    dont_notify_geode=get_config().email.dont_notify_geode,
):
    """TODO

    Args:
        subject (_type_): _description_
        body (_type_): _description_
        attachments (list[tuple[str, str]], optional): _description_. Defaults to None.
        send_attachments (str, optional): _description_. Defaults to True.

    Raises:
        e: _description_
        e: _description_
    """
    env = get_env()

    if send_attachments and not attachments:
        main_dir: str = get_config().directory
        log_dir: str = get_config().logger.directory
        path: str = os.path.join(main_dir, log_dir, "log")
        attachments: list[tuple[str, str]] = [(path, "log.txt")]

    msg: MIMEMultipart = MIMEMultipart()
    msg['From'] = env.SENDER_EMAIL
    msg['To'] = env.RECEIVER_EMAIL if env.RECEIVER_EMAIL else env.SENDER_EMAIL
    msg['Subject'] = f"[🧠 Geonius Alert for {get_name(env.OPERATOR_ID)}]: {subject}"
    if not dont_notify_geode:
        body += "\n\n Geodefi team was also notified of this error."
        msg['Cc'] = get_config().email.admin_email

    msg.attach(MIMEText(body, 'plain'))

    try:
        for file_path, file_name in attachments:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {file_name}')
            msg.attach(part)
    except Exception as e:
        get_logger().error(f"Failed to attach file {file_path}: {e}. Will try to send without it.")

    try:
        server = smtplib.SMTP(get_config().email.smtp_server, get_config().email.smtp_port)
        server.starttls()
        server.login(env.SENDER_EMAIL, env.SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        get_logger().error(f"Failed to send email!")
        raise EmailError(f"Failed to send an email!") from e
