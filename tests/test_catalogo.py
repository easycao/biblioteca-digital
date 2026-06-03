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


def _popular(cat, origem):
    """Adiciona alguns documentos variados ao catálogo de teste."""
    cat.adicionar(origem=origem, titulo="Artigo 2021", autor="Ana", tipo="artigo", ano=2021)
    cat.adicionar(origem=origem, titulo="Livro 2020", autor="Beto", tipo="livro", ano=2020)
    cat.adicionar(origem=origem, titulo="Artigo 2020", autor="Carla", tipo="artigo", ano=2020)


def test_listar_por_tipo_agrupa(catalogo):
    cat, origem = catalogo
    _popular(cat, origem)
    grupos = cat.listar_por_tipo()
    assert set(grupos.keys()) == {"artigo", "livro"}
    assert len(grupos["artigo"]) == 2
    assert len(grupos["livro"]) == 1


def test_listar_por_ano_agrupa(catalogo):
    cat, origem = catalogo
    _popular(cat, origem)
    grupos = cat.listar_por_ano()
    assert set(grupos.keys()) == {2020, 2021}
    assert len(grupos[2020]) == 2
    assert len(grupos[2021]) == 1


def test_buscar_por_titulo_e_autor(catalogo):
    cat, origem = catalogo
    _popular(cat, origem)
    assert len(cat.buscar("Artigo")) == 2  # por título
    assert len(cat.buscar("ana")) == 1     # por autor, case-insensitive
    assert cat.buscar("inexistente") == []


def test_obter_por_id(catalogo):
    cat, origem = catalogo
    doc = cat.adicionar(origem=origem, titulo="T", autor="A", tipo="tese", ano=2022)
    assert cat.obter(doc.id) == doc
    assert cat.obter("inexistente") is None


def test_renomear_atualiza_titulo(catalogo):
    cat, origem = catalogo
    doc = cat.adicionar(origem=origem, titulo="Antigo", autor="A", tipo="livro", ano=2020)
    cat.renomear(doc.id, novo_titulo="Novo Título")
    assert cat.obter(doc.id).titulo == "Novo Título"
    # persistido
    cat2 = Catalogo(caminho_json=cat.caminho_json, pasta_acervo=cat.pasta_acervo)
    assert cat2.obter(doc.id).titulo == "Novo Título"


def test_renomear_id_inexistente_levanta_erro(catalogo):
    cat, _ = catalogo
    with pytest.raises(KeyError):
        cat.renomear("nao_existe", novo_titulo="X")


def test_remover_apaga_arquivo_e_entrada(catalogo):
    cat, origem = catalogo
    doc = cat.adicionar(origem=origem, titulo="T", autor="A", tipo="artigo", ano=2020)
    caminho_arquivo = cat.pasta_acervo / doc.arquivo
    assert caminho_arquivo.is_file()
    cat.remover(doc.id)
    assert not caminho_arquivo.exists()      # arquivo apagado do disco
    assert cat.obter(doc.id) is None          # entrada removida do catálogo


def test_remover_id_inexistente_levanta_erro(catalogo):
    cat, _ = catalogo
    with pytest.raises(KeyError):
        cat.remover("nao_existe")


def test_contar_documentos(catalogo):
    cat, origem = catalogo
    assert cat.contar() == 0
    cat.adicionar(origem=origem, titulo="T", autor="A", tipo="artigo", ano=2020)
    assert cat.contar() == 1


def test_listar_por_formato_agrupa(catalogo):
    cat, tmp = catalogo
    # cria origens com formatos diferentes
    pdf = tmp.parent / "a.pdf"
    pdf.write_text("x", encoding="utf-8")
    epub = tmp.parent / "b.epub"
    epub.write_text("y", encoding="utf-8")
    cat.adicionar(origem=pdf, titulo="P1", autor="A", tipo="livro", ano=2020)
    cat.adicionar(origem=pdf, titulo="P2", autor="B", tipo="artigo", ano=2021)
    cat.adicionar(origem=epub, titulo="E1", autor="C", tipo="tese", ano=2022)
    grupos = cat.listar_por_formato()
    assert set(grupos.keys()) == {"pdf", "epub"}
    assert len(grupos["pdf"]) == 2
    assert len(grupos["epub"]) == 1
