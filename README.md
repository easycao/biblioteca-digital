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
