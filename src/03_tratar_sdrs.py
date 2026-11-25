"""Etapa 3 - Registros por bloco do RBD no SDRS (Service Difficulty Reporting System, FAA).

    python src/03_tratar_sdrs.py

O SDRS reúne os relatos de dificuldade em serviço que oficinas e operadores enviam à FAA, com o código
JASC (capítulo e subcapítulo ATA) do componente. Cada relato é atribuído a um bloco pelo mesmo mapa
dos achados do NTSB (config/mapa_componentes.csv, prefixo mais longo). As contagens dão as frações
n_i/N que repartem a taxa total da literatura entre os blocos (λ_i = λ × n_i/N) e a taxa das unidades
redundantes, quando `fonte_fracoes: sdrs` em parametros.yaml.

Entrada: data/raw/sdrs/{pistao,turboelice,turbofan}_*.csv, um arquivo por motor, exportados do site
(o prefixo do nome indica o motor). Filtros de `sdrs` em parametros.yaml: ano mínimo e modelos excluídos
(helicópteros, porque o NTSB só usa aviões). Códigos genéricos (comum.GENERICOS, ex.: 7200, 8500) e
componentes sem bloco no RBD (escapamento, partida, indicação, sistemas da célula) ficam fora.

  data/processed/contagens_sdrs.csv  relatos por bloco do RBD (motor, bloco, n), lida pela etapa 4
  saida/tabelas/sdrs_contagens.csv   relatos por motor em cada filtro e parcela do maior operador
"""
import re

import pandas as pd

from comum import BRUTO, GENERICOS, MOTORES, PROC, TABELAS, bloco_por_codigo, parametros

P = parametros()["sdrs"]
PASTA = BRUTO / "sdrs"

INSTRUCOES = f"""O SDRS (https://sdrs.faa.gov/Query.aspx) não tem download em lote; a consulta é feita no site.
Os campos de texto aceitam o curinga %. Faça uma consulta por motor:

  motor        Engine Make   Engine Model   salvar como
  pistao       %LYC%         %540%          pistao_lycoming540.csv
  turboelice   (vazio)       PT6A34%        turboelice_pt6a34.csv
  turbofan     (vazio)       CFM567%        turbofan_cfm56_7.csv

  - O SDRS grava o modelo sem hífen (PT6A34, CFM567B); "PT6A-34%" e "%PRATT%" não retornam nada.
  - Difficulty Date: o site para em 1.000 registros por consulta; consulte ano a ano.
  - JASC (ATA) Code: deixe em branco; esta etapa descarta o que não for do grupo motopropulsor.
Salve em {PASTA}/. O arquivo precisa ter as colunas jasc_code, difficulty_date, aircraft_model e
operator_designator."""


def arquivos():
    """{motor: arquivo} pelo prefixo do nome."""
    achados = {}
    for arq in sorted(PASTA.glob("*.csv")) if PASTA.exists() else []:
        motor = arq.name.split("_")[0].lower()
        if motor in MOTORES:
            achados[motor] = arq
    return achados


def tratar(motor, arq):
    """Devolve (relatos com bloco, linha do resumo)."""
    df = pd.read_csv(arq, dtype=str)
    total = len(df)
    df = df.drop_duplicates()
    duplicados = total - len(df)
    ano = pd.to_datetime(df["difficulty_date"], format="%m/%d/%Y", errors="coerce").dt.year
    antigos = ano < P["ano_inicio"]
    helic = df["aircraft_model"].str.match(P["excluir_modelos"], na=False)
    df = df[~antigos & ~helic].copy()
    df["codigo"] = df["jasc_code"].fillna("").map(lambda c: re.sub(r"\D", "", c))
    df["bloco"] = [bloco_por_codigo(c, motor) for c in df["codigo"]]
    com = df.dropna(subset=["bloco"])
    sem = df["bloco"].isna()
    oper = com["operator_designator"].fillna("").replace("", pd.NA).dropna()
    maior = oper.value_counts()
    resumo = dict(motor=motor, arquivo=arq.name, relatos=total, duplicados=duplicados,
                  antes_de_ano_inicio=int(antigos.sum()), helicopteros=int((helic & ~antigos).sum()),
                  analisados=len(df), com_bloco=len(com), genericos=int((sem & df["codigo"].isin(GENERICOS)).sum()),
                  fora_do_modelo=int((sem & ~df["codigo"].isin(GENERICOS)).sum()),
                  ano_min=int(ano[~antigos].min()), ano_max=int(ano[~antigos].max()),
                  maior_operador=maior.index[0] if len(maior) else "",
                  parcela_maior_operador=maior.iloc[0] / len(com) if len(maior) else float("nan"))
    return com[["bloco"]].assign(motor=motor), resumo


def main():
    achados = arquivos()
    faltando = [m for m in MOTORES if m not in achados]
    if faltando:
        print(f"SDRS: sem arquivo para {', '.join(faltando)} em {PASTA}/ - pulado.\n\n{INSTRUCOES}\n")
    if not achados:
        return
    partes, resumos = [], []
    for motor, arq in achados.items():
        com, resumo = tratar(motor, arq)
        partes.append(com)
        resumos.append(resumo)
    cont = pd.concat(partes).groupby(["motor", "bloco"]).size().rename("n").reset_index()
    cont.to_csv(PROC / "contagens_sdrs.csv", index=False)
    resumo = pd.DataFrame(resumos)
    resumo.to_csv(TABELAS / "sdrs_contagens.csv", index=False)

    pd.set_option("display.width", 200)
    print(f"SDRS: relatos de {P['ano_inicio']} em diante, sem os modelos {P['excluir_modelos']}")
    print("\n== Relatos por motor em cada filtro\n" + resumo.round(3).to_string(index=False))
    print("\n== Relatos por bloco\n"
          + cont.pivot(index="bloco", columns="motor", values="n").fillna(0).astype(int).to_string())


if __name__ == "__main__":
    main()
