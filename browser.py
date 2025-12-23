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
        
        # --- FIX: Explicitly find Chrome/Brave/Opera Binary ---
        import os
        possible_paths = [
            # Chrome
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            
            # Brave
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),

            # Opera GX / Opera (Pode funcionar com chromedriver dependendo da versao)
            os.path.expanduser(r"~\AppData\Local\Programs\Opera GX\opera.exe"),
            os.path.expanduser(r"~\AppData\Local\Programs\Opera\opera.exe"),
        ]
        
        binary_path = None
        found_browser_name = "Unknown"
        
        for p in possible_paths:
            if os.path.exists(p):
                binary_path = p
                if "brave" in p.lower(): found_browser_name = "Brave"
                elif "opera" in p.lower(): found_browser_name = "Opera"
                else: found_browser_name = "Chrome"
                
                print(f"DEBUG: Navegador encontrado ({found_browser_name}): {p}")
                break
        
        if binary_path:
            chrome_options.binary_location = binary_path
        else:
            print("WARNING: Nenhum navegador conhecido (Chrome/Brave/Opera) foi encontrado nos locais padrao.")
        # ------------------------------------------

        path = ChromeDriverManager().install()
        # Workaround for webdriver-manager returning random files instead of exe
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
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except WebDriverException as e:
            if "binary" in str(e).lower():
                print("ERRO CRITICO: O Selenium nao encontrou o Google Chrome instalado.")
                print("Solucao: Instale o Google Chrome ou verifique se esta em um local padrao.")
            raise e
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
