from __future__ import annotations

import os
import re
from pathlib import Path
from time import sleep

from playwright.sync_api import Page, Playwright, sync_playwright


LOGIN_URL = (
    "https://business.facebook.com/business/loginpage/?next="
    "https%3A%2F%2Fbusiness.facebook.com%2F%3Fnav_ref%3Dbiz_unified_f3_login_page_to_mbs"
    "&login_options%5B0%5D=FB&login_options%5B1%5D=IG&login_options%5B2%5D=SSO"
    "&config_ref=biz_login_tool_flavor_mbs"
)

NOME_DA_CONTA = "Trivento Educação"
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


def _selecionar_pagina(page: Page, nome_pagina: str) -> None:
    seletor_compacto = page.get_by_role("button", name="Pressable")
    seletor_compacto.hover()

    # O Meta substitui o botão compacto por um combobox durante o hover.
    # As classes CSS desse controle são geradas e mudam com frequência.
    page.get_by_role("combobox").click()
    page.get_by_role(
        "gridcell",
        name=re.compile(rf"^{re.escape(NOME_DA_CONTA)}(?:\s|$)"),
    ).click()
    page.get_by_role("gridcell", name=nome_pagina).click(no_wait_after=True)
    page.get_by_role("button", name="Baixar").first.wait_for(state="visible")


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
        _selecionar_pagina(page, pagina)

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


def baixar_formularios(output_dir: Path | str = "dataset", headless: bool = False) -> list[Path]:
    destino = Path(output_dir)
    with sync_playwright() as playwright:
        return run(playwright, destino, headless=headless)
