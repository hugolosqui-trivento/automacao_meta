# automacao-meta

App em Python para baixar os formulários do Meta, consolidar os CSVs e gerar o arquivo final `novos_leads.xlsx`.

## Como executar

1. Garanta que o Python 3.11 esteja instalado.
2. Na raiz do projeto, execute:

```bash
python main.py
```

Na primeira execução, o app:

1. Cria uma `.venv` local.
2. Instala as dependências automaticamente.
3. Baixa o Chromium do Playwright.
4. Executa a automação e gera o Excel final.

## Opções

```bash
python main.py --headless
python main.py --output saida/novos_leads.xlsx
python main.py --downloads datasets
```

## Estrutura

- `main.py`: ponto de entrada do app.
- `bootstrap.py`: cria a venv e instala dependências automaticamente.
- `baixar_formularios.py`: baixa os CSVs de leads.
- `concatenar_arquivos.py`: consolida os CSVs em `novos_leads.xlsx`.

## Observações

- O login no Meta ainda pode exigir autenticação manual na primeira vez.
- Os CSVs baixados são apagados após a consolidação, para evitar duplicidade em execuções seguintes.
