from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ProfileScraper:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.retry_count = 3
        self.base_wait_time = 5

    def scrape(self):
        """Main method to scrape profile data with robust error handling"""
        profile_data = {
            "ID": "unknown",
            "Acceptance Rate": None,
            "Institution": None,
            "Program": None,
            "Degree Type": None,
            "Degree's Country of Origin": None,
            "Decision": None,
            "Notification Date": None,
            "Notification Method": None,
            "Undergrad GPA": None,
            "GRE General": None,
            "GRE Verbal": None,
            "Analytical Writing": None,
            "Notes": None,
            "Timeline Event": None,
            "Timeline Date": None
        }
        
        try:
            # Extract profile ID from URL
            current_url = self.driver.current_url
            profile_id = current_url.split("/")[-1] if "/" in current_url else "unknown"
            profile_data["ID"] = profile_id
            self.logger.info(f"Scraping profile ID: {profile_id}")
            
            # Application Information section
            self._scrape_application_info(profile_data)

            # Acceptance Rate section
            self._scrape_acceptance_rate(profile_data)
            
            # Test Scores section
            self._scrape_test_scores(profile_data)
            
            # Notes section
            self._scrape_notes(profile_data)
            
            # Timeline section
            self._scrape_timeline(profile_data)
            
            # Clean and validate data
            profile_data = self._clean_profile_data(profile_data)
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Error in ProfileScraper.scrape: {str(e)}")
            return {"ID": profile_id if profile_id else "unknown"}
        
    def _scrape_acceptance_rate(self, profile_data):
        """Scrape the acceptance rate information"""
        self.logger.info("Scraping acceptance rate...")
        
        try:
            # Look for the acceptance rate field - may be in different formats
            # Try multiple possible XPath patterns
            acceptance_rate_xpaths = [
                # Direct label match
                "//dt[contains(@class,'tw-text-sm') and contains(text(),'Acceptance Rate')]/following-sibling::dd[1]",
                # Inside a stat component
                "//div[contains(@class,'tw-flex') and contains(text(),'Acceptance Rate')]/following-sibling::div[1]",
                # Inside a percentage component
                "//div[contains(@class,'tw-text-sm') and contains(text(),'Acceptance Rate')]/following-sibling::div[contains(@class,'tw-text')]",
                # Inside a label with percentage
                "//span[contains(@class,'tw-text-sm') and contains(text(),'Acceptance Rate:')]/following-sibling::span[1]"
            ]
            
            for xpath in acceptance_rate_xpaths:
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    acceptance_rate = element.text.strip()
                    
                    # Extract just the percentage if there's additional text
                    if "%" in acceptance_rate:
                        import re
                        percentage_match = re.search(r'(\d+(\.\d+)?)%', acceptance_rate)
                        if percentage_match:
                            acceptance_rate = percentage_match.group(0)
                    
                    profile_data["Acceptance Rate"] = acceptance_rate
                    self.logger.info(f"Extracted Acceptance Rate: {acceptance_rate}")
                    break
                except:
                    continue
            
            # If we didn't find the acceptance rate with specific XPaths, try a more generic approach
            if not profile_data["Acceptance Rate"]:
                # Try to find any element containing "Acceptance Rate" and get its nearby value
                container_xpath = "//*[contains(text(),'Acceptance Rate')]"
                container = self.driver.find_element(By.XPATH, container_xpath)
                
                # Find the closest parent div or element
                parent = container.find_element(By.XPATH, "./ancestor::div[contains(@class, 'tw-')]")
                
                # Look for the value - usually a child div or adjacent element
                value_xpath = ".//div[contains(@class, 'tw-text')] | .//span[contains(@class, 'tw-text')] | .//dd"
                value_element = parent.find_element(By.XPATH, value_xpath)
                
                if value_element:
                    acceptance_rate = value_element.text.strip()
                    profile_data["Acceptance Rate"] = acceptance_rate
                    self.logger.info(f"Extracted Acceptance Rate using alternative method: {acceptance_rate}")
        
        except Exception as e:
            self.logger.warning(f"Could not extract Acceptance Rate: {str(e)}")
    
    
    def _scrape_application_info(self, profile_data):
        """Scrape application information section using tailwind CSS classes"""
        self.logger.info("Scraping application information...")
        
        # Field mappings with xpath using tw- tailwind classes
        field_mappings = {
            "Institution": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Institution')]/following-sibling::dd[1]",
            "Program": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Program')]/following-sibling::dd[1]",
            "Degree Type": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Degree Type')]/following-sibling::dd[1]",
            "Degree's Country of Origin": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Degree')]/following-sibling::dd[1]",
            "Decision": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Decision')]/following-sibling::dd[1]"
        }
        
        for field, xpath in field_mappings.items():
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                profile_data[field] = element.text.strip()
                self.logger.info(f"Extracted {field}: {profile_data[field]}")
            except Exception as e:
                self.logger.warning(f"Could not extract {field}: {str(e)}")
        
        # Handle notification specifically as it has date and method components
        try:
            notification_xpath = "//dt[contains(@class,'tw-text-sm') and contains(text(),'Notification')]/following-sibling::dd[1]"
            notification_element = self.driver.find_element(By.XPATH, notification_xpath)
            notification_text = notification_element.text.strip()
            
            if "via" in notification_text:
                date_part, method_part = notification_text.split("via", 1)
                profile_data["Notification Date"] = date_part.replace("on", "").strip()
                profile_data["Notification Method"] = "via " + method_part.strip()
                self.logger.info(f"Extracted notification date: {profile_data['Notification Date']} and method: {profile_data['Notification Method']}")
            else:
                profile_data["Notification Date"] = notification_text
                self.logger.info(f"Extracted notification date: {profile_data['Notification Date']}")
        except Exception as e:
            self.logger.warning(f"Could not extract notification info: {str(e)}")
    
    def _scrape_test_scores(self, profile_data):
        """Scrape test scores with tailwind CSS classes"""
        self.logger.info("Scraping test scores...")
        
        # Extract GPA
        try:
            gpa_xpath = "//dt[contains(@class,'tw-text-sm') and contains(text(),'Undergrad GPA')]/following-sibling::dd[1]"
            gpa_element = self.driver.find_element(By.XPATH, gpa_xpath)
            profile_data["Undergrad GPA"] = gpa_element.text.strip()
            self.logger.info(f"Extracted GPA: {profile_data['Undergrad GPA']}")
        except Exception as e:
            self.logger.warning(f"Could not extract GPA: {str(e)}")
        
        # Extract GRE scores using span elements
        score_mappings = {
            "GRE General": "//span[contains(@class,'tw-text-sm') and contains(text(),'GRE General:')]/following-sibling::span[1]",
            "GRE Verbal": "//span[contains(@class,'tw-text-sm') and contains(text(),'GRE Verbal:')]/following-sibling::span[1]",
            "Analytical Writing": "//span[contains(@class,'tw-text-sm') and contains(text(),'Analytical Writing:')]/following-sibling::span[1]"
        }
        
        for field, xpath in score_mappings.items():
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                profile_data[field] = element.text.strip()
                self.logger.info(f"Extracted {field}: {profile_data[field]}")
            except Exception as e:
                self.logger.warning(f"Could not extract {field}: {str(e)}")
    
    def _scrape_notes(self, profile_data):
        """Scrape notes section"""
        self.logger.info("Scraping notes...")
        
        try:
            notes_xpath = "//dt[contains(@class,'tw-text-sm') and contains(text(),'Notes')]/following-sibling::dd[1]"
            notes_element = self.driver.find_element(By.XPATH, notes_xpath)
            profile_data["Notes"] = notes_element.text.strip()
            self.logger.info(f"Extracted notes (truncated): {profile_data['Notes'][:50]}...")
        except Exception as e:
            self.logger.warning(f"Could not extract notes: {str(e)}")
    
    def _scrape_timeline(self, profile_data):
        """Scrape timeline information"""
        self.logger.info("Scraping timeline...")
        
        try:
            # Timeline event using the strong element inside timeline section
            event_xpath = "//div[contains(@class,'timeline') or contains(@class,'tw-flex tw-min-w-0')]//strong"
            event_element = self.driver.find_element(By.XPATH, event_xpath)
            profile_data["Timeline Event"] = event_element.text.strip()
            self.logger.info(f"Extracted timeline event: {profile_data['Timeline Event']}")
            
            # Timeline date using the time element
            date_xpath = "//div[contains(@class,'timeline') or contains(@class,'tw-whitespace-nowrap')]//time"
            date_element = self.driver.find_element(By.XPATH, date_xpath)
            profile_data["Timeline Date"] = date_element.text.strip()
            self.logger.info(f"Extracted timeline date: {profile_data['Timeline Date']}")
        except Exception as e:
            self.logger.warning(f"Could not extract timeline: {str(e)}")
    
    def _clean_profile_data(self, data):
        """Clean and normalize scraped data"""
        self.logger.info("Cleaning scraped data...")
        
        # Clean GPA
        if data.get("Undergrad GPA") in ["0.00", "0", "N/A", ""]:
            self.logger.info("Converting invalid GPA to None")
            data["Undergrad GPA"] = None
        elif data.get("Undergrad GPA"):
            try:
                data["Undergrad GPA"] = float(data["Undergrad GPA"])
            except ValueError:
                data["Undergrad GPA"] = None
        
        # Clean GRE scores
        for field in ["GRE General", "GRE Verbal"]:
            if data.get(field) in ["0", "N/A", ""]:
                data[field] = None
            elif data.get(field):
                try:
                    data[field] = int(data[field])
                except ValueError:
                    data[field] = None
        
        # Clean Analytical Writing
        if data.get("Analytical Writing") in ["0.00", "0", "N/A", ""]:
            data["Analytical Writing"] = None
        elif data.get("Analytical Writing"):
            try:
                data["Analytical Writing"] = float(data["Analytical Writing"])
            except ValueError:
                data["Analytical Writing"] = None
        
        self.logger.info("Data cleaning completed")
        return data

# Fixed version of open_options_and_click_see_more in TheGradCafeScraper
def open_options_and_click_see_more(self, button):
    """Click the given options button, then click 'See More'."""
    try:
        self.scroll_to_element(button)
        button.click()
        self.logger.info("Clicked options menu button")
        
        # Extract the button ID for constructing the dropdown ID
        button_id = button.get_attribute('id')
        dropdown_id = button_id.replace('-button', '-list')
        
        # Wait for the dropdown to become visible
        self.logger.info(f"Waiting for dropdown with ID: {dropdown_id}")
        dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
            EC.visibility_of_element_located((By.ID, dropdown_id))
        )
        
        # Find the See More link within the dropdown using the correct selector
        # The class names are likely using tailwind CSS (tw-) prefixes
        see_more_xpath = ".//a[contains(text(), 'See More') or contains(@class, 'tw-text') and contains(text(), 'See More')]"
        see_more_link = dropdown.find_element(By.XPATH, see_more_xpath)
        
        self.logger.info("Found 'See More' link")
        self.scroll_to_element(see_more_link)
        see_more_link.click()
        self.logger.info("Clicked 'See More' link")
        
        # Wait for profile page to load - looking for tailwind classes
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//dt[contains(@class, 'tw-text-sm') and contains(text(),'Institution')]"))
        )
        
        return True
    except Exception as e:
        self.logger.error(f"Failed to open options and click 'See More': {str(e)}")
        return False