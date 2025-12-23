from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
import subprocess
import os

class BrowserManager:
    @staticmethod
    def get_file_version_powershell(file_path):
        try:
            cmd = f'(Get-Item "{file_path}").VersionInfo.FileVersion'
            result = subprocess.run(["powershell", "-command", cmd], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split(" ")[0]
        except:
            pass
        return None

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
        possible_paths = [
            # Chrome
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            
            # Brave
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"),

            # Opera GX / Opera
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
                break
        
        driver_path = None
        
        if binary_path:
            print(f"DEBUG: Navegador encontrado ({found_browser_name}): {binary_path}")
            chrome_options.binary_location = binary_path
            
            # Logic to install correct driver
            try:
                if found_browser_name == "Brave":
                    # For Brave, try letting webdriver_manager handle it with ChromeType.BRAVE
                    # Or fallback to generic install which usually picks latest
                    try:
                        print("DEBUG: Tentando instalar driver para Brave...")
                        driver_path = ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()
                    except:
                        # Fallback for older webdriver_manager versions or valid errors
                        driver_path = ChromeDriverManager().install()
                        
                elif found_browser_name == "Chrome":
                    # For Chrome, version match is important
                    driver_version = BrowserManager.get_file_version_powershell(binary_path)
                    if driver_version:
                        print(f"DEBUG: Versão Chrome detectada: {driver_version}")
                        driver_path = ChromeDriverManager(driver_version=driver_version).install()
                    else:
                        driver_path = ChromeDriverManager().install()
                else:
                    # Opera/Others
                    driver_path = ChromeDriverManager().install()
                    
            except Exception as e:
                print(f"DEBUG: Erro na instalação automática do driver: {e}")
                print("DEBUG: Tentando fallback para versão estável recente (131.0)...")
                try:
                    # EMERGENCY FALLBACK: Force a known recent stable version
                    driver_path = ChromeDriverManager(driver_version="131.0.6778.204").install()
                except Exception as e2:
                    print(f"DEBUG: Falha total no driver: {e2}")
        else:
            print("WARNING: Nenhum navegador conhecido encontrado. Tentando instanciar padrão...")
            try:
                driver_path = ChromeDriverManager().install()
            except:
                pass

        if not driver_path:
             raise Exception("Não foi possível baixar/encontrar o WebDriver.")

        # Workaround for webdriver-manager issues returning paths without extension
        if not driver_path.endswith(".exe"):
            dir_name = os.path.dirname(driver_path)
            candidate = os.path.join(dir_name, "chromedriver.exe")
            if os.path.exists(candidate):
                driver_path = candidate
            else:
                 # Search recursively
                 for root, dirs, files in os.walk(dir_name):
                     if "chromedriver.exe" in files:
                         driver_path = os.path.join(root, "chromedriver.exe")
                         break

        service = Service(driver_path)
        try:
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except WebDriverException as e:
            if "binary" in str(e).lower():
                print("ERRO CRITICO: Binário do navegador não encontrado pelo Selenium.")
            print(f"Erro ao iniciar driver: {e}")
            raise e
        except Exception as e:
            print(f"Erro genérico ao abrir navegador: {e}")
            raise e
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
