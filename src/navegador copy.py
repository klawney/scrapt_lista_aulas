import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

class Navegador:
    """
    Gerencia o ciclo de vida do driver do Selenium para o Microsoft Edge.
    """
    def __init__(self, caminho_perfil: str, caminho_driver: str = 'msedgedriver.exe'):
        self.caminho_perfil = caminho_perfil
        self.caminho_driver = caminho_driver
        self.driver = None

        if not os.path.exists(self.caminho_driver):
            raise FileNotFoundError(
                f"O driver '{self.caminho_driver}' não foi encontrado."
                "Faça o download e coloque-o na raiz do projeto."
            )

    def __enter__(self):
        """
        Inicia o navegador e o retorna ao entrar no bloco 'with'.
        """
        options = EdgeOptions()
        # Garante que o caminho do perfil seja absoluto
        caminho_abs_perfil = os.path.abspath(self.caminho_perfil)
        options.add_argument(f"user-data-dir={caminho_abs_perfil}")

        service = EdgeService(executable_path=self.caminho_driver)
        self.driver = webdriver.Edge(service=service, options=options)
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass