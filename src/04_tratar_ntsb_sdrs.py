"""Etapa 4 - Contagem de falhas por bloco do RBD no SDRS (FAA) e no NTSB.

    python src/04_tratar_ntsb_sdrs.py

Lê o que existir em data/raw/sdrs/ e data/raw/ntsb/ (ver etapa 1) e grava
data/processed/contagens_sdrs.csv e contagens_ntsb.csv (motor, bloco, n). A etapa 5 soma essas
contagens às da planilha do CENIPA para obter as frações n_i/N. Fontes ausentes são puladas.

SDRS: cada registro é atribuído a um bloco pelo código JASC (config/mapa_jasc.csv, prefixo mais longo).
NTSB: usa os 'findings' do grupo motopropulsor, classificados pelo texto de finding_description, e o
tipo de motor da tabela engines (REC = pistão, TP = turboélice, TF = turbofan).
"""
import re

import pandas as pd

from comum import BRUTO, CONFIG, MOTORES, PROC


# ------------------------------- SDRS -------------------------------
def bloco_por_jasc(codigo, motor, mapa):
    codigo = re.sub(r"\D", "", str(codigo))
    for n in (4, 3, 2):  # prefixo mais longo primeiro
        linha = mapa[mapa["jasc_prefixo"] == codigo[:n]]
        if len(linha) and isinstance(linha.iloc[0][motor], str):
            return linha.iloc[0][motor]
    return None


def tratar_sdrs():
    pasta = BRUTO / "sdrs"
    arquivos = sorted(list(pasta.glob("*.csv")) + list(pasta.glob("*.xls*"))) if pasta.exists() else []
    if not arquivos:
        print("SDRS: nenhum arquivo em data/raw/sdrs/ (rode `01_extrair_bases.py sdrs` para as instruções).")
        return None
    mapa = pd.read_csv(CONFIG / "mapa_jasc.csv", dtype=str)
    linhas, sem_bloco = [], 0
    for arq in arquivos:
        motor = arq.name.split("_")[0].lower()
        if motor not in MOTORES:
            print(f"SDRS: {arq.name} ignorado (o nome deve começar com pistao_, turboelice_ ou turbofan_).")
            continue
        df = pd.read_csv(arq, dtype=str) if arq.suffix == ".csv" else pd.read_excel(arq, dtype=str)
        col = next((c for c in df.columns if "jasc" in c.lower()), None)
        if col is None:
            print(f"SDRS: {arq.name} sem coluna de código JASC; colunas: {list(df.columns)[:8]}")
            continue
        df = df.drop_duplicates()
        blocos = df[col].map(lambda c: bloco_por_jasc(c, motor, mapa))
        sem_bloco += int(blocos.isna().sum())
        linhas.append(pd.DataFrame({"motor": motor, "bloco": blocos.dropna()}))
        print(f"SDRS: {arq.name}: {len(df)} registros, {int(blocos.notna().sum())} com bloco no RBD")
    if not linhas:
        return None
    cont = pd.concat(linhas).groupby(["motor", "bloco"]).size().rename("n").reset_index()
    cont.to_csv(PROC / "contagens_sdrs.csv", index=False)
    print(f"SDRS: {sem_bloco} registros fora dos blocos do modelo (JASC sem correspondência).")
    return cont


# ------------------------------- NTSB -------------------------------
TIPO_NTSB = {"REC": "pistao", "TP": "turboelice", "TF": "turbofan"}
# (expressão no texto do finding, bloco no pistão, no turboélice, no turbofan); a primeira que casar vale
REGRAS_NTSB = [
    (r"propeller|prop governor|governor", "helice_governador", "helice_governador", None),
    (r"magneto|ignition|spark plug", "magnetos", None, None),
    (r"fuel pump", "bombas", "combustivel_fcu", "combustivel"),
    (r"fadec|electronic eng(ine)? control|engine control unit", None, "combustivel_fcu", "fadec"),
    (r"carburetor|fuel inject|fuel control|fuel distrib|fuel nozzle|fuel", "carburador_injecao", "combustivel_fcu", "combustivel"),
    (r"induction|air intake|inlet|turbocharg|supercharg", "admissao", "entrada_ar", "fan"),
    (r"\boil\b|lubricat", "lubrificacao", "lubrificacao", "lubrificacao"),
    (r"cooling|baffle", "arrefecimento", None, None),
    (r"reduction gear", None, "caixa_reducao", None),
    (r"accessory (drive|gear)", "nucleo", "lubrificacao", "caixa_acessorios"),
    (r"\bfan\b", None, None, "fan"),
    (r"compressor", None, "compressor", "compressores"),
    (r"combust", None, "camara_combustao", "camara_combustao"),
    (r"power turbine|free turbine", None, "turbinas", "turbinas"),
    (r"turbine section|turbine", None, "turbinas", "turbinas"),
    (r"recip|cylinder|crankshaft|connecting rod|valve|piston|power section|crankcase|camshaft", "nucleo", None, None),
]


def bloco_ntsb(descricao, motor):
    d = str(descricao).lower()
    i = MOTORES.index(motor) + 1
    for regra in REGRAS_NTSB:
        if re.search(regra[0], d):
            return regra[i]
    return None


def tratar_ntsb():
    pasta = BRUTO / "ntsb"
    if not (pasta / "Findings.csv").exists() or not (pasta / "engines.csv").exists():
        print("NTSB: Findings.csv/engines.csv ausentes em data/raw/ntsb/ (rode `01_extrair_bases.py ntsb`).")
        return None
    fd = pd.read_csv(pasta / "Findings.csv", dtype=str, low_memory=False)
    eg = pd.read_csv(pasta / "engines.csv", dtype=str, low_memory=False)
    eg["motor"] = eg["eng_type"].str.strip().map(TIPO_NTSB)
    eg = eg.dropna(subset=["motor"]).drop_duplicates(subset=["ev_id", "Aircraft_Key"])[["ev_id", "Aircraft_Key", "motor"]]
    # só aviões, como no CENIPA: sem isso o rotor de helicóptero cai em helice_governador
    ac = pd.read_csv(pasta / "aircraft.csv", dtype=str, low_memory=False, usecols=["ev_id", "Aircraft_Key", "acft_category"])
    eg = eg.merge(ac[ac["acft_category"].str.strip() == "AIR"][["ev_id", "Aircraft_Key"]])
    fd = fd[fd["finding_description"].str.contains("power plant|propeller", case=False, na=False)]
    fd = fd.merge(eg, on=["ev_id", "Aircraft_Key"])
    # erro de uso do piloto não é falha do componente (equivale a so_operacional = S na planilha)
    oper = fd["finding_description"].str.contains("Incorrect use/operation|Not used/operated", case=False)
    fd = fd[~oper]
    fd["bloco"] = [bloco_ntsb(d, m) for d, m in zip(fd["finding_description"], fd["motor"])]
    print(f"NTSB: {len(fd)} findings de motopropulsor em aviões ({int(oper.sum())} de operação descartados); "
          f"{int(fd['bloco'].isna().sum())} sem bloco no modelo")
    # um evento conta uma vez por bloco, mesmo com vários findings no mesmo bloco
    fd = fd.dropna(subset=["bloco"]).drop_duplicates(subset=["ev_id", "Aircraft_Key", "bloco"])
    cont = fd.groupby(["motor", "bloco"]).size().rename("n").reset_index()
    cont.to_csv(PROC / "contagens_ntsb.csv", index=False)
    return cont


if __name__ == "__main__":
    for nome, f in (("SDRS", tratar_sdrs), ("NTSB", tratar_ntsb)):
        c = f()
        if c is not None:
            print(f"\n{nome}: contagens por bloco\n{c.pivot(index='bloco', columns='motor', values='n').fillna(0).astype(int)}")
