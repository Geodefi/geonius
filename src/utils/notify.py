import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from src.globals import CONFIG, OPERATOR_ID, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL


def send_email(subject, body, attachments=None):

    msg: str = MIMEMultipart()
    msg['From']: str = SENDER_EMAIL
    msg['To']: str = RECEIVER_EMAIL if RECEIVER_EMAIL else SENDER_EMAIL
    # TODO: make a way to prevent cc ing us.
    msg['Cc']: str = CONFIG.email.admin_email
    # TODO: get the Operator name on reboot and use it here.
    msg['Subject']: str = f"GEONIUS - {OPERATOR_ID}: {subject}"

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
                print(f"Failed to attach file {file_path}: {e}")
                # TODO: Add logging

    try:
        server = smtplib.SMTP(CONFIG.email.smtp_server, CONFIG.email.smtp_port)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")
        # TODO: Add logging
