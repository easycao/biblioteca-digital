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


# ---------------------------------------------------------------------------
# Arquivos
# ---------------------------------------------------------------------------

def salvar_arquivo(origem: str | Path, destino: str | Path) -> Path:
    """Copia um arquivo de origem para destino (criando pastas se preciso)."""
    caminho_origem = Path(origem)
    caminho_destino = Path(destino)
    if not caminho_origem.is_file():
        raise FileNotFoundError(f"Arquivo de origem não encontrado: {caminho_origem}")
    caminho_destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(caminho_origem, caminho_destino)
    return caminho_destino


def ler_arquivo(caminho: str | Path) -> str:
    """Abre e lê o conteúdo de texto de um arquivo."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
    return arquivo.read_text(encoding="utf-8")


def renomear_arquivo(antigo: str | Path, novo: str | Path) -> Path:
    """Renomeia/move um arquivo. Falha se o destino já existir."""
    caminho_antigo = Path(antigo)
    caminho_novo = Path(novo)
    if not caminho_antigo.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_antigo}")
    if caminho_novo.exists():
        raise FileExistsError(f"Já existe um arquivo com esse nome: {caminho_novo}")
    caminho_antigo.rename(caminho_novo)
    return caminho_novo


def remover_arquivo(caminho: str | Path) -> None:
    """Remove um arquivo do disco."""
    arquivo = Path(caminho)
    if not arquivo.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")
    arquivo.unlink()


def arquivo_existe(caminho: str | Path) -> bool:
    """Retorna True se o arquivo existir."""
    return Path(caminho).is_file()
