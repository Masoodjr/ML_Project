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
        self.LOGIN_TIMEOUT = 10  # Increased timeout
        self.last_page_file = "last_page.txt"
        self.data_file = "scraped_profiles.xlsx"
        self._initialize_data_file()

    def _initialize_data_file(self):
        """Initialize the output file with headers if it doesn't exist"""
        if not os.path.exists(self.data_file):
            columns = [
                "ID", "Acceptance Rate", "Institution", "Program", 
                "Degree Type", "Degree's Country of Origin", "Decision",
                "Notification Date", "Notification Method", "Undergrad GPA",
                "GRE General", "GRE Verbal", "Analytical Writing", "Notes",
                "Timeline Event", "Timeline Date", "Scraped Timestamp"
            ]
            pd.DataFrame(columns=columns).to_excel(self.data_file, index=False)
            self.logger.info(f"Created new output file: {self.data_file}")

    def scroll_to_element(self, element):
        """Scroll the element into center view with smooth behavior."""
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
            element
        )
        time.sleep(random_wait(0.5, 1))

    def go_to_page(self, page_number):
        """Directly go to a given page number with improved reliability"""
        try:
            if page_number == 1:
                self.driver.get("https://www.thegradcafe.com/survey/")
                self.logger.info("Navigated to page 1")
                return

            self.logger.info(f"Navigating to page {page_number}...")
            self.driver.get(f"https://www.thegradcafe.com/survey/?page={page_number}")
            
            # Verify page loaded
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='options-menu-']"))
            )
            time.sleep(random_wait(1, 2))

        except Exception as e:
            self.logger.error(f"Could not navigate to page {page_number}: {str(e)}")
            raise

    def open_options_and_click_see_more(self, button):
        """More reliable method to open options and click See More"""
        try:
            self.scroll_to_element(button)
            
            # Click using JavaScript to avoid interception
            self.driver.execute_script("arguments[0].click();", button)
            self.logger.info("Options button clicked")
            
            # Wait for dropdown to appear
            dropdown_id = button.get_attribute('id').replace('-button', '-list')
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, dropdown_id))
            
            # Find See More link within the dropdown
            see_more = WebDriverWait(dropdown, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "See More")))
            
            self.driver.execute_script("arguments[0].click();", see_more)
            self.logger.info("Clicked See More link")
            
            # Wait for profile page to load
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Application Information')]"))
            time.sleep(random_wait(1, 2))
            
        except Exception as e:
            self.logger.error(f"Failed to open profile: {str(e)}")
            raise

    def scrape_page_profiles(self):
        """Scrape all profiles on current page with better error handling"""
        try:
            # Wait for profiles to load
            WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='options-menu-']"))
            
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button[id^='options-menu-']")
            self.logger.info(f"Found {len(buttons)} profiles on page")
            
            for i, button in enumerate(buttons, 1):
                try:
                    self.logger.info(f"Processing profile {i}/{len(buttons)}")
                    
                    # Open profile
                    self.open_options_and_click_see_more(button)
                    
                    # Scrape profile data
                    profile_data = ProfileScraper(self.driver, self.logger).scrape()
                    
                    if profile_data and profile_data.get("ID") and profile_data["ID"] not in self.seen_ids:
                        self.profiles.append(profile_data)
                        self.seen_ids.add(profile_data["ID"])
                        self.logger.info(f"Successfully scraped profile {profile_data['ID']}")
                    
                    # Return to survey page
                    self.driver.back()
                    WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[id^='options-menu-']"))
                    time.sleep(random_wait(1, 2))
                    
                except Exception as e:
                    self.logger.error(f"Error processing profile {i}: {str(e)}")
                    # Try to recover by going back to survey page
                    if "survey" not in self.driver.current_url:
                        self.driver.get("https://www.thegradcafe.com/survey/")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error scraping page: {str(e)}")
            raise

    def save_profiles(self):
        """Save scraped profiles to Excel with append mode"""
        try:
            if not self.profiles:
                return
                
            # Read existing data if file exists
            if os.path.exists(self.data_file):
                existing_df = pd.read_excel(self.data_file)
            else:
                existing_df = pd.DataFrame()
            
            # Combine with new data
            new_df = pd.DataFrame(self.profiles)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            
            # Save to Excel
            combined_df.to_excel(self.data_file, index=False)
            self.logger.info(f"Saved {len(new_df)} profiles to {self.data_file}")
            self.profiles = []  # Clear saved profiles
            
        except Exception as e:
            self.logger.error(f"Error saving profiles: {str(e)}")

    def start_scraping(self, resume=False, max_pages=None):
        """Main scraping loop with improved resume functionality"""
        try:
            current_page = self.load_last_page() if resume else 1
            self.logger.info(f"Starting scraping from page {current_page}")
            
            while True:
                if max_pages and current_page > max_pages:
                    self.logger.info(f"Reached maximum page limit of {max_pages}")
                    break
                    
                self.go_to_page(current_page)
                self.scrape_page_profiles()
                self.save_profiles()
                self.save_last_page(current_page)
                
                # Check if there's a next page
                try:
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'Next')]")))
                    if "disabled" in next_button.get_attribute("class"):
                        self.logger.info("No more pages available")
                        break
                    current_page += 1
                except:
                    self.logger.info("No next page button found")
                    break
                    
        except Exception as e:
            self.logger.error(f"Scraping failed: {str(e)}")
            raise
        finally:
            self.logger.info("Scraping completed")

    def save_last_page(self, page_number):
        """Save the last scraped page number"""
        try:
            with open(self.last_page_file, 'w') as f:
                f.write(str(page_number))
        except Exception as e:
            self.logger.error(f"Error saving last page: {str(e)}")

    def load_last_page(self):
        """Load the last scraped page number"""
        try:
            if os.path.exists(self.last_page_file):
                with open(self.last_page_file, 'r') as f:
                    return int(f.read().strip())
        except Exception as e:
            self.logger.error(f"Error loading last page: {str(e)}")
        return 1