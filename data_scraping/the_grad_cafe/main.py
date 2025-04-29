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

# Configure logging levels - set to WARNING or ERROR in production for speed
# Logger.LEVEL = Logger.WARNING  # Uncomment for production

def worker_process(page_range, shared_profiles_list, process_id):
    logger = Logger()
    browser_manager = BrowserManager(headless=True)

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
        local_profiles = []

        for page in page_range:
            logger.info(f"[Process-{process_id}] Scraping page {page}")

            if not scraper.go_to_page(page):
                logger.warning(f"[Process-{process_id}] Failed to go to page {page}")
                continue

            page_profiles = scraper.scrape_page_profiles_improved(page)
            if page_profiles:
                local_profiles.extend(page_profiles)
            else:
                logger.warning(f"[Process-{process_id}] Problem scraping page {page}")

            # 🚀 After every 20 profiles, save immediately
            if len(local_profiles) >= 20:
                live_save_profiles(local_profiles)
                local_profiles.clear()

        # Final save if anything is left
        if local_profiles:
            live_save_profiles(local_profiles)
            local_profiles.clear()

    except Exception as e:
        logger.error(f"[Process-{process_id}] Error: {str(e)}")
    finally:
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

    # Optimize for M3 - use more efficient process count based on workload type
    # Web scraping is I/O bound, not CPU bound, so slightly more processes can help
    available_cpus = cpu_count()
    num_processes = min(available_cpus + 2, 8)  # Use up to available_cpus+2 but max 8
    
    logger.info(f"Starting scraping with {num_processes} processes on {available_cpus} CPU cores...")

    start_page = 5100
    end_page = 6300
    total_pages = end_page - start_page + 1
    
    # More intelligent page distribution
    pages_per_process = math.ceil(total_pages / num_processes)
    
    page_ranges = [
        range(start_page + i * pages_per_process, min(start_page + (i + 1) * pages_per_process, end_page + 1))
        for i in range(num_processes)
    ]

    with Manager() as manager:
        shared_profiles_list = manager.list()  # collect profiles across processes
        
        # Add process_id parameter for better logging/debugging
        worker_with_id = partial(worker_process, shared_profiles_list=shared_profiles_list)
        
        with Pool(processes=num_processes) as pool:
            pool.starmap(worker_process, [(page_range, shared_profiles_list, i) for i, page_range in enumerate(page_ranges)])

        logger.info("All processes completed. Saving collected profiles...")
        save_profiles_to_excel(shared_profiles_list)

def save_profiles_to_excel(profiles):
    """Extracted function to save profiles to Excel"""
    logger = Logger()
    data_file = "scraped_profiles.xlsx"

    new_df = pd.DataFrame(list(profiles))
    new_df['Scraped Timestamp'] = pd.Timestamp.now()

    if os.path.exists(data_file):
        try:
            existing_df = pd.read_excel(data_file)
            existing_ids = set(existing_df['ID'].values) if 'ID' in existing_df.columns else set()
            new_df = new_df[~new_df['ID'].isin(existing_ids)]
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception as e:
            logger.error(f"Error reading existing file: {str(e)}")
            combined_df = new_df
    else:
        combined_df = new_df

    combined_df.to_excel(data_file, index=False)
    logger.info(f"Saved {len(new_df)} new profiles to {data_file}")

if __name__ == "__main__":
    main()