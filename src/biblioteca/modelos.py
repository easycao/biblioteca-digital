"""Modelo de dados do documento digital."""
from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class Documento:
    """Representa um documento digital do acervo."""

    id: str
    titulo: str
    autor: str
    tipo: str       # "artigo" | "tese" | "livro"
    ano: int
    formato: str    # "pdf" | "epub" | "txt" | ...
    arquivo: str    # nome do arquivo correspondente em acervo/
    adicionado_em: str  # timestamp ISO

    @classmethod
    def novo(
        cls,
        titulo: str,
        autor: str,
        tipo: str,
        ano: int,
        formato: str,
        arquivo: str,
    ) -> "Documento":
        """Cria um documento novo, gerando id e timestamp automaticamente."""
        return cls(
            id=uuid.uuid4().hex[:8],
            titulo=titulo,
            autor=autor,
            tipo=tipo,
            ano=ano,
            formato=formato,
            arquivo=arquivo,
            adicionado_em=datetime.now().isoformat(timespec="seconds"),
        )

    def para_dict(self) -> dict:
        """Converte o documento em dicionário (para serializar em JSON)."""
        return asdict(self)

    @classmethod
    def de_dict(cls, dados: dict) -> "Documento":
        """Reconstrói um documento a partir de um dicionário."""
        return cls(**dados)
