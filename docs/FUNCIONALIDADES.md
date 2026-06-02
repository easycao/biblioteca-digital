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
