from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from university_data.login import YMGradLogin
from utils.logger import Logger
from utils.string_constants import *

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ymgrad_scraper.log'),
        logging.StreamHandler()
    ]
)

def main():
    # Initialize Chrome WebDriver with options
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    logger = Logger()
    string_constants = StringConstants()
    
    driver = None

    try:
        # Initialize WebDriver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Set script timeout
        driver.set_script_timeout(30)
        
        logger.info()
        scraper = YMGradLogin(driver)
        
        # Perform login and scraping
        if scraper.login():
            logger.info(string_constants.LOG_LOGIN_SUCCESS)
            university_data = scraper.scrape_university_data()
            
            if university_data:
                # Save to Excel file
                if scraper.save_to_excel():
                    logger.info(string_constants.LOG_DATA_SAVED)
                else:
                    logger.error(string_constants.LOG_DATA_SAVE_FAILED)
            else:
                logger.error(string_constants.LOG_NO_DATA)
        else:
            logger.error(string_constants.LOG_LOGIN_FAILED)
            
    except Exception as e:
        logger.error(f"{string_constants.LOG_ERROR_OCCURRED} {str(e)}", exc_info=True)
    finally:
        # Clean up - close the browser
        if driver:
            driver.quit()
            logger.info(string_constants.LOG_BROWSER_CLOSED)

if __name__ == "__main__":
    main()