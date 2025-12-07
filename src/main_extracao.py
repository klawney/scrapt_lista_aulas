import sys
import time
from selenium.webdriver.common.by import By

# Importações dos novos módulos
from navegador import Navegador
from servicos.extrator import ExtratorCoursera
from servicos.exportador import salvar_dados_json

# Configuração
try:
    from utils.configuracao import carregar_variaveis_ambiente
except ImportError:
    print("[ERRO] Config não encontrada.")
    sys.exit(1)

ARQUIVO_SAIDA = "dados_curso_segregado.json"
CAMINHO_PERFIL = "perfil_edge"

def espera_login(driver):
    """Mantém a lógica de esperar login manual se necessário."""
    print("⏳ Aguardando carregamento ou login...")
    for i in range(90):
        try:
            url = driver.current_url.lower()
            if any(x in url for x in ["login.microsoft", "oauth", "signin"]):
                print(f"\r[{i}s] 🔒 LOGIN DETECTADO. Aguardando usuário...", end="")
                time.sleep(1)
                continue
            
            # Se achou container de módulos
            if driver.find_elements(By.CSS_SELECTOR, "div.cds-AccordionRoot-container"):
                print("\n✅ Curso carregado!")
                return True
            time.sleep(1)
        except: time.sleep(1)
    return False

def main():
    url = carregar_variaveis_ambiente()
    if not url: return

    with Navegador(CAMINHO_PERFIL) as driver:
        print(f"🚀 Iniciando: {url}")
        driver.get(url)
        
        if not espera_login(driver):
            if input("Não detectado. Continuar? (s/n): ").lower() != 's': return
        
        # --- AQUI ESTÁ A MÁGICA DA SEGREGAÇÃO ---
        
        # 1. Instancia o Extrator
        extrator = ExtratorCoursera(driver)
        
        # 2. Executa e recebe a lista de objetos (Modelos)
        lista_de_aulas = extrator.executar_extracao()
        
        print(f"\n✅ Extração finalizada. Total: {len(lista_de_aulas)} itens.")

        # 3. Chama o Exportador para salvar
        if lista_de_aulas:
            salvar_dados_json(lista_de_aulas, ARQUIVO_SAIDA)

if __name__ == "__main__":
    main()