import unittest
from unittest.mock import Mock

from playwright.sync_api import Error, TimeoutError, sync_playwright

from baixar_formularios import _aguardar_botoes_baixar, _aguardar_saida_tabela


class SaidaTabelaTest(unittest.TestCase):
    def test_remocao_durante_espera_conclui_troca(self):
        tabela = Mock()
        tabela.wait_for_element_state.side_effect = Error(
            "ElementHandle.wait_for_element_state: Element is not attached to the DOM"
        )
        _aguardar_saida_tabela(tabela)

    def test_nao_oculta_timeout_ou_falha_do_navegador(self):
        for erro in (TimeoutError("Timeout 30000ms exceeded"), Error("Target closed")):
            with self.subTest(erro=str(erro)):
                tabela = Mock()
                tabela.wait_for_element_state.side_effect = erro
                with self.assertRaises(type(erro)) as capturado:
                    _aguardar_saida_tabela(tabela)
                self.assertIs(capturado.exception, erro)


class EsperaFormulariosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page()

    def tearDown(self):
        self.page.close()

    def test_tabela_removida_com_nova_tabela_visivel(self):
        self.page.set_content('<div role="grid" aria-label="Formulários">Antiga</div>')
        tabela_anterior = self.page.get_by_role("grid").element_handle()
        self.page.evaluate('''() => {
            document.querySelector('[role="grid"]').remove();
            document.body.innerHTML =
                '<div role="grid" aria-label="Formulários"><button>Baixar</button></div>';
        }''')
        _aguardar_saida_tabela(tabela_anterior)
        self.assertEqual(_aguardar_botoes_baixar(self.page, timeout=200).count(), 1)

    def test_aguarda_download_que_aparece_depois_da_tabela(self):
        self.page.set_content('''
            <div role="grid" aria-label="Formulários">Nome</div>
            <script>
                setTimeout(() => {
                    document.querySelector('[role="grid"]').innerHTML =
                        '<button>Baixar</button>';
                }, 300);
            </script>
        ''')
        self.assertEqual(_aguardar_botoes_baixar(self.page, timeout=2000).count(), 1)

    def test_sem_botoes_visiveis_continua_para_proxima_pagina(self):
        self.page.set_content('''
            <div role="grid" aria-label="Formulários">
                <div role="columnheader">Nome</div>
                <button style="display:none">Baixar</button>
            </div>
        ''')
        self.assertEqual(_aguardar_botoes_baixar(self.page, timeout=200).count(), 0)
        self.page.set_content('''
            <div role="grid" aria-label="Formulários"><button>Baixar</button></div>
        ''')
        self.assertEqual(_aguardar_botoes_baixar(self.page, timeout=200).count(), 1)

    def test_ignora_botao_de_dialogo_fora_da_tabela(self):
        self.page.set_content('''
            <button>Baixar</button>
            <div role="grid" aria-label="Formulários">
                <button>Baixar novos leads</button>
            </div>
        ''')
        self.assertEqual(_aguardar_botoes_baixar(self.page, timeout=200).count(), 0)


if __name__ == "__main__":
    unittest.main()
