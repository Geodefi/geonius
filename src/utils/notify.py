import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# from src.logger import log


def send_email(subject, body, attachments=None, send_attachments=True):
    from src.globals import CONFIG, OPERATOR_ID, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL

    # TODO: if send_attachments but no attachments => send the latest log.
    msg: MIMEMultipart = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL if RECEIVER_EMAIL else SENDER_EMAIL
    # TODO: make a way to prevent cc ing us: add --notify-geode : True > readme!
    msg['Cc'] = CONFIG.email.admin_email
    # TODO: get the Operator name on reboot and use it here.
    msg['Subject'] = f"GEONIUS - {OPERATOR_ID}: {subject}"

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
                # log.error(f"Failed to attach file {file_path}: {e}")
                raise e

    try:
        server = smtplib.SMTP(CONFIG.email.smtp_server, CONFIG.email.smtp_port)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        # log.error(f"Failed to send email: {e}")
        raise e
