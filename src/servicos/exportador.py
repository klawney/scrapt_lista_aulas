import json
import os

def salvar_dados_json(lista_aulas: list, caminho_arquivo: str):
    """
    Recebe uma lista de objetos do tipo Aula e salva em JSON.
    """
    print(f"💾 Salvando {len(lista_aulas)} itens em '{caminho_arquivo}'...")
    
    # Converte a lista de objetos Aula para lista de dicionários
    dados_dict = [aula.to_dict() for aula in lista_aulas]
    
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_dict, f, ensure_ascii=False, indent=2)
        print("✅ Arquivo salvo com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {e}")