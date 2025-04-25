from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

class ProfileParser:
    def __init__(self, logger):
        self.logger = logger

    def parse_profile(self, element):
        try:
            data = {
                "Profile ID": element.get_attribute("id"),
                "Name": self._safe_text(element, "h4.PopupModal_decision_h3__J2L__"),
                # Add other parsing logic...
            }
            return data
        except Exception as e:
            self.logger.error(f"Failed to parse profile: {str(e)}")
            return {}

    def _safe_text(self, element, selector):
        try:
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        except NoSuchElementException:
            return None
