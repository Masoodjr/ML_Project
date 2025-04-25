from data_scraping.student_admit_reject.pages.login_page import LoginPage
from data_scraping.student_admit_reject.components.profile_parser import ProfileParser
from utils.random_wait import random_wait
from config.admit_reject_platform_config import PLATFORM_CONFIG
from config.website_name import WebsiteName
from config.login_page_config import LOGIN_CONFIGS
from data_scraping.the_grad_cafe.the_grad_cafe_scraper import TheGradCafeScraper
from data_scraping.yocket.yocket_scraper import YocketScraper
from data_scraping.ymgrad.ymgrad_scraper import YMGradScraper

class TaskRunnerBot:
    def __init__(self, driver, logger, login_url, admit_reject_url, website_name, login_config, scraper):
        self.driver = driver
        self.logger = logger
        self.login_url = login_url
        self.admit_reject_url = admit_reject_url
        self.website_name = website_name
        self.login_config = login_config
        if self.website_name == WebsiteName.YMGRAD:
            self.scraper = YMGradScraper()
        elif self.website_name == WebsiteName.YOCKET:
            self.scraper = YocketScraper()
        elif self.website_name == WebsiteName.THEGRADCAFE:
            self.scraper = TheGradCafeScraper()

        # DIFFERENT FLAVORS
        self.login_page = LoginPage(driver, logger, self.login_config)
        self.parser = ProfileParser(logger)
        bot = TaskRunnerBot(driver, logger, login_url= PLATFORM_CONFIG['gradcafe']['login_url'], admit_reject_url= PLATFORM_CONFIG['gradcafe']['admit_reject_url'], website_name=WebsiteName.THEGRADCAFE, login_config=LOGIN_CONFIGS.LOGIN_CONFIG_FOR_THEGRADCAFE)
        bot.run()

    def run(self):
        self.login_page.open_login_page(self.login_url)
        self.login_page.login()
        self.login_page._submit_button()
        self.login_page.verify_login()
        self.driver.get(self.admit_reject_url)
        random_wait(1.0, 4.0)