import re
from playwright.sync_api import Playwright, sync_playwright, expect
from time import sleep
import os 
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        storage_state="cookies.json" if os.path.exists("cookies.json") else None
    )
    page = context.new_page()
    page.goto("https://business.facebook.com/business/loginpage/?next=https%3A%2F%2Fbusiness.facebook.com%2F%3Fnav_ref%3Dbiz_unified_f3_login_page_to_mbs&login_options%5B0%5D=FB&login_options%5B1%5D=IG&login_options%5B2%5D=SSO&config_ref=biz_login_tool_flavor_mbs")

    # aguarda a autenticação do usuário manualmente
    input("Pressione Enter após autenticar manualmente...")

    

    nomes_paginas = [
        "Facebook Serra Dourada Unidade Altamira Página do Facebook Owned by Faculdade",
        "Instagram Facebook Faculdade Alis de Itabirito , alis.itabirito Página do",
        "Instagram Facebook Serra Dourada Canaã dos Carajás , serradourada_canaa Página",
        "Instagram Facebook Faculdade Serra Dourada Unidade Lorena , serradouradalorena"]

    
    for pagina in nomes_paginas:
            page.goto("https://business.facebook.com/latest/instant_forms/")
            page.get_by_role("button", name="Pressable").hover()
            page.locator(".x6s0dn4.x78zum5.x13fuv20.x18b5jzi.x1q0q8m5.x1t7ytsu.x178xt8z.x1lun4ml.xso031l.xpilrb4.xwebqov.x1x9jw1y.xrsgblv.xceihxd.xjwep3j.x1t39747.x1wcsgtt.x1pczhz8.x1gzqxud.xbsr9hj.xm7lytj").click()
            page.locator("#north-star-scrollable-area").get_by_text("GSA Educacional").click()
            page.get_by_role("radio", name=pagina).click()
            # page.get_by_role("link", name="Todas as ferramentas").click()
            # page.get_by_text("Formulários instantâneos").nth(1).click()
            sleep(10)  # Aguarda 10 segundos para garantir que a página carregou completamente
            # # clica em algum canto da pagina para fechar o modal de seleção de página
            # page.click("body")  # Clica no corpo da página para fechar o modal
            botoes_baixar = page.get_by_role("button", name="Baixar")
            print(f"Total de botões 'Baixar' encontrados: {botoes_baixar.count()}")
            for i in range(botoes_baixar.count()):
                botoes_baixar.nth(i).click()
            # page.get_by_role("button", name="Baixar").first.click()
                page.get_by_role("button", name="Baixar novos leads").click()
                # page.locator("button").filter(has_text="Baixar").click()
                with page.expect_download() as download_info:
                    page.get_by_role("link", name="CSV").click()
                download = download_info.value
                # esperar até que o download seja concluído
                # download.wait_for_completion()
                caminho_download = 'datasets'

                download.save_as(f"{caminho_download}/{download.suggested_filename}")
                sleep(2)  # Aguarda 2 segundos antes de prosseguir para o próximo download
                page.get_by_role("button", name="Fechar").nth(1).click()  # Fecha o modal de download
                sleep(1)  # Aguarda 1 segundos antes de prosseguir para o próximo botão "Baixar"
    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
