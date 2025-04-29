from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
import re

class ProfileScraper:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger
        self.retry_count = 2  # Reduced from 3
        self.base_wait_time = 3  # Reduced from 5
        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
        self.LOGIN_TIMEOUT = 5  # Added for methods that need this

    def scrape(self):
        """Main method to scrape profile data with robust error handling and optimized performance"""
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
            
            # Use a single pass through the DOM to find all elements
            self._scrape_all_fields(profile_data)
            
            # Clean and validate data
            profile_data = self._clean_profile_data(profile_data)
            
            return profile_data
            
        except Exception as e:
            self.logger.error(f"Error in ProfileScraper.scrape: {str(e)}")
            profile_id = profile_data.get("ID", "unknown")
            return {"ID": profile_id}
    
    def _scrape_all_fields(self, profile_data):
        """Optimized method to scrape all fields in one pass"""
        try:
            # Application Information
            field_mappings = {
                "Institution": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Institution')]/following-sibling::dd[1]",
                "Program": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Program')]/following-sibling::dd[1]",
                "Degree Type": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Degree Type')]/following-sibling::dd[1]",
                "Degree's Country of Origin": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Degree')]/following-sibling::dd[1]",
                "Decision": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Decision')]/following-sibling::dd[1]",
                "Undergrad GPA": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Undergrad GPA')]/following-sibling::dd[1]",
                "Notes": "//dt[contains(@class,'tw-text-sm') and contains(text(),'Notes')]/following-sibling::dd[1]"
            }
            
            # Collect all elements in one go
            for field, xpath in field_mappings.items():
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    profile_data[field] = element.text.strip()
                except Exception:
                    # Skip logging for speed
                    pass
            
            # Special handling for specific fields
            
            # Acceptance Rate
            try:
                acceptance_rate_xpath = "//dt[contains(@class,'tw-text-sm') and contains(text(),'Acceptance Rate')]/following-sibling::dd[1]"
                element = self.driver.find_element(By.XPATH, acceptance_rate_xpath)
                acceptance_rate = element.text.strip()
                
                # Extract just the percentage if there's additional text
                if "%" in acceptance_rate:
                    percentage_match = re.search(r'(\d+(\.\d+)?)%', acceptance_rate)
                    if percentage_match:
                        acceptance_rate = percentage_match.group(0)
                
                profile_data["Acceptance Rate"] = acceptance_rate
            except Exception:
                # Fall back to alternate method
                try:
                    xpath_alt = "//div[contains(@class,'tw-flex') and contains(text(),'Acceptance Rate')]/following-sibling::div[1]"
                    element = self.driver.find_element(By.XPATH, xpath_alt)
                    profile_data["Acceptance Rate"] = element.text.strip()
                except Exception:
                    pass
            
            # Notification (Date and Method)
            try:
                notification_xpath = "//dt[contains(@class,'tw-text-sm') and contains(text(),'Notification')]/following-sibling::dd[1]"
                notification_element = self.driver.find_element(By.XPATH, notification_xpath)
                notification_text = notification_element.text.strip()
                
                if "via" in notification_text:
                    date_part, method_part = notification_text.split("via", 1)
                    profile_data["Notification Date"] = date_part.replace("on", "").strip()
                    profile_data["Notification Method"] = "via " + method_part.strip()
                else:
                    profile_data["Notification Date"] = notification_text
            except Exception:
                pass
            
            # GRE scores using span elements
            score_mappings = {
                "GRE General": "//span[contains(@class,'tw-text-sm') and contains(text(),'GRE General:')]/following-sibling::span[1]",
                "GRE Verbal": "//span[contains(@class,'tw-text-sm') and contains(text(),'GRE Verbal:')]/following-sibling::span[1]",
                "Analytical Writing": "//span[contains(@class,'tw-text-sm') and contains(text(),'Analytical Writing:')]/following-sibling::span[1]"
            }
            
            for field, xpath in score_mappings.items():
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                    profile_data[field] = element.text.strip()
                except Exception:
                    pass
            
            # Timeline
            try:
                event_xpath = "//div[contains(@class,'timeline') or contains(@class,'tw-flex tw-min-w-0')]//strong"
                date_xpath = "//div[contains(@class,'timeline') or contains(@class,'tw-whitespace-nowrap')]//time"
                
                event_element = self.driver.find_element(By.XPATH, event_xpath)
                date_element = self.driver.find_element(By.XPATH, date_xpath)
                
                profile_data["Timeline Event"] = event_element.text.strip()
                profile_data["Timeline Date"] = date_element.text.strip()
            except Exception:
                pass
                
        except Exception as e:
            self.logger.error(f"Error scraping all fields: {str(e)}")
    
    def _clean_profile_data(self, data):
        """Clean and normalize scraped data - optimized for speed"""
        # Clean GPA
        if data.get("Undergrad GPA") in ["0.00", "0", "N/A", ""]:
            data["Undergrad GPA"] = None
        elif data.get("Undergrad GPA"):
            try:
                data["Undergrad GPA"] = float(data["Undergrad GPA"])
            except ValueError:
                data["Undergrad GPA"] = None
        
        # Clean GRE scores - process all numeric fields at once
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
        
        return data

    def scroll_to_element(self, element):
        """Simplified scroll method with no sleep"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'instant'});", element)
        except Exception:
            pass  # Skip logging for speed

    def wait_for_element(self, by, selector, timeout=None):
        """Optimized wait for element"""
        if timeout is None:
            timeout = self.base_wait_time
            
        try:
            element = WebDriverWait(self.driver, timeout, ignored_exceptions=self.ignored_exceptions).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            return None

    def open_options_and_click_see_more(self, button):
        """Click the given options button, then click 'See More'."""
        try:
            self.scroll_to_element(button)
            button.click()
            
            # Extract the button ID for constructing the dropdown ID
            button_id = button.get_attribute('id')
            dropdown_id = button_id.replace('-button', '-list')
            
            # Wait for the dropdown to become visible
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, dropdown_id))
            )
            
            # Find the See More link within the dropdown
            see_more_xpath = ".//a[contains(text(), 'See More')]"
            see_more_link = dropdown.find_element(By.XPATH, see_more_xpath)
            
            self.scroll_to_element(see_more_link)
            see_more_link.click()
            
            # Wait for profile page to load
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(@class, 'tw-text-sm') and contains(text(),'Institution')]"))
            )
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to open options and click 'See More': {str(e)}")
            return False