# src/utils/excecoes.py

class ExcecaoDadosCriticosAusentes(Exception):
    """Lançada quando dados críticos (URL, tipo) não podem ser extraídos de um item."""
    pass

class ExcecaoContextoInvalido(Exception):
    """Lançada quando a página não é validada como a página correta do curso."""
    pass