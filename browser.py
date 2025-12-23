from selenium import webdriver
# Chrome Imports
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType

# Edge Imports
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from selenium.common.exceptions import WebDriverException
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
        driver = None
        
        # =========================================================================
        # 1. TENTATIVA PRIORITARIA: MICROSOFT EDGE
        # =========================================================================
        try:
            print("DEBUG: Tentando iniciar Microsoft Edge...")
            edge_options = EdgeOptions()
            if headless:
                edge_options.add_argument('--headless')
            
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--window-size=1920,1080')
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            
            # Detectar binario do Edge
            edge_paths = [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            ]
            
            edge_binary = None
            for p in edge_paths:
                if os.path.exists(p):
                    edge_binary = p
                    break
            
            if edge_binary:
                print(f"DEBUG: Edge encontrado em: {edge_binary}")
                edge_options.binary_location = edge_binary
                
                # Instalar Driver do Edge
                driver_path = EdgeChromiumDriverManager().install()
                
                driver = webdriver.Edge(service=EdgeService(driver_path), options=edge_options)
                print("DEBUG: Driver Edge iniciado com sucesso!")
                
                # Mascarar automação
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                return driver
            else:
                print("DEBUG: Executável do Edge não encontrado nos locais padrão.")

        except Exception as e:
            print(f"DEBUG: Falha ao iniciar Edge: {e}")
            print("DEBUG: Tentando fallback para Chrome/Brave...")

        # =========================================================================
        # 2. FALLBACK: CHROME / BRAVE / OPERA
        # =========================================================================
        try:
            chrome_options = ChromeOptions()
            if headless:
                chrome_options.add_argument('--headless')
            
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
                r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
            
            binary_path = None
            for p in possible_paths:
                if os.path.exists(p):
                    binary_path = p
                    break
            
            if binary_path:
                print(f"DEBUG: Fallback Browser encontrado: {binary_path}")
                chrome_options.binary_location = binary_path
            
            # Tentar instalação genérica que resolve a maioria dos casos de Chrome/Brave
            try:
                if binary_path and "brave" in binary_path.lower():
                     print("DEBUG: Tentando driver para Brave...")
                     driver_path = ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()
                else:
                     driver_path = ChromeDriverManager().install()
            except:
                 driver_path = ChromeDriverManager().install()

            # Corrigir caminho sem .exe se necessário
            if not driver_path.endswith(".exe"):
                d = os.path.dirname(driver_path)
                for root, dirs, files in os.walk(d):
                    if "chromedriver.exe" in files:
                        driver_path = os.path.join(root, "chromedriver.exe")
                        break
            
            driver = webdriver.Chrome(service=ChromeService(driver_path), options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver

        except Exception as e:
            print("\n" + "="*50)
            print("ERRO FATAL: Não foi possível iniciar Edge nem Chrome/Brave.")
            print(f"Detalhe do erro: {e}")
            print("="*50 + "\n")
            raise e
