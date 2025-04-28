from data_scraping.student_admit_reject.pages.login_page import LoginPage
from utils.random_wait import random_wait
from config.admit_reject_platform_config import PLATFORM_CONFIG
from config.website_name import WebsiteName
from config.login_page_config import LOGIN_CONFIGS
from data_scraping.the_grad_cafe.the_grad_cafe_scraper import TheGradCafeScraper
from data_scraping.yocket.yocket_scraper import YocketScraper
from data_scraping.ymgrad.ymgrad_scraper import YMGradScraper
from data_scraping.the_grad_cafe.the_grad_cafe_scraper import TheGradCafeScraper

class TaskRunnerBot:
    def __init__(self, driver, logger, login_url, admit_reject_url, website_name, login_config):
        self.driver = driver
        self.logger = logger
        self.login_url = login_url
        self.admit_reject_url = admit_reject_url
        self.website_name = website_name
        self.login_config = login_config
        random_wait(1, 4)
        if self.website_name == WebsiteName.YMGRAD:
            self.scraper = YMGradScraper(driver, logger, website_name)
        elif self.website_name == WebsiteName.YOCKET:
            self.scraper = YocketScraper()
        elif self.website_name == WebsiteName.THEGRADCAFE:
            self.scraper = TheGradCafeScraper(driver, logger, website_name)

# ✅ Pass locators + credentials (fixed!)
        self.login_page = LoginPage(
            logger=logger,
            driver=driver,
            username_field=self.login_config["USERNAME_FIELD"],
            password_field=self.login_config["PASSWORD_FIELD"],
            login_button=self.login_config['LOGIN_BUTTON'],
            logged_in_indicator=self.login_config['LOGGED_IN_INDICATOR'],
        )
        # DIFFERENT FLAVORS
        #self.login_page = LoginPage(logger=logger, driver=driver,username_field=self.login_config["USERNAME_FIELD"], password_field=self.login_config["PASSWORD_FIELD"], login_button=self.login_config['LOGIN_BUTTON'], logged_in_indicator=self.login_config['LOGGED_IN_INDICATOR'])

    def run(self):
        self.login_page.open_login_page(self.login_url)
        self.login_page.login()
        self.login_page._submit_button()
        self.login_page.verify_login()
        random_wait(1, 3)
        self.driver.get(self.admit_reject_url)
        if self.website_name == WebsiteName.THEGRADCAFE:
            self.scraper.start_scraping(resume=True)
        # random_wait(1.0, 4.0)
