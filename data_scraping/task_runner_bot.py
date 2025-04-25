from data_scraping.student_admit_reject.pages.login_page import LoginPage
from data_scraping.student_admit_reject.components.profile_scraper import ProfileScraper
from data_scraping.student_admit_reject.components.profile_parser import ProfileParser
from config.login_page_config import LOGIN_CONFIGS
from utils.random_wait import random_wait
from config.website_name import WebsiteName

class TaskRunnerBot:
    def __init__(self, driver, logger, login_url, admit_reject_url):
        self.driver = driver
        self.logger = logger
        self.login_url = login_url
        self.admit_reject_url = admit_reject_url
        # DIFFERENT FLAVORS
        # self.login_page = LoginPage(driver, logger, LOGIN_CONFIGS.LOGIN_CONFIG_FOR_YMGRAD)
        # self.login_page = LoginPage(driver, logger, LOGIN_CONFIGS.LOGIN_CONFIG_FOR_YOCKET)
        self.login_page = LoginPage(driver, logger, LOGIN_CONFIGS.LOGIN_CONFIG_FOR_THEGRADCAFE)
        # self.filter_page = AdmitRejectFilterPage(driver, logger)
        self.parser = ProfileParser(logger)
        # self.scraper = ProfileScraper(driver, logger, self.parser, website_name=WebsiteName.YMGRAD)
        # self.scraper = ProfileScraper(driver, logger, self.parser, website_name=WebsiteName.YOCKET)
        self.scraper = ProfileScraper(driver, logger, self.parser, website_name=WebsiteName.THEGRADCAFE)

    def run(self):
        self.login_page.open_login_page(self.login_url)
        self.login_page.login()
        self.login_page._submit_button()
        self.login_page.verify_login()
        self.driver.get(self.admit_reject_url)
        random_wait(1.0, 4.0)
        self.scraper.scrape_profile_and_save_data()
