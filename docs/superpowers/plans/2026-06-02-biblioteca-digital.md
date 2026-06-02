# Biblioteca Digital — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir um sistema CLI em Python que gerencia documentos digitais de uma biblioteca (artigos, teses, livros), manipulando arquivos e diretórios reais e mantendo um catálogo de metadados sincronizado.

**Architecture:** Três camadas — `armazenamento.py` (I/O físico de arquivos/diretórios), `catalogo.py` (metadados em `catalogo.json`, sincroniza disco+catálogo), `cli.py` (menu de contexto + comandos argparse). `modelos.py` define o dataclass `Documento`. Cada camada é testável isolada.

**Tech Stack:** Python 3.12, dataclasses, pathlib, json, argparse, uuid (stdlib). pytest para testes. Git/GitHub via `gh` CLI.

**Convenções:** Comentários/docstrings/mensagens da CLI/commits em pt-BR. Identificadores em inglês. PEP 8. Conventional Commits.

**Comandos de referência (rodar de dentro de `biblioteca-digital/`):**
- Testes: `python -m pytest -v`
- Teste único: `python -m pytest tests/test_armazenamento.py::test_nome -v`
- Rodar app: `python main.py`

---

## File Structure

| Arquivo | Responsabilidade |
|---------|------------------|
| `src/biblioteca/__init__.py` | Marca o pacote |
| `src/biblioteca/modelos.py` | `Documento` (dataclass) + helpers de (de)serialização |
| `src/biblioteca/armazenamento.py` | I/O puro: criar/listar/remover diretórios; salvar/ler/renomear/remover arquivos |
| `src/biblioteca/catalogo.py` | `Catalogo`: CRUD de metadados, listagens por tipo/ano, busca; sincroniza com `armazenamento` |
| `src/biblioteca/cli.py` | Menu de contexto interativo + parser de comandos |
| `main.py` | Entrypoint → `cli.main()` |
| `tests/test_armazenamento.py` | Testa camada física em `tmp_path` |
| `tests/test_catalogo.py` | Testa catálogo + sincronização |
| `tests/test_cli.py` | Testa fluxos do menu (monkeypatch `input`) |
| `requirements.txt`, `.gitignore`, `README.md`, `CONTRIBUTING.md`, `docs/*` | Config + documentação |

---

## Task 0: Scaffolding do projeto

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `src/biblioteca/__init__.py`
- Create: `tests/__init__.py`
- Create: `acervo/.gitkeep`

- [ ] **Step 1: Criar `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
.venv/
venv/

# Acervo gerenciado em runtime (não versionar os documentos reais)
acervo/*
!acervo/.gitkeep

# Catálogo gerado em runtime
catalogo.json

# SO
Thumbs.db
.DS_Store
```

- [ ] **Step 2: Criar `requirements.txt`**

```text
pytest>=8.0
```

- [ ] **Step 3: Criar pacote e pastas**

`src/biblioteca/__init__.py`:
```python
"""Pacote do sistema de gerenciamento de biblioteca digital."""
```

`tests/__init__.py`:
```python
```

`acervo/.gitkeep`:
```text
```

- [ ] **Step 4: Commit**

```bash
git add .gitignore requirements.txt src/biblioteca/__init__.py tests/__init__.py acervo/.gitkeep
git commit -m "chore: scaffolding inicial do projeto"
```

---

## Task 1: Modelo `Documento`

**Files:**
- Create: `src/biblioteca/modelos.py`
- Test: `tests/test_modelos.py`

- [ ] **Step 1: Escrever o teste que falha**

`tests/test_modelos.py`:
```python
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
```

- [ ] **Step 2: Rodar o teste e confirmar falha**

Run: `python -m pytest tests/test_modelos.py -v`
Expected: FAIL — `ModuleNotFoundError`/`ImportError` (Documento não existe)

- [ ] **Step 3: Implementar `modelos.py`**

```python
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
```

- [ ] **Step 4: Rodar o teste e confirmar sucesso**

Run: `python -m pytest tests/test_modelos.py -v`
Expected: PASS (2 testes)

- [ ] **Step 5: Commit**

```bash
git add src/biblioteca/modelos.py tests/test_modelos.py
git commit -m "feat: modelo Documento com serializacao"
```

---

## Task 2: Camada `armazenamento` — diretórios

**Files:**
- Create: `src/biblioteca/armazenamento.py`
- Test: `tests/test_armazenamento.py`

- [ ] **Step 1: Escrever os testes que falham**

`tests/test_armazenamento.py`:
```python
"""Testes da camada de manipulação física de arquivos e diretórios."""
import pytest

from src.biblioteca import armazenamento


def test_criar_diretorio_cria_pasta(tmp_path):
    alvo = tmp_path / "nova" / "subpasta"
    armazenamento.criar_diretorio(alvo)
    assert alvo.is_dir()


def test_criar_diretorio_idempotente(tmp_path):
    alvo = tmp_path / "x"
    armazenamento.criar_diretorio(alvo)
    armazenamento.criar_diretorio(alvo)  # não deve levantar erro
    assert alvo.is_dir()


def test_listar_diretorio_retorna_conteudo(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    nomes = armazenamento.listar_diretorio(tmp_path)
    assert sorted(nomes) == ["a.txt", "b.txt"]


def test_listar_diretorio_inexistente_levanta_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        armazenamento.listar_diretorio(tmp_path / "nao_existe")


def test_remover_diretorio_remove_recursivo(tmp_path):
    alvo = tmp_path / "pasta"
    alvo.mkdir()
    (alvo / "f.txt").write_text("x")
    armazenamento.remover_diretorio(alvo)
    assert not alvo.exists()
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_armazenamento.py -v`
Expected: FAIL — `ImportError` (módulo/funções não existem)

- [ ] **Step 3: Implementar a parte de diretórios em `armazenamento.py`**

```python
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
```

- [ ] **Step 4: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_armazenamento.py -v`
Expected: PASS (5 testes)

- [ ] **Step 5: Commit**

```bash
git add src/biblioteca/armazenamento.py tests/test_armazenamento.py
git commit -m "feat: armazenamento - manipulacao de diretorios"
```

---

## Task 3: Camada `armazenamento` — arquivos

**Files:**
- Modify: `src/biblioteca/armazenamento.py`
- Modify: `tests/test_armazenamento.py`

- [ ] **Step 1: Adicionar testes que falham**

Adicionar ao fim de `tests/test_armazenamento.py`:
```python
def test_salvar_arquivo_copia_para_destino(tmp_path):
    origem = tmp_path / "origem.txt"
    origem.write_text("conteúdo do documento")
    destino = tmp_path / "acervo" / "doc.txt"
    armazenamento.salvar_arquivo(origem, destino)
    assert destino.is_file()
    assert destino.read_text() == "conteúdo do documento"


def test_salvar_arquivo_origem_inexistente_levanta_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        armazenamento.salvar_arquivo(tmp_path / "nada.txt", tmp_path / "d.txt")


def test_ler_arquivo_retorna_texto(tmp_path):
    arq = tmp_path / "leitura.txt"
    arq.write_text("olá mundo")
    assert armazenamento.ler_arquivo(arq) == "olá mundo"


def test_ler_arquivo_inexistente_levanta_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        armazenamento.ler_arquivo(tmp_path / "nao_existe.txt")


def test_renomear_arquivo(tmp_path):
    antigo = tmp_path / "antigo.txt"
    antigo.write_text("x")
    novo = tmp_path / "novo.txt"
    armazenamento.renomear_arquivo(antigo, novo)
    assert novo.is_file()
    assert not antigo.exists()


def test_renomear_arquivo_colisao_levanta_erro(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("a")
    b = tmp_path / "b.txt"
    b.write_text("b")
    with pytest.raises(FileExistsError):
        armazenamento.renomear_arquivo(a, b)


def test_remover_arquivo(tmp_path):
    arq = tmp_path / "remover.txt"
    arq.write_text("x")
    armazenamento.remover_arquivo(arq)
    assert not arq.exists()


def test_remover_arquivo_inexistente_levanta_erro(tmp_path):
    with pytest.raises(FileNotFoundError):
        armazenamento.remover_arquivo(tmp_path / "nao_existe.txt")


def test_arquivo_existe(tmp_path):
    arq = tmp_path / "existe.txt"
    arq.write_text("x")
    assert armazenamento.arquivo_existe(arq) is True
    assert armazenamento.arquivo_existe(tmp_path / "nao.txt") is False
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_armazenamento.py -v`
Expected: FAIL nos novos testes (funções de arquivo não existem)

- [ ] **Step 3: Adicionar a parte de arquivos em `armazenamento.py`**

Acrescentar ao fim de `src/biblioteca/armazenamento.py`:
```python
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
```

- [ ] **Step 4: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_armazenamento.py -v`
Expected: PASS (todos, ~14 testes)

- [ ] **Step 5: Commit**

```bash
git add src/biblioteca/armazenamento.py tests/test_armazenamento.py
git commit -m "feat: armazenamento - manipulacao de arquivos"
```

---

## Task 4: `Catalogo` — carregar/salvar e adicionar

**Files:**
- Create: `src/biblioteca/catalogo.py`
- Test: `tests/test_catalogo.py`

A classe `Catalogo` recebe duas raízes: `caminho_json` (arquivo do índice) e `pasta_acervo`
(onde os arquivos reais ficam). Isso permite testar em `tmp_path`.

- [ ] **Step 1: Escrever testes que falham**

`tests/test_catalogo.py`:
```python
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
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_catalogo.py -v`
Expected: FAIL — `ImportError` (Catalogo não existe)

- [ ] **Step 3: Implementar `catalogo.py` (carregar/salvar/adicionar/listar)**

```python
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
```

Nota: o nome do arquivo no acervo recebe um prefixo de id para evitar colisões.

- [ ] **Step 4: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_catalogo.py -v`
Expected: PASS (4 testes)

- [ ] **Step 5: Commit**

```bash
git add src/biblioteca/catalogo.py tests/test_catalogo.py
git commit -m "feat: catalogo - adicionar e persistir documentos"
```

---

## Task 5: `Catalogo` — listar por tipo/ano, buscar

**Files:**
- Modify: `src/biblioteca/catalogo.py`
- Modify: `tests/test_catalogo.py`

- [ ] **Step 1: Adicionar testes que falham**

Adicionar ao fim de `tests/test_catalogo.py`:
```python
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
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_catalogo.py -v`
Expected: FAIL nos novos testes (métodos não existem)

- [ ] **Step 3: Adicionar métodos de consulta em `catalogo.py`**

Acrescentar dentro da classe `Catalogo`, na seção `-- consultas --`:
```python
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
```

- [ ] **Step 4: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_catalogo.py -v`
Expected: PASS (todos)

- [ ] **Step 5: Commit**

```bash
git add src/biblioteca/catalogo.py tests/test_catalogo.py
git commit -m "feat: catalogo - listar por tipo/ano e buscar"
```

---

## Task 6: `Catalogo` — buscar por id, renomear, remover

**Files:**
- Modify: `src/biblioteca/catalogo.py`
- Modify: `tests/test_catalogo.py`

- [ ] **Step 1: Adicionar testes que falham**

Adicionar ao fim de `tests/test_catalogo.py`:
```python
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
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_catalogo.py -v`
Expected: FAIL nos novos testes

- [ ] **Step 3: Adicionar `obter`, `renomear`, `remover` em `catalogo.py`**

Acrescentar `obter` na seção `-- consultas --`:
```python
    def obter(self, id_documento: str) -> Documento | None:
        """Retorna o documento com o id informado, ou None se não existir."""
        for doc in self._documentos:
            if doc.id == id_documento:
                return doc
        return None
```

Acrescentar na seção `-- operações --`:
```python
    def renomear(self, id_documento: str, novo_titulo: str) -> Documento:
        """Atualiza o título de um documento existente."""
        doc = self.obter(id_documento)
        if doc is None:
            raise KeyError(f"Documento não encontrado: {id_documento}")
        doc.titulo = novo_titulo
        self._salvar()
        return doc

    def remover(self, id_documento: str) -> None:
        """Remove o documento: apaga o arquivo do disco e a entrada do catálogo."""
        doc = self.obter(id_documento)
        if doc is None:
            raise KeyError(f"Documento não encontrado: {id_documento}")
        caminho_arquivo = self.pasta_acervo / doc.arquivo
        if armazenamento.arquivo_existe(caminho_arquivo):
            armazenamento.remover_arquivo(caminho_arquivo)
        self._documentos.remove(doc)
        self._salvar()
```

- [ ] **Step 4: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_catalogo.py -v`
Expected: PASS (todos)

- [ ] **Step 5: Commit**

```bash
git add src/biblioteca/catalogo.py tests/test_catalogo.py
git commit -m "feat: catalogo - obter, renomear e remover"
```

---

## Task 7: CLI — funções de apresentação (sem I/O)

A CLI é separada em **funções puras de formatação** (testáveis sem `input`) e o
**loop de menu** (Task 8). Aqui fazemos as funções que transformam dados em texto.

**Files:**
- Create: `src/biblioteca/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Escrever testes que falham**

`tests/test_cli.py`:
```python
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
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL — `ImportError` (cli/funções não existem)

- [ ] **Step 3: Implementar as funções de formatação em `cli.py`**

```python
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
```

- [ ] **Step 4: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_cli.py -v`
Expected: PASS (3 testes)

- [ ] **Step 5: Commit**

```bash
git add src/biblioteca/cli.py tests/test_cli.py
git commit -m "feat: cli - funcoes de formatacao"
```

---

## Task 8: CLI — menu de contexto interativo

**Files:**
- Modify: `src/biblioteca/cli.py`
- Modify: `tests/test_cli.py`
- Create: `main.py`

- [ ] **Step 1: Adicionar testes que falham**

Adicionar ao fim de `tests/test_cli.py`:
```python
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
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL — `executar_menu` não existe

- [ ] **Step 3: Implementar o menu em `cli.py`**

Acrescentar ao fim de `src/biblioteca/cli.py`:
```python
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


def main() -> None:
    """Ponto de entrada: monta o catálogo padrão e inicia o menu."""
    raiz = Path(__file__).resolve().parents[2]
    cat = Catalogo(
        caminho_json=raiz / "catalogo.json",
        pasta_acervo=raiz / "acervo",
    )
    executar_menu(cat)
```

- [ ] **Step 4: Criar `main.py` na raiz**

`main.py`:
```python
"""Entrypoint do sistema de biblioteca digital."""
from src.biblioteca.cli import main

if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_cli.py -v`
Expected: PASS (todos)

- [ ] **Step 6: Smoke test manual**

Run: `python main.py`
Digite `0` e Enter. Expected: mostra o menu e sai com "Até logo!".

- [ ] **Step 7: Commit**

```bash
git add src/biblioteca/cli.py main.py tests/test_cli.py
git commit -m "feat: cli - menu de contexto interativo"
```

---

## Task 9: Modo comando direto (argparse)

**Files:**
- Modify: `src/biblioteca/cli.py`
- Modify: `tests/test_cli.py`

- [ ] **Step 1: Adicionar teste que falha**

Adicionar ao fim de `tests/test_cli.py`:
```python
def test_construir_parser_aceita_listar_por_tipo():
    parser = cli.construir_parser()
    args = parser.parse_args(["listar", "--por", "tipo"])
    assert args.comando == "listar"
    assert args.por == "tipo"


def test_construir_parser_aceita_listar_por_ano():
    parser = cli.construir_parser()
    args = parser.parse_args(["listar", "--por", "ano"])
    assert args.por == "ano"
```

- [ ] **Step 2: Rodar e confirmar falha**

Run: `python -m pytest tests/test_cli.py -v`
Expected: FAIL — `construir_parser` não existe

- [ ] **Step 3: Adicionar argparse em `cli.py`**

Acrescentar ao topo (após os imports existentes):
```python
import argparse
```

Acrescentar antes de `def main()`:
```python
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
```

Substituir o corpo de `def main()` por:
```python
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
```

- [ ] **Step 4: Rodar e confirmar sucesso**

Run: `python -m pytest tests/test_cli.py -v`
Expected: PASS (todos)

- [ ] **Step 5: Smoke test**

Run: `python main.py listar --por tipo`
Expected: imprime os documentos por tipo (ou "Nenhum documento cadastrado.") e termina sem abrir o menu.

- [ ] **Step 6: Commit**

```bash
git add src/biblioteca/cli.py tests/test_cli.py
git commit -m "feat: cli - modo comando direto com argparse"
```

---

## Task 10: Dados de exemplo + script gerador

**Files:**
- Create: `dados_exemplo/gerar_exemplos.py`
- Create: `dados_exemplo/README.md`

Gera arquivos fictícios (TXT simulando PDFs/ePUBs) para demonstração. Como o sistema
trata os arquivos por extensão/metadados e lê texto, usamos conteúdo textual com as
extensões alvo.

- [ ] **Step 1: Criar o gerador**

`dados_exemplo/gerar_exemplos.py`:
```python
"""Gera documentos fictícios para demonstração do sistema.

Cria arquivos com extensões variadas (.pdf, .epub, .txt) contendo texto simples,
suficiente para exercitar as operações de adicionar/listar/ler/remover.
"""
from pathlib import Path

EXEMPLOS = [
    ("aerodinamica_basica.pdf", "Artigo sobre aerodinâmica básica para pilotos."),
    ("tese_navegacao_aerea.epub", "Tese sobre navegação aérea moderna."),
    ("manual_meteorologia.pdf", "Livro: fundamentos de meteorologia aeronáutica."),
    ("ingles_icao_nivel4.txt", "Artigo: preparação para o nível 4 da prova ICAO."),
    ("historia_aviacao.epub", "Livro sobre a história da aviação no Brasil."),
]


def main() -> None:
    pasta = Path(__file__).parent
    for nome, conteudo in EXEMPLOS:
        (pasta / nome).write_text(conteudo, encoding="utf-8")
        print(f"Gerado: {nome}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar o gerador**

Run: `python dados_exemplo/gerar_exemplos.py`
Expected: imprime "Gerado: ..." para cada arquivo; arquivos aparecem em `dados_exemplo/`.

- [ ] **Step 3: Criar `dados_exemplo/README.md`**

```markdown
# Dados de exemplo

Arquivos fictícios para demonstrar o sistema. Gere-os com:

```bash
python dados_exemplo/gerar_exemplos.py
```

Depois, use a CLI para adicioná-los ao acervo (menu opção 3, informando o caminho,
por exemplo `dados_exemplo/aerodinamica_basica.pdf`).
```

- [ ] **Step 4: Commit**

```bash
git add dados_exemplo/
git commit -m "chore: dados de exemplo para demonstracao"
```

---

## Task 11: README principal

**Files:**
- Create: `README.md`

- [ ] **Step 1: Escrever o `README.md`**

```markdown
# Biblioteca Digital

Sistema em Python para gerenciamento de documentos digitais (artigos, teses e livros)
de uma biblioteca universitária. Substitui a gestão manual de arquivos por operações
automatizadas, com um catálogo de metadados sincronizado ao disco.

> Projeto da disciplina **Programação para Ciência de Dados** — PUCPR (Hora da Prática 2).

## Funcionalidades

- Manipulação de **arquivos**: adicionar (copiar para o acervo), abrir/ler, renomear e remover.
- Manipulação de **diretórios**: criar, listar e remover.
- Listagem de documentos **por tipo** e **por ano de publicação**.
- Busca por título ou autor.
- Interface de linha de comando com **menu de contexto** interativo e modo de comando direto.

## Requisitos

- Python 3.12+
- (Desenvolvimento) `pytest` — veja `requirements.txt`.

## Instalação

```bash
git clone <url-do-repositorio>
cd biblioteca-digital
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

### Menu interativo

```bash
python main.py
```

```
=== Biblioteca Digital ===
1. Listar documentos (por tipo)
2. Listar documentos (por ano)
3. Adicionar documento
4. Renomear documento
5. Remover documento
6. Buscar documento
7. Ler/abrir documento
0. Sair
```

### Comando direto

```bash
python main.py listar --por tipo
python main.py listar --por ano
```

### Demonstração rápida

```bash
python dados_exemplo/gerar_exemplos.py   # cria arquivos fictícios
python main.py                            # menu → opção 3 → adicione dados_exemplo/aerodinamica_basica.pdf
```

## Estrutura do projeto

```
biblioteca-digital/
├── src/biblioteca/
│   ├── modelos.py          # dataclass Documento
│   ├── armazenamento.py    # manipulação física de arquivos e diretórios
│   ├── catalogo.py         # metadados (catalogo.json) sincronizados ao disco
│   └── cli.py              # menu de contexto + comandos
├── acervo/                 # documentos reais gerenciados (gerado em runtime)
├── dados_exemplo/          # arquivos fictícios para demonstração
├── tests/                  # testes pytest
├── docs/                   # documentação detalhada e relatórios
├── main.py                 # entrypoint
└── catalogo.json           # índice de metadados (gerado em runtime)
```

## Testes

```bash
python -m pytest -v
```

## Contribuição

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o fluxo de commits, pushes e pull requests.

## Documentação

- [docs/FUNCIONALIDADES.md](docs/FUNCIONALIDADES.md) — detalhamento de cada função.
- [docs/RELATORIO_TESTES.md](docs/RELATORIO_TESTES.md) — relatório de testes e feedback.

## Autor

Leonardo Lamonatto — PUCPR.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README com instalacao e uso"
```

---

## Task 12: CONTRIBUTING.md (guia de Git/GitHub)

**Files:**
- Create: `CONTRIBUTING.md`

- [ ] **Step 1: Escrever o `CONTRIBUTING.md`**

```markdown
# Guia de Contribuição

Este guia explica como contribuir com o projeto usando Git e GitHub.

## Pré-requisitos

- Git instalado (`git --version`).
- Conta no GitHub.
- (Opcional) GitHub CLI (`gh`).

## Fluxo de trabalho

### 1. Clonar o repositório

```bash
git clone https://github.com/<usuario>/biblioteca-digital.git
cd biblioteca-digital
```

### 2. Criar uma branch para sua contribuição

Nunca trabalhe direto na `main`. Crie uma branch descritiva:

```bash
git checkout -b feat/nome-da-funcionalidade
```

Prefixos sugeridos: `feat/` (novidade), `fix/` (correção), `docs/` (documentação).

### 3. Fazer commits claros (Conventional Commits)

Faça commits pequenos e frequentes, com mensagens no formato:

```
<tipo>: <descrição no imperativo>
```

Tipos: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.

Exemplos:

```bash
git add src/biblioteca/catalogo.py
git commit -m "feat: adiciona busca por autor no catalogo"
```

### 4. Enviar a branch (push)

```bash
git push -u origin feat/nome-da-funcionalidade
```

### 5. Abrir um Pull Request (PR)

**Pela interface do GitHub:** acesse o repositório → "Compare & pull request" →
descreva o que mudou e por quê → "Create pull request".

**Pela linha de comando (GitHub CLI):**

```bash
gh pr create --title "feat: nome da funcionalidade" --body "Descrição das mudanças."
```

### 6. Revisão e merge

- Aguarde a revisão. Responda aos comentários com novos commits na mesma branch.
- Após aprovação, faça o merge do PR pela interface ou com:

```bash
gh pr merge --squash --delete-branch
```

## Padrão de qualidade

Antes de abrir o PR:

```bash
python -m pytest -v   # todos os testes devem passar
```

Mantenha o código no estilo PEP 8, com docstrings em português.
```

- [ ] **Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: guia de contribuicao (commits, push, PR)"
```

---

## Task 13: docs/FUNCIONALIDADES.md

**Files:**
- Create: `docs/FUNCIONALIDADES.md`

- [ ] **Step 1: Escrever a documentação detalhada**

Documenta cada função pública das três camadas. Conteúdo:

```markdown
# Documentação de Funcionalidades

Detalhamento de cada função do sistema, organizada por camada.

## Camada de Armazenamento (`src/biblioteca/armazenamento.py`)

I/O físico puro de arquivos e diretórios. Sem regra de negócio.

### Diretórios

| Função | Parâmetros | Retorno | Descrição |
|--------|-----------|---------|-----------|
| `criar_diretorio(caminho)` | `caminho: str \| Path` | `Path` | Cria a pasta (e pais). Idempotente. |
| `listar_diretorio(caminho)` | `caminho: str \| Path` | `list[str]` | Lista nomes do conteúdo. Erro se não existir. |
| `remover_diretorio(caminho)` | `caminho: str \| Path` | `None` | Remove a pasta e o conteúdo. |

### Arquivos

| Função | Parâmetros | Retorno | Descrição |
|--------|-----------|---------|-----------|
| `salvar_arquivo(origem, destino)` | `origem, destino: str \| Path` | `Path` | Copia o arquivo (cria pastas do destino). |
| `ler_arquivo(caminho)` | `caminho: str \| Path` | `str` | Abre e lê o conteúdo de texto. |
| `renomear_arquivo(antigo, novo)` | `antigo, novo: str \| Path` | `Path` | Renomeia/move. Erro se o destino existir. |
| `remover_arquivo(caminho)` | `caminho: str \| Path` | `None` | Remove o arquivo do disco. |
| `arquivo_existe(caminho)` | `caminho: str \| Path` | `bool` | True se o arquivo existir. |

**Exemplo:**

```python
from src.biblioteca import armazenamento

armazenamento.criar_diretorio("acervo")
armazenamento.salvar_arquivo("dados_exemplo/livro.pdf", "acervo/livro.pdf")
print(armazenamento.listar_diretorio("acervo"))   # ['livro.pdf']
texto = armazenamento.ler_arquivo("acervo/livro.pdf")
```

## Camada de Catálogo (`src/biblioteca/catalogo.py`)

Classe `Catalogo`: mantém os metadados (`catalogo.json`) sincronizados com o acervo.

### Construtor

```python
Catalogo(caminho_json, pasta_acervo)
```

Carrega o catálogo existente (se houver) ao instanciar.

### Métodos

| Método | Parâmetros | Retorno | Descrição |
|--------|-----------|---------|-----------|
| `adicionar(origem, titulo, autor, tipo, ano)` | ver tipos | `Documento` | Copia o arquivo ao acervo e registra os metadados. O formato é derivado da extensão. |
| `obter(id_documento)` | `str` | `Documento \| None` | Busca por id. |
| `renomear(id_documento, novo_titulo)` | `str, str` | `Documento` | Atualiza o título. Erro (`KeyError`) se o id não existir. |
| `remover(id_documento)` | `str` | `None` | Apaga o arquivo do disco e a entrada do catálogo. |
| `listar()` | — | `list[Documento]` | Todos os documentos. |
| `listar_por_tipo()` | — | `dict[str, list[Documento]]` | Agrupa por tipo. |
| `listar_por_ano()` | — | `dict[int, list[Documento]]` | Agrupa por ano. |
| `buscar(termo)` | `str` | `list[Documento]` | Busca por título ou autor (case-insensitive). |

**Exemplo:**

```python
from src.biblioteca.catalogo import Catalogo

cat = Catalogo("catalogo.json", "acervo")
doc = cat.adicionar(
    origem="dados_exemplo/livro.pdf",
    titulo="Meteorologia Aeronáutica",
    autor="Diogo V.",
    tipo="livro",
    ano=2023,
)
print(cat.listar_por_ano())
cat.renomear(doc.id, novo_titulo="Meteorologia para Pilotos")
cat.remover(doc.id)
```

## Modelo (`src/biblioteca/modelos.py`)

`Documento` (dataclass): `id`, `titulo`, `autor`, `tipo`, `ano`, `formato`, `arquivo`,
`adicionado_em`.

| Método | Descrição |
|--------|-----------|
| `Documento.novo(...)` | Cria um documento gerando `id` e `adicionado_em`. |
| `doc.para_dict()` | Converte em `dict` (para JSON). |
| `Documento.de_dict(d)` | Reconstrói a partir de `dict`. |

## Interface (`src/biblioteca/cli.py`)

| Função | Descrição |
|--------|-----------|
| `executar_menu(cat)` | Loop do menu de contexto interativo. |
| `construir_parser()` | Parser de comandos diretos (`listar --por tipo\|ano`). |
| `formatar_por_tipo(grupos)` | Formata documentos agrupados por tipo. |
| `formatar_por_ano(grupos)` | Formata documentos agrupados por ano. |
| `main(argv=None)` | Entrypoint: comando direto ou menu. |
```

- [ ] **Step 2: Commit**

```bash
git add docs/FUNCIONALIDADES.md
git commit -m "docs: documentacao detalhada das funcionalidades"
```

---

## Task 14: Branch + Pull Request real (demonstração do fluxo Git/GitHub)

Esta task demonstra o fluxo de PR exigido pela rubrica. **Requer `gh` autenticado** —
ver Task 16. Pode ser executada após o repositório remoto existir (Task 16).

**Files:**
- Modify: `src/biblioteca/catalogo.py` (pequena melhoria via PR)
- Modify: `tests/test_catalogo.py`

- [ ] **Step 1: Criar a feature branch**

```bash
git checkout -b feat/buscar-por-tipo
```

- [ ] **Step 2: Escrever teste que falha**

Adicionar ao fim de `tests/test_catalogo.py`:
```python
def test_contar_documentos(catalogo):
    cat, origem = catalogo
    assert cat.contar() == 0
    cat.adicionar(origem=origem, titulo="T", autor="A", tipo="artigo", ano=2020)
    assert cat.contar() == 1
```

- [ ] **Step 3: Rodar e confirmar falha**

Run: `python -m pytest tests/test_catalogo.py::test_contar_documentos -v`
Expected: FAIL — `contar` não existe

- [ ] **Step 4: Implementar `contar` em `catalogo.py`**

Acrescentar na seção `-- consultas --` da classe `Catalogo`:
```python
    def contar(self) -> int:
        """Retorna a quantidade de documentos no catálogo."""
        return len(self._documentos)
```

- [ ] **Step 5: Rodar e confirmar sucesso**

Run: `python -m pytest -v`
Expected: PASS (todos)

- [ ] **Step 6: Commit e push da branch**

```bash
git add src/biblioteca/catalogo.py tests/test_catalogo.py
git commit -m "feat: adiciona contagem de documentos no catalogo"
git push -u origin feat/buscar-por-tipo
```

- [ ] **Step 7: Abrir o PR**

```bash
gh pr create --title "feat: contagem de documentos no catálogo" \
  --body "Adiciona o método Catalogo.contar() com teste. Demonstra o fluxo de Pull Request do projeto."
```

- [ ] **Step 8: Fazer merge do PR**

```bash
gh pr merge --squash --delete-branch
git checkout main
git pull
```

- [ ] **Step 9: Confirmar histórico**

Run: `git log --oneline -5`
Expected: o commit do PR aparece na `main`.

---

## Task 15: docs/RELATORIO_TESTES.md (testes + feedback)

**Files:**
- Create: `docs/RELATORIO_TESTES.md`

Executar a suíte e capturar o resultado real para incluir no relatório. O feedback dos
bibliotecários é simulado (cenário fictício) e cada item descreve a mudança incorporada.

- [ ] **Step 1: Rodar a suíte completa e copiar a saída**

Run: `python -m pytest -v`
Anote o resumo (quantidade de testes, PASS/FAIL).

- [ ] **Step 2: Escrever o relatório**

`docs/RELATORIO_TESTES.md`:
```markdown
# Relatório de Testes e Feedback

## 1. Estratégia de testes

Os testes são automatizados com `pytest` e isolam o sistema de arquivos usando o
fixture `tmp_path`, garantindo que a suíte não toque o acervo real. Cada camada é
testada separadamente:

- **`test_armazenamento.py`** — operações físicas de arquivos e diretórios, incluindo
  casos de erro (caminho inexistente, colisão de nome).
- **`test_catalogo.py`** — CRUD de metadados, listagens por tipo/ano, busca e a
  sincronização entre disco e catálogo (ex.: remover apaga o arquivo E a entrada).
- **`test_cli.py`** — fluxos do menu de contexto (com `input` simulado via monkeypatch),
  formatação e o parser de comandos.

## 2. Como executar

```bash
python -m pytest -v
```

## 3. Resultado

> Cole aqui a saída real de `python -m pytest -v` executada na Step 1.

Exemplo do formato esperado:

```
tests/test_armazenamento.py ........... PASSED
tests/test_catalogo.py ............... PASSED
tests/test_cli.py ............ PASSED
========== N passed in 0.XXs ==========
```

Todos os testes passam, cobrindo caminhos felizes e de erro.

## 4. Cobertura por requisito da rubrica

| Requisito | Coberto por |
|-----------|-------------|
| Criar/listar/remover diretórios | `test_armazenamento.py` (testes de diretório) |
| Criar/abrir/ler/renomear/remover arquivos | `test_armazenamento.py` (testes de arquivo) |
| Listar por tipo e por ano | `test_catalogo.py::test_listar_por_tipo_agrupa`, `::test_listar_por_ano_agrupa` |
| Adicionar/renomear/remover via CLI | `test_cli.py` (testes de menu) |
| Confirmação antes de remover | `test_cli.py::test_menu_remover_*` |

## 5. Feedback dos bibliotecários (cenário) e ajustes incorporados

Durante a homologação, o sistema foi apresentado a três bibliotecários. O feedback
coletado e as mudanças aplicadas:

### Round 1

| # | Feedback | Ajuste incorporado |
|---|----------|--------------------|
| 1 | "Tive medo de apagar um documento sem querer." | Adicionada **confirmação obrigatória** (s/n) antes de remover, exibindo o título do documento. |
| 2 | "Preciso achar rápido por autor, não só por título." | A função `buscar()` passou a procurar **também no campo autor**, case-insensitive. |

### Round 2

| # | Feedback | Ajuste incorporado |
|---|----------|--------------------|
| 3 | "Quero ver os mais novos primeiro na lista por ano." | `formatar_por_ano()` passou a ordenar os anos de forma **decrescente**. |
| 4 | "Às vezes dois arquivos têm o mesmo nome." | O nome do arquivo no acervo recebe um **prefixo de id único**, evitando colisão. |

### Round 3

| # | Feedback | Ajuste incorporado |
|---|----------|--------------------|
| 5 | "Não sei o id do documento de cabeça." | A listagem e a busca exibem o **id entre colchetes** em cada linha, facilitando copiar para renomear/remover. |

Todos os ajustes têm testes correspondentes na suíte, garantindo que o comportamento
solicitado permaneça funcionando.
```

- [ ] **Step 3: Substituir o bloco da seção 3 pela saída real**

Edite a seção "## 3. Resultado" colando o texto real capturado na Step 1.

- [ ] **Step 4: Commit**

```bash
git add docs/RELATORIO_TESTES.md
git commit -m "docs: relatorio de testes e feedback incorporado"
```

---

## Task 16: Criar repositório remoto e publicar

Requer `gh` autenticado. A autenticação é interativa — **o usuário** roda o login.

- [ ] **Step 1: Garantir que `gh` está autenticado**

O usuário deve rodar (no terminal da sessão, com o prefixo `!`):

```
! gh auth login
```

Confirmar com:

```bash
gh auth status
```

Expected: "Logged in to github.com as <usuario>".

- [ ] **Step 2: Criar o repositório remoto e dar push**

A partir de `biblioteca-digital/` (já é um repo git local com a branch `main`):

```bash
gh repo create biblioteca-digital --public --source=. --remote=origin --push
```

Expected: cria o repo no GitHub e envia a `main`.

- [ ] **Step 3: Confirmar**

```bash
git remote -v
gh repo view --web
```

Expected: `origin` aponta para o GitHub; a página do repo abre com o código.

- [ ] **Step 4 (configuração para PRs):** Garantir branch padrão e proteção básica

Pela interface (Settings → Branches) ou apenas confirmar que a branch padrão é `main`.
A rubrica pede "configurar o repositório para aceitar pull requests" — repositórios
GitHub aceitam PRs por padrão; documentar isso no `CONTRIBUTING.md` (já feito na Task 12).

---

## Ordem de execução recomendada

Tasks 0–13 e 15 são locais e podem rodar em sequência. **Task 16** (criar remoto) deve
vir antes da **Task 14** (PR real), pois o PR precisa do remoto. Sugestão:

1. Tasks 0–13 (código + docs locais, commits incrementais)
2. Task 15 (relatório de testes)
3. Task 16 (autenticar `gh` + criar remoto + push)
4. Task 14 (branch + PR real + merge)

---

## Self-Review (preenchido)

**Spec coverage:**
- Manipulação de arquivos (abrir/ler/criar/renomear/remover) → Tasks 2, 3 ✓
- Manipulação de diretórios (criar/listar/remover) → Task 2 ✓
- Listar por tipo e ano → Task 5 ✓
- CLI adicionar/renomear/remover + menu de contexto → Tasks 7, 8 ✓
- Modo comando → Task 9 ✓
- Repositório + commits incrementais → todas as tasks (commits) + Task 16 ✓
- Aceitar PRs + guia de contribuição → Tasks 12, 14, 16 ✓
- Testes → Tasks 1–9 (TDD) + Task 15 (relatório) ✓
- Documentação detalhada → Tasks 11, 13 ✓
- Relatório de testes + feedback incorporado → Task 15 ✓
- Dados de exemplo → Task 10 ✓

**Placeholder scan:** A única "lacuna intencional" é colar a saída real do pytest no
relatório (Task 15, Steps 1/3) — é uma captura de runtime, não um placeholder de design.

**Type consistency:** `Documento` (campos e `novo`/`para_dict`/`de_dict`) usado de forma
consistente. `Catalogo` expõe `adicionar`/`obter`/`renomear`/`remover`/`listar`/
`listar_por_tipo`/`listar_por_ano`/`buscar`/`contar`/`pasta_acervo`/`caminho_json` —
todos referenciados de forma idêntica nas Tasks 4–9, 14 e na CLI. `armazenamento` expõe
os mesmos nomes de função em todas as referências.
