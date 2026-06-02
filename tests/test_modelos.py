"""Testes do modelo Documento."""
from src.biblioteca.modelos import Documento


def test_documento_para_dict_e_de_dict_sao_simetricos():
    doc = Documento(
        id="abc123",
        titulo="Aerodinâmica Básica",
        autor="João Silva",
        tipo="livro",
        ano=2020,
        formato="pdf",
        arquivo="aerodinamica.pdf",
        adicionado_em="2026-06-02T10:00:00",
    )
    como_dict = doc.para_dict()
    reconstruido = Documento.de_dict(como_dict)
    assert reconstruido == doc


def test_documento_novo_gera_id_e_timestamp():
    doc = Documento.novo(
        titulo="Tese X",
        autor="Maria",
        tipo="tese",
        ano=2019,
        formato="epub",
        arquivo="tese_x.epub",
    )
    assert doc.id  # id não vazio
    assert doc.adicionado_em  # timestamp preenchido
    assert doc.titulo == "Tese X"
