from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import os
from filelock import FileLock  # <-- NEW

from utils.random_wait import random_wait
from data_scraping.the_grad_cafe.scrape_profile import ProfileScraper

class TheGradCafeScraper:
    def __init__(self, driver, logger, website_name):
        self.driver = driver
        self.logger = logger
        self.website_name = website_name
        self.seen_ids = set()
        self.profiles = []
        self.LOGIN_TIMEOUT = 10
        self.PAGE_LOAD_TIMEOUT = 15
        self.last_page_file = "last_page.txt"
        self.data_file = "scraped_profiles.xlsx"
        self.lock_file = self.data_file + ".lock"  # <-- NEW
        self.save_threshold = 10  # <-- NEW: Save every 10 profiles
        self._initialize_excel_file()
        self.survey_base_url = "https://www.thegradcafe.com/survey/"

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
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
        except Exception as e:
            self.logger.warning(f"Could not scroll to element: {str(e)}")

    def go_to_page(self, page_number):
        try:
            url = f"{self.survey_base_url}?page={page_number}" if page_number != 1 else self.survey_base_url
            self.driver.get(url)
            self.logger.info(f"Navigated to page {page_number}")
            self._wait_for_page_load()
            return True
        except Exception as e:
            self.logger.error(f"Failed to go to page {page_number}: {str(e)}")
            return False

    def _wait_for_page_load(self):
        try:
            WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"))
            )
            time.sleep(2)
        except Exception as e:
            self.logger.warning(f"Timeout during page load: {str(e)}")

    def open_options_and_click_see_more(self, profile_index):
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
            time.sleep(1)
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
        try:
            scraper = ProfileScraper(self.driver, self.logger)
            profile_data = scraper.scrape()
            return profile_data
        except Exception as e:
            self.logger.error(f"Error scraping profile: {str(e)}")
            return None

    def scrape_page_profiles_parallel(self, page_number):
        """Main function used by multiprocessing: scrape all profiles from given page."""
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

<<<<<<< HEAD
    def save_last_page(self, page_number):
        """Save the last scraped page number."""
        try:
            with open(self.last_page_file, "w") as f:
                f.write(str(page_number))
            self.logger.info(f"Saved last page {page_number} for recovery.")
        except Exception as e:
            self.logger.error(f"Error saving last page: {str(e)}")

    def load_last_page(self):
        """Load the last page number scraped."""
        try:
            if os.path.exists(self.last_page_file):
                with open(self.last_page_file, "r") as f:
                    return int(f.read().strip())
            return 1
        except Exception as e:
            self.logger.error(f"Error loading last page: {str(e)}")
            return 1

    def start_scraping(self, resume=False):
        """Complete scraping workflow across all pages."""
        try:
            if resume:
                current_page = self.load_last_page()
                if current_page < 1000:
                   current_page = 1000
                self.logger.info(f"Resuming from saved page {current_page}")
            else:
                current_page = 1000
                self.logger.info("Starting fresh from page 1000")
            
            # Go to the starting page
            if not self.go_to_page(current_page):
                self.logger.error("Failed to navigate to starting page. Exiting.")
                return False
            
            MAX_PAGES = 50  # Safety limit
            page_count = 0
            
            while current_page <= 1999:
                self.logger.info(f"Processing page {current_page}")
                
                # Scrape profiles on current page
                if not self.scrape_page_profiles(current_page):
                    self.logger.error(f"Failed while scraping page {current_page}")
                    break
                
                # Save progress
=======
            # Final save after page scrape
            if self.profiles:
>>>>>>> backup-before-switch
                self.save_profiles()

            return True

        except Exception as e:
            self.logger.error(f"Error scraping page {page_number}: {str(e)}")
            return False

    def save_profiles(self):
        """Save scraped profiles into Excel safely using file locking."""
        if not self.profiles:
            self.logger.info("No new profiles to save.")
            return

        try:
            new_df = pd.DataFrame(self.profiles)
            new_df['Scraped Timestamp'] = pd.Timestamp.now()

            lock = FileLock(self.lock_file, timeout=120)

            with lock:
                if os.path.exists(self.data_file):
                    existing_df = pd.read_excel(self.data_file)
                    existing_ids = set(existing_df['ID'].values) if 'ID' in existing_df.columns else set()
                    new_df = new_df[~new_df['ID'].isin(existing_ids)]
                    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                else:
                    combined_df = new_df

                combined_df.to_excel(self.data_file, index=False)
                self.logger.info(f"Saved {len(new_df)} new profiles to {self.data_file}")

            self.profiles = []  # Clear buffer after saving

        except Exception as e:
            self.logger.error(f"Error saving profiles: {str(e)}")
            raise
