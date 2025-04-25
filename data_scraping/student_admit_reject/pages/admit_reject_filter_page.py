from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from pages.base_page import BasePage
from selenium.webdriver.support import expected_conditions as EC
import time

class AdmitRejectFilterPage(BasePage):
    LOGIN_TIMEOUT = 30  # seconds

    def select_country(self, country_name="United States"):
            """Select a country from the country dropdown"""
            try:
                self.logger.info(f"Selecting country: {country_name}")

                # Click to activate the dropdown
                dropdown_container = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "css-yk16xz-control"))
                )
                dropdown_container.click()
                time.sleep(0.5)

                # Type in the country input field
                country_input = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "react-select-2-input"))
                )
                country_input.send_keys(country_name)
                time.sleep(0.5)
                country_input.send_keys(Keys.ENTER)

                self.logger.info(f"Country '{country_name}' selected successfully")
            except Exception as e:
                self.logger.error(f"Failed to select country: {str(e)}")
                raise

    def select_decision_types(self, options_to_select=["Admit", "Reject"]):
        """Select specific options (e.g., 'Admit' and 'Reject') in the Decision Type multi-select dropdown."""
        try:
            self.logger.info(f"Selecting decision types: {options_to_select}")

            # Click the dropdown to reveal the options
            dropdown = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.dropdown-container"))
            )
            dropdown.click()
            time.sleep(0.5)  # Wait for options to appear

            # Select each desired option
            for option in options_to_select:
                try:
                    option_xpath = f"//div[contains(@class, 'rmsc-option') and normalize-space(text())='{option}']"

                    # First wait for visibility
                    option_element = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                        EC.visibility_of_element_located((By.XPATH, option_xpath))
                    )

                    # Scroll to the option
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_element)
                    time.sleep(0.3)  # Give browser a moment to scroll

                    # Then click
                    option_element.click()
                    self.logger.info(f"Selected option: {option}")
                except Exception as e:
                    self.logger.warning(f"Could not select option '{option}': {str(e)}")
                    try:
                        available_options = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'rmsc-option')]")
                        self.logger.debug("Available dropdown options:")
                        for el in available_options:
                            self.logger.debug(f"- {el.text}")
                    except Exception:
                        self.logger.debug("No dropdown options found to debug.")
                    continue

            # Optional: Collapse dropdown by clicking again if needed
            try:
                if dropdown.get_attribute("aria-expanded") == "true":
                    dropdown.click()
            except Exception:
                pass

            # Verify selection from the rendered <span> text
            try:
                selected_span = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.dropdown-heading-value > span"))
                )
                selected_text = selected_span.text.strip()
                self.logger.info(f"Currently selected decision types: {selected_text}")
                for option in options_to_select:
                    if option not in selected_text:
                        self.logger.warning(f"Option '{option}' not found in selected text.")
            except Exception as e:
                self.logger.warning(f"Could not verify selection via span text: {str(e)}")

        except Exception as e:
            self.logger.error(f"Failed to select decision types: {str(e)}")
            raise
