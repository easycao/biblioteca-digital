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
    arq.write_text("olá mundo", encoding="utf-8")
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
