import time
import random
import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class YocketScraper:
    def __init__(self, driver, logger, parser, website_name):
        self.driver = driver
        self.logger = logger
        self.parser = parser
        self.website_name = website_name
        self.seen_ids = set()
        self.profiles = []

    