from __future__ import annotations

import argparse
from pathlib import Path

from bootstrap import ensure_runtime


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Baixa formulários do Meta, consolida os CSVs e gera o arquivo de leads."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Executa o navegador em modo headless.",
    )
    parser.add_argument(
        "--output",
        default="novos_leads.xlsx",
        help="Caminho do arquivo Excel final.",
    )
    parser.add_argument(
        "--downloads",
        default="datasets",
        help="Diretório onde os CSVs baixados serão salvos antes da consolidação.",
    )
    return parser.parse_args()


def main() -> None:
    ensure_runtime()

    args = parse_args()

    from baixar_formularios import baixar_formularios
    from concatenar_arquivos import consolidar_arquivos

    downloads_dir = Path(args.downloads)
    output_file = Path(args.output)

    # arquivos = baixar_formularios(output_dir=downloads_dir, headless=args.headless)
    # print(f"{len(arquivos)} arquivo(s) baixado(s).")

    planilha = consolidar_arquivos(input_dir=downloads_dir, output_file=output_file)
    print(f"Arquivo final gerado em: {planilha.resolve()}")


if __name__ == "__main__":
    main()
