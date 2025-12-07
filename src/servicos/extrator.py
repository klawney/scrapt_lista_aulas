import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from dominio.aula import Aula

class ExtratorCoursera:
    def __init__(self, driver):
        self.driver = driver
        # Configurações de Seletores
        self.seletor_modulos = "div.cds-AccordionRoot-container > div"
        self.seletor_botao_expandir = "button[aria-expanded='false']"
        self.seletor_titulo_modulo = "h3, span.cds-Accordion-headerContent"
        self.seletor_itens = "a[href*='/learn/'], a[data-click-key*='lecture']"
        self.seletor_status_ok = "svg[data-testid='learn-item-success-icon']"
        self.seletor_status_lock = "svg[data-testid='learn-item-lock-icon']"

    def executar_extracao(self) -> list[Aula]:
        """Método principal que coordena o scroll, expansão e leitura."""
        self._rolar_pagina()
        self._expandir_modulos()
        return self._ler_itens()

    def _rolar_pagina(self):
        print("🔄 Rolando página...")
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(0.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
                if self.driver.execute_script("return document.body.scrollHeight") == last_height:
                    break
            last_height = new_height
        self.driver.execute_script("window.scrollTo(0, 0);")

    def _expandir_modulos(self):
        print("📂 Expandindo módulos...")
        wait = WebDriverWait(self.driver, 4)
        botoes = self.driver.find_elements(By.CSS_SELECTOR, self.seletor_botao_expandir)
        for bt in botoes:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", bt)
                self.driver.execute_script("arguments[0].click();", bt)
                wait.until(lambda d: bt.get_attribute("aria-expanded") == "true")
                time.sleep(random.uniform(0.2, 0.4))
            except: pass

    def _ler_itens(self) -> list[Aula]:
        lista_aulas = []
        modulos = self.driver.find_elements(By.CSS_SELECTOR, self.seletor_modulos)
        print(f"📦 Extraindo de {len(modulos)} módulos...")

        contador = 1
        for i, mod in enumerate(modulos):
            try:
                nome_mod = mod.find_element(By.CSS_SELECTOR, self.seletor_titulo_modulo).text.strip()
            except: nome_mod = f"Módulo {i+1}"
            
            print(f"   > {nome_mod}")
            
            itens = mod.find_elements(By.CSS_SELECTOR, self.seletor_itens)
            for item in itens:
                obj_aula = self._parser_item(item, nome_mod, contador)
                if obj_aula:
                    lista_aulas.append(obj_aula)
                    contador += 1
        return lista_aulas
    
    def _extrair_dados_aria_label(_,texto_aria,texto_visivel)->dict:
        partes = [p.strip() for p in texto_aria.split(',')] if texto_aria else []
        dados = {
            "tipo": "Desconhecido",
            "titulo": "Sem Título",
            "status": "Pendente",
            "meta": ""
        }
        match partes:
            case [t, tit, *resto]:
                dados["tipo"] = t
                dados["titulo"] = tit
                if resto:
                    dados["status"] = resto[0]
                if len(resto) > 1:
                    dados["meta"] = ", ".join(resto[1:])
            case _:
                if texto_visivel:
                    dados["titulo"] = texto_visivel

        return dados

    def _parser_item(self, element, nome_modulo, id_seq) -> Aula:
        try:
            url = element.get_attribute("href")
            if not url: return None
            aria = element.get_attribute("aria-label")
            texto_visivel = element.text.split("\n")[0]

            dados = self._extrair_dados_aria_label(texto_aria = aria,texto_visivel=texto_visivel)
            # Validação visual de status
            str_status = dados["status"]
            if str_status == "Pendente":
                if element.find_elements(By.CSS_SELECTOR, self.seletor_status_ok): str_status = "Concluído"
                elif element.find_elements(By.CSS_SELECTOR, self.seletor_status_lock): str_status = "Bloqueado"

            return Aula(
                id_sequencial=id_seq,
                nome_modulo=nome_modulo,
                tipo_conteudo=dados["tipo"],
                titulo=dados["titulo"],
                status=str_status,
                metadados=dados["meta"],
                url=url
            )
        except StaleElementReferenceException:
            return None