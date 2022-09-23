import time
import platform
import os
import sys
import logging

from datetime import datetime
from dotenv import load_dotenv
from prefectures import prefectures

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

load_dotenv()
log_path = os.getenv('LOG_PATH')

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename=log_path + 'planning.log', level=logging.INFO)

class Appointment():

    def __init__(self, web_driver):
        self.web_driver = web_driver

    def set_up_driver(self):
        if self.web_driver == 'chrome':
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--window-size=1920,1080')

            chrome_prefs = {'https_only_mode_enabled': True}
            chrome_options.add_experimental_option("prefs", chrome_prefs)

            self.driver = webdriver.Chrome(executable_path='./libs/chromedriver', options=chrome_options)
            self.driver.implicitly_wait(10)

        elif self.web_driver == 'firefox':
            from selenium.webdriver.firefox.options import Options

            firefox_options = Options()
            firefox_options.add_argument('--headless')
            firefox_options.add_argument('--window-size=1920,1080')
            firefox_profile = webdriver.FirefoxProfile('./profiles/test')

            gecko_driver = {
                'Linux': 'geckodriver_linux',
                'Darwin': 'geckodriver_mac',
                'Windows': 'geckodriver_windows',
            }
            os_name = platform.system()
            gecko_binary = gecko_driver.get(os_name)
            self.driver = webdriver.Firefox(executable_path='./libs/'+gecko_binary, options=firefox_options, firefox_profile=firefox_profile, service_log_path=log_path + 'geckodriver.log')
            self.driver.implicitly_wait(10)

    def destroy_driver(self):
        self.driver.quit()

    def check_for_error_in_page(self):
        assert '403 Forbidden' not in self.driver.page_source, '403 Forbidden'
        assert '502 Bad Gateway' not in self.driver.page_source, '502 Bad Gateway'
        assert '503 Service Unavailable' not in self.driver.page_source, '503 Service Unavailable'
        assert '504 Gateway Timeout' not in self.driver.page_source, '504 Gateway Timeout'

        return True

    def slot_available(self, url, desk_id=None, delay_second=5):
        self.driver.get(url)
        self.driver.delete_all_cookies()
        time.sleep(delay_second)

        self.check_for_error_in_page()

        # Step #1 Agree on conditions
        condition_checkbox = self.driver.find_element('id', 'condition')
        submit_button = self.driver.find_element('name', 'nextButton')
        condition_checkbox.send_keys(Keys.SPACE)
        submit_button.send_keys(Keys.SPACE)
        time.sleep(delay_second)

        self.check_for_error_in_page()

        if desk_id and 'Veuillez recommencer' in self.driver.page_source:
            return False

        # Step 2 Select proposed plannings 
        if desk_id:
            radio_button_list = self.driver.find_element('id', desk_id)
            submit_button = self.driver.find_element('name', 'nextButton')
            radio_button_list.send_keys(Keys.SPACE)
            submit_button.send_keys(Keys.SPACE)
            time.sleep(delay_second)

        self.check_for_error_in_page()
        
        # Result Page
        try:
            next_button = self.driver.find_element('name', 'nextButton')
            
            return True
        except:
            pass
        
        return False

    def scrape_for_slot(self, url, operation_name, prefecture_name, visa_name, desk_ids):
        try:
            file = open(log_path + operation_name + '_checkpoint.txt', 'r+')
        except OSError:
            file = open(log_path + operation_name + '_checkpoint.txt', 'w+')

        try:
            found = False
            desk_id_found = ''
            if desk_ids:
                for desk_id in desk_ids:
                    logging.info('CHECKING FOR SLOT USING PLANNING ID {} AT {} FOR {}'.format(desk_id, prefecture_name, visa_name))
                    found = self.slot_available(url, desk_id)
                    if found:
                        desk_id_found = desk_id
                        break
                    time.sleep(5)
            else:
                found = False

            if found:
                logging.info('{}: SLOT AVAILABLE FOR PLANNING ID {}'.format(prefecture_name, desk_id_found))
                current_time = datetime.now().strftime("%H:%M:%S")
                message = "{} - {} - {}: SLOT AVAILABLE AT {} OPTION {}".format(current_time, prefecture_name, visa_name, url, desk_ids.index(desk_id_found)+1)
                last_result = file.read()
                if 'available' in last_result:
                    logging.info('{}: SLOT ALREADY AVAILABLE: SKIPPING EMAIL'.format(prefecture_name))
                else:
                    logging.info('{}: NEW AVAILABLE SLOT: SENDING EMAIL!'.format(prefecture_name))

                    if os.getenv('EMAIL_NOTIFY_ENABLED'):
                        # TODO Send email
                        pass
                    if os.getenv('SMS_NOTIFY_ENABLED'):
                        # TODO Send sms
                        pass
                file.seek(0)
                file.write('available')
                file.truncate()
            else:
                logging.info('{}: NO SLOT AVAILABLE'.format(prefecture_name))
                file.seek(0)
                file.write('unavailable')
                file.truncate() 

        except AssertionError as err:
            logging.error('{}: SITE DOWN ({})'.format(prefecture_name, err))
        except:
            logging.error('{}: UNEXPECTED ERROR: {}'.format(prefecture_name, sys.exc_info()))


def run(web_driver='firefox'):
    appointment = Appointment(web_driver=web_driver)
    appointment.set_up_driver()

    for prefecture in prefectures:
        appointment.scrape_for_slot(prefecture['url'], prefecture['operation_name'], prefecture['prefecture_name'], prefecture['appointment_name'], prefecture['desk_ids'])

    appointment.destroy_driver()