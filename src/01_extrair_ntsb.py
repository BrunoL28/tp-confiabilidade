"""Etapa 1 - Extração da base do NTSB.

    python src/01_extrair_ntsb.py

Baixa o avall.zip (base Access do NTSB, 2008 em diante), extrai o avall.mdb e exporta para CSV em
data/raw/ntsb/ as tabelas usadas pela etapa 2. Precisa do mdbtools (apt install mdbtools). Se o
download falhar, o script diz onde baixar o arquivo à mão; com o avall.zip ou o avall.mdb já na pasta,
só exporta.
"""
import shutil
import subprocess
import zipfile

import requests

from comum import BRUTO

NTSB_ZIP = "https://data.ntsb.gov/avdata/FileDirectory/DownloadFile?fileID=C%3A%5Cavdata%5Cavall.zip"
# Events_Sequence: tipo de evento (perda de potência, pane seca...). A tabela Occurrences é do esquema
# anterior a 2008 e vem vazia no avall.
TABELAS_NTSB = ["events", "aircraft", "engines", "Findings", "Events_Sequence"]


def baixar(url, destino, minimo=10**6):
    r = requests.get(url, timeout=600, headers={"User-Agent": "tp-confiabilidade"})
    r.raise_for_status()
    if len(r.content) < minimo or b"<html" in r.content[:500].lower():
        raise ValueError("resposta não é o arquivo esperado (página HTML ou vazia)")
    destino.write_bytes(r.content)
    return len(r.content)


def main():
    pasta = BRUTO / "ntsb"
    pasta.mkdir(parents=True, exist_ok=True)
    mdb = next(pasta.glob("*.mdb"), None)
    if mdb is None:
        zip_ = pasta / "avall.zip"
        if not zip_.exists():
            try:
                print(f"  avall.zip: {baixar(NTSB_ZIP, zip_) / 1e6:.0f} MB")
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


if __name__ == "__main__":
    main()
