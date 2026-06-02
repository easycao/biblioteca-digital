# Design — Sistema de Gerenciamento de Biblioteca Digital

**Data:** 2026-06-02
**Contexto:** PUCPR — Programação para Ciência de Dados — Hora da Prática 2
**Autor:** Leonardo Lamonatto

---

## 1. Objetivo

Construir um sistema em Python que permita a uma biblioteca universitária gerenciar
sua coleção de documentos digitais (artigos, teses, livros em PDF, ePUB, etc.),
substituindo a gestão manual atual por operações automatizadas e confiáveis.

O sistema deve permitir:
- Manipular arquivos digitais: abrir, ler, criar, renomear e remover.
- Gerenciar diretórios: listar, criar e remover.
- Listar documentos organizados por tipo de arquivo e por ano de publicação.
- Interface de linha de comando (com **menu de contexto** interativo) para
  bibliotecários adicionarem, renomearem e removerem documentos.

## 2. Critérios de avaliação (rubrica)

| Peso | Critério |
|------|----------|
| 35% | Manipulação de arquivos (abrir, ler, criar, renomear, remover) + diretórios (listar, criar, remover). Código limpo, comentado, PEP 8. |
| 30% | Uso de Git/GitHub: commits claros, pushes, pull requests, repositório bem configurado. |
| 35% | Documentação completa + relatório de testes e feedback incorporado. |

## 3. Decisões de escopo

- **Abordagem B — Catálogo + arquivos:** documentos reais vivem em `acervo/`; um índice
  `catalogo.json` guarda os metadados. Cada operação sincroniza disco **e** catálogo.
  (Escolhida sobre filesystem-puro e SQLite: cobre todos os verbos da rubrica, mantém
  metadados confiáveis para listagem por tipo/ano, e o JSON é transparente para o avaliador.)
- **Idioma:** comentários, docs, mensagens da CLI e commits em **pt-BR**. Identificadores
  de código (funções/variáveis) em inglês, seguindo convenção Python.
- **Dados de exemplo:** gerar PDFs/ePUBs/TXT fictícios em `dados_exemplo/` para demo e testes.
- **Pull Request:** demonstrar o fluxo real — feature branch → push → PR no GitHub → merge.
- **Feedback dos bibliotecários:** cenário fictício; simular 2–3 rounds de feedback plausível
  e documentar como o código evoluiu em resposta.
- **GitHub:** repositório criado via `gh` CLI.
- **Local do projeto:** `C:\Users\pcleo\workspace\Faculdade\Programação\biblioteca-digital`.

## 4. Arquitetura em camadas

```
CLI (cli.py)              ← menu de contexto interativo + comandos diretos (argparse)
   │
   ├── catalogo.py        ← CRUD de metadados (catalogo.json), validação, listagens
   │
   └── armazenamento.py   ← manipulação física: arquivos + diretórios em acervo/
        │
   modelos.py             ← dataclass Documento + enums TipoDocumento, Formato
```

Cada módulo tem uma responsabilidade única e é testável de forma isolada:
- `cli.py` não toca o disco diretamente — chama `catalogo`.
- `catalogo.py` não conhece menus — opera sobre dados e delega I/O físico a `armazenamento`.
- `armazenamento.py` é I/O puro de arquivos/diretórios, sem regra de negócio.

## 5. Estrutura de pastas

```
biblioteca-digital/
├── src/biblioteca/
│   ├── __init__.py
│   ├── modelos.py          # dataclass Documento + enums TipoDocumento, Formato
│   ├── armazenamento.py    # camada física (open/read/create/rename/remove + dirs)
│   ├── catalogo.py         # camada de metadados (catalogo.json)
│   └── cli.py              # menu de contexto + comandos
├── acervo/                 # docs reais gerenciados (.gitkeep; conteúdo gitignored)
├── dados_exemplo/          # PDFs/ePUBs/TXT fictícios para demo (commitados)
├── tests/
│   ├── test_armazenamento.py
│   ├── test_catalogo.py
│   └── test_cli.py
├── docs/
│   ├── FUNCIONALIDADES.md  # documentação detalhada de cada função
│   └── RELATORIO_TESTES.md # relatório de testes + feedback incorporado
├── README.md
├── CONTRIBUTING.md         # guia de commits/push/PR
├── catalogo.json           # índice de metadados
├── requirements.txt        # pytest (dev)
├── .gitignore
└── main.py                 # entrypoint → chama cli.py
```

## 6. Modelo de dados

`Documento` (dataclass):

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | str | uuid curto, identificador único |
| `titulo` | str | título do documento |
| `autor` | str | autor |
| `tipo` | str | `"artigo"` \| `"tese"` \| `"livro"` |
| `ano` | int | ano de publicação |
| `formato` | str | `"pdf"` \| `"epub"` \| `"txt"` \| ... |
| `arquivo` | str | nome do arquivo correspondente em `acervo/` |
| `adicionado_em` | str | timestamp ISO da inclusão |

`catalogo.json` = `{"documentos": [ {<Documento>}, ... ]}`

## 7. Camada `armazenamento.py` (rubrica 35%)

| Função | Verbo da rubrica | Comportamento |
|--------|------------------|---------------|
| `criar_diretorio(caminho)` | criar diretório | cria pasta, incl. pais (idempotente) |
| `remover_diretorio(caminho)` | remover diretório | remove pasta (vazia ou recursiva) |
| `listar_diretorio(caminho)` | listar diretório | retorna lista do conteúdo |
| `salvar_arquivo(origem, destino)` | criar arquivo | copia documento para `acervo/` |
| `ler_arquivo(caminho)` | abrir + ler | abre e lê o arquivo, retorna conteúdo/tamanho |
| `renomear_arquivo(antigo, novo)` | renomear | renomeia no disco |
| `remover_arquivo(caminho)` | remover arquivo | remove o arquivo do disco |
| `arquivo_existe(caminho)` | — | guarda de validação |

Tratamento de erros: caminho inexistente, permissão negada, colisão de nome. Cada
função levanta/retorna erro claro em pt-BR.

## 8. Camada `catalogo.py` (metadados)

- `carregar()` / `salvar()` — leitura/escrita de `catalogo.json`.
- `adicionar(documento, origem)` — copia o arquivo para `acervo/` e registra metadados.
- `renomear(id, novo_titulo|novo_arquivo)` — renomeia no disco e atualiza a entrada.
- `remover(id)` — apaga o arquivo do disco **e** remove a entrada do catálogo.
- `listar_por_tipo()` — agrupa documentos por tipo.
- `listar_por_ano()` — agrupa documentos por ano de publicação.
- `buscar(termo)` — busca por título/autor.

Invariante: disco e catálogo permanecem sincronizados após cada operação.

## 9. CLI `cli.py` — menu de contexto

Menu interativo em loop (atende ao requisito "tem menu de contexto"):

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
Escolha:
```

Também aceita modo comando direto via `argparse` (ex.: `python main.py listar --por tipo`)
para uso scriptável. Menu = experiência guiada; comandos = automação.

Confirmação obrigatória antes de operações destrutivas (remover).

## 10. Testes (`pytest`)

- `test_armazenamento.py` — cria/lê/renomeia/remove em `tmp_path` (isolado do acervo real).
- `test_catalogo.py` — adicionar/remover/listar por tipo e ano; valida sincronização disco+catálogo.
- `test_cli.py` — simula entrada de menu (monkeypatch em `input`), valida fluxos.
- Cobertura de caminhos felizes **e** de erro (arquivo inexistente, nome duplicado).

## 11. Git/GitHub (rubrica 30%)

1. Repositório local com commits incrementais semânticos (Conventional Commits), um por
   funcionalidade: `feat:`, `test:`, `docs:`, `chore:`.
2. Repositório remoto criado via `gh repo create`.
3. Fluxo de Pull Request real: feature branch → push → `gh pr create` → merge.
4. `CONTRIBUTING.md` documenta passo a passo de commits, pushes e pull requests.

## 12. Documentação & relatórios (rubrica 35%)

- `README.md` — visão geral, instalação, uso (menu + comandos), exemplos.
- `docs/FUNCIONALIDADES.md` — cada função documentada (assinatura, parâmetros, retorno, exemplo).
- `docs/RELATORIO_TESTES.md` — resultados do pytest + relatório de feedback simulado dos
  bibliotecários, com os ajustes incorporados ao projeto descritos.

## 13. Fora de escopo (YAGNI)

- Banco de dados relacional (SQLite) — JSON é suficiente e mais transparente.
- Interface gráfica/web — apenas CLI.
- Parsing real de metadados de dentro de PDFs/ePUBs — metadados vêm do cadastro.
- Autenticação/multiusuário.
