import tempfile
import unittest
from pathlib import Path

import pandas as pd

from concatenar_arquivos import consolidar_arquivos


class ConsolidacaoTest(unittest.TestCase):
    def test_csv_sem_leads_gera_planilha_vazia(self):
        with tempfile.TemporaryDirectory() as temporario:
            pasta = Path(temporario)
            (pasta / "sem_leads.csv").write_text(
                "full_name\temail\tphone_number\tform_name\n", encoding="utf-16"
            )
            saida = pasta / "leads.xlsx"
            consolidar_arquivos(input_dir=pasta, output_file=saida)
            planilha = pd.read_excel(saida)
            self.assertEqual(len(planilha), 0)
            self.assertIn("Nome Completo", planilha.columns)
            self.assertIn("Unidadeform (crmeduc_unidadeform)", planilha.columns)


if __name__ == "__main__":
    unittest.main()
