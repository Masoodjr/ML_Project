from multiprocessing import Pool, Manager, cpu_count
import os
import math
from filelock import FileLock
import pandas as pd
from functools import partial

from data_scraping.browser_manager import BrowserManager
from data_scraping.task_runner_bot import TaskRunnerBot
from config.admit_reject_platform_config import PLATFORM_CONFIG
from utils.logger import Logger
from config.login_page_config import LOGIN_CONFIGS
from config.website_name import WebsiteName
from data_scraping.the_grad_cafe.the_grad_cafe_scraper import TheGradCafeScraper

# Configure logging levels - set to WARNING or ERROR in production for speed
# Logger.LEVEL = Logger.WARNING  # Uncomment for production

def worker_process(page_range, shared_profiles_list, process_id):
    logger = Logger()
    browser_manager = BrowserManager(headless=True)
    scraper = None
    local_profiles = []  # Move this outside try block!!

    try:
        driver = browser_manager.get_driver()
        bot = TaskRunnerBot(
            driver,
            logger,
            login_url=PLATFORM_CONFIG['gradcafe']['login_url'],
            admit_reject_url=PLATFORM_CONFIG['gradcafe']['admit_reject_url'],
            website_name=WebsiteName.THEGRADCAFE,
            login_config=LOGIN_CONFIGS.LOGIN_CONFIG_FOR_THEGRADCAFE
        )

        bot.login()
        scraper = bot.scraper

        for page in page_range:
            logger.info(f"[Process-{process_id}] Scraping page {page}")

            if not scraper.go_to_page(page):
                logger.warning(f"[Process-{process_id}] Failed to go to page {page}")
                continue

            page_profiles = scraper.scrape_page_profiles_improved(page)
            if page_profiles:
                local_profiles.extend(page_profiles)
                # Save live if you want inside here, optional
                scraper.save_profiles(local_profiles)
                local_profiles.clear()
                
    except Exception as e:
        logger.error(f"[Process-{process_id}] Error: {str(e)}")
    finally:
        # Final save if anything remains
        if scraper is not None and hasattr(scraper, "save_profiles") and local_profiles:
            scraper.save_profiles(local_profiles)
        browser_manager.quit()
   
def live_save_profiles(profiles):
    """Save small batches of profiles live to Excel using a lock."""
    if not profiles:
        return

    data_file = "scraped_profiles.xlsx"
    lock_file = data_file + ".lock"

    try:
        new_df = pd.DataFrame(profiles)
        new_df['Scraped Timestamp'] = pd.Timestamp.now()

        lock = FileLock(lock_file, timeout=120)

        with lock:
            if os.path.exists(data_file):
                existing_df = pd.read_excel(data_file)
                existing_ids = set(existing_df['ID'].values) if 'ID' in existing_df.columns else set()
                new_df = new_df[~new_df['ID'].isin(existing_ids)]
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            else:
                combined_df = new_df

            combined_df.to_excel(data_file, index=False)
        
    except Exception as e:
        print(f"Error in live_save_profiles: {str(e)}")


def main():
    logger = Logger()
    available_cpus = cpu_count()
    num_processes = min(available_cpus + 2, 8)
    
    logger.info(f"Starting scraping with {num_processes} processes...")

    start_page = 5500
    end_page = 6300
    
    with Manager() as manager:
        shared_profiles_list = manager.list()
        
        with Pool(processes=num_processes) as pool:
            pool.starmap(worker_process, 
                        [(page_range, shared_profiles_list, i) 
                         for i, page_range in enumerate(divide_range(start_page, end_page, num_processes))])

        logger.info("All processes completed. Final save...")
        if shared_profiles_list:
            # Initialize a scraper just for final saving
            temp_scraper = TheGradCafeScraper(None, logger, WebsiteName.THEGRADCAFE)
            temp_scraper.save_profiles(list(shared_profiles_list))

def divide_range(start, end, num_parts):
    """Divide a range into approximately equal parts"""
    total = end - start + 1
    part_size = total // num_parts
    remainder = total % num_parts
    
    ranges = []
    current = start
    
    for i in range(num_parts):
        extra = 1 if i < remainder else 0
        ranges.append(range(current, current + part_size + extra))
        current += part_size + extra
    
    return ranges

if __name__ == "__main__":
    main()


