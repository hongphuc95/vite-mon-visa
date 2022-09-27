from email import message
import os
import base64
import logging
import requests
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


def send_sms(message):
    url = 'https://api.sendwithses.com/send-sms'
    to_number = os.environ.get('SMS_TO_NUMBER')
    template_key = os.environ.get('SMS_API_KEY')

    headers = {'template-key': template_key}
    payload = {'mobile': to_number, 'message': message}
    
    try:
        r = requests.post(url=url, data=payload, headers=headers)
        logging.info('Email sent with status code {}'.format(r.status_code))
    except Exception as e:
        logging.error('An error occured while sending sms: {}'.format(e))

if __name__ == '__main__':
    from datetime import datetime
    prefecture_name = 'Val d\'Oise'
    current_time = datetime.now().strftime("%H:%M:%S")
    visa_name = 'naturalisation'
    url = 'https://www.val-doise.gouv.fr/booking/create/11343/0'
    message = f'''
        Slot available at prefecture {prefecture_name}
        Found at: {current_time}
        Type: {visa_name}
        Option order: '1'
        Link: {url}
    '''
    send_sms(message=message)