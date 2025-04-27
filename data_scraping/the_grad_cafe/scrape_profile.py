from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.random_wait import random_wait

class ProfileScraper:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

    def scrape(self):
        profile_data = {}
        try:
            url = self.driver.current_url
            profile_id = url.split("/")[-1]
            profile_data["ID"] = profile_id
            self.logger.info(f"🔵 Scraping profile ID: {profile_id}")

            # Wait for the main content to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'tw-flex tw-flex-col lg:tw-flex-row')]"))
            )
            self.logger.info("✅ Main profile block loaded.")

            # Scrape all sections
            profile_data.update(self._scrape_acceptance_rate())
            profile_data.update(self._scrape_application_info())
            profile_data.update(self._scrape_gre_scores())
            profile_data.update(self._scrape_timeline())

            self.logger.info(f"✅ Finished scraping profile ID: {profile_id}")
            return profile_data

        except Exception as e:
            self.logger.error(f"❌ Failed scraping profile page: {str(e)}")
            return None

    def _scrape_acceptance_rate(self):
        data = {}
        try:
            rate = self._safe_text((By.XPATH, "//dt[contains(., 'Acceptance Rate')]/following-sibling::dd[1]"))
            data["Acceptance Rate"] = rate
        except Exception as e:
            self.logger.warning(f"Couldn't scrape acceptance rate: {str(e)}")
        return data

    def _scrape_application_info(self):
        data = {}
        fields = [
            ("Institution", "Institution"),
            ("Program", "Program"),
            ("Degree Type", "Degree Type"),
            ("Degree's Country of Origin", "Country of Origin"),
            ("Decision", "Decision"),
            ("Notification", "Notification"),
            ("Undergrad GPA", "Undergrad GPA"),
            ("Notes", "Notes")
        ]

        for field_name, field_text in fields:
            try:
                xpath = f"//dt[contains(., '{field_text}')]/following-sibling::dd[1]"
                value = self._safe_text((By.XPATH, xpath))
                data[field_name] = value
            except Exception as e:
                self.logger.warning(f"Couldn't scrape {field_name}: {str(e)}")
        
        return data

    def _scrape_gre_scores(self):
        data = {}
        try:
            gre_section = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//ul[@class='tw-list-none']"))
            )
            
            gre_fields = {
                "GRE General": "GRE General:",
                "GRE Verbal": "GRE Verbal:",
                "Analytical Writing": "Analytical Writing:"
            }

            for field, text in gre_fields.items():
                try:
                    xpath = f"//span[contains(., '{text}')]/following-sibling::span[1]"
                    value = self._safe_text((By.XPATH, xpath))
                    data[field] = value
                except Exception as e:
                    self.logger.warning(f"Couldn't scrape {field}: {str(e)}")

        except Exception as e:
            self.logger.warning(f"Couldn't find GRE section: {str(e)}")
        
        return data

    def _scrape_timeline(self):
        data = {}
        try:
            timeline_section = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//h3[contains(., 'Timeline')]/following-sibling::div[1]"))
            )
            
            # Timeline event
            try:
                event = self._safe_text((By.XPATH, "//p[contains(@class, 'tw-text-sm')]/strong"))
                data["Timeline Event"] = event
            except Exception as e:
                self.logger.warning(f"Couldn't scrape timeline event: {str(e)}")
            
            # Timeline date
            try:
                date = self._safe_text((By.XPATH, "//time"))
                data["Timeline Date"] = date
            except Exception as e:
                self.logger.warning(f"Couldn't scrape timeline date: {str(e)}")

        except Exception as e:
            self.logger.warning(f"Couldn't find timeline section: {str(e)}")
        
        return data

    def _safe_text(self, locator):
        """Helper function to safely get text or return None."""
        try:
            element = WebDriverWait(self.driver, random_wait(2, 3)).until(
                EC.visibility_of_element_located(locator)
            )
            return element.text.strip()
        except Exception:
            return None