from __future__ import annotations

import os
import re
from pathlib import Path
from time import sleep

from playwright.sync_api import Playwright, sync_playwright


LOGIN_URL = (
    "https://business.facebook.com/business/loginpage/?next="
    "https%3A%2F%2Fbusiness.facebook.com%2F%3Fnav_ref%3Dbiz_unified_f3_login_page_to_mbs"
    "&login_options%5B0%5D=FB&login_options%5B1%5D=IG&login_options%5B2%5D=SSO"
    "&config_ref=biz_login_tool_flavor_mbs"
)

NOME_DA_CONTA = "GSA Educacional"
NOMES_PAGINAS = [
    "Facebook Serra Dourada Unidade Altamira Página do Facebook Owned by Faculdade",
    "Instagram Facebook Faculdade Alis de Itabirito , alis.itabirito Página do",
    "Instagram Facebook Serra Dourada Canaã dos Carajás , serradourada_canaa Página",
    "Instagram Facebook Faculdade Serra Dourada Unidade Lorena , serradouradalorena",
]


def _slugify(texto: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", texto.lower())
    return slug.strip("_")


def _download_nome(prefixo: str, indice: int, nome_original: str) -> str:
    return f"{prefixo}_{indice:02d}_{nome_original}"


def run(playwright: Playwright, output_dir: Path, headless: bool = False) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    browser = playwright.chromium.launch(headless=headless)
    context = browser.new_context(
        storage_state="cookies.json" if os.path.exists("cookies.json") else None
    )
    page = context.new_page()
    page.goto(LOGIN_URL)

    primeiro_login = not os.path.exists("cookies.json")

    if primeiro_login:
        input("Pressione Enter após autenticar manualmente...")
        context.storage_state(path="cookies.json")

    arquivos_baixados: list[Path] = []
    page.goto("https://business.facebook.com/latest/instant_forms/")
    page.get_by_role("button", name="Filtros:").click()
    page.get_by_role("button", name="Selecionar datas").click()
    page.get_by_role("radio", name="Este trimestre").check()
    page.get_by_role("button", name="Aplicar").click()
    for pagina in NOMES_PAGINAS:
        

        # acrescentar um filtro de DATA
        page.get_by_role("button", name="Pressable").hover()
        page.locator(
            ".x6s0dn4.x78zum5.x13fuv20.x18b5jzi.x1q0q8m5.x1t7ytsu.x178xt8z.x1lun4ml"
            ".xso031l.xpilrb4.xwebqov.x1x9jw1y.xrsgblv.xceihxd.xjwep3j.x1t39747"
            ".x1wcsgtt.x1pczhz8.x1gzqxud.xbsr9hj.xm7lytj"
        ).click()
        page.locator("#north-star-scrollable-area").get_by_text(NOME_DA_CONTA).click()
        page.get_by_role("radio", name=pagina).click()

        sleep(10)

        botoes_baixar = page.get_by_role("button", name="Baixar")
        print(f"Total de botões 'Baixar' encontrados para '{pagina}': {botoes_baixar.count()}")

        for indice in range(botoes_baixar.count()):
            botoes_baixar.nth(indice).click()
            page.get_by_role("button", name="Baixar novos leads").click()

            with page.expect_download() as download_info:
                page.get_by_role("link", name="CSV").click()

            download = download_info.value
            nome_arquivo = _download_nome(_slugify(pagina), indice + 1, download.suggested_filename)
            destino = output_dir / nome_arquivo
            download.save_as(str(destino))
            arquivos_baixados.append(destino)

            sleep(2)
            page.get_by_role("button", name="Fechar").nth(1).click()
            sleep(1)

    context.close()
    browser.close()
    return arquivos_baixados


def baixar_formularios(output_dir: Path | str = "datasets", headless: bool = False) -> list[Path]:
    destino = Path(output_dir)
    with sync_playwright() as playwright:
        return run(playwright, destino, headless=headless)
