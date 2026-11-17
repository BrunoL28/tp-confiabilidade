"""Etapa 2 - Tratamento dos dados abertos do CENIPA.

Monta uma linha por aeronave-ocorrência (somente aviões a pistão, turboélice e jato), marca as
ocorrências SCF-PP (falha ou mau funcionamento do grupo motopropulsor) e gera as tabelas que
dependem só da base aberta:

  cenipa_contagens.csv            ocorrências SCF-PP e relatórios finais por tipo de motor
  cenipa_subtipos.csv             subtipos SCF-PP (em voo, no solo, hélice...) por tipo de motor
  cenipa_prob_acidente.csv        P(acidente | falha de motor), por motor e nº de motores
  cenipa_origem.csv               origem das falhas com relatório final (fatores contribuintes)
  cenipa_combustivel_a_parte.csv  falhas operacionais (pane seca / combustível), contadas à parte

    python src/02_tratar_cenipa.py
"""
import pandas as pd

from comum import MOTOR_CENIPA, PROC, TABELAS, ler_cenipa, wilson

AUSENTE = ["***", "**", "****", "DESCONHECIDO", "NULL", ""]


def montar_base():
    oc = ler_cenipa("ocorrencia").replace(AUSENTE, pd.NA)
    tp = ler_cenipa("ocorrencia_tipo")
    an = ler_cenipa("aeronave").replace(AUSENTE, pd.NA)

    oc["data"] = pd.to_datetime(oc["ocorrencia_dia"], format="%d/%m/%Y", errors="coerce")
    oc["ano"] = oc["data"].dt.year
    oc["tem_relatorio"] = oc["divulgacao_relatorio_publicado"].eq("SIM")
    oc = oc[["codigo_ocorrencia", "ocorrencia_classificacao", "data", "ano", "ocorrencia_uf",
             "divulgacao_relatorio_numero", "tem_relatorio", "total_aeronaves_envolvidas"]]

    # Uma ocorrência pode ter vários tipos: resume em marcações por ocorrência
    tp["taxonomia_tipo_icao"] = tp["taxonomia_tipo_icao"].str.strip()
    por_oc = tp.groupby("codigo_ocorrencia1").agg(
        taxonomias=("taxonomia_tipo_icao", lambda s: "|".join(sorted(set(s.dropna())))),
        tipos=("ocorrencia_tipo", lambda s: "|".join(sorted(set(s.dropna())))),
    )
    pp = tp[tp["taxonomia_tipo_icao"] == "SCF-PP"].groupby("codigo_ocorrencia1")["ocorrencia_tipo"] \
        .agg(lambda s: "|".join(sorted(set(s))))
    por_oc["scf_pp"] = por_oc.index.isin(pp.index)
    por_oc["subtipo_scf_pp"] = pp
    por_oc["combustivel"] = por_oc["taxonomias"].str.split("|").apply(lambda x: "FUEL" in x)

    an = an[an["aeronave_tipo_equipamento"] == "AVIÃO"].copy()
    an["motor"] = an["aeronave_motor_tipo"].map(MOTOR_CENIPA)
    an = an.dropna(subset=["motor"])
    an["n_motores"] = pd.to_numeric(an["anv_motor_qtd"], errors="coerce")
    an["fatalidades"] = pd.to_numeric(an["aeronave_fatalidades_total"], errors="coerce").fillna(0).astype(int)
    an = an[["codigo_ocorrencia2", "aeronave_matricula", "aeronave_fabricante", "aeronave_modelo", "motor",
             "n_motores", "aeronave_ano_fabricacao", "aeronave_fase_operacao", "aeronave_tipo_operacao",
             "aeronave_nivel_dano", "fatalidades"]]

    base = an.merge(oc, left_on="codigo_ocorrencia2", right_on="codigo_ocorrencia", how="inner") \
        .merge(por_oc, left_on="codigo_ocorrencia", right_index=True, how="left").drop(columns="codigo_ocorrencia2")
    base["scf_pp"] = base["scf_pp"].fillna(False).astype(bool)
    base["combustivel"] = base["combustivel"].fillna(False).astype(bool)
    base["acidente"] = base["ocorrencia_classificacao"].eq("ACIDENTE")
    antes = len(base)
    base = base.drop_duplicates(subset=["codigo_ocorrencia", "aeronave_matricula"])
    print(f"Aviões (pistão, turboélice, jato): {len(base)} aeronave-ocorrências "
          f"({antes - len(base)} duplicatas removidas), {base['data'].min():%d/%m/%Y} a {base['data'].max():%d/%m/%Y}")
    return base


def tabela_prob_acidente(pp):
    linhas = []

    def linha(motor, grupo, d):
        n, k = len(d), int(d["acidente"].sum())
        lo, hi = wilson(k, n)
        linhas.append(dict(motor=motor, grupo=grupo, falhas=n, acidentes=k,
                           incidentes_graves=int(d["ocorrencia_classificacao"].eq("INCIDENTE GRAVE").sum()),
                           fatais=int((d["fatalidades"] > 0).sum()),
                           p_acidente=k / n if n else float("nan"), ic95_inf=lo, ic95_sup=hi))

    for motor, d in pp.groupby("motor"):
        linha(motor, "todos", d)
        linha(motor, "monomotor", d[d["n_motores"] == 1])
        linha(motor, "multimotor", d[d["n_motores"] >= 2])
        linha(motor, "somente falha em voo", d[d["subtipo_scf_pp"].str.contains("FALHA DO MOTOR EM VOO", na=False)])
    return pd.DataFrame(linhas)


def tabela_origem(pp):
    """Origem das falhas segundo os fatores contribuintes dos relatórios finais (não exclusivas)."""
    ft = ler_cenipa("fator_contribuinte")
    ft = ft[ft["codigo_ocorrencia3"].isin(pp["codigo_ocorrencia"])]
    marca = {
        "projeto": ft["fator_nome"].eq("PROJETO"),
        "fabricacao": ft["fator_nome"].isin(["FABRICAÇÃO", "MANUSEIO DO MATERIAL"]),
        "manutencao": ft["fator_nome"].eq("MANUTENÇÃO DA AERONAVE"),
        "operacao": ft["fator_condicionante"].eq("OPERAÇÃO DA AERONAVE"),
    }
    cod = {k: set(ft.loc[m, "codigo_ocorrencia3"]) for k, m in marca.items()}
    com_fator = set(ft["codigo_ocorrencia3"])
    rel = pp[pp["tem_relatorio"]]
    linhas = []
    for motor, d in rel.groupby("motor"):
        n = len(d)
        r = dict(motor=motor, relatorios=n)
        for k, s in cod.items():
            r[k] = int(d["codigo_ocorrencia"].isin(s).sum())
        r["sem_fator_registrado"] = int((~d["codigo_ocorrencia"].isin(com_fator)).sum())
        linhas.append(r)
    return pd.DataFrame(linhas)


def main():
    base = montar_base()
    base.to_csv(PROC / "cenipa_avioes.csv", index=False)
    pp = base[base["scf_pp"]].copy()
    pp.to_csv(PROC / "cenipa_scf_pp.csv", index=False)

    cont = pp.groupby("motor").agg(
        ocorrencias_scf_pp=("codigo_ocorrencia", "size"), com_relatorio_final=("tem_relatorio", "sum"),
        tambem_combustivel=("combustivel", "sum")).reset_index()
    cont.to_csv(TABELAS / "cenipa_contagens.csv", index=False)

    sub = pp.assign(subtipo=pp["subtipo_scf_pp"].str.split("|")).explode("subtipo")
    pd.crosstab(sub["subtipo"], sub["motor"]).to_csv(TABELAS / "cenipa_subtipos.csv")

    prob = tabela_prob_acidente(pp)
    prob.to_csv(TABELAS / "cenipa_prob_acidente.csv", index=False)
    origem = tabela_origem(pp)
    origem.to_csv(TABELAS / "cenipa_origem.csv", index=False)

    # Falhas operacionais de combustível (pane seca etc.): fora do modelo, contadas à parte
    fuel = base[base["combustivel"]]
    fuel_t = fuel.groupby("motor").agg(ocorrencias=("codigo_ocorrencia", "size"), acidentes=("acidente", "sum"),
                                       tambem_scf_pp=("scf_pp", "sum")).reset_index()
    fuel_t.to_csv(TABELAS / "cenipa_combustivel_a_parte.csv", index=False)

    pd.crosstab(pp["ano"], pp["motor"]).to_csv(TABELAS / "cenipa_scf_pp_por_ano.csv")

    pd.set_option("display.width", 200)
    for titulo, t in [("SCF-PP por tipo de motor", cont), ("P(acidente | falha de motor)", prob.round(3)),
                      ("Origem (relatórios finais)", origem), ("Combustível, à parte", fuel_t)]:
        print(f"\n== {titulo}\n{t.to_string(index=False)}")


if __name__ == "__main__":
    main()
