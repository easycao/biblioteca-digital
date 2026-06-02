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
