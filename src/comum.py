"""Caminhos, leitura das tabelas e utilidades compartilhadas pelos scripts."""
from pathlib import Path
import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "config"
BRUTO = RAIZ / "data" / "raw"
PROC = RAIZ / "data" / "processed"
TABELAS = RAIZ / "saida" / "tabelas"
FIGURAS = RAIZ / "saida" / "figuras"
for _d in (BRUTO, PROC, TABELAS, FIGURAS):
    _d.mkdir(parents=True, exist_ok=True)

MOTORES = ["pistao", "turboelice", "turbofan"]
ROTULO_MOTOR = {"pistao": "Pistão", "turboelice": "Turboélice", "turbofan": "Turbofan"}
# Como o CENIPA nomeia o tipo de motor -> nome usado no trabalho
MOTOR_CENIPA = {"PISTÃO": "pistao", "TURBOÉLICE": "turboelice", "JATO": "turbofan"}


def parametros():
    return yaml.safe_load((CONFIG / "parametros.yaml").read_text(encoding="utf-8"))


def ler_cenipa(nome):
    """Lê uma tabela dos dados abertos (ocorrencia, ocorrencia_tipo, aeronave, fator_contribuinte)."""
    caminho = BRUTO / "cenipa" / f"{nome}.csv"
    if not caminho.exists():
        raise FileNotFoundError(f"{caminho} não existe. Rode: python src/01_extrair_bases.py cenipa")
    # Cópia do GitHub vem em latin-1; o portal oficial publica em UTF-8 com BOM.
    try:
        return pd.read_csv(caminho, sep=";", dtype=str, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(caminho, sep=";", dtype=str, encoding="latin-1")


def wilson(k, n, z=1.96):
    """Intervalo de Wilson de 95% para uma proporção k/n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    meia = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, centro - meia), min(1.0, centro + meia))
