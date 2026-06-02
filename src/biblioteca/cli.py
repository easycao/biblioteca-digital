"""Interface de linha de comando: menu de contexto + comandos diretos.

Camada de apresentação. Funções de formatação são puras (testáveis sem input).
"""
from __future__ import annotations

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
