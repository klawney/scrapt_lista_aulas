# src/mapeador.py

import time
import re
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class MapeadorCurso:
    """
    Responsável por navegar até a página correta e extrair as informações do curso.
    """
    def __init__(self, driver: WebDriver, seletores: dict):
        self.driver = driver
        self.seletores = seletores
        self.wait = WebDriverWait(self.driver, 20)
        self.short_wait = WebDriverWait(self.driver, 5) # Um wait mais curto para tentativas

    # --- MÉTODO MODIFICADO ---
    def _aguardar_navegacao_manual(self, proxima_url_parcial: str):
        """Pausa e espera que o usuário navegue manualmente para a próxima etapa."""
        print("\n--- AÇÃO MANUAL NECESSÁRIA ---")
        print(f"Por favor, realize a ação necessária no navegador para prosseguir.")
        print(f"O script está aguardando a URL conter: '{proxima_url_parcial}'")
        self.wait.until(EC.url_contains(proxima_url_parcial))
        print("Navegação manual detectada. Continuando automação...")
        # Adiciona uma pequena pausa para a nova página começar a carregar
        time.sleep(2)

    def _clicar_botao_por_texto(self, seletor_generico: str, textos_possiveis: list[str]) -> bool:
        """Helper para encontrar e clicar em um botão com base em uma lista de textos."""
        try:
            # Usa o wait curto para não bloquear por muito tempo se não encontrar
            botoes_candidatos = self.short_wait.until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR, seletor_generico))
            )
            for botao in botoes_candidatos:
                if botao.text.strip() in textos_possiveis:
                    print(f"Botão '{botao.text.strip()}' encontrado. Clicando...")
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                    time.sleep(0.5)
                    botao.click()
                    return True
        except TimeoutException:
            return False # Se não encontrar, apenas retorna False
        return False

    # --- MÉTODO MODIFICADO ---
    def _tratar_estado_apresentacao(self):
        """Ação para sair do Nível 1 (Apresentação)."""
        print("Nível 1 (Apresentação) detectado. Procurando botão 'Ir para o Curso'...")
        seletores = self.seletores['navegacaoApresentacao']
        
        if not self._clicar_botao_por_texto(seletores['fallbackPorTexto']['seletorGenerico'], seletores['fallbackPorTexto']['textos']):
            # Se a automação falhar, pede ajuda ao usuário
            self._aguardar_navegacao_manual(self.seletores['navegacaoHome']['identificadorURL'])
        else:
            self.wait.until(EC.url_contains(self.seletores['navegacaoHome']['identificadorURL']))
            print("Transição para Nível 2 (Home) bem-sucedida.")

    # --- MÉTODO MODIFICADO ---
    def _tratar_estado_home(self):
        """Ação para sair do Nível 2 (Home) e ir para o Nível 3 (Player)."""
        print("Nível 2 (Home) detectado. Tentando clicar em 'Retomar'...")
        seletores = self.seletores['navegacaoHome']
        ids_url_player = self.seletores['identificacaoPaginaPlayer']['identificadorURL']
        
        if not self._clicar_botao_por_texto(seletores['seletorGenericoBotao'], seletores['textosBotao']):
            # Se a automação falhar, pede ajuda ao usuário
            self._aguardar_navegacao_manual(ids_url_player[0])
        else:
            self.wait.until(EC.any_of(
                *[EC.url_contains(id_url) for id_url in ids_url_player]
            ))
            print("Transição para Nível 3 (Player) bem-sucedida.")

    # --- Orquestração Principal (sem alterações) ---

    def navegar_e_preparar_pagina(self, tempo_max_espera_login: int):
        print("\nIniciando orquestração de navegação e preparação...")
        time.sleep(2)
        inicio_espera = time.time()
        
        while True:
            if time.time() - inicio_espera > tempo_max_espera_login:
                raise TimeoutException("Tempo máximo de espera para login e navegação esgotado.")
            
            url_atual = self.driver.current_url
            ids_url_player = self.seletores['identificacaoPaginaPlayer']['identificadorURL']

            if any(id_url in url_atual for id_url in ids_url_player):
                print(">>> Nível 3 (Player) detectado. Validando contexto...")
                self.validar_contexto_pagina_player()
                break
            elif self.seletores['navegacaoHome']['identificadorURL'] in url_atual:
                self._tratar_estado_home()
                continue
            elif re.search(self.seletores['navegacaoApresentacao']['identificadorRegex'], url_atual):
                self._tratar_estado_apresentacao()
                continue
            else:
                print(f"URL atual '{url_atual}' não corresponde a nenhum estado conhecido. Aguardando login...")
                time.sleep(5)
        
        self.expandir_todos_os_modulos()

    def validar_contexto_pagina_player(self):
        try:
            seletor = self.seletores['identificacaoPaginaPlayer']['containerPrincipal']
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor)))
            print("Contexto da página do Player validado com sucesso!")
        except TimeoutException:
            raise TimeoutException("O elemento principal do curso (menu lateral) não foi encontrado no Player.")

    def expandir_todos_os_modulos(self):
        # ... (código sem alterações)
        print("\nIniciando a expansão de todos os módulos do curso...")
        try:
            seletor_botao = self.seletores['navegacaoMenuPlayer']['botaoExpansaoModulo']
            atributo_status = self.seletores['navegacaoMenuPlayer']['atributoStatusExpansao']
            seletor_item_aula = self.seletores['extracaoDadosItem']['seletorTodosItensDeAula']

            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, seletor_botao)))
            botoes_expansao = self.driver.find_elements(By.CSS_SELECTOR, seletor_botao)
            
            if not botoes_expansao:
                print("Aviso: Nenhum botão de expansão de módulo foi encontrado.")
                return

            print(f"Encontrados {len(botoes_expansao)} módulos. Verificando e expandindo...")
            modulos_expandidos = 0
            for i, botao in enumerate(botoes_expansao):
                if botao.get_attribute(atributo_status) == 'false':
                    botao_clicavel = self.wait.until(EC.element_to_be_clickable(botao))
                    botao_clicavel.click()
                    modulos_expandidos += 1
                    
                    modulo_pai = botao.find_element(By.XPATH, "./ancestor::div[contains(@class, 'cds-AccordionItem-container')]")
                    self.wait.until(
                        EC.visibility_of_element_located(
                            (By.CSS_SELECTOR, seletor_item_aula)
                        )
                    )
                    print(f"Módulo {i+1} expandido com sucesso.")
            
            print(f"Processo de expansão finalizado. {modulos_expandidos} módulos foram abertos.")
            if modulos_expandidos == 0:
                print("Todos os módulos já estavam expandidos.")

        except (NoSuchElementException, TimeoutException) as e:
            raise type(e)(f"Erro durante a expansão dos módulos: {e.__class__.__name__} - {getattr(e, 'msg', str(e))}")