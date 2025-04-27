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
            print(f"🔵 Scraping profile ID: {profile_id}")

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//dt[contains(text(),'Acceptance Rate')]"))
            )
            print("✅ Page ready, Acceptance Rate visible.")

            # Now scrape each field and print status
            profile_data["Acceptance Rate"] = self._scrape_and_log("Acceptance Rate", (By.XPATH, "//dt[contains(text(),'Acceptance Rate')]/following::dd[1]"))
            profile_data["Timeline"] = self._scrape_and_log("Timeline", (By.CSS_SELECTOR, "ul[role='list'] li div p"))
            profile_data["Institution"] = self._scrape_and_log("Institution", (By.XPATH, "//dt[text()='Institution']/following::dd[1]"))
            profile_data["Program"] = self._scrape_and_log("Program", (By.XPATH, "//dt[text()='Program']/following::dd[1]"))
            profile_data["Degree Type"] = self._scrape_and_log("Degree Type", (By.XPATH, "//dt[text()='Degree Type']/following::dd[1]"))
            profile_data["Degree's Country of Origin"] = self._scrape_and_log("Degree's Country of Origin", (By.XPATH, "//dt[contains(text(),\"Degree's Country of Origin\")]/following::dd[1]"))
            profile_data["Decision"] = self._scrape_and_log("Decision", (By.XPATH, "//dt[text()='Decision']/following::dd[1]"))
            profile_data["Notification"] = self._scrape_and_log("Notification", (By.XPATH, "//dt[text()='Notification']/following::dd[1]"))
            profile_data["Undergrad GPA"] = self._scrape_and_log("Undergrad GPA", (By.XPATH, "//dt[text()='Undergrad GPA']/following::dd[1]"))
            profile_data["GRE General"] = self._scrape_and_log("GRE General", (By.XPATH, "//span[contains(text(),'GRE General:')]/following::span[1]"))
            profile_data["GRE Verbal"] = self._scrape_and_log("GRE Verbal", (By.XPATH, "//span[contains(text(),'GRE Verbal:')]/following::span[1]"))
            profile_data["Analytical Writing"] = self._scrape_and_log("Analytical Writing", (By.XPATH, "//span[contains(text(),'Analytical Writing:')]/following::span[1]"))
            profile_data["Notes"] = self._scrape_and_log("Notes", (By.XPATH, "//dt[text()='Notes']/following::dd[1]"))

            print(f"✅ Finished scraping profile ID: {profile_id}")

        except Exception as e:
            self.logger.error(f"❌ Failed scraping profile page: {str(e)}")

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

    def _scrape_and_log(self, field_name, locator):
        """Helper to scrape field and log the result."""
        print(f"🔍 Scraping {field_name}...")
        value = self._safe_text(locator)
        if value:
            print(f"✅ {field_name}: {value}")
        else:
            print(f"⚠️ {field_name}: Not found or empty.")
        return value
