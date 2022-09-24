import os
import base64
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
from dotenv import load_dotenv

load_dotenv()
log_path = os.getenv('LOG_PATH')

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename=log_path + 'planning.log', level=logging.INFO)

def send_email(subjects, content, attachment_file=None):
    message = Mail(
        from_email=os.environ.get('SENDGRID_SENDER') if os.environ.get('SENDGRID_SENDER') else 'alert@hongphucvu.com',
        to_emails=os.environ.get('SENDGRID_EMAIL'),
        subject=subjects,
        html_content=content
    )

    if attachment_file:
        with open(attachment_file['path'], 'rb') as f:
            data = f.read()
            f.close()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType(attachment_file['type'])
        attachment.file_name = FileName(attachment_file['name'])
        attachment.disposition = Disposition('attachment')
        attachment.content_id = ContentId(attachment_file['content_id'])
        message.attachment = attachment

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logging.info('Email sent with status code {}'.format(response.status_code))
    except Exception as e:
        logging.error('An error occured while sending email: {}'.format(e))
        print(e)


def send_sms():
    pass