import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException
)
import time
from config.credentials import Credentials
from selenium.webdriver.common.keys import Keys

class AdmitReject:
    # Configuration
    LOGIN_TIMEOUT = 30  # seconds
    PAGE_LOAD_TIMEOUT = 40  # seconds
    SEARCH_URL = "https://ymgrad.com/admits_rejects"
    LOGIN_URL = "https://ymgrad.com/account/login"

    def __init__(self, driver):
        self.driver = driver
        self.driver.set_page_load_timeout(self.PAGE_LOAD_TIMEOUT)
        self.logger = logging.getLogger(__name__)
        self.data = []

    def login(self):
        """Main login method that orchestrates the entire login process"""
        try:
            self._navigate_to_login_page()
            self._enter_credentials()
            self._submit_button()
            self._verify_login()
            self._select_country()
            self._select_masters_degree()
            self._select_decision_types()
            return True
        except TimeoutException as e:
            self.logger.error(f"Timeout while waiting for element: {str(e)}")
        except NoSuchElementException as e:
            self.logger.error(f"Element not found: {str(e)}")
        except WebDriverException as e:
            self.logger.error(f"WebDriver error occurred: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
        return False
    

    def _navigate_to_login_page(self):
        """Navigate directly to the login page"""
        try:
            self.logger.info(f"Navigating to login page: {self.LOGIN_URL}")
            self.driver.get(self.LOGIN_URL)
            
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.visibility_of_element_located(self.USERNAME_FIELD)
            )
            self.logger.info("Login page loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load login page: {str(e)}")
            raise
    def _enter_credentials(self):
        """Enter username and password into their respective fields"""
        try:
            username_field = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable(self.USERNAME_FIELD)
            )
            password_field = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable(self.PASSWORD_FIELD)
            )

            username_field.clear()
            username_field.send_keys(Credentials.email)
            
            password_field.clear()
            password_field.send_keys(Credentials.password)

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

    def _verify_login(self):
        """Verify that login was successful"""
        try:
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                lambda d: "dashboard" in d.current_url.lower() or 
                        "account" in d.current_url.lower() or
                        d.find_element(*self.LOGGED_IN_INDICATOR)
            )
            self.logger.info("Login verification successful")
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Login verification failed: {str(e)}")
            raise

    def _select_country(self, country_name="United States"):
            """Select a country from the country dropdown"""
            try:
                self.logger.info(f"Selecting country: {country_name}")

                # Click to activate the dropdown
                dropdown_container = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "css-yk16xz-control"))
                )
                dropdown_container.click()
                time.sleep(0.5)

                # Type in the country input field
                country_input = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "react-select-2-input"))
                )
                country_input.send_keys(country_name)
                time.sleep(0.5)
                country_input.send_keys(Keys.ENTER)

                self.logger.info(f"Country '{country_name}' selected successfully")
            except Exception as e:
                self.logger.error(f"Failed to select country: {str(e)}")
                raise

    def _select_masters_degree(self):
        """Ensure the Master's degree level switch is turned on"""
        try:
            self.logger.info("Checking Master's degree switch status...")

            # Locate the input element for the switch
            checkbox = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='checkbox'][role='switch']"))
            )

            # Check if it's already selected (checked)
            is_checked = self.driver.execute_script("return arguments[0].checked;", checkbox)

            if not is_checked:
                # Click the visual toggle (react-switch-bg or surrounding container)
                toggle_bg = checkbox.find_element(By.XPATH, "./ancestor::div[contains(@class, 'react-switch')]")
                self.driver.execute_script("arguments[0].click();", toggle_bg)
                self.logger.info("Master's degree switch turned ON")
            else:
                self.logger.info("Master's degree switch already ON")

        except Exception as e:
            self.logger.error(f"Failed to toggle Master's degree switch: {str(e)}")
            raise


    def _select_decision_types(self, options_to_select=["Admit", "Reject"]):
        """Select specific options (e.g., 'Admit' and 'Reject') in the Decision Type multi-select"""
        try:
            self.logger.info(f"Selecting decision types: {options_to_select}")

            # Click the dropdown to reveal options
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "dropdown-container"))
            )
            dropdown.click()
            time.sleep(0.5)

            for option in options_to_select:
                try:
                    # Find label containing the option text
                    checkbox_label = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'rmsc')]//label[contains(., '{option}')]"))
                    )

                    # Check if already selected
                    input_box = checkbox_label.find_element(By.TAG_NAME, "input")
                    is_checked = self.driver.execute_script("return arguments[0].checked;", input_box)

                    if not is_checked:
                        self.driver.execute_script("arguments[0].click();", checkbox_label)
                        self.logger.info(f"Option '{option}' selected")
                    else:
                        self.logger.info(f"Option '{option}' was already selected")

                except Exception as e:
                    self.logger.warning(f"Could not select option '{option}': {str(e)}")

            # Optional: close the dropdown (if needed)
            dropdown.click()

        except Exception as e:
            self.logger.error(f"Failed to select decision types: {str(e)}")
            raise