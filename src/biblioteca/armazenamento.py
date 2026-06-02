"""Camada de manipulação física: arquivos e diretórios.

Responsável apenas por I/O. Não conhece regras de negócio nem o catálogo.
Todas as mensagens de erro são em português.
"""
from __future__ import annotations

import shutil
from pathlib import Path


# ---------------------------------------------------------------------------
# Diretórios
# ---------------------------------------------------------------------------

def criar_diretorio(caminho: str | Path) -> Path:
    """Cria um diretório (incluindo pais). Idempotente."""
    destino = Path(caminho)
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def listar_diretorio(caminho: str | Path) -> list[str]:
    """Lista os nomes do conteúdo de um diretório."""
    pasta = Path(caminho)
    if not pasta.is_dir():
        raise FileNotFoundError(f"Diretório não encontrado: {pasta}")
    return [item.name for item in pasta.iterdir()]


def remover_diretorio(caminho: str | Path) -> None:
    """Remove um diretório e todo o seu conteúdo."""
    pasta = Path(caminho)
    if not pasta.is_dir():
        raise FileNotFoundError(f"Diretório não encontrado: {pasta}")
    shutil.rmtree(pasta)
