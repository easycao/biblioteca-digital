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
