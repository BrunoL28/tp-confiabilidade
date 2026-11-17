"""Etapa 1 - Extração das bases públicas.

    python src/01_extrair_bases.py cenipa     # dados abertos do CENIPA (4 CSV)
    python src/01_extrair_bases.py cenipa /mnt/c/Users/<voce>/Downloads   # importa CSV baixados no navegador
    python src/01_extrair_bases.py ntsb       # base avall.zip do NTSB (Access .mdb)
    python src/01_extrair_bases.py sdrs       # instruções: o SDRS só exporta pela consulta web

Nada aqui contorna bloqueio de site: se o download direto falhar, o script diz qual arquivo
baixar à mão e em que pasta colocá-lo. As etapas seguintes só leem data/raw/.
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import requests

from comum import BRUTO

TABELAS_CENIPA = ["ocorrencia", "ocorrencia_tipo", "aeronave", "fator_contribuinte"]
# Endereços em que o CENIPA já publicou os CSV; o portal muda de tempos em tempos.
BASES_CENIPA = [
    "https://sistema.cenipa.fab.mil.br/cenipa/media/opendata/",
]
PORTAL_CENIPA = "https://dados.gov.br/dados/conjuntos-dados/ocorrencias-aeronauticas-da-aviacao-civil-brasileira"
NTSB_ZIP = "https://data.ntsb.gov/avdata/FileDirectory/DownloadFile?fileID=C%3A%5Cavdata%5Cavall.zip"
TABELAS_NTSB = ["events", "aircraft", "engines", "Findings", "Occurrences"]


def baixar(url, destino, minimo=1000):
    r = requests.get(url, timeout=120, headers={"User-Agent": "tp-confiabilidade-ufmg"})
    if r.headers.get("cf-mitigated") == "challenge":
        raise RuntimeError("bloqueado pelo desafio anti-robô do Cloudflare; o arquivo só sai pelo navegador")
    r.raise_for_status()
    if len(r.content) < minimo or b"<html" in r.content[:500].lower():
        raise ValueError("resposta não é o arquivo esperado (página HTML ou vazia)")
    destino.write_bytes(r.content)
    return len(r.content)


def validar_csv_cenipa(dados):
    if b"<html" in dados[:500].lower() or b";" not in dados[:2000]:
        raise ValueError("não parece o CSV do CENIPA (HTML ou sem separador ';')")


def importar_cenipa(origem, pasta):
    """Copia para data/raw/cenipa os CSV baixados à mão, conferindo cada um."""
    importados = 0
    for nome in TABELAS_CENIPA:
        arq = Path(origem) / f"{nome}.csv"
        try:
            validar_csv_cenipa(arq.read_bytes()[:2000])
        except Exception as e:
            print(f"  {nome}.csv: ignorado ({e})")
            continue
        shutil.copyfile(arq, pasta / f"{nome}.csv")
        print(f"  {nome}.csv: importado de {arq}")
        importados += 1
    if importados < len(TABELAS_CENIPA):
        print("Importação parcial: FONTE.txt não foi alterado (pasta mistura fontes).")
        return
    (pasta / "FONTE.txt").write_text(
        f"Baixado manualmente do portal do CENIPA e importado de {origem} por 01_extrair_bases.py.\n", encoding="utf-8")


def cenipa(origem=None):
    pasta = BRUTO / "cenipa"
    pasta.mkdir(parents=True, exist_ok=True)
    if origem:
        return importar_cenipa(origem, pasta)
    falhou = []
    for nome in TABELAS_CENIPA:
        ok = False
        for base in BASES_CENIPA:
            try:
                tmp = pasta / f"{nome}.csv.novo"
                n = baixar(f"{base}{nome}.csv", tmp)
                validar_csv_cenipa(tmp.read_bytes()[:2000])
                tmp.replace(pasta / f"{nome}.csv")
                print(f"  {nome}.csv: {n/1e6:.1f} MB de {base}")
                ok = True
                break
            except Exception as e:  # tenta o próximo endereço
                print(f"  {nome}.csv: falhou em {base} ({e})")
        if not ok:
            falhou.append(nome)
    if falhou:
        print(f"\nNão foi possível baixar: {', '.join(falhou)}.")
        print(f"Baixe pelo navegador em {PORTAL_CENIPA} (ou nos links acima) e rode:")
        print("  python src/01_extrair_bases.py cenipa <pasta onde os CSV foram salvos>")
        print("A cópia que já está na pasta (ver FONTE.txt) continua sendo usada enquanto isso.")
    else:
        (pasta / "FONTE.txt").write_text("Baixado do portal do CENIPA por 01_extrair_bases.py.\n", encoding="utf-8")


def ntsb():
    pasta = BRUTO / "ntsb"
    pasta.mkdir(parents=True, exist_ok=True)
    zip_ = pasta / "avall.zip"
    if not zip_.exists():
        try:
            print(f"  avall.zip: {baixar(NTSB_ZIP, zip_, 10**6)/1e6:.0f} MB")
        except Exception as e:
            print(f"Download falhou ({e}). Baixe avall.zip em https://data.ntsb.gov/avdata/ e salve em {pasta}/.")
            return
    with zipfile.ZipFile(zip_) as z:
        z.extractall(pasta)
    mdb = next(pasta.glob("*.mdb"), None)
    if mdb is None:
        print("avall.zip não contém .mdb; confira o arquivo.")
        return
    if shutil.which("mdb-export") is None:
        print("Instale o mdbtools (Linux: apt install mdbtools; macOS: brew install mdbtools) e rode de novo,")
        print(f"ou exporte no Access as tabelas {TABELAS_NTSB} de {mdb.name} para CSV em {pasta}/.")
        return
    for t in TABELAS_NTSB:
        with open(pasta / f"{t}.csv", "w", encoding="utf-8") as f:
            subprocess.run(["mdb-export", str(mdb), t], stdout=f, check=True)
        print(f"  {t}.csv exportada")


def sdrs():
    pasta = BRUTO / "sdrs"
    pasta.mkdir(parents=True, exist_ok=True)
    print(f"""O SDRS (https://sdrs.faa.gov/Query.aspx) não tem download em lote; a consulta é feita no site.
Os campos de texto aceitam o curinga %. Faça uma consulta por motor:

  motor        Engine Make   Engine Model   salvar como
  pistao       %LYC%         %540%          pistao_lycoming540.csv
  turboelice   (vazio)       PT6A34%        turboelice_pt6a34.csv
  turbofan     (vazio)       CFM567%        turbofan_cfm56_7.csv

  - O SDRS grava o modelo sem hífen (PT6A34, CFM567B); "PT6A-34%" e "%PRATT%" não retornam nada.
  - Difficulty Date From/To: 01/01/2007 a 12/31/2025 (mesmo período do CENIPA). O site para em
    1.000 registros por consulta: consulte ano a ano (o CFM56-7 tem ~500 por ano).
  - JASC (ATA) Code: deixe em branco; a etapa 4 descarta o que não for do grupo motopropulsor.
    Se vier registro demais, refaça por grupo: 72%, 73%, 74%, 79%, 61%...
  - Problem Description: não preencha (deixa a consulta lenta).
  - Se o fabricante não retornar nada, consulte só pelo modelo e veja como o Engine Make aparece no resultado.
Exporte o resultado (ou copie a tabela para uma planilha) e salve em {pasta}/.
O prefixo do nome (pistao_, turboelice_, turbofan_) indica o motor, e o arquivo precisa ter uma coluna com "jasc" no nome.
Depois rode: python src/04_tratar_ntsb_sdrs.py""")


if __name__ == "__main__":
    alvo = sys.argv[1] if len(sys.argv) > 1 else ""
    if alvo == "cenipa":
        cenipa(sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        {"ntsb": ntsb, "sdrs": sdrs}.get(alvo, lambda: print(__doc__))()
