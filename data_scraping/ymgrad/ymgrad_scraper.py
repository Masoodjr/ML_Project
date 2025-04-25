import time
import random
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class YMGradScraper:
    def __init__(self, driver, logger, parser, website_name):
        self.driver = driver
        self.logger = logger
        self.parser = parser
        self.website_name = website_name
        self.seen_ids = set()
        self.profiles = []

    def scrape_profile_and_save_data(self):
        output_file=f"historical_data_{self.website_name}.xlsx"
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
