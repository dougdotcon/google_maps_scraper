from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
import subprocess
import os
import socket

class BrowserManager:
    @staticmethod
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0

    @staticmethod
    def create_driver(headless=False):
        driver = None
        attach_mode = False
        
        # 1. Verifica se ja existe navegador rodando com debug (Porta 9222)
        if BrowserManager.is_port_open(9222):
            print("=========================================================")
            print("DEBUG: Instância de navegador detectada na porta 9222!")
            print("DEBUG: O robô vai tentar se conectar ao navegador que já está aberto.")
            print("=========================================================")
            attach_mode = True
        
        # Configura as opcoes
        options = ChromeOptions()
        
        if attach_mode:
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        else:
            # Opções normais para abrir navegador novo
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--remote-allow-origins=*')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

        # ------------------------------------------------------------------
        # ESTRATEGIA DE DRIVER:
        # Se estamos anexando (attach_mode), precisamos de QUALQUER driver que fale o protocolo.
        # Driver 131 (estavel) geralmente funciona bem mesmo com versoes diferentes se for via remote.
        # Se nao estamos anexando, tentamos achar o driver correto.
        # ------------------------------------------------------------------
        
        driver_path = None
        
        try:
             print("DEBUG: Gerenciando WebDriver...")
             # Tente instalar a versao estavel conhecida (Chrome 131)
             # Isso e o mais seguro para evitar erros de "latest" ou versoes beta do Brave
             driver_path = ChromeDriverManager(driver_version="131.0.6778.204").install()
        except Exception as e:
             print(f"DEBUG: Falha ao baixar driver fixo: {e}")
             print("DEBUG: Tentando driver 'latest'...")
             try:
                 driver_path = ChromeDriverManager().install()
             except:
                 pass

        if not driver_path:
            # Fallback local
            if os.path.exists("chromedriver.exe"):
                driver_path = os.path.abspath("chromedriver.exe")

        if not driver_path:
             raise Exception("Nao foi possivel baixar o WebDriver.")

        # Garantir que caminho aponta para exe
        if not driver_path.endswith(".exe") and "chromedriver" not in driver_path:
            d = os.path.dirname(driver_path)
            for root, dirs, files in os.walk(d):
                 if "chromedriver.exe" in files:
                     driver_path = os.path.join(root, "chromedriver.exe")
                     break

        print(f"DEBUG: Usando driver em: {driver_path}")
        
        # Inicializa o Driver
        try:
            service = ChromeService(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            
            if not attach_mode:
                # Ocultar automacao
                try:
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                except: pass
            
            return driver
            
        except Exception as e:
            print(f"ERRO ao criar driver: {e}")
            if "binary" in str(e).lower() and not attach_mode:
                 # Se falhar por causa de binario nao encontrado, tente achar manualmente
                 # So faz sentido se estiver tentando abrir um novo (nao attach)
                 print("Tentando localizar binarios manualmente...")
                 # (Aqui poderia ir a logica antiga de achar binario, mas vamos focar no attach)
            raise e
