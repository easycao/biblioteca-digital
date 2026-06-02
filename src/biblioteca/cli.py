"""Interface de linha de comando: menu de contexto + comandos diretos.

Camada de apresentação. Funções de formatação são puras (testáveis sem input).
"""
from __future__ import annotations

import argparse

from src.biblioteca.modelos import Documento


# ---------------------------------------------------------------------------
# Formatação (funções puras)
# ---------------------------------------------------------------------------

def _linha_documento(doc: Documento) -> str:
    """Formata um documento em uma linha legível."""
    return f"  [{doc.id}] {doc.titulo} — {doc.autor} ({doc.ano}, {doc.formato})"


def formatar_por_tipo(grupos: dict[str, list[Documento]]) -> str:
    """Formata os documentos agrupados por tipo."""
    if not grupos:
        return "Nenhum documento cadastrado."
    partes: list[str] = []
    for tipo in sorted(grupos):
        partes.append(f"== {tipo.upper()} ==")
        for doc in grupos[tipo]:
            partes.append(_linha_documento(doc))
    return "\n".join(partes)


def formatar_por_ano(grupos: dict[int, list[Documento]]) -> str:
    """Formata os documentos agrupados por ano (mais recente primeiro)."""
    if not grupos:
        return "Nenhum documento cadastrado."
    partes: list[str] = []
    for ano in sorted(grupos, reverse=True):
        partes.append(f"== {ano} ==")
        for doc in grupos[ano]:
            partes.append(_linha_documento(doc))
    return "\n".join(partes)


# ---------------------------------------------------------------------------
# Menu de contexto interativo
# ---------------------------------------------------------------------------

from pathlib import Path

from src.biblioteca.catalogo import Catalogo

MENU = """
=== Biblioteca Digital ===
1. Listar documentos (por tipo)
2. Listar documentos (por ano)
3. Adicionar documento
4. Renomear documento
5. Remover documento
6. Buscar documento
7. Ler/abrir documento
0. Sair
"""


def _opcao_listar_por_tipo(cat: Catalogo) -> None:
    print(formatar_por_tipo(cat.listar_por_tipo()))


def _opcao_listar_por_ano(cat: Catalogo) -> None:
    print(formatar_por_ano(cat.listar_por_ano()))


def _opcao_adicionar(cat: Catalogo) -> None:
    origem = input("Caminho do arquivo de origem: ").strip()
    titulo = input("Título: ").strip()
    autor = input("Autor: ").strip()
    tipo = input("Tipo (artigo/tese/livro): ").strip()
    ano = input("Ano de publicação: ").strip()
    try:
        doc = cat.adicionar(
            origem=origem, titulo=titulo, autor=autor, tipo=tipo, ano=int(ano)
        )
        print(f"Documento adicionado com id {doc.id}.")
    except (FileNotFoundError, ValueError) as erro:
        print(f"Erro ao adicionar: {erro}")


def _opcao_renomear(cat: Catalogo) -> None:
    id_doc = input("Id do documento: ").strip()
    novo = input("Novo título: ").strip()
    try:
        cat.renomear(id_doc, novo_titulo=novo)
        print("Título atualizado.")
    except KeyError as erro:
        print(f"Erro: {erro}")


def _opcao_remover(cat: Catalogo) -> None:
    id_doc = input("Id do documento a remover: ").strip()
    doc = cat.obter(id_doc)
    if doc is None:
        print(f"Documento não encontrado: {id_doc}")
        return
    confirma = input(f'Remover "{doc.titulo}"? Isso apaga o arquivo. (s/n): ').strip().lower()
    if confirma == "s":
        cat.remover(id_doc)
        print("Documento removido.")
    else:
        print("Remoção cancelada.")


def _opcao_buscar(cat: Catalogo) -> None:
    termo = input("Buscar por título ou autor: ").strip()
    resultados = cat.buscar(termo)
    if not resultados:
        print("Nenhum documento encontrado.")
        return
    for doc in resultados:
        print(_linha_documento(doc))


def _opcao_ler(cat: Catalogo) -> None:
    from src.biblioteca import armazenamento

    id_doc = input("Id do documento: ").strip()
    doc = cat.obter(id_doc)
    if doc is None:
        print(f"Documento não encontrado: {id_doc}")
        return
    caminho = cat.pasta_acervo / doc.arquivo
    try:
        conteudo = armazenamento.ler_arquivo(caminho)
        print(f"--- Conteúdo de {doc.titulo} ---")
        print(conteudo[:500])  # mostra os primeiros 500 caracteres
    except (FileNotFoundError, UnicodeDecodeError) as erro:
        print(f"Não foi possível ler o arquivo: {erro}")


_ACOES = {
    "1": _opcao_listar_por_tipo,
    "2": _opcao_listar_por_ano,
    "3": _opcao_adicionar,
    "4": _opcao_renomear,
    "5": _opcao_remover,
    "6": _opcao_buscar,
    "7": _opcao_ler,
}


def executar_menu(cat: Catalogo) -> None:
    """Roda o loop do menu de contexto até o usuário escolher sair."""
    while True:
        print(MENU)
        escolha = input("Escolha: ").strip()
        if escolha == "0":
            print("Até logo!")
            break
        acao = _ACOES.get(escolha)
        if acao is None:
            print("Opção inválida. Tente novamente.")
            continue
        acao(cat)


def construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de comandos diretos (modo não interativo)."""
    parser = argparse.ArgumentParser(
        description="Sistema de gerenciamento de biblioteca digital."
    )
    sub = parser.add_subparsers(dest="comando")
    p_listar = sub.add_parser("listar", help="Lista documentos.")
    p_listar.add_argument(
        "--por", choices=["tipo", "ano"], default="tipo", help="Critério de agrupamento."
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada: comando direto se houver args, senão menu interativo."""
    raiz = Path(__file__).resolve().parents[2]
    cat = Catalogo(
        caminho_json=raiz / "catalogo.json",
        pasta_acervo=raiz / "acervo",
    )
    args = construir_parser().parse_args(argv)
    if args.comando == "listar":
        if args.por == "ano":
            print(formatar_por_ano(cat.listar_por_ano()))
        else:
            print(formatar_por_tipo(cat.listar_por_tipo()))
    else:
        executar_menu(cat)
