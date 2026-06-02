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


import builtins

import pytest

from src.biblioteca.catalogo import Catalogo


@pytest.fixture
def cat_pronto(tmp_path):
    cat = Catalogo(
        caminho_json=tmp_path / "catalogo.json", pasta_acervo=tmp_path / "acervo"
    )
    origem = tmp_path / "fonte.pdf"
    origem.write_text("x")
    cat.adicionar(origem=origem, titulo="Doc Teste", autor="Aut", tipo="artigo", ano=2021)
    return cat, origem


def _entradas(monkeypatch, respostas):
    """Faz input() retornar cada item de `respostas` em sequência."""
    it = iter(respostas)
    monkeypatch.setattr(builtins, "input", lambda *a, **k: next(it))


def test_menu_lista_por_tipo_e_sai(monkeypatch, capsys, cat_pronto):
    cat, _ = cat_pronto
    _entradas(monkeypatch, ["1", "0"])  # opção 1 (listar por tipo) e depois sair
    cli.executar_menu(cat)
    saida = capsys.readouterr().out
    assert "Doc Teste" in saida


def test_menu_remover_pede_confirmacao(monkeypatch, capsys, cat_pronto):
    cat, _ = cat_pronto
    doc_id = cat.listar()[0].id
    # opção 5 (remover), informa id, confirma com "s", depois sai
    _entradas(monkeypatch, ["5", doc_id, "s", "0"])
    cli.executar_menu(cat)
    assert cat.obter(doc_id) is None  # removido após confirmação


def test_menu_remover_cancela_sem_confirmar(monkeypatch, capsys, cat_pronto):
    cat, _ = cat_pronto
    doc_id = cat.listar()[0].id
    _entradas(monkeypatch, ["5", doc_id, "n", "0"])  # responde "n" → não remove
    cli.executar_menu(cat)
    assert cat.obter(doc_id) is not None  # permanece


def test_menu_opcao_invalida_continua(monkeypatch, capsys, cat_pronto):
    cat, _ = cat_pronto
    _entradas(monkeypatch, ["99", "0"])  # opção inválida, depois sai
    cli.executar_menu(cat)
    saida = capsys.readouterr().out
    assert "inválida" in saida.lower()


def test_construir_parser_aceita_listar_por_tipo():
    parser = cli.construir_parser()
    args = parser.parse_args(["listar", "--por", "tipo"])
    assert args.comando == "listar"
    assert args.por == "tipo"


def test_construir_parser_aceita_listar_por_ano():
    parser = cli.construir_parser()
    args = parser.parse_args(["listar", "--por", "ano"])
    assert args.por == "ano"
