"""Roda as etapas que não dependem de download nem de preenchimento manual, na ordem."""
import subprocess
import sys
from pathlib import Path

for etapa in ["02_tratar_cenipa.py", "03_amostra_relatorios.py", "04_tratar_ntsb_sdrs.py",
              "05_analise_confiabilidade.py", "06_bayes_weibull.py"]:
    print(f"\n{'=' * 20} {etapa} {'=' * 20}", flush=True)
    subprocess.run([sys.executable, etapa], cwd=Path(__file__).parent, check=True)
