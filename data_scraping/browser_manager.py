from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class BrowserManager:
    def __init__(self, headless=True):
        self.driver = None
        self.headless = headless
        
    def get_driver(self):
        options = webdriver.ChromeOptions()
        
        # Fast loading
        options.page_load_strategy = 'eager'  # Loads DOM faster without waiting for full page

        # Window and appearance
        options.add_argument("--window-size=1920,1080")  # Specific size, faster than "start-maximized"
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 🚀 Block heavy resources
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
            "profile.managed_default_content_settings.fonts": 2
        }
        options.add_experimental_option("prefs", prefs)

        # Headless mode with new engine if requested
        if self.headless:
            options.add_argument("--headless=new")  # Faster headless (v2)

        # You could optionally fake user-agent for even faster mobile loading
        # options.add_argument("user-agent=Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        self.driver.set_script_timeout(30)  # JS execution timeout
        self.driver.set_page_load_timeout(30)  # Total page load timeout
        return self.driver
        
    def quit(self):
        if self.driver:
            self.driver.quit()
