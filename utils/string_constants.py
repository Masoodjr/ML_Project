class StringConstants:
     # Log messages
    LOG_INIT_SCRAPER = "Initializing YMGrad scraper..."
    LOG_LOGIN_SUCCESS = "Login successful! Scraping data..."
    LOG_DATA_SAVED = "Data successfully saved to university_data.xlsx"
    LOG_DATA_SAVE_FAILED = "Failed to save data to Excel"
    LOG_NO_DATA = "No data was scraped"
    LOG_LOGIN_FAILED = "Login failed. Please check your credentials or the website status."
    LOG_BROWSER_CLOSED = "Browser closed."
    LOG_ERROR_OCCURRED = "An error occurred: "

     # URLs
    LOGIN_URL = "https://ymgrad.com/account/login"
    SEARCH_URL = "https://ymgrad.com/search/United%20States"

    # Locators
    USERNAME_FIELD = ("xpath", "//input[@id='id_username']")
    PASSWORD_FIELD = ("xpath", "//input[@id='id_password']")
    LOGIN_BUTTON = ("xpath", "//input[@type='submit' and @value='Login']")
    LOGGED_IN_INDICATOR = ("xpath", "//*[contains(text(), 'Welcome') or contains(text(), 'Dashboard')]")
    UNIVERSITY_CARD = ("css selector", "div.UniversityCardNew_super_wrapper__l2dMw")

    # CSS selectors
    RANK_SELECTOR = "div.UniversityCardNew_university_rank__yTV30"
    NAME_SELECTOR = "h2.UniversityCardNew_main_title__5ewCb"
    LOCATION_SELECTOR = "div.UniversityCardNew_address__ultV_"
    STAT_CONTAINER_SELECTOR = "div.UniversityCardNew_stat_container__aGWTW"
    STATS_HEADING_SELECTOR = "div.UniversityCardNew_stats-heading__tNoYp"
    STATS_TEXT_SELECTOR = "div.UniversityCardNew_stats-text__LQZfD"
    DESCRIPTION_SELECTOR = "div.UniversityCardNew_extra_info__zfV1R p"

    # Timeouts
    LOGIN_TIMEOUT = 30
    PAGE_LOAD_TIMEOUT = 40
    CARD_RETRY_ATTEMPTS = 3
    SCROLL_MAX_ATTEMPTS = 5

    # Log messages
    LOG_NAVIGATE_LOGIN = "Navigating to login page: "
    LOG_LOGIN_PAGE_LOADED = "Login page loaded successfully"
    LOG_CREDENTIALS_ENTERED = "Credentials entered successfully"
    LOG_LOGIN_CLICKED = "Login button clicked successfully"
    LOG_LOGIN_VERIFIED = "Login verification successful"
    LOG_NAVIGATE_SEARCH = "Navigating to search page: "
    LOG_UNIVERSITY_FOUND = "Found {count} university cards on attempt {attempt}"
    LOG_SEARCH_SUCCESS = "Search page loaded successfully"
    LOG_SCROLL_FAIL = "Couldn't complete page scrolling: "
    LOG_CARD_SCRAPED = "Successfully scraped data from {count} universities"
    LOG_SAVE_SUCCESS = "Data saved to {filename}"
    LOG_SCREENSHOT_SAVED = "Screenshot saved to {path}"
    SCREENSHOT_PATH = "search_page_error.png"

    # Excel
    EXCEL_FILENAME = "university_data.xlsx"
    NUMERIC_COLS = ['Rank', 'Average_GMAT', 'Average_GRE', 'Average_GPA', 'Average_Salary', 'Tuition_Fees']
    PERCENT_COL = "Acceptance_Rate"