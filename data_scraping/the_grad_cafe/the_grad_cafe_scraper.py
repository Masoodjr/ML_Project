from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os

class TheGradCafeScraper:
    def __init__(self, driver, logger, website_name):
        self.driver = driver
        self.logger = logger
        self.website_name = website_name
        self.seen_ids = set()
        self.profiles = []
        self.LOGIN_TIMEOUT = 30  # You can set this when initializing the object too
        self.last_page_file = "last_page.txt"
        self.data_file = "scraped_profiles.xlsx"

    def scroll_to_element(self, element):
        """Scroll the element into center view."""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.3)

    def go_to_page(self, page_number):
        """Directly go to a given page number."""
        try:
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

    def open_options_and_click_see_more(self, button):
        """Click the given options button, then click 'See More'."""
        try:
            self.scroll_to_element(button)
            button.click()
            time.sleep(0.5)

            see_more_link = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'See More')]"))
            )
            self.scroll_to_element(see_more_link)
            see_more_link.click()
            time.sleep(1)

        except Exception as e:
            self.logger.error(f"Failed during open options and click 'See More': {str(e)}")
            raise

    def scrape_profile(self):
        """Scrape the currently opened profile page."""
        profile_data = {}
        try:
            url = self.driver.current_url
            profile_id = url.split("/")[-1]
            profile_data["ID"] = profile_id

            # Example scraping: Expand as needed
            try:
                uni_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1.tw-text-lg"))
                )
                profile_data["University"] = uni_element.text.strip()
            except Exception:
                profile_data["University"] = None

            # TODO: Add more parsing here if needed
        except Exception as e:
            self.logger.error(f"Failed scraping profile page: {str(e)}")

        return profile_data

    def scrape_page_profiles(self):
        """Scrape all profiles on the current page."""
        try:
            options_buttons = WebDriverWait(self.driver, self.LOGIN_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "button[id^='options-menu-'][aria-haspopup='true']"))
            )
            self.logger.info(f"Found {len(options_buttons)} profiles on this page.")

            for idx, button in enumerate(options_buttons):
                self.logger.info(f"Scraping profile {idx + 1}...")
                try:
                    self.open_options_and_click_see_more(button)

                    # Switch to new tab
                    self.driver.switch_to.window(self.driver.window_handles[-1])

                    # Scrape profile
                    profile_data = self.scrape_profile()
                    if profile_data.get("ID") and profile_data["ID"] not in self.seen_ids:
                        self.profiles.append(profile_data)
                        self.seen_ids.add(profile_data["ID"])

                    # Close the new tab and return
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

                except Exception as e:
                    self.logger.error(f"Error scraping a profile: {str(e)}")
                    if len(self.driver.window_handles) > 1:
                        self.driver.close()
                        self.driver.switch_to.window(self.driver.window_handles[0])
                    continue

        except Exception as e:
            self.logger.error(f"Error scraping profiles from page: {str(e)}")

    def save_profiles(self):
        """Save all scraped profiles into an Excel file."""
        try:
            if self.profiles:
                df = pd.DataFrame(self.profiles)
                df.to_excel(self.data_file, index=False)
                self.logger.info(f"Saved {len(self.profiles)} profiles into {self.data_file}")
        except Exception as e:
            self.logger.error(f"Error saving profiles: {str(e)}")

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

    def start_scraping(self):
        """Complete scraping workflow across all pages."""
        try:
            current_page = self.load_last_page()
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

def scrape_profile_details(self):
    """Scrape detailed information from the opened 'See More' profile page."""
    profile_data = {}

    try:
        # ID from URL
        url = self.driver.current_url
        profile_id = url.split("/")[-1]
        profile_data["ID"] = profile_id

        # Acceptance Rate
        try:
            acceptance_rate = self.driver.find_element(By.XPATH, "//dt[text()='Acceptance Rate']/following-sibling::dd")
            profile_data["Acceptance Rate"] = acceptance_rate.text.strip()
        except Exception:
            profile_data["Acceptance Rate"] = None

        # Institution
        try:
            institution = self.driver.find_element(By.XPATH, "//dt[text()='Institution']/following-sibling::dd")
            profile_data["Institution"] = institution.text.strip()
        except Exception:
            profile_data["Institution"] = None

        # Program
        try:
            program = self.driver.find_element(By.XPATH, "//dt[text()='Program']/following-sibling::dd")
            profile_data["Program"] = program.text.strip()
        except Exception:
            profile_data["Program"] = None

        # Degree Type
        try:
            degree_type = self.driver.find_element(By.XPATH, "//dt[text()='Degree Type']/following-sibling::dd")
            profile_data["Degree Type"] = degree_type.text.strip()
        except Exception:
            profile_data["Degree Type"] = None

        # Degree's Country of Origin
        try:
            country_origin = self.driver.find_element(By.XPATH, "//dt[contains(text(), \"Degree's Country of Origin\")]/following-sibling::dd")
            profile_data["Degree's Country of Origin"] = country_origin.text.strip()
        except Exception:
            profile_data["Degree's Country of Origin"] = None

        # Decision
        try:
            decision = self.driver.find_element(By.XPATH, "//dt[text()='Decision']/following-sibling::dd")
            profile_data["Decision"] = decision.text.strip()
        except Exception:
            profile_data["Decision"] = None

        # Notification Date and Method
        try:
            notification = self.driver.find_element(By.XPATH, "//dt[text()='Notification']/following-sibling::dd")
            full_text = notification.text.strip()
            if "via" in full_text:
                date_part, method_part = full_text.split("via")
                profile_data["Notification Date"] = date_part.strip()
                profile_data["Notification Method"] = method_part.strip()
            else:
                profile_data["Notification Date"] = full_text
                profile_data["Notification Method"] = None
        except Exception:
            profile_data["Notification Date"] = None
            profile_data["Notification Method"] = None

        # Undergrad GPA
        try:
            gpa = self.driver.find_element(By.XPATH, "//dt[text()='Undergrad GPA']/following-sibling::dd")
            profile_data["Undergrad GPA"] = gpa.text.strip()
        except Exception:
            profile_data["Undergrad GPA"] = None

        # GRE Scores
        try:
            gre_general = self.driver.find_element(By.XPATH, "//span[contains(text(), 'GRE General:')]/following-sibling::span")
            profile_data["GRE General Score"] = gre_general.text.strip()
        except Exception:
            profile_data["GRE General Score"] = None

        try:
            gre_verbal = self.driver.find_element(By.XPATH, "//span[contains(text(), 'GRE Verbal:')]/following-sibling::span")
            profile_data["GRE Verbal Score"] = gre_verbal.text.strip()
        except Exception:
            profile_data["GRE Verbal Score"] = None

        try:
            gre_awa = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Analytical Writing:')]/following-sibling::span")
            profile_data["GRE Analytical Writing Score"] = gre_awa.text.strip()
        except Exception:
            profile_data["GRE Analytical Writing Score"] = None

        # Notes
        try:
            notes = self.driver.find_element(By.XPATH, "//dt[text()='Notes']/following-sibling::dd")
            profile_data["Notes"] = notes.text.strip()
        except Exception:
            profile_data["Notes"] = None

        # Timeline Event and Date
        try:
            timeline_event = self.driver.find_element(By.XPATH, "//p[contains(@class,'tw-text-sm')]/strong")
            profile_data["Timeline Event"] = timeline_event.text.strip()

            timeline_date = self.driver.find_element(By.XPATH, "//div[@class='tw-whitespace-nowrap tw-text-right tw-text-sm tw-text-gray-500']/time")
            profile_data["Timeline Date"] = timeline_date.text.strip()
        except Exception:
            profile_data["Timeline Event"] = None
            profile_data["Timeline Date"] = None

    except Exception as e:
        self.logger.error(f"Error scraping profile details: {str(e)}")

    return profile_data
