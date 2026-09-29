from __future__ import annotations

import re
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
    "full_name": "nome_completo",
    "email": "email",
    "numero_do_whatsapp": "numero_do_whatsapp",
    "eu_concordo_em_receber_comunicacoes": "Concordo em Receber Comunicações",
    "phone_number": "telefone",
    "whatsapp_number": "telefone",
    "inbox_url": "URL Caixa de Entrada",
}


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    return texto.strip().lower().replace(" ", "_")

def normalizar_colunas(colunas: list) -> list:
    colunas_limpas = [str(coluna).strip().lower().replace(" ", "_") for coluna in colunas]

    corresp_colunas = {
         "numero_do_whatsapp": "telefone",
         "celular": "telefone"
    }
     

    return [corresp_colunas.get(col, col) for col in colunas_limpas]


def obter_unidadeform(nome_formulario: object) -> object:
    if pd.isna(nome_formulario):
        return pd.NA

    nome_normalizado = _normalizar(str(nome_formulario))
    unidades = (
        ("lorena", "Lorena"),
        ("canaa", "Canaã"),
        ("itabirito", "Itabirito"),
        ("altamira", "Altamira"),
    )
    unidade_encontrada = next(
        (
            nome_exibicao
            for termo, nome_exibicao in unidades
            if termo in nome_normalizado
        ),
        None,
    )

    if unidade_encontrada is None:
        return pd.NA

    return (
        f"Medicina {unidade_encontrada}"
        if "medicina" in nome_normalizado
        else unidade_encontrada
    )


def obter_origem_formulario(nome_formulario: object) -> object:
    if pd.isna(nome_formulario):
        return pd.NA

    nome_normalizado = _normalizar(str(nome_formulario))
    mapeamento = (
        ("medicina", "Medicina - Formulário Meta"),
        ("to", "TO - Formulário Meta"),
        ("arquitetura", "ARQ - Formulário Meta"),
        ("agronomia", "AGR - Formulário Meta"),
        ("wpp", "Whatsapp - Formulário Meta"),
    )

    for palavra, origem in mapeamento:
        padrao = rf"(?<![a-z0-9]){re.escape(palavra)}(?![a-z0-9])"
        if re.search(padrao, nome_normalizado):
            return origem

    return pd.NA

def obter_intake(nome_formulario):
    if pd.isna(nome_formulario):
        return None
    nome_normalizado = _normalizar(str(nome_formulario))

    if '2027' in nome_normalizado:
        return "2027/1"

    else:
        return "2026/2"

    

def consolidar_arquivos(
    input_dir: Path | str = "dataset",
    output_file: Path | str = "novos_leads.xlsx",
    limpar_csvs: bool = False,
) -> Path:
    input_path = Path(input_dir)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Diretório de entrada não encontrado: {input_path}")

    arquivos_csv = sorted(input_path.rglob("*.csv"))
    if not arquivos_csv:
        raise FileNotFoundError(f"Nenhum arquivo CSV encontrado em {input_path}")

    dfs: list[pd.DataFrame] = []

    for arquivo in arquivos_csv:
        df = pd.read_csv(arquivo, sep="\t", encoding="utf-16", dtype=str)
        rename_map = {
            coluna: COLUNAS_RENOMEADAS[_normalizar(coluna)]
            for coluna in df.columns
            if _normalizar(coluna) in COLUNAS_RENOMEADAS
        }
        df = df.rename(columns=rename_map)

        df.columns  = normalizar_colunas(df.columns)
        # Alguns formulários têm mais de um campo de telefone.
        if df.columns.duplicated().any():
            df = df.T.groupby(level=0, sort=False).first().T
        dfs.append(df)

    consolidado = pd.concat(dfs, ignore_index=True)

    # Um lead pode aparecer em mais de uma execução de download.
    if "id" in consolidado.columns:
        repetidos = consolidado["id"].notna() & consolidado["id"].duplicated()
        consolidado = consolidado.loc[~repetidos].copy()


    # filtrando colunas para importar
    colunas_filtro = ['nome_completo', 'email', 'telefone', 'nome_do_formulário']
    consolidado = consolidado[colunas_filtro]

    consolidado['nome_do_formulário'] =  consolidado['nome_do_formulário'].str.lower()
    
   
    consolidado["unidadeform"] = consolidado[colunas_filtro[3]].apply(
        obter_unidadeform
    )
    consolidado["Landing Page ou Formulário de Origem"] = consolidado[
        colunas_filtro[3]
    ].apply(obter_origem_formulario)

    # consolidado["intake"] = consolidado[colunas_filtro[3]].apply(obter_intake)
    consolidado["intake"] = '2027/1'
    
    if "Criado em" in consolidado.columns:
        consolidado["Criado em"] = pd.to_datetime(
            consolidado["Criado em"], errors="coerce"
        ).dt.date

    if "telefone" in consolidado.columns:
        consolidado["telefone"] = consolidado["telefone"].fillna("").astype(str).str.replace(
            r"\D",
            "",
            regex=True,
        )
    colunas_final = {
        'nome_completo': 'Nome Completo',
        'email': 'Email',
        'telefone': 'Telefone Celular',
        'unidadeform': 'Unidadeform (crmeduc_unidadeform)'
    }
    consolidado = consolidado.rename(columns= colunas_final)

    consolidado.to_excel(output_path, index=False)

    

    if limpar_csvs:
        input(f"Pressione Enter para apagar os arquivos baixados em '{input_path}'...")
        for arquivo in arquivos_csv:
            arquivo.unlink(missing_ok=True)

    return output_path
