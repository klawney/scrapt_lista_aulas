import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService

print("--- Iniciando Teste Simples do Selenium ---")

driver = None  # Inicializa a variável driver

try:
    # Passo 1: Tenta instalar/carregar o driver do Edge automaticamente
    print("Tentando configurar o EdgeDriver automaticamente...")
    caminho_do_driver = 'msedgedriver.exe'
    servico = EdgeService(executable_path=caminho_do_driver)

    # Passo 2: Inicia uma instância do navegador Edge
    driver = webdriver.Edge(service=servico)
    print("Navegador Edge iniciado com sucesso!")

    # Passo 3: Navega para uma página
    url = "https://www.google.com"
    print(f"Navegando para: {url}")
    driver.get(url)

    # Passo 4: Verifica o título da página para confirmar que carregou
    print(f"Título da página: '{driver.title}'")
    print("\n>>> TESTE BEM-SUCEDIDO! <<<")
    print("O Selenium está configurado e funcionando.")

except Exception as e:
    print("\n--- OCORREU UM ERRO ---")
    print(f"Detalhes do erro: {e}")
    print("\nIsso geralmente acontece se o webdriver-manager for bloqueado.")
    print("Tente o 'Plano B' (download manual do Edgedriver) que discutimos anteriormente.")

finally:
    if driver:
        # Mantém o navegador aberto por 10 segundos para você ver
        print("\nO navegador fechará em 10 segundos...")
        time.sleep(10)
        
        # Fecha o navegador e encerra o processo do driver
        driver.quit()
        print("Navegador fechado. Teste finalizado.")