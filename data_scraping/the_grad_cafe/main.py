from data_scraping.browser_manager import BrowserManager
from data_scraping.task_runner_bot import TaskRunnerBot
from config.admit_reject_platform_config import PLATFORM_CONFIG
from utils.logger import Logger
from config.login_page_config import LOGIN_CONFIGS
from config.website_name import WebsiteName

def main():
    logger = Logger()
    browser_manager = BrowserManager()
    
    try:
        driver = browser_manager.get_driver()
        # Platform independant
        bot = TaskRunnerBot(driver, logger, login_url= PLATFORM_CONFIG['gradcafe']['login_url'], admit_reject_url= PLATFORM_CONFIG['gradcafe']['admit_reject_url'], website_name=WebsiteName.THEGRADCAFE, login_config=LOGIN_CONFIGS.LOGIN_CONFIG_FOR_THEGRADCAFE)
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
