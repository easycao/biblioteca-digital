"""Testes do catálogo de metadados e sua sincronização com o disco."""
import pytest

from src.biblioteca.catalogo import Catalogo


@pytest.fixture
def catalogo(tmp_path):
    """Catálogo isolado em tmp_path, com um arquivo de origem pronto."""
    cat = Catalogo(
        caminho_json=tmp_path / "catalogo.json",
        pasta_acervo=tmp_path / "acervo",
    )
    origem = tmp_path / "fonte.pdf"
    origem.write_text("conteúdo pdf falso")
    return cat, origem


def test_catalogo_vazio_no_inicio(catalogo):
    cat, _ = catalogo
    assert cat.listar() == []


def test_adicionar_copia_arquivo_e_registra(catalogo):
    cat, origem = catalogo
    doc = cat.adicionar(
        origem=origem,
        titulo="Artigo A",
        autor="Autor A",
        tipo="artigo",
        ano=2021,
    )
    # arquivo foi para o acervo
    assert (cat.pasta_acervo / doc.arquivo).is_file()
    # registrado no catálogo
    assert len(cat.listar()) == 1
    assert cat.listar()[0].titulo == "Artigo A"
    assert doc.formato == "pdf"  # derivado da extensão da origem


def test_adicionar_persiste_no_json(catalogo):
    cat, origem = catalogo
    cat.adicionar(origem=origem, titulo="T", autor="A", tipo="livro", ano=2020)
    # nova instância lê o mesmo json
    cat2 = Catalogo(caminho_json=cat.caminho_json, pasta_acervo=cat.pasta_acervo)
    assert len(cat2.listar()) == 1


def test_adicionar_origem_inexistente_levanta_erro(catalogo):
    cat, _ = catalogo
    with pytest.raises(FileNotFoundError):
        cat.adicionar(
            origem="nao_existe.pdf", titulo="X", autor="Y", tipo="artigo", ano=2020
        )
