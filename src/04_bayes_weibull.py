"""Etapa 4 - Extensões: Gama-Poisson das taxas e teste da taxa constante.

    python src/04_bayes_weibull.py

Só com dados:  Gama-Poisson das taxas (precisa de exposicao_horas em parametros.yaml); sem isso é
               avisado e pulado.
Tempo de motor: forma de Weibull pelo TSO e pelo TSN dos monomotores do NTSB (caso-controle, ver
               estatistica.forma_por_caso_controle) e chance relativa de falha por quartil de tempo.
"""
import pandas as pd

import estatistica as es
import rbd
from comum import MOTORES, PROC, TABELAS, parametros

P = parametros()


def gama_poisson():
    """Taxas absolutas por Gama-Poisson: só com exposicao_horas em parametros.yaml."""
    cont = rbd.carregar_contagens()
    lit = rbd.ler_config()[1]
    linhas = []
    for m in MOTORES:
        horas = (P.get("exposicao_horas") or {}).get(m)
        n = int(cont[cont["motor"] == m]["n"].sum()) if not cont.empty else 0
        if horas:
            linhas.append({"motor": m, "falhas": n, "horas": horas,
                           **es.gama_poisson(lit.loc[m, "lambda_nom"] * P["unidade_taxa"], 1.0, n, horas)})
    if linhas:
        pd.DataFrame(linhas).to_csv(TABELAS / "taxas_gama_poisson.csv", index=False)
        print("\n== Gama-Poisson das taxas\n" + pd.DataFrame(linhas).to_string(index=False))
    else:
        print("Gama-Poisson das taxas: exposicao_horas não informada em parametros.yaml - pulada "
              "(o NTSB não traz horas voadas da frota).")


MIN_FALHAS = 20  # abaixo disso o teste não é feito (turbofan: quase nenhum monomotor com horas)


def tempo_motor():
    arq = PROC / "ntsb_avioes.csv"
    if not arq.exists():
        print("Tempo de motor: ntsb_avioes.csv ausente (rode a etapa 2) - pulado.")
        return
    b = pd.read_csv(arq)
    b = b[b["n_motores"] == 1]
    caso = b["falha_motor"]
    controle = ~b["falha_motor"] & ~b["combustivel"] & ~b["finding_motopropulsor"]
    forma, faixas = [], []
    for m in MOTORES:
        for var, nome in (("tso_h", "TSO (desde a revisão geral)"), ("tsn_h", "TSN (desde novo)")):
            d = b[(b["motor"] == m) & b[var].notna()]
            tf, tc = d.loc[caso, var], d.loc[controle, var]
            if len(tf) < MIN_FALHAS:
                print(f"Tempo de motor: {m}, {var}: {len(tf)} falhas com horas - pulado (mínimo {MIN_FALHAS}).")
                continue
            forma.append({"motor": m, "tempo": nome, **es.forma_por_caso_controle(tf, tc),
                          "mediana_falhas_h": tf.median(), "mediana_controles_h": tc.median()})
            # sem modelo: quartis do tempo dos controles; razão falhas/controles relativa ao 1º quartil
            q = tc.quantile([0, .25, .5, .75, 1]).to_numpy(copy=True)
            q[0], q[-1] = 0, float("inf")
            cf = pd.cut(tf, q, labels=False).value_counts().sort_index()
            cc = pd.cut(tc, q, labels=False).value_counts().sort_index()
            for i in range(4):
                faixas.append({"motor": m, "tempo": var, "faixa_h": f"{q[i]:.0f} a {q[i + 1]:.0f}", "falhas": int(cf.get(i, 0)),
                               "controles": int(cc.get(i, 0)),
                               "chance_relativa": (cf.get(i, 0) / cc.get(i, 1)) / (cf.get(0, 0) / cc.get(0, 1))})
    if forma:
        forma, faixas = pd.DataFrame(forma), pd.DataFrame(faixas)
        forma.to_csv(TABELAS / "weibull_tempo_motor.csv", index=False)
        faixas.to_csv(TABELAS / "chance_falha_por_tempo.csv", index=False)
        print("\n== Forma de Weibull pelo tempo de motor (monomotores; k = 1 é taxa constante)\n"
              + forma.round(3).to_string(index=False))
        print("\n== Chance relativa de falha por quartil de tempo (1º quartil = 1)\n" + faixas.round(2).to_string(index=False))


if __name__ == "__main__":
    gama_poisson()
    tempo_motor()
