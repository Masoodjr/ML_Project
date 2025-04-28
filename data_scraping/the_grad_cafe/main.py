from multiprocessing import Pool, Manager
import os
import math
import pandas as pd

from data_scraping.browser_manager import BrowserManager
from data_scraping.task_runner_bot import TaskRunnerBot
from config.admit_reject_platform_config import PLATFORM_CONFIG
from utils.logger import Logger
from config.login_page_config import LOGIN_CONFIGS
from config.website_name import WebsiteName

def worker_process(args):
    """Worker process that handles a range of pages"""
    page_range, shared_profiles_list = args
    logger = Logger()
    browser_manager = BrowserManager()

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
            logger.info(f"[Process-{os.getpid()}] Scraping page {page}...")

            if not scraper.go_to_page(page):
                logger.warning(f"[Process-{os.getpid()}] Failed to go to page {page}")
                continue

            if not scraper.scrape_page_profiles_parallel(page):
                logger.warning(f"[Process-{os.getpid()}] Problem scraping page {page}")
                continue

        # After scraping all assigned pages, add all collected profiles to shared list
        if scraper.profiles:
            shared_profiles_list.extend(scraper.profiles)

    except Exception as e:
        logger.error(f"[Process-{os.getpid()}] Error: {str(e)}", exc_info=True)
    finally:
        browser_manager.quit()

def main():
    logger = Logger()

    num_processes = min(5, os.cpu_count() - 1)  # use 7 or available cores minus 1
    logger.info(f"Starting scraping with {num_processes} processes...")

    start_page = 173
    end_page = 1000
    total_pages = end_page - start_page + 1
    pages_per_process = math.ceil(total_pages / num_processes)

    page_ranges = [
        range(start_page + i * pages_per_process, min(start_page + (i + 1) * pages_per_process, end_page + 1))
        for i in range(num_processes)
    ]

    with Manager() as manager:
        shared_profiles_list = manager.list()  # collect profiles across processes

        with Pool(processes=num_processes) as pool:
            pool.map(worker_process, [(page_range, shared_profiles_list) for page_range in page_ranges])

        logger.info("All processes completed. Saving collected profiles...")
        data_file = "scraped_profiles.xlsx"

        new_df = pd.DataFrame(list(shared_profiles_list))
        new_df['Scraped Timestamp'] = pd.Timestamp.now()

        if os.path.exists(data_file):
            existing_df = pd.read_excel(data_file)
            existing_ids = set(existing_df['ID'].values) if 'ID' in existing_df.columns else set()
            new_df = new_df[~new_df['ID'].isin(existing_ids)]
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df

        combined_df.to_excel(data_file, index=False)
        logger.info(f"Saved {len(new_df)} new profiles to {data_file}")

if __name__ == "__main__":
    main()
