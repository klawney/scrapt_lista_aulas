import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from navegador import Navegador
# Certifique-se de que utils.configuracao existe ou substitua pela string direta
try:
    from utils.configuracao import carregar_variaveis_ambiente
except ImportError:
    # Fallback caso não tenha o arquivo utils
    def carregar_variaveis_ambiente():
        return "URL_DO_CURSO_AQUI" 

CAMINHO_PERFIL_NAVEGADOR = 'perfil_edge'
seletor_css = "div.cds-AccordionRoot-container a[href*='/learn/']"

def main():
    try:
        url_curso = carregar_variaveis_ambiente()
        
        # O bloco with garante que o navegador feche, mas precisamos tratar interrupções
        with Navegador(caminho_perfil=CAMINHO_PERFIL_NAVEGADOR) as driver:
            print("Navegador iniciado com sucesso.")
            
            try:
                driver.get(url_curso)
            except WebDriverException:
                print("Erro: Não foi possível carregar a página (o navegador foi fechado?)")
                return

            wait = WebDriverWait(driver, 20)
            print("Aguardando elementos...")
            
            try:
                elementos = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, seletor_css)))
            except Exception:
                print("Tempo esgotado ou elementos não encontrados.")
                elementos = []

            # Extrai os links (href) para uma lista
            lista_links = []
            for item in elementos:
                try:
                    link = item.get_attribute("href")
                    if link:
                        lista_links.append(link)
                except:
                    continue # Ignora elementos estragados (stale)

            # Exibe os resultados
            print("\n" + "="*40)
            print("--- Lista de Links Encontrados ---")
            print("="*40)
            
            for link in lista_links:
                print(link)
            
            print(f"\nTotal de links encontrados: {len(lista_links)}")
            print("\nPágina pronta para extração de dados.")
            
            # Input protegido contra Ctrl+C
            input("Pressione Enter para finalizar e fechar o navegador...")

    except KeyboardInterrupt:
        print("\n\n⚠️ Operação interrompida pelo usuário (Ctrl+C).")
        # O __exit__ do 'with' será chamado aqui automaticamente
    
    except (FileNotFoundError, ValueError) as e:
        print(f"\n❌ ERRO DE CONFIGURAÇÃO: {e}")
    
    except Exception as e:
        # Captura erros genéricos apenas se não for interrupção do usuário
        print(f"\n❌ Ocorreu um erro inesperado: {e}")

    finally:
        print("Script finalizado.")

if __name__ == "__main__":
    main()