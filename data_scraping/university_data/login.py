from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException
)
import time
import logging
import pandas as pd
from config.credentials import Credentials
import os 

class YMGradLogin:
    # Locators
    USERNAME_FIELD = (By.XPATH, "//input[@id='id_username']")
    PASSWORD_FIELD = (By.XPATH, "//input[@id='id_password']")
    LOGIN_BUTTON = (By.XPATH, "//input[@type='submit' and @value='Login']")
    LOGGED_IN_INDICATOR = (By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'Dashboard')]")
    UNIVERSITY_CARD = (By.CSS_SELECTOR, "div.UniversityCardNew_super_wrapper__l2dMw")
    
    # Configuration
    LOGIN_TIMEOUT = 30  # seconds
    PAGE_LOAD_TIMEOUT = 40  # seconds
    SEARCH_URL = "https://ymgrad.com/search/United%20States"
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
            self._navigate_to_search_page()
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

    def _navigate_to_search_page(self):
        """Navigate to the search page after successful login"""
        try:
            self.logger.info(f"Navigating to search page: {self.SEARCH_URL}")
            
            # First try to load the page normally
            self.driver.get(self.SEARCH_URL)
            
            # Wait for either the body tag or university cards to appear
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                lambda d: d.find_element(By.TAG_NAME, "body") or 
                        d.find_elements(*self.UNIVERSITY_CARD)
            )
            
            # Additional check for university cards with retry logic
            attempts = 3
            for attempt in range(attempts):
                try:
                    university_cards = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_all_elements_located(self.UNIVERSITY_CARD)
                    )
                    if university_cards:
                        self.logger.info(f"Found {len(university_cards)} university cards on attempt {attempt + 1}")
                        return
                    
                    # If no cards found, try refreshing
                    if attempt < attempts - 1:
                        self.logger.info(f"No cards found, refreshing page (attempt {attempt + 1})")
                        self.driver.refresh()
                        time.sleep(3)
                        
                except TimeoutException:
                    if attempt < attempts - 1:
                        self.logger.info(f"Timeout waiting for cards, refreshing page (attempt {attempt + 1})")
                        self.driver.refresh()
                        time.sleep(3)
                    else:
                        raise
            
            self.logger.info("Search page loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to search page: {str(e)}")
            # Take screenshot for debugging
            screenshot_path = "search_page_error.png"
            self.driver.save_screenshot(screenshot_path)
            self.logger.info(f"Screenshot saved to {screenshot_path}")
            raise

    def _scroll_page_to_load_all_cards(self):
        """Scroll page to ensure all cards are loaded"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_attempts = 5
            
            while scroll_attempts < max_attempts:
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2.5)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
                
        except Exception as e:
            self.logger.warning(f"Couldn't complete page scrolling: {str(e)}")

    def scrape_university_data(self):
        """Scrape all university data from the loaded search page"""
        try:
            # First scroll to load all cards
            self._scroll_page_to_load_all_cards()
            
            # Wait for cards to be present in DOM
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.presence_of_all_elements_located(self.UNIVERSITY_CARD)
            )
            
            # Get fresh list of cards after scrolling
            university_cards = self.driver.find_elements(*self.UNIVERSITY_CARD)
            self.logger.info(f"Found {len(university_cards)} university cards")
            
            for i in range(len(university_cards)):
                retries = 3
                while retries > 0:
                    try:
                        # Get fresh reference to the card
                        current_cards = self.driver.find_elements(*self.UNIVERSITY_CARD)
                        if i >= len(current_cards):
                            self.logger.warning(f"Card index {i} out of range")
                            break
                            
                        card = current_cards[i]
                        
                        # Scroll to card with some padding
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                            card
                        )
                        time.sleep(0.8)
                        
                        university_data = {
                            'Rank': self._get_university_rank(card),
                            'Name': self._get_university_name(card),
                            'Location': self._get_university_location(card),
                            'Acceptance_Rate': self._get_stat_value(card, "Acceptance rate"),
                            'Average_GMAT': self._get_stat_value(card, "Average GMAT score"),
                            'Average_GRE': self._get_stat_value(card, "Average GRE score"),
                            'Average_GPA': self._get_stat_value(card, "Average GPA"),
                            'Average_Salary': self._get_salary_value(card),
                            'Tuition_Fees': self._get_stat_value(card, "Tuition fees"),
                            'Description': self._get_university_description(card)
                        }
                        self.data.append(university_data)
                        break  # Success, exit retry loop
                        
                    except StaleElementReferenceException:
                        retries -= 1
                        if retries == 0:
                            self.logger.warning(f"Failed to scrape card {i} after 3 retries")
                        else:
                            self.logger.info(f"Stale element, retrying ({retries} attempts left)")
                            time.sleep(1)
                    except Exception as e:
                        self.logger.warning(f"Couldn't scrape card {i}: {str(e)}")
                        break
            
            self.logger.info(f"Successfully scraped data from {len(self.data)} universities")
            return self.data
            
        except TimeoutException:
            self.logger.error("Timed out waiting for university data to load")
            return None
        except Exception as e:
            self.logger.error(f"Failed to scrape university data: {str(e)}")
            raise

    def _get_university_rank(self, card):
        """Extract university rank from card"""
        try:
            return card.find_element(
                By.CSS_SELECTOR, "div.UniversityCardNew_university_rank__yTV30"
            ).text.strip()
        except NoSuchElementException:
            return "N/A"

    def _get_university_name(self, card):
        """Extract university name from card"""
        try:
            return card.find_element(
                By.CSS_SELECTOR, "h2.UniversityCardNew_main_title__5ewCb"
            ).text.strip()
        except NoSuchElementException:
            return "N/A"

    def _get_university_location(self, card):
        """Extract university location from card"""
        try:
            return card.find_element(
                By.CSS_SELECTOR, "div.UniversityCardNew_address__ultV_"
            ).text.replace("📍", "").replace("\n", " ").strip()
        except NoSuchElementException:
            return "N/A"

    def _get_stat_value(self, card, stat_name):
        """Extract specific statistic value from card"""
        try:
            containers = card.find_elements(
                By.CSS_SELECTOR, "div.UniversityCardNew_stat_container__aGWTW"
            )
            for container in containers:
                heading = container.find_element(
                    By.CSS_SELECTOR, "div.UniversityCardNew_stats-heading__tNoYp"
                ).text.strip()
                if stat_name.lower() in heading.lower():
                    value = container.find_element(
                        By.CSS_SELECTOR, "div.UniversityCardNew_stats-text__LQZfD"
                    ).text.strip()
                    # Clean numeric values
                    if stat_name in ["Average GMAT score", "Average GRE score", "Average GPA", "Tuition fees"]:
                        return ''.join(c for c in value if c.isdigit() or c == '.')
                    return value
            return "N/A"
        except NoSuchElementException:
            return "N/A"

    def _get_salary_value(self, card):
        """Special handling for salary value which might include dollar signs"""
        try:
            value = self._get_stat_value(card, "Average salary")
            if value != "N/A":
                # Clean salary value (remove currency symbols, commas, etc.)
                return ''.join(c for c in value if c.isdigit() or c == '.')
            return value
        except Exception as e:
            self.logger.warning(f"Error processing salary value: {str(e)}")
            return "N/A"

    def _get_university_description(self, card):
        """Extract the university description text"""
        try:
            return card.find_element(
                By.CSS_SELECTOR, "div.UniversityCardNew_extra_info__zfV1R p"
            ).text.strip()
        except NoSuchElementException:
            return "N/A"

    # def save_to_excel(self, filename="university_data.xlsx"):
    #     """Save scraped data to Excel file"""
    #     try:
    #         df = pd.DataFrame(self.data)
            
    #         # Convert numeric columns to appropriate types
    #         numeric_cols = ['Rank', 'Average_GMAT', 'Average_GRE', 'Average_GPA', 
    #                       'Average_Salary', 'Tuition_Fees']
    #         for col in numeric_cols:
    #             if col in df.columns:
    #                 df[col] = pd.to_numeric(df[col], errors='coerce')
            
    #         # Format percentage columns
    #         if 'Acceptance_Rate' in df.columns:
    #             df['Acceptance_Rate'] = df['Acceptance_Rate'].str.rstrip('%')
    #             df['Acceptance_Rate'] = pd.to_numeric(df['Acceptance_Rate'], errors='coerce')
            
    #         df.to_excel(filename, index=False)
    #         self.logger.info(f"Data saved to {filename}")
    #         return True
    #     except Exception as e:
    #         self.logger.error(f"Failed to save data to Excel: {str(e)}")
    #         return False


    def save_to_excel(self, filename="university_data.xlsx"):
        """Save scraped data to Excel file if it does not already exist"""
        try:
            # Check if the file already exists
            if os.path.exists(filename):
                self.logger.info(f"File '{filename}' already exists. Skipping save.")
                return False

            df = pd.DataFrame(self.data)

            # Convert numeric columns to appropriate types
            numeric_cols = ['Rank', 'Average_GMAT', 'Average_GRE', 'Average_GPA', 
                            'Average_Salary', 'Tuition_Fees']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Format percentage columns
            if 'Acceptance_Rate' in df.columns:
                df['Acceptance_Rate'] = df['Acceptance_Rate'].str.rstrip('%')
                df['Acceptance_Rate'] = pd.to_numeric(df['Acceptance_Rate'], errors='coerce')

            df.to_excel(filename, index=False)
            self.logger.info(f"Data saved to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save data to Excel: {str(e)}")
            return False
