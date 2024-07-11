# -*- coding: utf-8 -*-

import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.exceptions import EmailError
from src.globals import get_env, get_config, get_logger


def send_email(
    subject: str,
    body: str,
    attachments: list[tuple[str, str]] = None,
    dont_notify_devs=None,
):
    """Sends an email to the provided developer address, as well as admin when allowed and applicable.

    Args:
        subject (_type_): The header for the mail
        body (_type_): Contents of th mail
        attachments (list[tuple[str, str]], optional): Defaults to None, in which case
        the log file will be provided as an attachment.
        attachments (list[tuple[str, str]], optional): Defaults to None, in which case
        will rely on --dont-notify-devs flag, to inform geodefi developers on crashes.

    Raises:
        e: _description_
        e: _description_
    """

    if not attachments:
        main_dir: str = get_config().directory
        log_dir: str = get_config().logger.directory
        path: str = os.path.join(main_dir, log_dir, "log")
        attachments: list[tuple[str, str]] = [(path, "log.txt")]

    if dont_notify_devs is None:
        dont_notify_devs = get_config().email.dont_notify_devs

    env = get_env()

    msg: MIMEMultipart = MIMEMultipart()
    msg['From'] = env.SENDER_EMAIL
    msg['To'] = env.RECEIVER_EMAIL if env.RECEIVER_EMAIL else env.SENDER_EMAIL
    msg['Subject'] = f"[🧠 Geonius Alert]: {subject}"
    if not dont_notify_devs:
        body += "\n\nGeodefi team also notified of this error. You can use '--dont-notify-devs' flag to prevent this."
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
