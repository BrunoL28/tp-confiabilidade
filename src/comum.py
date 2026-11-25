"""Caminhos, leitura das tabelas e utilidades compartilhadas pelos scripts."""
from functools import cache
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


def parametros():
    return yaml.safe_load((CONFIG / "parametros.yaml").read_text(encoding="utf-8"))


# Código de componente (4 dígitos, capítulo e subcapítulo ATA) -> bloco do RBD. O mesmo esquema serve
# para os findings do NTSB (section_no + subsection_no) e para o código JASC do SDRS.
# "(general)" de seções que cobrem vários blocos não diz o componente e fica fora de n_i/N.
GENERICOS = {"0000", "7100", "7200", "7300", "8500"}


@cache
def _mapa():
    return pd.read_csv(CONFIG / "mapa_componentes.csv", dtype=str).set_index("codigo")


def bloco_por_codigo(codigo, motor):
    """Bloco do RBD pelo prefixo mais longo de config/mapa_componentes.csv. Um prefixo sem bloco para o
    motor cai para o prefixo mais curto (ex.: 7322 no turboélice usa 732). None: genérico ou fora do modelo."""
    mapa = _mapa()
    codigo = str(codigo)
    for n in (4, 3, 2):
        p = codigo[:n]
        if p in mapa.index and isinstance(mapa.at[p, motor], str):
            return mapa.at[p, motor]
    return None


def wilson(k, n, z=1.96):
    """Intervalo de Wilson de 95% para uma proporção k/n."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    meia = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (max(0.0, centro - meia), min(1.0, centro + meia))
