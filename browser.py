import subprocess
import os
import socket
import sys
import time
import tempfile
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
# Try to import ChromeType from possible locations depending on version
try:
    from webdriver_manager.core.utils import ChromeType
except ImportError:
    try:
        from webdriver_manager.core.os_manager import ChromeType
    except ImportError:
        ChromeType = None

class BrowserManager:
    @staticmethod
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0

    @staticmethod
    def launch_debug_browser():
        print("DEBUG: Nenhuma instância de navegador aberta detectada.")
        print("DEBUG: O Python vai tentar abrir um navegador automaticamente...")

        browsers = [
            ("Brave", r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", "brave.exe"),
            ("Edge x86", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "msedge.exe"),
            ("Edge x64", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "msedge.exe"),
            ("Chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe", "chrome.exe"),
        ]

        selected_browser = None
        for name, path, proc in browsers:
            if os.path.exists(path):
                selected_browser = (name, path, proc)
                break
        
        if not selected_browser:
            raise Exception("Nenhum navegador (Brave, Edge ou Chrome) encontrado.")

        name, path, proc_name = selected_browser
        print(f"DEBUG: Navegador escolhido: {name}")

        try:
            subprocess.run(f"taskkill /F /IM {proc_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except: pass

        temp_dir = os.path.join(tempfile.gettempdir(), "selenium_automation_profile")
        if os.path.exists(temp_dir):
            try: shutil.rmtree(temp_dir, ignore_errors=True)
            except: pass
        os.makedirs(temp_dir, exist_ok=True)

        print(f"DEBUG: Iniciando {name} na porta 9222...")
        try:
            subprocess.Popen([
                path,
                "--remote-debugging-port=9222",
                f"--user-data-dir={temp_dir}",
                "--no-first-run",
                "--no-default-browser-check"
            ])
            for i in range(10):
                if BrowserManager.is_port_open(9222):
                    print("DEBUG: Porta 9222 aberta! Navegador pronto.")
                    return True
                time.sleep(1)
        except Exception as e:
            print(f"ERRO ao lançar navegador: {e}")
            raise e

    @staticmethod
    def create_driver(headless=False):
        driver = None
        
        # 1. Start browser if needed
        if not BrowserManager.is_port_open(9222):
            BrowserManager.launch_debug_browser()
        else:
             print("DEBUG: Usando navegador já aberto (Porta 9222).")
        
        options = ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        driver_path = None
        
        # 2. Try to get the BEST driver
        # First, try specifically for Brave if available, as that is the user's primary
        print("DEBUG: Buscando driver compatível...")
        try:
            # Try to use 'brave' type explicitly to handle version mapping
            driver_path = ChromeDriverManager(chrome_type='brave').install()
            print("DEBUG: Driver otimizado para Brave encontrado.")
        except Exception as e:
            print(f"DEBUG: Driver Brave falhou ({e}), tentando 'google-chrome' padrão...")
            try:
                # Fallback to standard Chrome (often compatible)
                driver_path = ChromeDriverManager().install()
            except Exception as e2:
                print(f"DEBUG: Driver padrão falhou: {e2}")
                # Ultimate fallback
                if os.path.exists("chromedriver.exe"):
                    driver_path = os.path.abspath("chromedriver.exe")

        if not driver_path:
             raise Exception("Erro crítico: Impossível obter um WebDriver.")

        if not driver_path.endswith(".exe") and "chromedriver" not in driver_path:
             d = os.path.dirname(driver_path)
             for root, dirs, files in os.walk(d):
                 if "chromedriver.exe" in files:
                     driver_path = os.path.join(root, "chromedriver.exe")
                     break

        print(f"DEBUG: Driver Path final: {driver_path}")
        
        try:
            service = ChromeService(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            print(f"ERRO DE CONEXÃO: {e}")
            print("Tentativa final: ignorando verificação de versão...")
            raise e
