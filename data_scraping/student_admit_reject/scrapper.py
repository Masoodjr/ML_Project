import time
import random
import pandas as pd
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (TimeoutException, NoSuchElementException, 
                                      WebDriverException, StaleElementReferenceException)

class AdmitRejectScraper:
    # Move all locators and config here
    LOGIN_URL = "https://ymgrad.com/account/login"
    ADMIT_REJECT_URL = "https://ymgrad.com/admits_rejects"
    TIMEOUT = 30
    
    def __init__(self, driver):
        self.driver = driver
        self.driver.set_page_load_timeout(self.TIMEOUT)
        
    def run(self):
        try:
            self.login()
            self.scrape_profiles()
            return True
        except Exception as e:
            return False
    
    # Keep all your existing methods but:
    # 1. Remove logger (use the one from utils)
    # 2. Move credentials to config.py
    # 3. Simplify the structure