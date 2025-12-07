from dataclasses import dataclass, asdict

@dataclass
class Aula:
    id_sequencial: int
    nome_modulo: str
    tipo_conteudo: str
    titulo: str
    status: str
    metadados: str
    url: str

    def to_dict(self):
        """Converte o objeto para dicionário (para salvar em JSON)."""
        return asdict(self)