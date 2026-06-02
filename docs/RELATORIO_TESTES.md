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

Saída real de `python -m pytest -v`:

```
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\pcleo\AppData\Local\Programs\Python\Python312\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\pcleo\workspace\Faculdade\Programação\biblioteca-digital
plugins: anyio-4.13.0
collecting ... collected 38 items

tests/test_armazenamento.py::test_criar_diretorio_cria_pasta PASSED      [  2%]
tests/test_armazenamento.py::test_criar_diretorio_idempotente PASSED     [  5%]
tests/test_armazenamento.py::test_listar_diretorio_retorna_conteudo PASSED [  7%]
tests/test_armazenamento.py::test_listar_diretorio_inexistente_levanta_erro PASSED [ 10%]
tests/test_armazenamento.py::test_remover_diretorio_remove_recursivo PASSED [ 13%]
tests/test_armazenamento.py::test_salvar_arquivo_copia_para_destino PASSED [ 15%]
tests/test_armazenamento.py::test_salvar_arquivo_origem_inexistente_levanta_erro PASSED [ 18%]
tests/test_armazenamento.py::test_ler_arquivo_retorna_texto PASSED       [ 21%]
tests/test_armazenamento.py::test_ler_arquivo_inexistente_levanta_erro PASSED [ 23%]
tests/test_armazenamento.py::test_renomear_arquivo PASSED                [ 26%]
tests/test_armazenamento.py::test_renomear_arquivo_colisao_levanta_erro PASSED [ 28%]
tests/test_armazenamento.py::test_remover_arquivo PASSED                 [ 31%]
tests/test_armazenamento.py::test_remover_arquivo_inexistente_levanta_erro PASSED [ 34%]
tests/test_armazenamento.py::test_arquivo_existe PASSED                  [ 36%]
tests/test_catalogo.py::test_catalogo_vazio_no_inicio PASSED             [ 39%]
tests/test_catalogo.py::test_adicionar_copia_arquivo_e_registra PASSED   [ 42%]
tests/test_catalogo.py::test_adicionar_persiste_no_json PASSED           [ 44%]
tests/test_catalogo.py::test_adicionar_origem_inexistente_levanta_erro PASSED [ 47%]
tests/test_catalogo.py::test_listar_por_tipo_agrupa PASSED               [ 50%]
tests/test_catalogo.py::test_listar_por_ano_agrupa PASSED                [ 52%]
tests/test_catalogo.py::test_buscar_por_titulo_e_autor PASSED            [ 55%]
tests/test_catalogo.py::test_obter_por_id PASSED                         [ 57%]
tests/test_catalogo.py::test_renomear_atualiza_titulo PASSED             [ 60%]
tests/test_catalogo.py::test_renomear_id_inexistente_levanta_erro PASSED [ 63%]
tests/test_catalogo.py::test_remover_apaga_arquivo_e_entrada PASSED      [ 65%]
tests/test_catalogo.py::test_remover_id_inexistente_levanta_erro PASSED  [ 68%]
tests/test_catalogo.py::test_contar_documentos PASSED                    [ 71%]
tests/test_cli.py::test_formatar_por_tipo_mostra_cabecalhos PASSED       [ 73%]
tests/test_cli.py::test_formatar_por_ano_ordena_decrescente PASSED       [ 76%]
tests/test_cli.py::test_formatar_lista_vazia PASSED                      [ 78%]
tests/test_cli.py::test_menu_lista_por_tipo_e_sai PASSED                 [ 81%]
tests/test_cli.py::test_menu_remover_pede_confirmacao PASSED             [ 84%]
tests/test_cli.py::test_menu_remover_cancela_sem_confirmar PASSED        [ 86%]
tests/test_cli.py::test_menu_opcao_invalida_continua PASSED              [ 89%]
tests/test_cli.py::test_construir_parser_aceita_listar_por_tipo PASSED   [ 92%]
tests/test_cli.py::test_construir_parser_aceita_listar_por_ano PASSED    [ 94%]
tests/test_modelos.py::test_documento_para_dict_e_de_dict_sao_simetricos PASSED [ 97%]
tests/test_modelos.py::test_documento_novo_gera_id_e_timestamp PASSED    [100%]

============================= 38 passed in 0.18s ==============================
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
