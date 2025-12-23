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

class BrowserManager:
    @staticmethod
    def is_port_open(port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0

    @staticmethod
    def launch_debug_browser():
        """
        Tenta encontrar um navegador instalado e abri-lo em modo de depuração (Porta 9222).
        Isso permite que o Selenium se conecte a ele sem problemas de versão de driver.
        """
        print("DEBUG: Nenhuma instância de navegador aberta detectada.")
        print("DEBUG: O Python vai tentar abrir um navegador automaticamente...")

        browsers = [
            # Nome, Executável, Nome do Processo
            ("Brave", r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", "brave.exe"),
            ("Edge x86", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "msedge.exe"),
            ("Edge x64", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "msedge.exe"),
            ("Chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe", "chrome.exe"),
            ("Chrome Local", os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"), "chrome.exe"),
        ]

        selected_browser = None
        for name, path, proc in browsers:
            if os.path.exists(path):
                selected_browser = (name, path, proc)
                break
        
        if not selected_browser:
            raise Exception("Nenhum navegador (Brave, Edge ou Chrome) encontrado nos locais padrão.")

        name, path, proc_name = selected_browser
        print(f"DEBUG: Navegador escolhido: {name}")

        # 1. Matar processos antigos para liberar a porta (opcional, mas recomendado)
        try:
            subprocess.run(f"taskkill /F /IM {proc_name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except:
            pass

        # 2. Criar perfil temporário
        temp_dir = os.path.join(tempfile.gettempdir(), "selenium_automation_profile")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        os.makedirs(temp_dir, exist_ok=True)

        # 3. Lançar o navegador
        print(f"DEBUG: Iniciando {name} na porta 9222...")
        try:
            # Popen não bloqueia o script
            subprocess.Popen([
                path,
                "--remote-debugging-port=9222",
                f"--user-data-dir={temp_dir}",
                "--no-first-run",
                "--no-default-browser-check"
            ])
            # Esperar o navegador subir
            for i in range(10):
                if BrowserManager.is_port_open(9222):
                    print("DEBUG: Porta 9222 aberta! Navegador pronto.")
                    return True
                time.sleep(1)
            
            print("WARNING: O navegador abriu, mas a porta 9222 não respondeu rápido. Tentando conectar mesmo assim...")
        except Exception as e:
            print(f"ERRO ao lançar navegador: {e}")
            raise e

    @staticmethod
    def create_driver(headless=False):
        driver = None
        
        # 1. Verifica se ja existe navegador rodando. Se não, abre um.
        if not BrowserManager.is_port_open(9222):
            BrowserManager.launch_debug_browser()
        else:
             print("DEBUG: Navegador já estava aberto na porta 9222. Conectando...")
        
        # Configura as opcoes para ANEXAR (Attach)
        options = ChromeOptions()
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        # ------------------------------------------------------------------
        # ESTRATEGIA DE DRIVER:
        # ------------------------------------------------------------------
        driver_path = None
        
        try:
             print("DEBUG: Obtendo WebDriver compatível (Fallback Estável)...")
             # Como estamos usando DEBUGGER ADDRESS, a versão exata do driver importa menos.
             # Um driver 131 costuma controlar um Chrome/Brave 143 via CDP sem falhar handshake.
             driver_path = ChromeDriverManager(driver_version="131.0.6778.204").install()
        except Exception as e:
             try:
                 driver_path = ChromeDriverManager().install()
             except:
                 if os.path.exists("chromedriver.exe"):
                    driver_path = os.path.abspath("chromedriver.exe")

        if not driver_path:
             raise Exception("Nao foi possivel baixar o WebDriver.")

        if not driver_path.endswith(".exe") and "chromedriver" not in driver_path:
            d = os.path.dirname(driver_path)
            for root, dirs, files in os.walk(d):
                 if "chromedriver.exe" in files:
                     driver_path = os.path.join(root, "chromedriver.exe")
                     break

        print(f"DEBUG: Usando driver em: {driver_path}")
        
        try:
            service = ChromeService(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            return driver
            
        except Exception as e:
            print(f"ERRO ao conectar ao navegador: {e}")
            raise e
