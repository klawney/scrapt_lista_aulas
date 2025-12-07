import json
import os
from dotenv import load_dotenv

def carregar_variaveis_ambiente():
    """
    Carrega as variáveis do arquivo .env para o ambiente e valida a URL_CURSO.
    """
    load_dotenv()
    url_curso = os.getenv("URL_CURSO")
    if not url_curso:
        raise ValueError("A variável de ambiente 'URL_CURSO' não foi encontrada no arquivo .env.")
    return url_curso

def carregar_seletores(caminho_arquivo: str) -> dict:
    """
    Lê o arquivo JSON de seletores e o retorna como um dicionário.
    """
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: O arquivo de seletores '{caminho_arquivo}' não foi encontrado.")
        raise
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON em '{caminho_arquivo}'. Verifique a sintaxe.")
        raise