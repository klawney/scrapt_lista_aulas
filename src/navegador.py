import os
import shutil
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

class Navegador:
    def __init__(self, caminho_perfil: str, caminho_driver: str = 'msedgedriver.exe'):
        self.caminho_perfil = caminho_perfil
        self.caminho_driver = caminho_driver
        self.driver = None

        if not os.path.exists(self.caminho_driver):
            if shutil.which(self.caminho_driver) is None:
                 raise FileNotFoundError(f"Driver não encontrado: {self.caminho_driver}")

    def __enter__(self):
        options = EdgeOptions()
        caminho_abs_perfil = os.path.abspath(self.caminho_perfil)
        
        options.add_argument(f"user-data-dir={caminho_abs_perfil}")

        options.add_argument("about:blank") 
        
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-session-crashed-bubble") 
        
        options.page_load_strategy = 'eager'
        options.add_argument("--disable-features=msSmartScreenProtection,RendererCodeIntegrity")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")

        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0")

        # Configurações de Download (Pode manter no prefs)
        prefs = {
            "safebrowsing.enabled": False,
            "safebrowsing.disable_download_protection": True
            # Nota: Removi as linhas de session.restore aqui pois não funcionaram para o seu perfil
        }
        options.add_experimental_option("prefs", prefs)


        service = EdgeService(executable_path=self.caminho_driver)
        self.driver = webdriver.Edge(service=service, options=options)
        
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass