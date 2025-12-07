# main.py

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from src.navegador import Navegador
from src.mapeador import MapeadorCurso
from src.utils.configuracao import carregar_seletores, carregar_variaveis_ambiente

# --- Constantes de Configuração ---
CAMINHO_ARQUIVO_SELETORES = 'config/mapaDeSeletores.json'
CAMINHO_PERFIL_NAVEGADOR = 'perfil_edge'
TEMPO_MAX_ESPERA_GERAL_SEGUNDOS = 300

def main():
    """
    Função principal que orquestra a execução do script.
    """
    print("Inicializando script mapeador...")
    
    try:
        url_curso = carregar_variaveis_ambiente()
        seletores = carregar_seletores(CAMINHO_ARQUIVO_SELETORES)
        print("Configurações carregadas com sucesso.")

        with Navegador(caminho_perfil=CAMINHO_PERFIL_NAVEGADOR) as driver:
            print("Navegador iniciado com sucesso.")
            driver.get(url_curso)

            mapeador = MapeadorCurso(driver, seletores)
            
            # UMA ÚNICA CHAMADA que resolve a navegação e prepara a página
            mapeador.navegar_e_preparar_pagina(TEMPO_MAX_ESPERA_GERAL_SEGUNDOS)

            print("\nPágina pronta para extração de dados.")
            input("Pressione Enter para finalizar...")

    except (FileNotFoundError, ValueError) as e:
        print(f"\nERRO DE CONFIGURAÇÃO: {e}")
    except (NoSuchElementException, TimeoutException) as e:
        print(f"\nERRO DE NAVEGAÇÃO/MAPEAMENTO: {e}")
    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")
    
    print("Script finalizado.")

if __name__ == '__main__':
    main()