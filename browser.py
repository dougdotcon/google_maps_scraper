from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class BrowserManager:
    @staticmethod
    def create_driver(headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        path = ChromeDriverManager().install()
        # Workaround for webdriver-manager returning random files instead of exe
        import os
        if not path.endswith(".exe"):
            print(f"DEBUG: WebDriverManager returned {path}, searching for exe...")
            dir_name = os.path.dirname(path)
            candidate = os.path.join(dir_name, "chromedriver.exe")
            if os.path.exists(candidate):
                path = candidate
            else:
                 # Search recursively in the directory
                 found = False
                 for root, dirs, files in os.walk(dir_name):
                     if "chromedriver.exe" in files:
                         path = os.path.join(root, "chromedriver.exe")
                         found = True
                         break
                 if not found:
                     # Try one level up just in case
                     for root, dirs, files in os.walk(os.path.dirname(dir_name)):
                         if "chromedriver.exe" in files:
                             path = os.path.join(root, "chromedriver.exe")
                             break
            print(f"DEBUG: Resolved WebDriver path to: {path}")

        service = Service(path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
