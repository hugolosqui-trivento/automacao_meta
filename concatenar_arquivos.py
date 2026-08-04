import pandas as pd
import os

# iterar sobre os arquivos CSV baixados e ler cada um deles
dfs = []
caminho_diretorio = 'datasets'
arquivos_csv = [f for f in os.listdir(caminho_diretorio) if f.endswith('.csv')]
print(f"Lendo {len(arquivos_csv)} arquivos:")


for arquivo in arquivos_csv:
    caminho_arquivo = os.path.join(caminho_diretorio, arquivo)
    
    df = pd.read_csv(caminho_arquivo, sep = '\t', encoding = 'utf-16')
    dfs.append(df)
df = pd.concat(dfs, ignore_index=True)


dicionário_colunas = {
    
    'created_time': 'Criado em',
    'ad_id': 'ID Anúncio',
    'ad_name': 'Nome Anúncio',
    'adset_id': 'ID Conjunto de Anúncios',
    'adset_name': 'Nome do Conjunto de Anúncios',
    'campaign_id': 'ID da Campanha',
    'campaign_name': 'Nome da Campanha',
    'form_id': 'ID do Formulário',
    'form_name': 'Nome do Formulário',
    'is_organic': 'É Orgânico',
    'platform': 'Plataforma',
    'full_name': 'Nome Completo',
    'email': 'E-mail',
    'número_do_whatsapp': 'Número do WhatsApp',
    'eu_concordo_em_receber_comunicações': 'Concordo em Receber Comunicações',
    'phone_number': 'Telefone',
    'inbox_url': 'URL Caixa de Entrada'
}
# renomenar as colunas do DataFrame
df.rename(columns=dicionário_colunas, inplace=True)

df['Criado em'] = pd.to_datetime(df['Criado em'], format='ISO8601').dt.date

df['Telefone'] = df['Telefone'].astype(str).str.replace(r'\D', '', regex=True)


df.to_excel('novos_leads.xlsx', index=False)


# apagar os arquivos CSV baixados
for arquivo in arquivos_csv:
    caminho_arquivo = os.path.join(caminho_diretorio, arquivo)
    os.remove(caminho_arquivo)