from email import message
import os
import time
import base64
import logging
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName,
    FileType, Disposition, ContentId)
from dotenv import load_dotenv

load_dotenv()
log_path = os.getenv("LOG_PATH")

logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", filename=log_path + "planning.log", level=logging.INFO)

def send_email(subjects, content, attachment_file=None):
    message = Mail(
        from_email=os.environ.get("SENDGRID_SENDER") if os.environ.get("SENDGRID_SENDER") else "alert@hongphucvu.com",
        to_emails=os.environ.get("SENDGRID_EMAIL"),
        subject=subjects,
        html_content=content
    )

    if attachment_file:
        with open(attachment_file["path"], "rb") as f:
            data = f.read()
            f.close()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.file_content = FileContent(encoded)
        attachment.file_type = FileType(attachment_file["type"])
        attachment.file_name = FileName(attachment_file["name"])
        attachment.disposition = Disposition("attachment")
        attachment.content_id = ContentId(attachment_file["content_id"])
        message.attachment = attachment

    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        logging.info("Email sent with status code {}".format(response.status_code))
    except Exception as e:
        logging.error("An error occured while sending email: {}".format(e))


def send_sms(message):
    url = "https://api.sendwithses.com/send-sms"
    to_number = os.environ.get("SMS_TO_NUMBER")
    template_key = os.environ.get("SMS_API_KEY")

    headers = {"template-key": template_key}
    payload = {"mobile": to_number, "message": message}
    
    try:
        r = requests.post(url=url, data=payload, headers=headers)
        logging.info("Email sent with status code {}".format(r.status_code))
    except Exception as e:
        logging.error("An error occured while sending sms: {}".format(e))


def solve_captcha(page_url, site_key):
    retry_time = 5
    api_key = os.getenv("CAPTCHA_API_KEY")
    form = {
        "method": "userrecaptcha",
        "googlekey": site_key,
        "key": api_key, 
        "pageurl": page_url,
    }
    response = requests.post("http://2captcha.com/in.php", data=form)

    if response.text[0:2] != "OK": 
        logging.error("Service error. Error code:" + response.text) 
    captcha_id = response.text[3:]

    token_url = "http://2captcha.com/res.php?key="+ api_key + "&action=get&id=" + captcha_id

    captcha_result = ""
    for i in range(1, 25):  
        response = requests.get(token_url)
        if response.text[0:2] == "OK":
            logging.info("Take {} tries to solve the captcha".format(i))
            captcha_result = response.text[3:]
            break
        else:
            time.sleep(retry_time)

    return captcha_result
