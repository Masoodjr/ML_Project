from data_scraping.ymgrad.student_admit_reject.pages.login_page import LoginPage
from data_scraping.ymgrad.student_admit_reject.pages.admit_reject_filter_page import AdmitRejectFilterPage
from data_scraping.ymgrad.student_admit_reject.components.profile_scraper import ProfileScraper
from data_scraping.ymgrad.student_admit_reject.components.profile_parser import ProfileParser
from utils.random_wait import random_wait

class AdmitRejectBot:
    def __init__(self, driver, logger, login_url, admit_reject_url):
        self.driver = driver
        self.logger = logger
        self.login_page = LoginPage(driver, logger)
        self.filter_page = AdmitRejectFilterPage(driver, logger)
        self.parser = ProfileParser(logger)
        self.scraper = ProfileScraper(driver, logger, self.parser)

    def run(self):
        self.login_page.open_login_page(self.login_url)
        self.login_page.login()
        self.login_page._submit_button()
        self.login_page.verify_login()
        self.driver.get(self.admit_reject_url)
        random_wait(1.0, 4.0)
        self.filter_page.select_country("United States")
        # self.filter_page.select_decision_types(["Admit", "Reject"])
        self.scraper.scrape_100k_profiles()
