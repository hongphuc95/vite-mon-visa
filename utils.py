import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()
log_path = os.getenv('LOG_PATH')

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename=log_path + 'planning.log', level=logging.INFO)

def send_email(subjects, content):
    logging.info(os.environ.get('SENDGRID_SENDER'))
    logging.info(os.environ.get('SENDGRID_EMAIL'))
    logging.info(os.environ.get('SENDGRID_API_KEY'))
    logging.info(subjects)
    logging.info(content)

    message = Mail(
        from_email=os.environ.get('SENDGRID_SENDER') if os.environ.get('SENDGRID_SENDER') else 'alert@hongphucvu.com',
        to_emails=os.environ.get('SENDGRID_EMAIL'),
        subject=subjects,
        html_content=content
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        logging.info('Email sent with status code {}'.format(response.status_code))
    except Exception as e:
        logging.error('An error occured while sending email: {}'.format(e))
        print(e)


def send_sms():
    pass