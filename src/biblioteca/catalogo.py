"""Catálogo de metadados dos documentos.

Mantém o índice em catalogo.json sincronizado com os arquivos reais no acervo.
Delega toda a manipulação física ao módulo `armazenamento`.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.biblioteca import armazenamento
from src.biblioteca.modelos import Documento


class Catalogo:
    """Gerencia os metadados dos documentos e os mantém em sincronia com o disco."""

    def __init__(self, caminho_json: str | Path, pasta_acervo: str | Path) -> None:
        self.caminho_json = Path(caminho_json)
        self.pasta_acervo = Path(pasta_acervo)
        self._documentos: list[Documento] = []
        self._carregar()

    # -- persistência -------------------------------------------------------

    def _carregar(self) -> None:
        """Carrega os documentos do arquivo JSON, se existir."""
        if self.caminho_json.is_file():
            dados = json.loads(self.caminho_json.read_text(encoding="utf-8"))
            self._documentos = [Documento.de_dict(d) for d in dados.get("documentos", [])]
        else:
            self._documentos = []

    def _salvar(self) -> None:
        """Grava os documentos no arquivo JSON."""
        self.caminho_json.parent.mkdir(parents=True, exist_ok=True)
        dados = {"documentos": [d.para_dict() for d in self._documentos]}
        self.caminho_json.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # -- consultas ----------------------------------------------------------

    def listar(self) -> list[Documento]:
        """Retorna todos os documentos do catálogo."""
        return list(self._documentos)

    def listar_por_tipo(self) -> dict[str, list[Documento]]:
        """Agrupa os documentos por tipo (artigo/tese/livro)."""
        grupos: dict[str, list[Documento]] = {}
        for doc in self._documentos:
            grupos.setdefault(doc.tipo, []).append(doc)
        return grupos

    def listar_por_ano(self) -> dict[int, list[Documento]]:
        """Agrupa os documentos por ano de publicação."""
        grupos: dict[int, list[Documento]] = {}
        for doc in self._documentos:
            grupos.setdefault(doc.ano, []).append(doc)
        return grupos

    def buscar(self, termo: str) -> list[Documento]:
        """Busca documentos por título ou autor (case-insensitive)."""
        alvo = termo.lower()
        return [
            doc
            for doc in self._documentos
            if alvo in doc.titulo.lower() or alvo in doc.autor.lower()
        ]

    # -- operações ----------------------------------------------------------

    def adicionar(
        self,
        origem: str | Path,
        titulo: str,
        autor: str,
        tipo: str,
        ano: int,
    ) -> Documento:
        """Adiciona um documento: copia o arquivo ao acervo e registra os metadados."""
        caminho_origem = Path(origem)
        if not caminho_origem.is_file():
            raise FileNotFoundError(f"Arquivo de origem não encontrado: {caminho_origem}")

        formato = caminho_origem.suffix.lstrip(".").lower()
        # Cria o documento com nome de arquivo provisório; depois aplica prefixo de id único.
        doc = Documento.novo(
            titulo=titulo,
            autor=autor,
            tipo=tipo,
            ano=ano,
            formato=formato,
            arquivo=caminho_origem.name,
        )
        # Prefixo de id evita colisão entre arquivos de mesmo nome no acervo.
        doc.arquivo = f"{doc.id}_{caminho_origem.name}"
        destino = self.pasta_acervo / doc.arquivo
        armazenamento.salvar_arquivo(caminho_origem, destino)
        self._documentos.append(doc)
        self._salvar()
        return doc
