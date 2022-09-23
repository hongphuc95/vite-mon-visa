# Vite Mon Visa

This tool will notify users if an appointment is available in a prefecture

# Supported prefectures
This tool is currently support for the following prefecture
- Val d'Oise

To add support for more prefectures, please refer to the prefecture configuration

# Prerequisites
This tool uses `Selenium` to be able to scrape and function. You will need a web browser binary installed on your machine, make sure you have `Firefox` installed

**(*)Chrome will be supported in the future**

# Deployment
## Docker
```
docker run -d --name <app_name> --env-file <env_file_path> hongphuc95/vite-mon-visa
```
To configure the environment file please refer the `Configuration` section in this doc 

## Build the project from the code source
```
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

# Configuration
## Environment variables
The following configurations are optionals. You can either use `.env` file or set environment variables manually

To enable notifications via email, set these environment variables below
```
EMAIL_NOTIFY_ENABLED=true
SENDGRID_API_KEY=<api_key>
SENDGRID_EMAIL=<your_destination_email>
(optional) SENDGRID_SENDER=<sender_address>
```

To enable notifications via sms, set these environment variables below
```
SMS_NOTIFY_ENABLED=true
TWILIO_AUTH_TOKEN=<token>
TWILIO_FROM_NUMBER=<twilio_trial_number>
TWILIO_TO_NUMBER=<your_phone_number>
```

To configure the logs path, set a desired path like following
```
LOG_PATH=<log_path>
ENGINE=<browser_engine> # Will be supported in the future, default to Firefox
```

## Prefectures list <Advanced>
To tell the tool what prefecture needed to be monitored, modify the list of prefectures in the `prefectures.py` file using the template below
```
{
    'url': <reservation_url>,
    'desk_ids': <planning_or_desk_id> # Look up manually by inspecting the code source,
    'operation_name': <operation_name>,
    'prefecture_name': <prefecture_name>,
    'appointment_name': <appointment_name>,
}
```