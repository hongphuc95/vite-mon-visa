import json
import time
import platform
import os
import sys
import logging

from datetime import datetime
from utils import send_email, send_sms, solve_captcha

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

log_path = os.getenv("LOG_PATH", "./logs/")
auto_reservation = os.getenv("AUTO_RESERVATION", 'False').lower() == "true"

logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", filename=log_path + "planning.log", level=logging.INFO)

class Appointment():

    def __init__(self, web_driver):
        self.web_driver = web_driver

    def set_up_driver(self):
        if self.web_driver == "chrome":
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--window-size=1920,1080")

            chrome_prefs = {"https_only_mode_enabled": True}
            chrome_options.add_experimental_option("prefs", chrome_prefs)

            self.driver = webdriver.Chrome(executable_path="./libs/chromedriver", options=chrome_options)

        elif self.web_driver == "firefox":
            from selenium.webdriver.firefox.options import Options

            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--window-size=1920,1080")
            firefox_profile = webdriver.FirefoxProfile("./profiles/test")

            gecko_driver = {
                "Linux": "geckodriver_linux",
                "Darwin": "geckodriver_mac",
                "Windows": "geckodriver_windows",
            }
            os_name = platform.system()
            gecko_binary = gecko_driver.get(os_name)
            self.driver = webdriver.Firefox(executable_path="./libs/"+gecko_binary, options=firefox_options, firefox_profile=firefox_profile, service_log_path=log_path + "geckodriver.log")

    def destroy_driver(self):
        self.driver.quit()

    def check_for_error_in_page(self):
        assert "403 Forbidden" not in self.driver.page_source, "403 Forbidden"
        assert "502 Bad Gateway" not in self.driver.page_source, "502 Bad Gateway"
        assert "503 Service Unavailable" not in self.driver.page_source, "503 Service Unavailable"
        assert "504 Gateway Timeout" not in self.driver.page_source, "504 Gateway Timeout"
        assert "Service surchargé" not in self.driver.page_source, "Service surchargé"

        return True

    def slot_available(self, url, warning=False, desk_id=None, delay_second=5):
        self.driver.get(url)
        self.driver.delete_all_cookies()
        time.sleep(delay_second)
        self.driver.save_screenshot(log_path +"welcome.png")

        # Step 0 Accept cookies
        try:
            accept_cookie = self.driver.find_element("id", "tarteaucitronPersonalize2")
            accept_cookie.click()
        except:
            pass

        self.check_for_error_in_page()

        # Step 1 Agree on conditions
        condition_checkbox = self.driver.find_element("id", "condition")
        submit_button = self.driver.find_element("name", "nextButton")
        condition_checkbox.send_keys(Keys.SPACE)
        submit_button.send_keys(Keys.SPACE)
        time.sleep(delay_second)

        self.check_for_error_in_page()

        if desk_id and "Veuillez recommencer" in self.driver.page_source:
            return False

        # Step 2 Select proposed plannings
        if desk_id:
            radio_button_list = self.driver.find_element("id", desk_id)
            submit_button = self.driver.find_element("name", "nextButton")
            radio_button_list.send_keys(Keys.SPACE)
            submit_button.send_keys(Keys.SPACE)
            time.sleep(delay_second)

            self.check_for_error_in_page()

        # Step 3 Accept on warnings
        if warning:
            try:
                self.driver.save_screenshot(log_path +"warning.png")
                next_button = self.driver.find_element("name", "nextButton")
                next_button.send_keys(Keys.SPACE)
                time.sleep(delay_second)
            except:
                return False

            self.check_for_error_in_page()
        
        # Step 4 Select date
        try:
            self.driver.save_screenshot(log_path +"layout_slot.png")
            next_button = self.driver.find_element("name", "nextButton")
            next_button.send_keys(Keys.SPACE)
            time.sleep(delay_second)
            self.driver.save_screenshot(log_path +"result_slot.png")
        except:
            return False

        self.check_for_error_in_page()

        if not auto_reservation:
            return True
        else:
            # Step 5 Solve captcha
            try:
                site_key_element = self.driver.find_element("css selector", "[data-sitekey]")
                site_key = site_key_element.get_attribute("data-sitekey")
                current_url = self.driver.current_url
                captcha_result = solve_captcha(site_key=site_key, page_url=current_url)
                google_captcha_response_input = self.driver.find_element("id", "g-recaptcha-response")
                # make input visible
                self.driver.execute_script("arguments[0].setAttribute('style','type: text; visibility:visible;');", google_captcha_response_input)
                google_captcha_response_input.send_keys(captcha_result)
                # hide the captch input
                self.driver.execute_script("arguments[0].setAttribute('style', 'display:none;');", google_captcha_response_input)

                next_button = self.driver.find_element("name", "nextButton")
                next_button.send_keys(Keys.SPACE)
                time.sleep(delay_second)
                self.driver.save_screenshot(log_path +"result_captcha.png")
            except Exception as e:
                logging.error("Something went wrong while bypassing the captcha: ", e)
                return False

            self.check_for_error_in_page()

            try:
                self.driver.maximize_window()
                self.driver.execute_script("window.scrollTo(0, 300)") 
                form_raw = self.driver.find_element("id", "FormBookingCreate")
                try:
                    file = open(log_path + "form_raw.txt", "r+")
                except OSError:
                    file = open(log_path + "form_raw.txt", "w+")
                file.seek(0)
                file.write(form_raw.get_attribute('innerHTML'))
                file.truncate()
                file.close()

                first_name = self.driver.find_element("name", "firstname")
                last_name = self.driver.find_element("name", "lastname")
                email = self.driver.find_element("name", "email")
                email_check = self.driver.find_element("name", "emailcheck")
                nationality = self.driver.find_element("name", "eZBookingAdditionalField_value_21067")
                entry_date = self.driver.find_element("name", "eZBookingAdditionalField_value_21071")
                zip_code = self.driver.find_element("name", "eZBookingAdditionalField_value_21073")

                first_name.send_keys(os.getenv("FIRST_NAME"))
                last_name.send_keys(os.getenv("LAST_NAME"))
                email.send_keys(os.getenv("EMAIL"))
                email_check.send_keys(os.getenv("EMAIL"))
                nationality.send_keys(os.getenv("NATIONALITY"))
                entry_date.send_keys(os.getenv("ENTRY_DATE"))
                actions = ActionChains(self.driver)
                actions.click(on_element = zip_code).send_keys(os.getenv("ZIP_CODE"))
                actions.perform()

                self.driver.save_screenshot(log_path +"result_formular.png")
                next_button = self.driver.find_element("name", "nextButton")
                next_button.send_keys(Keys.SPACE)
                time.sleep(delay_second)
                self.driver.save_screenshot(log_path +"result_confirmation.png")
            except Exception as e:
                logging.error("Something went wrong while filling the personal information form: ", e)
                return False

        return True

    def scrape_for_slot(self, url, operation_name, prefecture_name, visa_name, desk_ids, warning, delay_second=5):
        try:
            file = open(log_path + operation_name + "_checkpoint.txt", "r+")
        except OSError:
            file = open(log_path + operation_name + "_checkpoint.txt", "w+")

        try:
            found = False
            desk_id_found = ""
            if desk_ids:
                for desk_id in desk_ids:
                    logging.info("CHECKING FOR SLOT USING PLANNING ID {} AT {} FOR {}".format(desk_id, prefecture_name, visa_name))
                    found = self.slot_available(url, warning, desk_id)
                    if found:
                        desk_id_found = desk_id
                        break
                    time.sleep(delay_second)
            else:
                logging.info("CHECKING FOR SLOT AT {} FOR {}".format(prefecture_name, visa_name))
                found = self.slot_available(url, warning)

            if found:
                logging.info("{}: SLOT AVAILABLE FOR PLANNING ID {}".format(prefecture_name, desk_id_found))
                current_time = datetime.now().strftime("%H:%M:%S")
                last_result = file.read()
                if "available" in last_result:
                    logging.info("{}: SLOT ALREADY AVAILABLE: SKIPPING EMAIL".format(prefecture_name))
                else:
                    logging.info("{}: NEW AVAILABLE SLOT: SENDING EMAIL!".format(prefecture_name))

                    if os.getenv("EMAIL_NOTIFY_ENABLED", "False").lower() == "true" or os.getenv("EMAIL_NOTIFY_ENABLED") == True:
                        if not auto_reservation:
                            subjects = "[Visa Alert] New slot found for {}".format(prefecture_name)
                            content = f'''
                                <h1>Slot available at prefecture {prefecture_name}</h1>
                                <p>Found at: <strong>{current_time}</strong></p>
                                <p>Type: <strong>{visa_name}</strong></p>
                                <p>Link: <a href={url}>Click here to access prefecture site</a></p>
                            '''
                            if desk_id_found:
                                content += f"<br><p>Option order: <strong>{desk_ids.index(desk_id_found)+1}</strong></p>"

                            attachment_file = {
                                "path": log_path+"result_slot.png",
                                "type": "img/png",
                                "name": "result_slot.png",
                                "content_id": "Result image" 
                            }

                            send_email(subjects=subjects, content=content, attachment_file=attachment_file)
                        else:
                            subjects = "[Visa Alert] Slot reserved automatically for {}".format(prefecture_name)
                            content = f'''
                                <h1>Slot available at prefecture {prefecture_name}</h1>
                                <p>Found at: <strong>{current_time}</strong></p>
                                <p>Type: <strong>{visa_name}</strong></p>
                                <p>Link: <a href={url}>Click here to access prefecture site</a></p>
                            '''       
                            if desk_id_found:
                                content += f"<br><p>Option order: <strong>{desk_ids.index(desk_id_found)+1}</strong></p>"

                            send_email(subjects=subjects, content=content)

                    if os.getenv("SMS_NOTIFY_ENABLED", "False").lower() == "true" or os.getenv("SMS_NOTIFY_ENABLED") == True:
                        message = f'''
                            Slot available at prefecture {prefecture_name}
                            Found at: {current_time}
                            Type: {visa_name}
                            Option order: {desk_ids.index(desk_id_found)+1}
                            Link: {url}
                        '''
                        send_sms(message=message)

                file.seek(0)
                file.write("available")
                file.truncate()
                file.close()
            else:
                logging.info("{}: NO SLOT AVAILABLE".format(prefecture_name))
                file.seek(0)
                file.write("not found")
                file.truncate()
                file.close()

        except AssertionError as err:
            logging.error("{}: SITE DOWN ({})".format(prefecture_name, err))
        except:
            logging.error("{}: UNEXPECTED ERROR: {}".format(prefecture_name, sys.exc_info()))


def run(web_driver="firefox"):
    appointment = Appointment(web_driver=web_driver)
    appointment.set_up_driver()

    prefectures_path = "./prefectures.json"

    with open(prefectures_path, "r") as j:
        prefectures = json.loads(j.read())

    for prefecture in prefectures:
        pass
        appointment.scrape_for_slot(prefecture["url"], prefecture["operation_name"], prefecture["prefecture_name"], prefecture["appointment_name"], prefecture["desk_ids"], prefecture["warning"])

    appointment.destroy_driver()