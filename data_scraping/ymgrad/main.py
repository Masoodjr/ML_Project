from data_scraping.browser_manager import BrowserManager
from data_scraping.admit_reject_bot import AdmitRejectBot
from config.admit_reject_platform_config import PLATFORM_CONFIG
from utils.logger import Logger

def main():
    logger = Logger()
    browser_manager = BrowserManager()
    
    try:
        driver = browser_manager.get_driver()
        # bot = AdmitRejectBot(driver, logger, login_url= PLATFORM_CONFIG['ymgrad']['login_url'], admit_reject_url= PLATFORM_CONFIG['ymgrad']['admit_reject_url'])
        # bot = AdmitRejectBot(driver, logger, login_url= PLATFORM_CONFIG['yocket']['login_url'], admit_reject_url= PLATFORM_CONFIG['yocket']['admit_reject_url'])
        bot = AdmitRejectBot(driver, logger, login_url= PLATFORM_CONFIG['gradcafe']['login_url'], admit_reject_url= PLATFORM_CONFIG['gradcafe']['admit_reject_url'])

        if bot.run():
            logger.info("Scraping completed successfully!")
        else:
            logger.warning("Scraping completed with some issues")
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        input("Press Enter to close browser...")
        browser_manager.quit()

if __name__ == "__main__":
    main()
