import json
import sys
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException, 
    StaleElementReferenceException, 
    TimeoutException
)

# Importa a classe do navegador (Certifique-se que navegador.py está atualizado com 'eager')
from navegador import Navegador

# Importa configuração de URL
try:
    from utils.configuracao import carregar_variaveis_ambiente
except ImportError:
    print("\n[ERRO CRÍTICO] Arquivo 'utils/configuracao.py' não encontrado.")
    sys.exit(1)

# --- CONSTANTES ---
CAMINHO_PERFIL_NAVEGADOR = 'perfil_edge' 
ARQUIVO_SAIDA = 'dados_extraidos.json'

# --- SELETORES CSS ---
CONFIG = {
    "modulos": "div.cds-AccordionRoot-container > div", 
    "botao_expandir": "button[aria-expanded='false']",
    "titulo_modulo": "h3, span.cds-Accordion-headerContent",
    "itens_aula": "a[href*='/learn/'], a[data-click-key*='lecture']",
    
    # Fallbacks para dados
    "status_concluido": "svg[data-testid='learn-item-success-icon']",
    "status_bloqueado": "svg[data-testid='learn-item-lock-icon']"
}

def espera_inteligente_inicial(driver, timeout=90):
    """
    Substitui o wait.until rígido.
    Monitora a URL para saber se o usuário está logando ou se o curso carregou.
    """
    print("⏳ Aguardando carregamento ou login (Max 90s)...")
    
    for i in range(timeout):
        try:
            url = driver.current_url.lower()
            
            # 1. Detecta Login Corporativo / SSO / Microsoft
            if any(x in url for x in ["login.microsoft", "oauth", "signin", "sharepoint", "coursera.org/login"]):
                print(f"\r[{i}s] 🔒 Detectado tela de LOGIN. Por favor, faça login manualmente...", end="")
                time.sleep(1)
                continue

            # 2. Detecta a página do curso carregada (Sucesso)
            # Procura por container de acordeão OU cabeçalho principal
            elementos_curso = driver.find_elements(By.CSS_SELECTOR, "div.cds-AccordionRoot-container, h1.cds-119")
            
            if elementos_curso and "learn" in url:
                print("\n✅ Página do curso detectada e carregada!")
                return True
            
            # Feedback visual de carregamento
            print(f"\r[{i}s] Carregando... ", end="")
            time.sleep(1)
            
        except Exception:
            time.sleep(1)
            
    print("\n❌ Tempo esgotado aguardando carregamento.")
    return False

def rolar_pagina_ate_fim(driver):
    """
    Rola a página até o fim para disparar o Lazy Loading do React.
    """
    print("🔄 Rolando página para carregar estrutura DOM...")
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Rola 600px
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(0.5) 
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Se altura não mudou, tenta forçar o final
        if new_height == last_height:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            if driver.execute_script("return document.body.scrollHeight") == last_height:
                break
        last_height = new_height
    
    # Volta ao topo
    driver.execute_script("window.scrollTo(0, 0);")

def expandir_modulos(driver):
    """
    Clica em todos os botões 'aria-expanded=false' para carregar as aulas ocultas.
    """
    print("📂 Verificando módulos fechados...")
    wait_ui = WebDriverWait(driver, 4)
    
    try:
        # Busca botões fechados
        botoes = driver.find_elements(By.CSS_SELECTOR, CONFIG["botao_expandir"])
        print(f"   > Encontrados {len(botoes)} módulos para abrir.")
        
        for i, bt in enumerate(botoes):
            try:
                # Scroll até o botão (centralizado)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bt)
                
                # Clique JS (Ignora bloqueios de UI)
                driver.execute_script("arguments[0].click();", bt)
                
                # Aguarda mudança de estado (Isso confirma que o site processou)
                wait_ui.until(lambda d: bt.get_attribute("aria-expanded") == "true")
                
                # Pequena pausa aleatória para não parecer robô
                time.sleep(random.uniform(0.3, 0.7))
                
            except (TimeoutException, StaleElementReferenceException):
                pass # Segue para o próximo se falhar
    except NoSuchElementException:
        pass

def extrair_dados(driver):
    """
    Varre o DOM extraindo as informações organizadas.
    """
    lista_final = []
    
    # Seleciona os containers de módulos
    modulos = driver.find_elements(By.CSS_SELECTOR, CONFIG["modulos"])
    print(f"📦 Processando {len(modulos)} módulos...")

    contador_geral = 0
    
    for i, modulo in enumerate(modulos):
        # 1. Tenta pegar o Nome do Módulo
        try:
            nome_modulo = modulo.find_element(By.CSS_SELECTOR, CONFIG["titulo_modulo"]).text.strip()
        except:
            nome_modulo = f"Módulo {i+1}"
        
        print(f"   > Lendo: {nome_modulo}")

        # 2. Busca itens (aulas) DENTRO deste módulo
        itens = modulo.find_elements(By.CSS_SELECTOR, CONFIG["itens_aula"])
        
        for item in itens:
            try:
                url = item.get_attribute("href")
                if not url: continue

                # Estrutura base
                dados = {
                    "idSequencial": contador_geral,
                    "nomeDoModulo": nome_modulo,
                    "tipoDeConteudo": "Desconhecido",
                    "titulo": "Sem Título",
                    "status": "Pendente",
                    "metadados": "",
                    "url": url
                }

                # --- Parser do Aria-Label (Mais preciso) ---
                aria_label = item.get_attribute("aria-label")
                if aria_label:
                    partes = [p.strip() for p in aria_label.split(',')]
                    # Ex: "Vídeo, Introdução, Concluído, 5 min"
                    if len(partes) >= 2:
                        dados["tipoDeConteudo"] = partes[0]
                        dados["titulo"] = partes[1]
                        if len(partes) > 2: dados["status"] = partes[2]
                        if len(partes) > 3: dados["metadados"] = ", ".join(partes[3:])
                    else:
                        dados["titulo"] = item.text.split("\n")[0]
                else:
                    # Fallback visual
                    dados["titulo"] = item.text.split("\n")[0]

                # --- Validação Visual de Status ---
                # Se aria-label não deu certeza, olha o ícone
                if dados["status"] in ["Pendente", "Não enviado", "Desconhecido"]:
                    if item.find_elements(By.CSS_SELECTOR, CONFIG["status_concluido"]):
                        dados["status"] = "Concluído"
                    elif item.find_elements(By.CSS_SELECTOR, CONFIG["status_bloqueado"]):
                        dados["status"] = "Bloqueado"

                lista_final.append(dados)
                contador_geral += 1

            except StaleElementReferenceException:
                # Se o item sumiu da memória durante o loop, ignora
                continue

    return lista_final

def main():
    try:
        url = carregar_variaveis_ambiente()
        if not url: raise ValueError("URL não configurada no arquivo .env ou utils.")

        with Navegador(CAMINHO_PERFIL_NAVEGADOR) as driver:
            print(f"🚀 Iniciando acesso: {url}")
            
            # Carrega a página (Não deve travar graças ao 'eager' no navegador.py)
            driver.get(url)
            
            # 1. Espera Inteligente (Login ou Carregamento)
            conectado = espera_inteligente_inicial(driver)
            
            if not conectado:
                resp = input("\n⚠️ Não foi possível confirmar o carregamento automático.\nDeseja tentar extrair mesmo assim? (s/n): ")
                if resp.lower() != 's':
                    return

            # Pausa tática para React terminar renders iniciais
            time.sleep(3)
            
            # Validação de página errada
            if "syllabus" in driver.current_url.lower():
                print("\n⚠️ AVISO: Você está na página de EMENTA (Syllabus).")
                print("Recomendado trocar URL para a página 'Home' ou 'Modules'.")
            
            # 2. Executa a Raspagem
            rolar_pagina_ate_fim(driver)
            expandir_modulos(driver)
            dados = extrair_dados(driver)
            
            # 3. Salva Resultado
            print(f"\n✅ Extração Finalizada! {len(dados)} itens capturados.")
            with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
            
            print(f"📁 Arquivo salvo em: {ARQUIVO_SAIDA}")

    except KeyboardInterrupt:
        print("\n🛑 Script interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        # input("Pressione Enter para ver o erro antes de fechar...") # Opcional para debug

if __name__ == "__main__":
    main()