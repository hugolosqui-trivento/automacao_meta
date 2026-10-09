# Automação de leads do Meta

Este programa baixa os formulários de leads das páginas configuradas no Meta e reúne os dados em uma planilha Excel chamada `novos_leads.xlsx`.

## Antes de começar

- Use um computador com **Windows** e acesso à internet.
- Instale o **Python 3.11 ou mais recente**. Durante a instalação, marque a opção **Add Python to PATH**, se ela aparecer.
- Tenha acesso à conta do Meta usada para consultar os formulários. No primeiro uso, você precisará entrar nessa conta pelo navegador.

Você não precisa instalar as bibliotecas do projeto manualmente. O programa faz isso na primeira execução, que pode demorar alguns minutos.

## Como executar

1. Clique em View na barra de opções superior
2. Procure por terminal
3. Confira se o Python está disponível:

   ```powershell
   python --version
   ```

   O resultado deve mostrar `Python 3.11` ou uma versão mais recente. Se o comando não funcionar, tente `py --version`. Caso nenhum dos dois funcione, instale o Python e abra um novo terminal.

4. Execute o programa:

   ```powershell
   python main.py
   ```

   Se você usou `py --version` no passo anterior, execute `py main.py`.

5. Na primeira execução, aguarde a instalação automática dos componentes. Quando o navegador abrir, entre na sua conta do Meta. **Só depois de terminar o login**, volte ao terminal e pressione **Enter** quando aparecer a mensagem `Pressione Enter após autenticar manualmente...`.
6. Aguarde o término da execução. O terminal mostrará `Arquivo final gerado em:` seguido do caminho da planilha.

A planilha `novos_leads.xlsx` fica na pasta do projeto. Os arquivos CSV baixados ficam em `dataset/`. Nas próximas execuções, basta repetir o passo 4; o programa tenta reutilizar a sessão salva em `cookies.json`. Se o Meta pedir login novamente, pode ser necessário autenticar de novo.

7. Após enviar ao CRM e constar status "importação Completa", você pode fechar o vscode, ir ao github desktop, clicar em branch na barra superior e depois em "Discart all changes". Isso permite descartar os dados dos leads com segurança, já que eles já estão no CRM.

## Cuidados ao executar novamente

- Se a planilha `novos_leads.xlsx` estiver aberta no Excel, feche-a antes de executar o programa.

- Uma nova execução substitui a planilha de saída com o mesmo nome.

- O arquivo `cookies.json` contém dados da sua sessão no Meta. Não o compartilhe.
