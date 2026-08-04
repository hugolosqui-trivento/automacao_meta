from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"
BOOTSTRAP_MARKER = VENV_DIR / ".bootstrap-complete"


def _run(command: list[str]) -> None:
    subprocess.check_call(command)


def _run_optional(command: list[str], label: str) -> None:
    try:
        _run(command)
    except subprocess.CalledProcessError as exc:
        print(
            f"Aviso: não foi possível concluir '{label}'. "
            f"O app vai seguir com a versão disponível. Detalhe: {exc}"
        )


def _current_python_path() -> Path:
    return Path(sys.executable).resolve()


def ensure_runtime() -> None:
    """
    Garante que o projeto esteja executando dentro de uma venv local com
    dependências instaladas e o Chromium do Playwright disponível.
    """
    if not VENV_PYTHON.exists():
        _run([sys.executable, "-m", "venv", str(VENV_DIR)])

    needs_install = not BOOTSTRAP_MARKER.exists()

    if needs_install:
        _run([str(VENV_PYTHON), "-m", "ensurepip", "--upgrade"])
        _run_optional(
            [str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"],
            "upgrade do pip",
        )
        _run([str(VENV_PYTHON), "-m", "pip", "install", "-r", str(REQUIREMENTS_FILE)])
        _run([str(VENV_PYTHON), "-m", "playwright", "install", "chromium"])
        BOOTSTRAP_MARKER.write_text("ok", encoding="utf-8")

    if _current_python_path() != VENV_PYTHON.resolve():
        os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv])
