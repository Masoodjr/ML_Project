from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import pandas as pd
import os
from filelock import FileLock
import random
from utils.random_wait import random_wait
from data_scraping.the_grad_cafe.scrape_profile import ProfileScraper

class TheGradCafeScraper:
    def __init__(self, driver, logger, website_name):
        self.driver = driver
        self.logger = logger
        self.website_name = website_name
        self.seen_ids = set()
        self.profiles = []
        self.LOGIN_TIMEOUT = 5  # Reduced from 10
        self.PAGE_LOAD_TIMEOUT = 10  # Reduced from 15
        self.last_page_file = "last_page.txt"
        self.data_file = "scraped_profiles.xlsx"
        self.lock_file = self.data_file + ".lock"
        self.save_threshold = 20  # Increased from 10 to reduce disk I/O
        self._initialize_excel_file()
        self.survey_base_url = "https://www.thegradcafe.com/survey/"
        
        # For improved element detection
        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)

    def _initialize_excel_file(self):
        try:
            if not os.path.exists(self.data_file):
                columns = [
                    "ID", "Acceptance Rate", "Institution", "Program", 
                    "Degree Type", "Degree's Country of Origin", "Decision",
                    "Notification Date", "Notification Method", "Undergrad GPA",
                    "GRE General", "GRE Verbal", "Analytical Writing", "Notes",
                    "Timeline Event", "Timeline Date", "Scraped Timestamp"
                ]
                df = pd.DataFrame(columns=columns)
                df.to_excel(self.data_file, index=False)
                self.logger.info(f"Created Excel file: {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error initializing Excel: {str(e)}")
            raise

    def scroll_to_element(self, element):
        """More efficient scrolling with no sleep"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
            # No sleep needed, the script executes synchronously
        except Exception as e:
            self.logger.warning(f"Could not scroll to element: {str(e)}")

    def go_to_page(self, page_number):
        """Optimized page navigation with better error handling"""
        try:
            url = f"{self.survey_base_url}?page={page_number}" if page_number != 1 else self.survey_base_url
            self.driver.get(url)
            
            # Use a short explicit wait instead of sleep
            self._wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to go to page {page_number}: {str(e)}")
            return False

    def _wait_for_page_load(self):
        """More efficient page load waiting"""
        try:
            # Use a more reliable wait condition
            WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT, ignored_exceptions=self.ignored_exceptions).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"))
            )
            # No need for additional sleep
        except Exception as e:
            self.logger.warning(f"Timeout during page load: {str(e)}")

    def _get_profile_url_from_button(self, button):
        """Extract profile URL from the options menu without clicking through"""
        try:
            # Click the options button
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            button.click()
            
            dropdown_id = button.get_attribute('id').replace('-button', '-list')
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, dropdown_id))
            )
            
            # Find the See More link without clicking it
            see_more_link = dropdown.find_element(By.XPATH, ".//a[contains(text(), 'See More')]")
            profile_url = see_more_link.get_attribute('href')
            
            # Close dropdown by clicking elsewhere
            self.driver.find_element(By.TAG_NAME, 'body').click()
            
            return profile_url
        except Exception as e:
            self.logger.error(f"Error getting profile URL: {str(e)}")
            return None

    def scrape_profile_by_url(self, url):
        """Directly scrape a profile from its URL"""
        try:
            self.driver.get(url)
            
            # Wait for profile to load
            WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(text(),'Institution')]"))
            )
            
            scraper = ProfileScraper(self.driver, self.logger)
            profile_data = scraper.scrape()
            return profile_data
        except Exception as e:
            self.logger.error(f"Error scraping profile URL: {str(e)}")
            return None

    def scrape_page_profiles_improved(self, page_number):
        """Improved method that collects all profile URLs first, then scrapes them"""
        profile_urls = []
        scraped_profiles = []
        
        try:
            self.logger.info(f"Collecting profile URLs on page {page_number}")
            
            # Find all option buttons
            options_buttons = WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"))
            )
            
            if not options_buttons:
                self.logger.warning("No profiles found on page")
                return []
                
            # First pass: collect all profile URLs
            for button in options_buttons:
                try:
                    profile_url = self._get_profile_url_from_button(button)
                    if profile_url:
                        profile_urls.append(profile_url)
                except Exception as e:
                    self.logger.error(f"Error collecting profile URL: {str(e)}")
                    continue
                    
            self.logger.info(f"Found {len(profile_urls)} profile URLs on page {page_number}")
            
            # Second pass: scrape all profiles
            for url in profile_urls:
                try:
                    profile_data = self.scrape_profile_by_url(url)
                    
                    if profile_data and profile_data.get("ID") and profile_data["ID"] not in self.seen_ids:
                        scraped_profiles.append(profile_data)
                        self.seen_ids.add(profile_data["ID"])
                        self.logger.info(f"Scraped profile ID: {profile_data['ID']}")
                except Exception as e:
                    self.logger.error(f"Error scraping profile URL: {str(e)}")
                    continue
                    
            self.logger.info(f"Successfully scraped {len(scraped_profiles)} profiles from page {page_number}")
            return scraped_profiles
            
        except Exception as e:
            self.logger.error(f"Error scraping page {page_number}: {str(e)}")
            return []

    def scrape_page_profiles_parallel(self, page_number):
        """Maintain backward compatibility with original method"""
        try:
            self.logger.info(f"Scraping profiles on page {page_number}")

            options_buttons = self.driver.find_elements(
                By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"
            )

            if not options_buttons:
                self.logger.warning("No profiles found on page")
                return False

            for idx, _ in enumerate(options_buttons):
                try:
                    if not self.open_options_and_click_see_more(idx):
                        self.logger.warning(f"Skipping profile {idx} due to failure")
                        continue

                    profile_data = self.scrape_profile()

                    if profile_data and profile_data.get("ID") and profile_data["ID"] not in self.seen_ids:
                        self.profiles.append(profile_data)
                        self.seen_ids.add(profile_data["ID"])
                        self.logger.info(f"Scraped profile ID: {profile_data['ID']}")

                    # Save periodically every N profiles
                    if len(self.profiles) >= self.save_threshold:
                        self.save_profiles()

                    self.driver.back()
                    self._wait_for_page_load()

                except Exception as e:
                    self.logger.error(f"Error scraping profile {idx}: {str(e)}")
                    continue

            # Final save after page scrape
            if self.profiles:
                self.save_profiles()

            return True

        except Exception as e:
            self.logger.error(f"Error scraping page {page_number}: {str(e)}")
            return False

    def open_options_and_click_see_more(self, profile_index):
        """Original method kept for backward compatibility"""
        try:
            WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[id^='options-menu-']"))
            )
            options_buttons = self.driver.find_elements(
                By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"
            )

            if profile_index >= len(options_buttons):
                self.logger.error(f"Profile index {profile_index} out of range.")
                return False

            button = options_buttons[profile_index]
            self.scroll_to_element(button)
            button.click()

            dropdown_id = button.get_attribute('id').replace('-button', '-list')
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, dropdown_id))
            )

            see_more_link = WebDriverWait(dropdown, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, ".//a[contains(text(), 'See More')]"))
            )

            self.scroll_to_element(see_more_link)
            see_more_link.click()

            WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(text(),'Acceptance Rate')]"))
            )
            return True
        except TimeoutException:
            self.logger.warning("Timeout clicking See More; refreshing...")
            self.driver.refresh()
            self._wait_for_page_load()
            return False
        except Exception as e:
            self.logger.error(f"Error opening See More: {str(e)}")
            return False

    def scrape_profile(self):
        """Original method kept for backward compatibility"""
        try:
            scraper = ProfileScraper(self.driver, self.logger)
            profile_data = scraper.scrape()
            return profile_data
        except Exception as e:
            self.logger.error(f"Error scraping profile: {str(e)}")
            return None

def save_profiles(self):
    """Save scraped profiles into a new Excel file if the base filename exists."""
    if not self.profiles:
        self.logger.info("No new profiles to save.")
        return

    try:
        new_df = pd.DataFrame(self.profiles)
        new_df['Scraped Timestamp'] = pd.Timestamp.now()

        # Check if base file exists and generate new filename if needed
        if os.path.exists(self.data_file):
            random_suffix = random.randint(1, 99999999999)
            new_filename = f"scraped_profiles_{random_suffix}.xlsx"
            self.logger.info(f"Base file exists, creating new file: {new_filename}")
        else:
            new_filename = self.data_file

        # Save to the appropriate filename
        new_df.to_excel(new_filename, index=False)
        self.logger.info(f"Saved {len(new_df)} profiles to {new_filename}")

        self.profiles = []  # Clear buffer after saving

    except Exception as e:
        self.logger.error(f"Error saving profiles: {str(e)}")
        raise