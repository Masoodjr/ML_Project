from selenium.webdriver.common.by import By
from .base_page import BasePage
from config.credentials import Credentials
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class LoginPage(BasePage):
    def __init__(self, driver, username_field, password_field, login_button, logged_in_indicator, login_timeout=30):
        super().__init__(driver)
        self.USERNAME_FIELD = username_field
        self.PASSWORD_FIELD = password_field
        self.LOGIN_BUTTON = login_button
        self.LOGGED_IN_INDICATOR = logged_in_indicator
        self.LOGIN_TIMEOUT = login_timeout

    def open_login_page(self, url):
        self.driver.get(url)
        self.wait_for_element(self.USERNAME_FIELD)
        self.logger.info("Login page loaded")

    def login(self):
        """Enter username and password into their respective fields"""
        self.logger.info(f"Attempting to enter credentials...")
        try:
            username_field = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable(self.USERNAME_FIELD)
            )
            password_field = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable(self.PASSWORD_FIELD)
            )

            username_field.clear()
            username_field.send_keys(Credentials.EMAIL)
            
            password_field.clear()
            password_field.send_keys(Credentials.PASSWORD)

            self.logger.info("Credentials entered successfully")
        except Exception as e:
            self.logger.error(f"Failed to enter credentials: {str(e)}")
            raise

    def _submit_button(self):
        """Click the login button to submit credentials"""
        try:
            login_button = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable(self.LOGIN_BUTTON)
            )
            
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", login_button)
            time.sleep(0.5)
            self.driver.execute_script("arguments[0].click();", login_button)
            
            self.logger.info("Login button clicked successfully")
        except Exception as e:
            self.logger.error(f"Failed to submit login: {str(e)}")
            raise

    def verify_login(self):
        WebDriverWait(self.driver, 30).until(
            lambda d: "dashboard" in d.current_url.lower() or 
                    d.find_element(*self.LOGGED_IN_INDICATOR)
        )
        self.logger.info("Login verified")