"""Etapa 6 - Extensões: rede bayesiana, atualização das frações e taxas, Weibull e consistência.

    python src/06_bayes_weibull.py

Sempre roda:   diagnóstico (dada a falha do motor, qual subsistema é a causa mais provável) e
               previsão com evidência (risco no voo com uma unidade redundante já inoperante).
Só com dados:  atualização das frações (precisa de contagens por bloco), Gama-Poisson das taxas
               (precisa de exposicao_horas em parametros.yaml), Weibull (precisa de TSO na planilha)
               e kappa de Cohen (precisa das classificações duplas). O que faltar é avisado e pulado.
"""
import pandas as pd

import estatistica as es
import rbd
import rede_bayesiana as rb
from comum import MOTORES, PROC, TABELAS, parametros

P = parametros()


def rede():
    diag, prev = [], []
    for m in MOTORES:
        M = rbd.construir(m)
        for t in P["missoes_h"]:
            d, pf = rb.diagnostico(M, float(t))
            assert abs(pf - float(M.F(t))) < 1e-9 * max(pf, 1e-300) + 1e-15, "rede e RBD divergem"
            diag.append(d.assign(motor=m, t_h=t, p_falha_motor=pf))
        base = rb.previsao(M, {}, 1.0)
        for p in M.pares:
            com = rb.previsao(M, {f"{p.nome}:A": 1}, 1.0)
            prev.append(dict(motor=m, evidencia=f"uma unidade de {p.rotulo} já inoperante", p_falha_1h_sem_evidencia=base,
                             p_falha_1h_com_evidencia=com, fator=com / base))
    diag = pd.concat(diag, ignore_index=True)[["motor", "t_h", "no", "rotulo", "p_priori", "p_dado_falha", "p_falha_motor"]]
    diag.to_csv(TABELAS / "rede_bayesiana_diagnostico.csv", index=False)
    prev = pd.DataFrame(prev)
    prev.to_csv(TABELAS / "rede_bayesiana_previsao.csv", index=False)
    print("== Diagnóstico: P(subsistema falhou | motor falhou em 1 h), três mais prováveis")
    print(diag[diag["t_h"] == 1].groupby("motor", sort=False).head(3)[["motor", "rotulo", "p_dado_falha"]].round(3).to_string(index=False))
    print("\n== Previsão com evidência\n" + prev.to_string(index=False, float_format=lambda v: f"{v:.3g}"))


def atualizacoes():
    cont = rbd.carregar_contagens()
    blocos, lit = rbd.ler_config()
    if cont.empty:
        print("\nAtualização das frações: sem contagens (planilha do CENIPA vazia, SDRS e NTSB ausentes) - pulada.")
    else:
        partes = []
        for m in MOTORES:
            s = blocos[(blocos["motor"] == m) & (blocos["estrutura"] == "serie")]
            n = s["bloco"].map(cont[cont["motor"] == m].groupby("bloco")["n"].sum()).fillna(0)
            if n.sum() == 0:
                continue
            post = es.atualizar_fracoes(s["frac_nom"] / s["frac_nom"].sum(), n, P["forca_prior"])
            partes.append(post.assign(motor=m, bloco=s["bloco"].values))
        if partes:
            pd.concat(partes).to_csv(TABELAS / "fracoes_posteriori.csv", index=False)
            print("\n== Frações: prior (provisório) x posteriori\n" + pd.concat(partes).round(3).to_string(index=False))
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
              "(o CENIPA não traz horas voadas; as contagens precisam vir de uma frota com horas conhecidas).")


def planilha():
    arq = PROC / "planilha_relatorios.xlsx"
    if not arq.exists():
        print("Planilha de relatórios não encontrada - Weibull e kappa pulados.")
        return
    p = pd.read_excel(arq, sheet_name="relatorios", dtype=str).fillna("")
    tso = pd.to_numeric(p["tso_h"].str.replace(",", "."), errors="coerce")
    res = []
    for m in MOTORES:
        r = es.ajustar_weibull(tso[p["motor"] == m].dropna().tolist())
        if r:
            res.append({"motor": m, **r})
    if res:
        pd.DataFrame(res).to_csv(TABELAS / "weibull_tso.csv", index=False)
        print("\n== Weibull do TSO (indicativo: só motores que falharam)\n" + pd.DataFrame(res).round(3).to_string(index=False))
    else:
        print("Weibull: menos de 8 valores de TSO por motor na planilha - pulado.")
    d = p[(p["dupla"] == "S") & (p["bloco_rbd"] != "") & (p["bloco_rbd_2"] != "")]
    if len(d) >= 5:
        k = pd.DataFrame([{"campo": "bloco_rbd", **es.kappa_cohen(d["bloco_rbd"], d["bloco_rbd_2"])},
                          {"campo": "origem", **es.kappa_cohen(d["origem"], d["origem_2"])}])
        k.to_csv(TABELAS / "consistencia_kappa.csv", index=False)
        print("\n== Consistência da classificação dupla\n" + k.round(3).to_string(index=False))
    else:
        print("Kappa: classificações duplas ainda não preenchidas - pulado.")


if __name__ == "__main__":
    rede()
    atualizacoes()
    planilha()
