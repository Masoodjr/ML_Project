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
import os
import pandas as pd
from datetime import datetime, timedelta
import random
import math

class AdmitReject:
    # Locators
    USERNAME_FIELD = (By.XPATH, "//input[@id='id_username']")
    PASSWORD_FIELD = (By.XPATH, "//input[@id='id_password']")
    LOGIN_BUTTON = (By.XPATH, "//input[@type='submit' and @value='Login']")
    LOGGED_IN_INDICATOR = (By.XPATH, "//*[contains(text(), 'Welcome') or contains(text(), 'Dashboard')]")
    UNIVERSITY_CARD = (By.CSS_SELECTOR, "div.UniversityCardNew_super_wrapper__l2dMw")
    # Configuration
    LOGIN_TIMEOUT = 30  # seconds
    PAGE_LOAD_TIMEOUT = 40  # seconds
    ADMIT_REJECT_URL = "https://ymgrad.com/admits_rejects"
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
            self._navigate_to_admit_reject_page()
            self._select_country()
            self._select_decision_types()
            # self._scrape_and_save_profiles()
            self._scrape_100k_profiles()
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

    def _navigate_to_admit_reject_page(self):
        """Navigate to the search page after successful login"""
        try:
            self.logger.info(f"Navigating to admit and rejects page: {self.ADMIT_REJECT_URL}")
            self.driver.get(self.ADMIT_REJECT_URL)
            self.logger.info("ADMIT REJECT page loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load ADMIT REJECT page: {str(e)}")
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

    
    def _select_decision_types(self, options_to_select=["Admit", "Reject"]):
        """Select specific options (e.g., 'Admit' and 'Reject') in the Decision Type multi-select"""
        try:
            self.logger.info(f"Selecting decision types: {options_to_select}")

            # Wait for and click the dropdown to reveal options
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.dropdown-container"))
            )
            
            # Click to expand the dropdown
            dropdown.click()
            time.sleep(0.5)
            
            # Verify dropdown is expanded
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                lambda d: d.find_element(By.CSS_SELECTOR, "div.dropdown-container").get_attribute("aria-expanded") == "true"
            )

            # Select each option
            for option in options_to_select:
                try:
                    # Find the option in the dropdown
                    option_element = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'dropdown-container')]//div[contains(@class, 'dropdown-option') and contains(., '{option}')]"))
                    )
                    
                    # Scroll to and click the option
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_element)
                    time.sleep(0.2)
                    option_element.click()
                    self.logger.info(f"Selected option: {option}")
                    
                except Exception as e:
                    self.logger.warning(f"Could not select option '{option}': {str(e)}")
                    continue

            # Verify selection was successful
            try:
                selected_text = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.dropdown-heading-value span:not(.gray)"))
                ).text
                
                self.logger.info(f"Current selection: {selected_text}")
                
                # Close dropdown if still open
                if dropdown.get_attribute("aria-expanded") == "true":
                    dropdown.click()
                    
            except Exception as e:
                self.logger.warning(f"Could not verify selection: {str(e)}")

        except Exception as e:
            self.logger.error(f"Failed to select decision types: {str(e)}")
            raise

    def _scrape_and_save_profiles(self, excel_path="admission_profiles.xlsx", target_profiles=100000, batch_size=100):
        try:
            # Initialize or load existing Excel file
            if os.path.exists(excel_path):
                existing_df = pd.read_excel(excel_path)
                existing_profiles = existing_df.to_dict('records')
            else:
                existing_profiles = []
                
            seen_profile_ids = set(p['Profile ID'] for p in existing_profiles)
            last_profile_count = 0
            retry_count = 0
            max_retries = 5
            
            while len(existing_profiles) < target_profiles and retry_count < max_retries:
                # Get current height and all profile elements
                current_height = self.driver.execute_script("return document.body.scrollHeight")
                profile_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.admits_rejects_box11__3nraI")))
                
                current_batch = []
                
                for profile_element in profile_elements[-batch_size:]:  # Focus on newest elements first
                    try:
                        profile_id = profile_element.get_attribute("id")
                        if profile_id in seen_profile_ids:
                            continue
                            
                        # Scroll to element with offset to ensure proper loading
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", profile_element)
                        time.sleep(0.3)
                        
                        # Scrape profile data
                        profile_data = self._scrape_admission_profile(profile_element)
                        if not profile_data.get('Name'):  # Skip if no name found
                            continue
                            
                        profile_data['Profile ID'] = profile_id
                        current_batch.append(profile_data)
                        seen_profile_ids.add(profile_id)
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing profile: {str(e)}")
                        continue
                
                if current_batch:
                    existing_profiles.extend(current_batch)
                    pd.DataFrame(existing_profiles).to_excel(excel_path, index=False)
                    self.logger.info(f"Saved {len(current_batch)} new profiles. Total: {len(existing_profiles)}/{target_profiles}")
                    retry_count = 0  # Reset retry counter if we found new profiles
                else:
                    retry_count += 1
                    self.logger.info(f"No new profiles found. Retry {retry_count}/{max_retries}")
                
                # Aggressive scrolling to trigger loading
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)  # Wait for potential loading
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == current_height:
                    # Try alternative scroll methods if normal scroll isn't working
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)
                    self.driver.execute_script("window.scrollBy(0, -100);")
                    time.sleep(1)
                
                # Periodically refresh to reset the page (every 500 profiles)
                if len(existing_profiles) > 0 and len(existing_profiles) % 500 == 0:
                    self.logger.info("Performing periodic refresh...")
                    self.driver.refresh()
                    time.sleep(3)
                    # Re-select filters if needed
                    self._select_country("United States")
                    self._select_masters_degree()
                    self._select_decision_types(["Admit", "Reject"])
            
            self.logger.info(f"Scraping completed. Total profiles saved: {len(existing_profiles)}")
            self._wait_before_close(minutes=5)

            return True
            
        except Exception as e:
            self.logger.error(f"Fatal error in scrape_and_save_profiles: {str(e)}")
            return False
        
    def wait_before_close(self, minutes=5):
        """Keep the browser open for specified minutes before closing"""
        try:
            end_time = datetime.now() + timedelta(minutes=minutes)
            self.logger.info(f"Waiting for {minutes} minutes before closing browser...")
            
            while datetime.now() < end_time:
                remaining = (end_time - datetime.now()).total_seconds()
                mins, secs = divmod(remaining, 60)
                self.logger.info(f"Time remaining: {int(mins)}m {int(secs)}s")
                time.sleep(10)  # Sleep in smaller intervals to allow keyboard interrupt
                
            self.logger.info("Wait period completed, closing browser")
            self.driver.quit()
            
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, closing browser early")
            self.driver.quit()
        except Exception as e:
            self.logger.error(f"Error during wait period: {str(e)}")
            self.driver.quit()

    def _scrape_admission_profile(self, profile_element):
        """Scrape all details from an admission profile card (updated version)"""
        profile_data = {
            "Profile ID": None,
            "Name": None,
            "Location": None,
            "Admission Term": None,
            "Admission Status": None,
            "Work Experience": None,
            "Research Papers": None,
            "University": None,
            "Program": None,
            "Level": None,
            "CGPA": None,
            "Applied on": None,
            "Decision Date": None,
            "Scholarship": "Not specified"  # Default value
        }
        
        try:
            # Get profile ID
            profile_id = profile_element.get_attribute("id")
            profile_data["Profile ID"] = profile_id
            
            # Extract name
            name_element = profile_element.find_element(By.CSS_SELECTOR, "h4.PopupModal_decision_h3__J2L__")
            profile_data["Name"] = name_element.text.strip() if name_element else None

            # Extract location and admission term
            location_div = profile_element.find_element(By.CSS_SELECTOR, "div[style='font-weight: normal; display: flex; align-items: center;']")
            if location_div:
                location_text = location_div.text
                if "|" in location_text:
                    parts = [part.strip() for part in location_text.split("|")]
                    profile_data["Location"] = parts[0]
                    profile_data["Admission Term"] = parts[1] if len(parts) > 1 else None

            # Extract admission status (from ribbon)
            try:
                ribbon = profile_element.find_element(By.CSS_SELECTOR, "div.ribbon")
                profile_data["Admission Status"] = ribbon.text.strip() if ribbon else None
            except NoSuchElementException:
                profile_data["Admission Status"] = None

            # Extract work experience and research papers
            try:
                highlights = profile_element.find_elements(By.CSS_SELECTOR, "div.admits_rejects_back_ground_color__0Dwu3.admits_rejects_exam_scores__6ZloL")
                for highlight in highlights:
                    text = highlight.text.strip()
                    if "month" in text or "year" in text:
                        profile_data["Work Experience"] = text
                    elif "research papers" in text:
                        profile_data["Research Papers"] = text
            except NoSuchElementException:
                pass

            # Extract university and program
            try:
                uni_name = profile_element.find_element(By.CSS_SELECTOR, "span.PopupModal_decision_university_name__IREOK")
                profile_data["University"] = uni_name.text.strip()
                
                program = profile_element.find_element(By.CSS_SELECTOR, "div.admits_rejects_uni_sub_container__J5RzY > span")
                profile_data["Program"] = program.text.strip()
            except NoSuchElementException:
                pass

            # Extract level
            try:
                hr = profile_element.find_element(By.CSS_SELECTOR, "hr.admits_rejects_hr-text___E5eW")
                profile_data["Level"] = hr.get_attribute("data-content")
            except NoSuchElementException:
                pass

            # Extract CGPA
            try:
                cgpa = profile_element.find_element(By.CSS_SELECTOR, "div.admits_rejects_exam_outer_view__0mhEE span")
                profile_data["CGPA"] = cgpa.text.strip()
            except NoSuchElementException:
                pass

            # Extract applied date
            try:
                applied_div = profile_element.find_element(By.CSS_SELECTOR, "div.admits_rejects_dates_view__oXNqM")
                if "Applied:" in applied_div.text:
                    profile_data["Applied on"] = applied_div.text.replace("Applied:", "").strip()
            except NoSuchElementException:
                pass

            return profile_data

        except Exception as e:
            self.logger.error(f"Error scraping profile {profile_id}: {str(e)}")
            return profile_data   

    def _scrape_100k_profiles(self, output_file="profiles_100k.xlsx"):
        """Scroll continuously and scrape until 100,000 profiles are collected"""
        try:
            # Initialize variables
            all_profiles = []
            seen_ids = set()
            last_count = 0
            no_new_profiles_count = 0
            max_no_new_profiles = 100000  # Max consecutive scrolls without new profiles
            scroll_pause = random.choice([
                random.uniform(0.5, 1.5),  # 70% chance quick scroll
                random.uniform(2.0, 4.0)   # 30% chance longer pause
            ])
            batch_save_interval = 100  # Save every 100 profiles
            
            # Get initial height and profiles
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            self.logger.info(f"Starting scrape with target of 100,000 profiles at {datetime.now()}")
            
            while len(all_profiles) < 100000 and no_new_profiles_count < max_no_new_profiles:
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_pause)
                
                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    no_new_profiles_count += 1
                    self.logger.info(f"No new content loaded ({no_new_profiles_count}/{max_no_new_profiles})")
                    # Try alternative scrolling method
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(1)
                else:
                    no_new_profiles_count = 0
                    last_height = new_height
                
                # Find all profile elements on page
                profile_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.admits_rejects_box11__3nraI")))
                
                # Process new profiles
                current_batch = []
                for element in profile_elements:
                    try:
                        profile_id = element.get_attribute("id")
                        if profile_id not in seen_ids:
                            # Scroll element into view before scraping
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                            time.sleep(0.1)
                            
                            profile_data = self._scrape_admission_profile(element)
                            if profile_data:
                                profile_data['Profile ID'] = profile_id
                                current_batch.append(profile_data)
                                seen_ids.add(profile_id)
                    except Exception as e:
                        self.logger.warning(f"Error processing profile: {str(e)}")
                        continue
                
                # Add to main collection
                if current_batch:
                    all_profiles.extend(current_batch)
                    self.logger.info(f"Found {len(current_batch)} new profiles. Total: {len(all_profiles)}")
                    
                    # Periodically save progress
                    if len(all_profiles) % batch_save_interval == 0:
                        pd.DataFrame(all_profiles).to_excel(output_file, index=False)
                        self.logger.info(f"Saved progress to {output_file}")
                
                # Check if we're stuck
                if len(all_profiles) == last_count:
                    no_new_profiles_count += 1
                last_count = len(all_profiles)
                
                # Refresh every 1000 profiles to prevent memory issues
                if len(all_profiles) > 0 and len(all_profiles) % 1000 == 0:
                    self.logger.info("Performing periodic refresh...")
                    self.driver.refresh()
                    time.sleep(5)
                    # Reapply filters if needed
                    self._select_country("United States")
                    self._select_masters_degree()
                    self._select_decision_types(["Admit", "Reject"])
            
            # Final save
            pd.DataFrame(all_profiles).to_excel(output_file, index=False)
            self.logger.info(f"Scraping complete. Total profiles saved: {len(all_profiles)}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in scrape_100k_profiles: {str(e)}")
            # Save whatever we collected before failing
            if all_profiles:
                pd.DataFrame(all_profiles).to_excel(output_file, index=False)
            return False
