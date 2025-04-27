from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.random_wait import random_wait

class ProfileScraper:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger

    def scrape(self):
        """Scrape the current profile page."""
        profile_data = {}
        try:
            url = self.driver.current_url
            profile_id = url.split("/")[-1]
            profile_data["ID"] = profile_id

            # ✅ Only wait for the main important element
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1.tw-text-lg"))
            )

            # Immediately start scraping once critical data is visible
            profile_data["University"] = self._safe_text((By.CSS_SELECTOR, "h1.tw-text-lg"))
            profile_data["Acceptance Rate"] = self._safe_text((By.XPATH, "//dt[contains(text(),'Acceptance Rate')]/following-sibling::dd"))
            profile_data["Timeline"] = self._safe_text((By.CSS_SELECTOR, "ul[role='list'] li p"))
            profile_data["Institution"] = self._safe_text((By.XPATH, "//dt[text()='Institution']/following-sibling::dd"))
            profile_data["Program"] = self._safe_text((By.XPATH, "//dt[text()='Program']/following-sibling::dd"))
            profile_data["Degree Type"] = self._safe_text((By.XPATH, "//dt[text()='Degree Type']/following-sibling::dd"))
            profile_data["Degree's Country of Origin"] = self._safe_text((By.XPATH, "//dt[contains(text(),\"Degree's Country of Origin\")]/following-sibling::dd"))
            profile_data["Decision"] = self._safe_text((By.XPATH, "//dt[text()='Decision']/following-sibling::dd"))
            profile_data["Notification"] = self._safe_text((By.XPATH, "//dt[text()='Notification']/following-sibling::dd"))
            profile_data["Undergrad GPA"] = self._safe_text((By.XPATH, "//dt[text()='Undergrad GPA']/following-sibling::dd"))
            profile_data["GRE General"] = self._safe_text((By.XPATH, "//span[contains(text(),'GRE General:')]/following-sibling::span"))
            profile_data["GRE Verbal"] = self._safe_text((By.XPATH, "//span[contains(text(),'GRE Verbal:')]/following-sibling::span"))
            profile_data["Analytical Writing"] = self._safe_text((By.XPATH, "//span[contains(text(),'Analytical Writing:')]/following-sibling::span"))
            profile_data["Notes"] = self._safe_text((By.XPATH, "//dt[text()='Notes']/following-sibling::dd"))

        except Exception as e:
            self.logger.error(f"Failed scraping profile page: {str(e)}")

        return profile_data

    def _safe_text(self, locator):
        """Helper function to safely get text or return None."""
        try:
            element = WebDriverWait(self.driver, random_wait(1, 2)).until(
                EC.presence_of_element_located(locator)
            )
            return element.text.strip()
        except Exception:
            return None
