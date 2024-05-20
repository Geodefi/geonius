import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

from src.globals import CONFIG, OPERATOR_ID, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL


def send_email(subject, body, attachments=None):

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL if RECEIVER_EMAIL else SENDER_EMAIL
    msg['Cc'] = CONFIG.email.admin_email
    msg['Subject'] = f"GEOSCOPE - {OPERATOR_ID}: {subject}"

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
