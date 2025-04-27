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
        self.LOGIN_TIMEOUT = 5  # You can set this when initializing the object too
        self.last_page_file = "last_page.txt"
        self.data_file = "scraped_profiles.xlsx"
        self._initialize_excel_file()

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
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)

    def go_to_page(self, page_number):
        """Directly go to a given page number."""
        try:
            if page_number == 1:
                self.logger.info("Already on page 1, no navigation needed.")
                return

            self.logger.info(f"Navigating to page {page_number}...")
            page_link = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@href='/survey/?page={page_number}']"))
            )
            self.scroll_to_element(page_link)
            page_link.click()
            time.sleep(2)

        except Exception as e:
            self.logger.error(f"Could not navigate to page {page_number}: {str(e)}")
            raise

    def go_to_next_page(self):
        """Click the 'Next' button to move to the next survey page."""
        try:
            self.logger.info("Clicking the Next button...")
            next_button = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Next')]"))
            )
            self.scroll_to_element(next_button)
            next_button.click()
            time.sleep(2)
        except Exception as e:
            self.logger.error(f"Could not move to next page: {str(e)}")
            raise
        
    # def open_options_and_click_see_more(self, button):
    #     """Click the given options button, then click 'See More'."""
    #     try:
    #         self.scroll_to_element(button)
    #         button.click()
    #         print("Clicked options menu button, now trying to locate 'See More' link...")

    #         # Wait until the dropdown menu becomes visible (id ends with '-list')
    #         WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
    #             EC.visibility_of_element_located((By.ID, f"{button.get_attribute('id').replace('-button', '-list')}"))
    #         )

    #         # Wait until the dropdown is visible
    #         WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
    #             EC.visibility_of_element_located((By.ID, f"{button.get_attribute('id').replace('-button', '-list')}"))
    #         )

    #         print("Trying to open dropdown ID:", button.get_attribute('id').replace('-button', '-list'))

    #         # Now find and click the "See More" link
    #         see_more_link = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
    #             EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'See More')]"))
    #         )
    #         self.scroll_to_element(see_more_link)
    #         see_more_link.click()
    #         time.sleep(1)

    #     except Exception as e:
    #         self.logger.error(f"Failed during open options and click 'See More': {str(e)}")
    #         raise

    def open_options_and_click_see_more(self, button):
        """Click the given options button, then click 'See More'."""
        try:
            self.scroll_to_element(button)
            button.click()
            print("Options button clicked, waiting for dropdown...")

            dropdown_id = button.get_attribute('id').replace('-button', '-list')
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, dropdown_id))
            )
            print(f"Dropdown with ID {dropdown_id} visible.")

            see_more_link = dropdown.find_element(By.XPATH, ".//a[contains(text(), 'See More')]")
            self.scroll_to_element(see_more_link)
            see_more_link.click()
            print("'See More' link clicked.")
            time.sleep(2)

        except Exception as e:
            self.logger.error(f"Failed during open options and click 'See More': {str(e)}")
            raise



    def scrape_profile(self):
        scraper = ProfileScraper(self.driver, self.logger)
        profile_data = scraper.scrape()
        return profile_data


    def scrape_page_profiles(self):
        """Scrape all profiles on the current page."""
        try:
            total_profiles = len(self.driver.find_elements(By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"))
            if not total_profiles:
                self.logger.info("No profiles found on this page.")
                return

            self.logger.info(f"Found {total_profiles} profiles on this page.")

            idx = 0
            while idx < total_profiles:
                self.logger.info(f"Scraping profile {idx + 1}...")
                try:
                    options_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']")
                    button = options_buttons[idx]

                    self.open_options_and_click_see_more(button)

                    # Wait until the profile page loads
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//dt[contains(text(),'Acceptance Rate')]"))
                    )
                    time.sleep(1)

                    profile_data = self.scrape_profile()
                    if profile_data.get("ID") and profile_data["ID"] not in self.seen_ids:
                        self.profiles.append(profile_data)
                        self.seen_ids.add(profile_data["ID"])

                    # Instead of .back(), reload /survey/
                    self.driver.get("https://www.thegradcafe.com/survey/")

                    # Wait until survey page loads
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"))
                    )
                    time.sleep(1)

                    idx += 1

                except Exception as e:
                    self.logger.error(f"Error scraping a profile: {str(e)}")
                    # If failed, move to next profile
                    idx += 1
                    continue

        except Exception as e:
            self.logger.error(f"Error scraping profiles from page: {str(e)}")

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
        if os.path.exists(self.last_page_file):
            with open(self.last_page_file, "r") as f:
                return int(f.read().strip())
        return 1

    def start_scraping(self, resume = False):
        """Complete scraping workflow across all pages."""
        try:
            if resume:
                current_page = self.load_last_page()
                self.logger.info(f"Resuming from saved page {current_page}")

            else:
                current_page = 1
                self.logger.info("Starting fresh from page 1")
               
            self.go_to_page(current_page)

            while True:
                self.scrape_page_profiles()
                self.save_profiles()
                self.save_last_page(current_page)

                try:
                    self.go_to_next_page()
                    current_page += 1
                except Exception:
                    self.logger.info("No more pages to scrape.")
                    break

        except Exception as e:
            self.logger.error(f"Fatal error during scraping: {str(e)}")

    def save_profiles(self):
        """Save scraped profiles to Excel file"""
        if not self.profiles:
            self.logger.info("No profiles to save")
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