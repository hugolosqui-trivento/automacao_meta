from __future__ import annotations

import unicodedata
from pathlib import Path

import pandas as pd


COLUNAS_RENOMEADAS = {
    "created_time": "Criado em",
    "ad_id": "ID Anúncio",
    "ad_name": "Nome Anúncio",
    "adset_id": "ID Conjunto de Anúncios",
    "adset_name": "Nome do Conjunto de Anúncios",
    "campaign_id": "ID da Campanha",
    "campaign_name": "Nome da Campanha",
    "form_id": "ID do Formulário",
    "form_name": "Nome do Formulário",
    "is_organic": "É Orgânico",
    "platform": "Plataforma",
    "full_name": "Nome Completo",
    "email": "E-mail",
    "numero_do_whatsapp": "Número do WhatsApp",
    "eu_concordo_em_receber_comunicacoes": "Concordo em Receber Comunicações",
    "phone_number": "Telefone",
    "inbox_url": "URL Caixa de Entrada",
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    return texto.strip().lower().replace(" ", "_")


def consolidar_arquivos(
    input_dir: Path | str = "datasets",
    output_file: Path | str = "novos_leads.xlsx",
    limpar_csvs: bool = True,
) -> Path:
    input_path = Path(input_dir)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Diretório de entrada não encontrado: {input_path}")

    arquivos_csv = sorted(input_path.glob("*.csv"))
    if not arquivos_csv:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {input_path}")

    dfs: list[pd.DataFrame] = []

    for arquivo in arquivos_csv:
        df = pd.read_csv(arquivo, sep="\t", encoding="utf-16")
        rename_map = {
            coluna: COLUNAS_RENOMEADAS[_normalizar(coluna)]
            for coluna in df.columns
            if _normalizar(coluna) in COLUNAS_RENOMEADAS
        }
        df = df.rename(columns=rename_map)
        dfs.append(df)

    consolidado = pd.concat(dfs, ignore_index=True)

    if "Criado em" in consolidado.columns:
        consolidado["Criado em"] = pd.to_datetime(
            consolidado["Criado em"], errors="coerce"
        ).dt.date

    if "Telefone" in consolidado.columns:
        consolidado["Telefone"] = consolidado["Telefone"].astype(str).str.replace(
            r"\D",
            "",
            regex=True,
        )

    consolidado.to_excel(output_path, index=False)

    if limpar_csvs:
        for arquivo in arquivos_csv:
            arquivo.unlink(missing_ok=True)

    return output_path
