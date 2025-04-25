from browser_manager import BrowserManager
from scraper import AdmitRejectScraper
from utils.logger import setup_logger

def main():
    logger = setup_logger()
    browser_manager = BrowserManager()
    
    try:
        driver = browser_manager.get_driver()
        scraper = AdmitRejectScraper(driver)
        
        if scraper.run():
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