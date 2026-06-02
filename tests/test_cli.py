"""Testes da camada de interface de linha de comando."""
from src.biblioteca import cli
from src.biblioteca.modelos import Documento


def _doc(titulo, tipo, ano):
    return Documento.novo(
        titulo=titulo, autor="Autor", tipo=tipo, ano=ano, formato="pdf", arquivo="x.pdf"
    )


def test_formatar_por_tipo_mostra_cabecalhos():
    grupos = {"artigo": [_doc("A1", "artigo", 2021)], "livro": [_doc("L1", "livro", 2020)]}
    texto = cli.formatar_por_tipo(grupos)
    assert "ARTIGO" in texto.upper()
    assert "LIVRO" in texto.upper()
    assert "A1" in texto
    assert "L1" in texto


def test_formatar_por_ano_ordena_decrescente():
    grupos = {2020: [_doc("X", "artigo", 2020)], 2022: [_doc("Y", "tese", 2022)]}
    texto = cli.formatar_por_ano(grupos)
    # 2022 aparece antes de 2020
    assert texto.index("2022") < texto.index("2020")


def test_formatar_lista_vazia():
    assert "Nenhum documento" in cli.formatar_por_tipo({})
