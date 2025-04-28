from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
from utils.random_wait import random_wait
from data_scraping.the_grad_cafe.scrape_profile import ProfileScraper

class TheGradCafeScraper:
    def __init__(self, driver, logger, website_name):
        self.driver = driver
        self.logger = logger
        self.website_name = website_name
        self.seen_ids = set()
        self.profiles = []
        self.LOGIN_TIMEOUT = 10  # Increased timeout for more reliability
        self.PAGE_LOAD_TIMEOUT = 15  # Added separate timeout for page loads
        self.last_page_file = "last_page.txt"
        self.data_file = "scraped_profiles.xlsx"
        self._initialize_excel_file()
        self.survey_base_url = "https://www.thegradcafe.com/survey/"

    def _initialize_excel_file(self):
        """Initialize the Excel file with headers if it doesn't exist"""
        try:
            if not os.path.exists(self.data_file):
                # Define the column headers
                columns = [
                    "ID", "Acceptance Rate", "Institution", "Program", 
                    "Degree Type", "Degree's Country of Origin", "Decision",
                    "Notification Date", "Notification Method", "Undergrad GPA",
                    "GRE General", "GRE Verbal", "Analytical Writing", "Notes",
                    "Timeline Event", "Timeline Date", "Scraped Timestamp"
                ]
                
                # Create a DataFrame with just the headers
                df = pd.DataFrame(columns=columns)
                
                # Save to Excel
                df.to_excel(self.data_file, index=False)
                self.logger.info(f"Created new Excel file: {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error initializing Excel file: {str(e)}")
            raise

    def scroll_to_element(self, element):
        """Scroll the element into center view."""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)  # Increased wait time after scrolling
        except Exception as e:
            self.logger.warning(f"Could not scroll to element: {str(e)}")

    def go_to_page(self, page_number):
        """Directly go to a given page number."""
        try:
            if page_number == 1:
                # Go directly to the base URL for page 1
                self.driver.get(self.survey_base_url)
                self.logger.info("Navigated to page 1 directly.")
                self._wait_for_page_load()
                return True

            self.logger.info(f"Navigating to page {page_number}...")
            # Directly navigate to the specific page URL instead of clicking
            self.driver.get(f"{self.survey_base_url}?page={page_number}")
            self._wait_for_page_load()
            self.logger.info(f"Successfully navigated to page {page_number}")
            return True

        except Exception as e:
            self.logger.error(f"Could not navigate to page {page_number}: {str(e)}")
            return False

    def _wait_for_page_load(self):
        """Wait for the page to fully load by checking for profile options buttons."""
        try:
            WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"))
            )
            time.sleep(2)  # Additional wait to ensure JavaScript is fully loaded
        except Exception as e:
            self.logger.warning(f"Timeout waiting for page to load completely: {str(e)}")

    def go_to_next_page(self, current_page):
        """Navigate to the next page by URL rather than clicking."""
        try:
            next_page = current_page + 1
            self.logger.info(f"Navigating to next page (page {next_page})...")
            return self.go_to_page(next_page)
        except Exception as e:
            self.logger.error(f"Could not move to next page: {str(e)}")
            return False
        
    def open_options_and_click_see_more(self, profile_index):
        """Click options and 'See More' for a profile by index."""
        MAX_RETRIES = 2
        for attempt in range(MAX_RETRIES):
            try:
                # Wait for profiles to load with a more reliable locator
                WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[id^='options-menu-']"))
                )
                
                # Get fresh list of options buttons
                options_buttons = self.driver.find_elements(
                    By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"
                )
                
                if profile_index >= len(options_buttons):
                    self.logger.error(f"Profile index {profile_index} out of range. Only {len(options_buttons)} profiles available.")
                    return False
                
                button = options_buttons[profile_index]
                button_id = button.get_attribute('id')
                self.logger.info(f"Opening options menu for button ID: {button_id}")
                
                # Scroll to and click the options button
                self.scroll_to_element(button)
                button.click()
                
                # Wait for dropdown to be visible and clickable
                dropdown_id = button_id.replace('-button', '-list')
                dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                    EC.visibility_of_element_located((By.ID, dropdown_id)))
                
                # Find and click See More with explicit wait
                see_more_link = WebDriverWait(dropdown, self.LOGIN_TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, ".//a[contains(text(), 'See More')]")))
                
                self.scroll_to_element(see_more_link)
                see_more_link.click()
                
                # Wait for profile page to load with a more reliable indicator
                WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
                    EC.presence_of_element_located((By.XPATH, "//dt[contains(text(),'Acceptance Rate')]")))
                
                # Additional stability wait
                time.sleep(1)
                return True
                
            except TimeoutException:
                self.logger.warning(f"Timeout on attempt {attempt + 1}. Refreshing page...")
                self.driver.refresh()
                self._wait_for_page_load()
                continue
                
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    self.logger.info("Retrying...")
                    continue
                else:
                    self.logger.error("Failed to open profile after maximum retries")
                    return False

    # def open_options_and_click_see_more(self, profile_index):
    #     """Click options and 'See More' for a profile by index."""
    #     MAX_RETRIES = 3
    #     for attempt in range(MAX_RETRIES):
    #         try:
    #             # Get a fresh list of options buttons
    #             options_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
    #                               "button[id^='options-menu-'][aria-haspopup='true']")
                
    #             if profile_index >= len(options_buttons):
    #                 self.logger.error(f"Profile index {profile_index} out of range. Only {len(options_buttons)} profiles available.")
    #                 return False
                
    #             button = options_buttons[profile_index]
    #             button_id = button.get_attribute('id')
    #             self.logger.info(f"Opening options menu for button ID: {button_id}")
                
    #             # Scroll and click the options button
    #             self.scroll_to_element(button)
    #             button.click()
    #             self.logger.info("Options button clicked, waiting for dropdown...")
                
    #             # Wait for dropdown to appear
    #             dropdown_id = button_id.replace('-button', '-list')
    #             dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
    #                 EC.visibility_of_element_located((By.ID, dropdown_id))
    #             )
    #             self.logger.info(f"Dropdown with ID {dropdown_id} visible.")
                
    #             # Find and click See More
    #             see_more_link = dropdown.find_element(By.XPATH, ".//a[contains(text(), 'See More')]")
    #             self.scroll_to_element(see_more_link)
    #             see_more_link.click()
    #             self.logger.info("'See More' link clicked.")
                
    #             # Wait for profile page to load
    #             WebDriverWait(self.driver, self.PAGE_LOAD_TIMEOUT).until(
    #                 EC.presence_of_element_located((By.XPATH, "//dt[contains(text(),'Acceptance Rate')]"))
    #             )
    #             time.sleep(1.5)  # Increased wait time
    #             return True
                
    #         except Exception as e:
    #             self.logger.warning(f"Attempt {attempt+1}/{MAX_RETRIES} failed: {str(e)}")
    #             if attempt < MAX_RETRIES - 1:
    #                 self.logger.info("Refreshing page and retrying...")
    #                 self.driver.refresh()
    #                 self._wait_for_page_load()
    #             else:
    #                 self.logger.error("Failed to open profile after maximum retries")
    #                 return False

    def scrape_profile(self):
        """Scrape the current profile page."""
        try:
            scraper = ProfileScraper(self.driver, self.logger)
            profile_data = scraper.scrape()
            return profile_data
        except Exception as e:
            self.logger.error(f"Error in profile scraper: {str(e)}")
            return None

    def return_to_survey_page(self, current_page):
        """Return to the survey page at the specified page number."""
        try:
            self.logger.info(f"Returning to survey page {current_page}...")
            success = self.go_to_page(current_page)
            if success:
                self.logger.info(f"Successfully returned to survey page {current_page}")
                return True
            else:
                self.logger.error(f"Failed to return to survey page {current_page}")
                return False
        except Exception as e:
            self.logger.error(f"Error returning to survey page: {str(e)}")
            return False

    def scrape_page_profiles(self, current_page):
        """Scrape all profiles on the current page."""
        try:
            options_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']")
            total_profiles = len(options_buttons)
            
            if not total_profiles:
                self.logger.info("No profiles found on this page.")
                return True  # Return True to continue to next page
            
            self.logger.info(f"Found {total_profiles} profiles on this page.")
            
            # Process each profile
            idx = 0
            while idx < total_profiles:
                self.logger.info(f"Scraping profile {idx + 1}/{total_profiles}...")
                try:
                    # Open the profile
                    if not self.open_options_and_click_see_more(idx):
                        self.logger.warning(f"Skipping profile {idx + 1} due to access failure")
                        idx += 1  # Move to next profile
                        continue
                    
                    # Scrape the profile data
                    profile_data = self.scrape_profile()
                    if profile_data and profile_data.get("ID") and profile_data["ID"] not in self.seen_ids:
                        self.profiles.append(profile_data)
                        self.seen_ids.add(profile_data["ID"])
                        self.logger.info(f"Successfully scraped profile ID: {profile_data['ID']}")
                    
                    # Return to the survey page
                    if not self.return_to_survey_page(current_page):
                        self.logger.warning("Failed to return to survey page, trying to recover...")
                        if not self.go_to_page(current_page):
                            self.logger.error("Recovery failed, saving data and exiting...")
                            self.save_profiles()
                            return False
                    
                    # After every 5 profiles, save progress
                    if (idx + 1) % 5 == 0:
                        self.save_profiles()
                        
                    idx += 1
                    
                except Exception as e:
                    self.logger.error(f"Error scraping profile {idx + 1}: {str(e)}")
                    # Try to recover by returning to the survey page
                    self.return_to_survey_page(current_page)
                    idx += 1  # Move to next profile
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fatal error scraping profiles from page: {str(e)}")
            return False

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
                   current_page = 172
                self.logger.info(f"Resuming from saved page {current_page}")
            else:
                current_page = 172
                self.logger.info("Starting fresh from page 48")
            
            # Go to the starting page
            if not self.go_to_page(current_page):
                self.logger.error("Failed to navigate to starting page. Exiting.")
                return False
            
            MAX_PAGES = 50  # Safety limit
            page_count = 0
            
            while page_count < 1000:
                self.logger.info(f"Processing page {current_page}")
                
                # Scrape profiles on current page
                if not self.scrape_page_profiles(current_page):
                    self.logger.error(f"Failed while scraping page {current_page}")
                    break
                
                # Save progress
                self.save_profiles()
                self.save_last_page(current_page)
                
                # Try to move to next page
                if not self.go_to_next_page(current_page):
                    self.logger.info("No more pages to scrape or navigation failed.")
                    break
                
                current_page += 1
                page_count += 1
                time.sleep(2)  # Short pause between pages
            
            self.logger.info("Scraping completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Fatal error during scraping: {str(e)}")
            # Save whatever we've got so far
            self.save_profiles()
            return False

    def save_profiles(self):
        """Save scraped profiles to Excel file"""
        if not self.profiles:
            self.logger.info("No new profiles to save")
            return
        
        try:
            # Create DataFrame from scraped profiles
            new_df = pd.DataFrame(self.profiles)
            
            # Add timestamp for when the data was scraped
            new_df['Scraped Timestamp'] = pd.Timestamp.now()
            
            # Check if file exists
            if os.path.exists(self.data_file):
                # Read existing data
                existing_df = pd.read_excel(self.data_file)
                
                # Filter out duplicates by ID
                existing_ids = set(existing_df['ID'].values) if 'ID' in existing_df.columns else set()
                new_df = new_df[~new_df['ID'].isin(existing_ids)]
                
                # Combine old and new data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df
            
            # Save to Excel
            combined_df.to_excel(self.data_file, index=False)
            self.logger.info(f"Saved {len(new_df)} profiles to {self.data_file}")
            
            # Clear the saved profiles
            self.profiles = []
            
        except Exception as e:
            self.logger.error(f"Error saving profiles: {str(e)}")
            raise
