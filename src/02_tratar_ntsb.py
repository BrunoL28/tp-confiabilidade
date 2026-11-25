"""Etapa 2 - Tratamento da base do NTSB (avall: events, aircraft, engines, Findings, Events_Sequence).

    python src/02_tratar_ntsb.py

Uma linha por avião-evento (só aviões com motor a pistão, turboélice ou turbofan; sem construção
amadora se `excluir_construcao_amadora`). Um avião teve falha de motor quando a sequência de eventos
(Events_Sequence) tem um dos códigos de `eventos_falha_motor` e nenhum de `eventos_combustivel`:
perda de potência depois de pane seca é falha operacional, contada à parte.

  data/processed/ntsb_avioes.csv     base tratada (horas do motor só em monomotores), lida pela etapa 5
  data/processed/contagens_ntsb.csv  falhas por bloco do RBD (motor, bloco, n), lida pelas etapas 4 e 5
  saida/tabelas/ntsb_contagens.csv           aviões, falhas, acidentes e incidentes por motor
  saida/tabelas/ntsb_eventos.csv             tipo de evento das falhas por motor
  saida/tabelas/ntsb_prob_fatal.csv          P(evento fatal | falha de motor), monomotor x multimotor
  saida/tabelas/ntsb_combustivel_a_parte.csv falhas operacionais de combustível
  saida/tabelas/ntsb_falhas_por_ano.csv      falhas por ano

Blocos: cada finding de motopropulsor (category_no 01, subcategory_no 04 hélice ou 05 grupo
motopropulsor) de um avião com falha é atribuído a um bloco pelo código section_no + subsection_no
(capítulo e subcapítulo ATA), com o prefixo mais longo de config/mapa_componentes.csv. Códigos que não
dizem o bloco, como "Engine (reciprocating) (general)" (8500) ou "Engine (turbine/turboprop)
(general)" (7200), ficam fora. Um avião conta uma vez por bloco. Erro de uso do piloto
(modifier_no 10 "Not used/operated" e 11 "Incorrect use/operation") não é falha de componente e fica fora.
"""
import numpy as np
import pandas as pd

from comum import BRUTO, GENERICOS, PROC, TABELAS, bloco_por_codigo, parametros, wilson

P = parametros()
CHAVE = ["ev_id", "Aircraft_Key"]
# eng_type do NTSB -> motor do trabalho. GTFN = turbofan com engrenagem. TJ, TS (turboeixo) e ELEC ficam fora.
TIPO_NTSB = {"REC": "pistao", "TP": "turboelice", "TF": "turbofan", "GTFN": "turbofan"}
# Jatos monomotores reais; os demais turbofans com num_eng = 1 são erro de cadastro (o NTSB às vezes lista
# só o motor envolvido: há B747, 777 e A380 com 1 motor) e ficam com número de motores desconhecido.
JATO_MONOMOTOR = r"SF50|L-?39"
EV_MOTOR = {str(k): v for k, v in P["eventos_falha_motor"].items()}
EV_FUEL = {str(k): v for k, v in P["eventos_combustivel"].items()}

# Findings de motopropulsor: Aircraft (01) > propeller/rotor (04) ou power plant (05)
SUBCATEGORIAS_MOTOPROPULSOR = {"04", "05"}
# modifier_no de erro de uso do piloto: 10 Not used/operated, 11 Incorrect use/operation
MODIFICADOR_OPERACAO = {"10", "11"}


def ler(nome, **kw):
    arq = BRUTO / "ntsb" / f"{nome}.csv"
    if not arq.exists():
        raise FileNotFoundError(f"{arq} não existe. Rode: python src/01_extrair_ntsb.py")
    df = pd.read_csv(arq, dtype=str, low_memory=False, **kw)
    return df.apply(lambda s: s.str.strip())


def horas(s):
    """Horas do motor: 0 no NTSB quer dizer 'não informado'."""
    h = pd.to_numeric(s, errors="coerce")
    return h.where(h > 0)


def findings_motopropulsor():
    fd = ler("Findings", usecols=CHAVE + ["category_no", "subcategory_no", "section_no", "subsection_no",
                                          "modifier_no", "finding_description"])
    fd = fd[fd["category_no"].eq("01") & fd["subcategory_no"].isin(SUBCATEGORIAS_MOTOPROPULSOR)].copy()
    fd["codigo"] = fd["section_no"].str.zfill(2) + fd["subsection_no"].str.zfill(2)
    return fd


def montar_base():
    ev = ler("events", usecols=["ev_id", "ntsb_no", "ev_type", "ev_year", "ev_country", "ev_highest_injury"])
    ac = ler("aircraft", usecols=CHAVE + ["acft_category", "homebuilt", "far_part", "num_eng", "damage",
                                          "acft_make", "acft_model"])
    eg = ler("engines", usecols=CHAVE + ["eng_no", "eng_type", "eng_mfgr", "eng_model",
                                         "eng_time_total", "eng_time_overhaul"])
    sq = ler("Events_Sequence", usecols=CHAVE + ["eventsoe_no", "Defining_ev"])

    ac = ac[ac["acft_category"] == "AIR"]
    n_amador = int(ac["homebuilt"].eq("Y").sum())
    if P["excluir_construcao_amadora"]:
        ac = ac[ac["homebuilt"] != "Y"]

    eg["motor"] = eg["eng_type"].map(TIPO_NTSB)
    tipos = eg.groupby(CHAVE)["motor"].agg(lambda s: "|".join(sorted(set(s.dropna()))))
    mot = eg.dropna(subset=["motor"]).sort_values("eng_no").groupby(CHAVE).agg(
        motor=("motor", "first"), linhas_motor=("eng_no", "size"), fabricante_motor=("eng_mfgr", "first"),
        modelo_motor=("eng_model", "first"), tsn_h=("eng_time_total", "first"), tso_h=("eng_time_overhaul", "first"))
    mot = mot[tipos.reindex(mot.index).str.count(r"\|").eq(0)]  # descarta aviões com tipos de motor misturados

    base = ac.merge(mot.reset_index(), on=CHAVE).merge(ev, on="ev_id", how="left")
    base["n_motores"] = pd.to_numeric(base["num_eng"], errors="coerce")
    base["n_motores"] = base["n_motores"].where(base["n_motores"] > 0, base["linhas_motor"]).astype("Int64")
    erro_jato = (base["motor"] == "turbofan") & (base["n_motores"] == 1) & \
        ~base["acft_model"].str.contains(JATO_MONOMOTOR, case=False, na=False)
    base.loc[erro_jato, "n_motores"] = pd.NA
    base["ano"] = pd.to_numeric(base["ev_year"], errors="coerce").astype("Int64")
    base["acidente"] = base["ev_type"].eq("ACC")
    base["fatal"] = base["ev_highest_injury"].eq("FATL")

    # horas do motor: só em monomotor se sabe qual motor é o da falha
    for c in ("tsn_h", "tso_h"):
        base[c] = horas(base[c]).where(base["n_motores"].eq(1).fillna(False))
    incoerente = base["tso_h"] > base["tsn_h"]
    base.loc[incoerente, ["tsn_h", "tso_h"]] = np.nan

    # sequência de eventos
    sq = sq[sq["eventsoe_no"].isin(EV_MOTOR.keys() | EV_FUEL.keys())]
    por = sq.groupby(CHAVE)["eventsoe_no"].agg(set)
    base = base.merge(por.rename("codigos").reset_index(), on=CHAVE, how="left")
    cod = base["codigos"].apply(lambda s: s if isinstance(s, set) else set())
    base["eventos_motor"] = cod.apply(lambda s: "|".join(EV_MOTOR[c] for c in sorted(s) if c in EV_MOTOR))
    base["combustivel"] = cod.apply(lambda s: bool(s & EV_FUEL.keys()))
    base["falha_motor"] = base["eventos_motor"].ne("") & ~base["combustivel"]
    pp = findings_motopropulsor()[CHAVE]
    base["finding_motopropulsor"] = base.set_index(CHAVE).index.isin(pd.MultiIndex.from_frame(pp.drop_duplicates()))
    base = base.drop(columns=["codigos", "num_eng", "ev_year", "linhas_motor", "acft_category"])

    print(f"NTSB: {len(base)} avião-eventos (pistão, turboélice, turbofan), anos {base['ano'].min()} a {base['ano'].max()}"
          f"; {n_amador} de construção amadora {'excluídos' if P['excluir_construcao_amadora'] else 'mantidos'}; "
          f"{int(incoerente.sum())} com TSO > TSN descartados; {int(erro_jato.sum())} turbofans com num_eng = 1 "
          f"tratados como número de motores desconhecido")
    return base


def contar_blocos(base):
    fd = findings_motopropulsor().merge(base.loc[base["falha_motor"], CHAVE + ["motor"]], on=CHAVE)
    oper = fd["modifier_no"].isin(MODIFICADOR_OPERACAO)
    fd = fd[~oper].copy()
    fd["bloco"] = [bloco_por_codigo(c, m) for c, m in zip(fd["codigo"], fd["motor"])]
    sem = fd["bloco"].isna()
    generico = sem & fd["codigo"].isin(GENERICOS)
    print(f"Findings de motopropulsor nos aviões com falha: {len(fd)} ({int(oper.sum())} de operação descartados; "
          f"sem bloco: {int(generico.sum())} genéricos, sem componente, e {int((sem & ~generico).sum())} "
          f"de componentes fora do modelo)")
    fd = fd.dropna(subset=["bloco"]).drop_duplicates(subset=CHAVE + ["bloco"])
    return fd.groupby(["motor", "bloco"]).size().rename("n").reset_index()


def tabela_prob_fatal(base):
    linhas = []

    def linha(motor, grupo, d):
        n, k = len(d), int(d["fatal"].sum())
        lo, hi = wilson(k, n)
        linhas.append(dict(motor=motor, grupo=grupo, eventos=n, fatais=k, acidentes=int(d["acidente"].sum()),
                           p_fatal=k / n if n else float("nan"), ic95_inf=lo, ic95_sup=hi))

    for motor, d in base.groupby("motor"):
        f = d[d["falha_motor"]]
        linha(motor, "falha de motor", f)
        linha(motor, "monomotor", f[f["n_motores"] == 1])
        linha(motor, "multimotor", f[f["n_motores"] >= 2])
        linha(motor, "qualquer evento (referência)", d)
    return pd.DataFrame(linhas)


def main():
    base = montar_base()
    base.to_csv(PROC / "ntsb_avioes.csv", index=False)
    cont_blocos = contar_blocos(base)
    cont_blocos.to_csv(PROC / "contagens_ntsb.csv", index=False)

    f = base[base["falha_motor"]]
    cont = base.groupby("motor").agg(avioes=("ev_id", "size")).join(
        f.groupby("motor").agg(falhas=("ev_id", "size"), acidentes=("acidente", "sum"),
                               monomotor=("n_motores", lambda s: int((s == 1).sum())),
                               com_tso=("tso_h", "count"), com_tsn=("tsn_h", "count"))).reset_index()
    cont.to_csv(TABELAS / "ntsb_contagens.csv", index=False)

    ev = f.assign(evento=f["eventos_motor"].str.split("|")).explode("evento")
    ev = pd.crosstab(ev["evento"], ev["motor"]).reindex(EV_MOTOR.values(), fill_value=0)
    ev.to_csv(TABELAS / "ntsb_eventos.csv")

    prob = tabela_prob_fatal(base)
    prob.to_csv(TABELAS / "ntsb_prob_fatal.csv", index=False)

    fuel = base[base["combustivel"]].groupby("motor").agg(ocorrencias=("ev_id", "size"),
                                                          fatais=("fatal", "sum")).reset_index()
    fuel.to_csv(TABELAS / "ntsb_combustivel_a_parte.csv", index=False)
    pd.crosstab(f["ano"], f["motor"]).to_csv(TABELAS / "ntsb_falhas_por_ano.csv")

    pd.set_option("display.width", 200)
    for titulo, t in [("Aviões e falhas de motor", cont), ("Tipo de evento nas falhas", ev),
                      ("P(evento fatal | falha de motor)", prob.round(3)), ("Combustível, à parte", fuel),
                      ("Falhas por bloco", cont_blocos.pivot(index="bloco", columns="motor", values="n").fillna(0).astype(int))]:
        print(f"\n== {titulo}\n{t.to_string()}")


if __name__ == "__main__":
    main()
