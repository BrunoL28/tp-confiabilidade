"""Etapa 4 - Métricas de confiabilidade dos três motores (Seção IV da proposta).

    python src/04_analise_confiabilidade.py

A taxa total de cada motor vem da literatura; as frações dos blocos e a taxa das unidades redundantes
vêm das contagens da fonte `fonte_fracoes` (sdrs, etapa 3, ou ntsb, etapa 2).

Tabelas em saida/tabelas/:
  metricas_motores.csv       lambda, MTBF, R(1 h), R(1000 h) por tecnologia
  lambda_blocos.csv          lambda de cada bloco (e de cada unidade dos pares), com faixa
  fracoes_ntsb_vs_sdrs.csv   frações dos blocos e taxa das unidades nas duas fontes, lado a lado
  pareto_blocos.csv          parcela de cada subsistema na falha do motor
  redundancia_interna.csv    efeito de magnetos, bombas e FADEC duplicados
  bimotor_vs_monomotor.csv   dois motores menos confiáveis x um mais confiável
  sensibilidade.csv          efeito das faixas de lambda, beta e taxas de unidade
Figuras (inclui P(fatal | falha de motor) do NTSB, de ntsb_prob_fatal.csv) em saida/figuras/.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from scipy.optimize import brentq

import rbd
from comum import FIGURAS, MOTORES, ROTULO_MOTOR, TABELAS, parametros

COR = {"pistao": "#2a78d6", "turboelice": "#eb6834", "turbofan": "#1baf7a"}
TINTA, TINTA2, GRADE, FUNDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": GRADE, "axes.labelcolor": TINTA2, "text.color": TINTA,
                     "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": FUNDO, "axes.facecolor": FUNDO,
                     "savefig.facecolor": FUNDO, "axes.titlesize": 10, "axes.titleweight": "bold",
                     "axes.titlelocation": "left", "grid.color": GRADE, "grid.linewidth": 0.6})
# Versão das figuras para o artigo (IEEE, coluna de 3,5 pol. ou página de 7,16 pol.): PDF vetorial,
# fundo branco, sem título nem nota de rodapé (a legenda do artigo faz esse papel), fontes TrueType embutidas.
RC_ARTIGO = {"font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
             "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
             "pdf.fonttype": 42, "axes.titlesize": 8}
TRACO = {"pistao": "-", "turboelice": (0, (5, 2)), "turbofan": (0, (1, 1.5))}  # legível em tons de cinza
P = parametros()
U = P["unidade_taxa"]
BLOCOS, LIT = rbd.ler_config()
FONTE_ROTULO = {"sdrs": "relatos de dificuldade em serviço (SDRS, FAA)", "ntsb": "achados de falha de motor (NTSB)"}


def sem_redundancia(motor):
    """Contrafactual: cada par vira uma única unidade em série."""
    extra = [rbd.Bloco(p.nome, p.rotulo.replace("(par)", "(unidade única)"), p.taxa_unidade) for p in motor.pares]
    return rbd.Motor(motor.nome, motor.serie + extra, [], motor.fracoes_provisorias)


# ------------------------------- tabelas -------------------------------
def metricas():
    linhas = []
    for m in MOTORES:
        M, Mc = rbd.construir(m), rbd.construir(m, calibrar=True)  # M segue calibrar_total
        lo, hi = rbd.construir(m, nivel_taxa="min"), rbd.construir(m, nivel_taxa="max")
        le1 = float(M.taxa_equivalente(1))
        linhas.append({
            "motor": m, "lambda_literatura_1e5h": LIT.loc[m, "lambda_nom"],
            "lambda_eq_1h_1e5h": le1 / U, "lambda_eq_1000h_1e5h": float(M.taxa_equivalente(1000)) / U,
            "mtbf_sem_reparo_h": M.mtbf(), "mtbf_redundancia_restaurada_h": 1 / le1,
            "R_1h": float(M.R(1)), "F_1h": float(M.F(1)), "F_1h_lambda_min": float(lo.F(1)),
            "F_1h_lambda_max": float(hi.F(1)), "R_1000h_sem_reparo": float(M.R(1000)),
            "R_1000h_redundancia_restaurada": float(np.exp(-1000 * M.menos_ln_R(1))),
            "F_1h_total_preservado": float(Mc.F(1)), "fracoes_provisorias": M.fracoes_provisorias})
    df = pd.DataFrame(linhas)
    ref = df.set_index("motor")["F_1h"]
    df["razao_para_pistao"] = (ref["pistao"] / df["F_1h"]).values
    return df


def lambda_blocos():
    """λ de cada bloco em série (λ_série × n_i/N) e de cada unidade dos pares, com as taxas nominais.
    Faixa: taxa mínima da literatura com o limite inferior da fração (ou da taxa da unidade) até a
    máxima com o limite superior, como em reparticao.py."""
    fonte = P["fonte_fracoes"]
    cont = rbd.carregar_contagens()
    linhas = []
    for m in MOTORES:
        M = rbd.construir(m)
        lo = rbd.construir(m, nivel_taxa="min", nivel_unidade="min")
        hi = rbd.construir(m, nivel_taxa="max", nivel_unidade="max")
        fr, provisorio = rbd.fracoes_serie(m, BLOCOS)
        N = int(fr["n"].sum())
        taxa = {b.nome: b.taxa for b in M.serie}
        for r in fr.itertuples():
            linhas.append(dict(motor=m, fonte="blocos_rbd.csv" if provisorio else fonte, bloco=r.bloco,
                               rotulo=r.rotulo, estrutura="serie", n=r.n, N_serie=N, fracao=r.frac,
                               fracao_ic_inf=r.frac_min, fracao_ic_sup=r.frac_max,
                               lambda_1e5h=taxa[r.bloco] / U, lambda_inf_1e5h=lo.taxa_serie * r.frac_min / U,
                               lambda_sup_1e5h=hi.taxa_serie * r.frac_max / U))
        for p in M.pares:
            ext = [next(q.taxa_unidade for q in X.pares if q.nome == p.nome) for X in (lo, hi)]
            n = int(cont[(cont["motor"] == m) & (cont["bloco"] == p.nome)]["n"].sum())
            linhas.append(dict(motor=m, fonte=fonte if p.medida else "blocos_rbd.csv", bloco=p.nome,
                               rotulo=p.rotulo.replace("(par)", "(cada unidade)"), estrutura="par redundante",
                               n=n, N_serie=N, fracao=np.nan, fracao_ic_inf=np.nan, fracao_ic_sup=np.nan,
                               lambda_1e5h=p.taxa_unidade / U, lambda_inf_1e5h=ext[0] / U, lambda_sup_1e5h=ext[1] / U))
    return pd.DataFrame(linhas)


def fracoes_por_fonte():
    """Fração de cada bloco em série e taxa de cada unidade redundante com as contagens do NTSB e do SDRS,
    lado a lado. Uma fonte sem contagens (etapa não rodada) fica em branco."""
    partes = []
    for fonte in rbd.FONTES:
        cont = rbd.carregar_contagens(fonte)
        if cont.empty:
            continue
        for m in MOTORES:
            fr, _ = rbd.fracoes_serie(m, BLOCOS, cont)
            d = fr.rename(columns={"frac": "fracao", "frac_min": "ic_inf", "frac_max": "ic_sup"})
            d["lambda_unidade_1e5h"] = np.nan
            M = rbd.construir(m, fonte=fonte)
            pares = pd.DataFrame([dict(bloco=p.nome, rotulo=p.rotulo,
                                       n=int(cont[(cont["motor"] == m) & (cont["bloco"] == p.nome)]["n"].sum()),
                                       lambda_unidade_1e5h=p.taxa_unidade / U) for p in M.pares])
            partes.append(pd.concat([d, pares], ignore_index=True).assign(motor=m, fonte=fonte))
    if not partes:
        return pd.DataFrame()
    longo = pd.concat(partes, ignore_index=True)
    chave = ["motor", "bloco", "rotulo"]
    valores = ["n", "fracao", "ic_inf", "ic_sup", "lambda_unidade_1e5h"]
    largo = longo.set_index(chave + ["fonte"])[valores].unstack("fonte")
    largo.columns = [f"{v}_{f}" for v, f in largo.columns]
    ordem = [f"{v}_{f}" for f in rbd.FONTES for v in valores]
    linhas = pd.MultiIndex.from_frame(longo[chave].drop_duplicates())  # ordem de blocos_rbd.csv
    return largo.reindex(linhas)[[c for c in ordem if c in largo.columns]].reset_index()


def pareto(t=1.0):
    partes = []
    for m in MOTORES:
        M = rbd.construir(m)
        base = M.contribuicoes(t)
        fr, _ = rbd.fracoes_serie(m, BLOCOS)
        fr = fr.set_index("bloco")
        faixa = {}
        for bloco in fr.index:  # varia a fração de um bloco e reescala as demais
            vals = []
            for extremo in ("frac_min", "frac_max"):
                f = fr["frac"].copy()
                resto = 1 - fr.loc[bloco, extremo]
                f = f / (1 - f[bloco]) * resto
                f[bloco] = fr.loc[bloco, extremo]
                c = rbd.construir(m, fracoes=f.to_dict()).contribuicoes(t).set_index("bloco")
                vals.append(c.loc[bloco, "parcela"])
            faixa[bloco] = vals
        for p in M.pares:  # pares: varia a taxa da unidade
            vals = []
            for nivel in ("min", "max"):
                c = rbd.construir(m, nivel_unidade=nivel).contribuicoes(t).set_index("bloco")
                vals.append(c.loc[p.nome, "parcela"])
            faixa[p.nome] = vals
        base["parcela_min"] = base["bloco"].map(lambda b: min(faixa[b]))
        base["parcela_max"] = base["bloco"].map(lambda b: max(faixa[b]))
        base["taxa_1e5h"] = base["contrib"] / t / U
        base["acumulado"] = base["parcela"].cumsum()
        base.insert(0, "motor", m)
        assumida = {q.nome: not q.medida for q in M.pares}
        base["provisorio"] = [assumida.get(b, M.fracoes_provisorias) for b in base["bloco"]]
        partes.append(base.drop(columns="contrib"))
    return pd.concat(partes, ignore_index=True)


def redundancia_interna(t=1.0):
    linhas = []
    for m in MOTORES:
        M = rbd.construir(m)
        S = sem_redundancia(M)
        for p in M.pares:
            f_par = float(-np.expm1(-p.menos_ln_R(t)))
            f_un = float(-np.expm1(-p.taxa_unidade * t))
            cc = float(-np.expm1(-p.beta * p.taxa_unidade * t))
            unico = rbd.Motor(m, M.serie + [rbd.Bloco(p.nome, p.rotulo, p.taxa_unidade)],
                              [q for q in M.pares if q is not p])
            linhas.append({"motor": m, "par": p.rotulo, "taxa_unidade_1e5h": p.taxa_unidade / U, "beta": p.beta,
                           "F_unidade_unica": f_un, "F_par": f_par, "ganho_do_par": f_un / f_par,
                           "parcela_causa_comum": cc / f_par, "F_motor_com_par": float(M.F(t)),
                           "F_motor_sem_este_par": float(unico.F(t)),
                           "aumento_sem_este_par_pct": 100 * (float(unico.F(t)) / float(M.F(t)) - 1),
                           "F_motor_sem_nenhum_par": float(S.F(t))})
    return pd.DataFrame(linhas)


def bimotor(t=1.0):
    lam = {m: float(rbd.construir(m).taxa_equivalente(t)) for m in MOTORES}
    linhas = [{"configuracao": f"1 motor - {ROTULO_MOTOR[m]}", "motor": m, "n_motores": 1, "beta_motores": np.nan,
               "p_perda_total": float(-np.expm1(-lam[m] * t)), "p_alguma_falha_de_motor": float(-np.expm1(-lam[m] * t))}
              for m in MOTORES]
    for m in MOTORES:
        for beta in (0.0, 0.01, 0.05, 0.10, 0.20, 0.30):
            linhas.append({"configuracao": f"2 motores - {ROTULO_MOTOR[m]}", "motor": m, "n_motores": 2,
                           "beta_motores": beta, "p_perda_total": float(1 - rbd.R_dois_motores(lam[m], beta, t)),
                           "p_alguma_falha_de_motor": float(-np.expm1(-(2 - beta) * lam[m] * t))})
    df = pd.DataFrame(linhas)
    # beta de equilíbrio: dois pistões empatam com um motor a turbina
    eq = []
    for alvo in ("turboelice", "turbofan"):
        for nivel in ("min", "nom", "max"):
            la = float(rbd.construir(alvo, nivel_taxa=nivel).taxa_equivalente(t))
            g = lambda b: (1 - rbd.R_dois_motores(lam["pistao"], b, t)) - (-np.expm1(-la * t))
            beta_eq = brentq(g, 0, 1) if g(0) < 0 < g(1) else (np.nan if g(0) >= 0 else 1.0)
            eq.append({"dois_pistoes_contra": f"1 {ROTULO_MOTOR[alvo]}", "nivel_lambda_turbina": nivel,
                       "lambda_turbina_1e5h": la / U, "beta_equilibrio": beta_eq})
    return df, pd.DataFrame(eq)


def sensibilidade(t=1.0):
    linhas = []
    for m in MOTORES:
        nom = float(rbd.construir(m).F(t))

        def reg(par, vmin, vmax, fmin, fmax):
            linhas.append({"motor": m, "parametro": par, "valor_min": vmin, "valor_max": vmax, "F_min": fmin,
                           "F_max": fmax, "F_nominal": nom, "variacao_relativa": max(fmax, fmin) / min(fmax, fmin)})

        reg("taxa total do motor (/1e5 h)", LIT.loc[m, "lambda_min"], LIT.loc[m, "lambda_max"],
            float(rbd.construir(m, nivel_taxa="min").F(t)), float(rbd.construir(m, nivel_taxa="max").F(t)))
        M = rbd.construir(m)
        if M.pares:
            reg("beta dos pares", P["beta"]["min"], P["beta"]["max"],
                float(rbd.construir(m, beta=P["beta"]["min"]).F(t)), float(rbd.construir(m, beta=P["beta"]["max"]).F(t)))
        for p in M.pares:  # faixa medida (intervalo das contagens) ou assumida (blocos_rbd.csv)
            lo, hi = (next(q.taxa_unidade for q in rbd.construir(m, nivel_unidade=n).pares if q.nome == p.nome)
                      for n in ("min", "max"))
            reg(f"taxa da unidade: {p.rotulo} (/1e5 h)", lo / U, hi / U,
                float(rbd.construir(m, taxa_unidade={p.nome: lo}).F(t)), float(rbd.construir(m, taxa_unidade={p.nome: hi}).F(t)))
    return pd.DataFrame(linhas)


# ------------------------------- figuras -------------------------------
def salvar(fig, nome, artigo):
    if artigo:
        (FIGURAS / "artigo").mkdir(exist_ok=True)
        fig.savefig(FIGURAS / "artigo" / f"{nome}.pdf", bbox_inches="tight", pad_inches=0.02)
    else:
        fig.savefig(FIGURAS / f"{nome}.png", dpi=200)
    plt.close(fig)


def nota_provisorio(fig, provisorio):
    if provisorio:
        fig.text(0.01, 0.005, f"Frações por subsistema provisórias (config/blocos_rbd.csv) até a "
                 f"{rbd.FONTES[P['fonte_fracoes']]} ({P['fonte_fracoes'].upper()}) gerar as contagens.",
                 fontsize=7, color=TINTA2, ha="left", va="bottom")


def fig_prob_tempo(artigo=False):
    t = np.logspace(0, 4, 200)
    fig, ax = plt.subplots(figsize=(3.5, 2.45) if artigo else (6.4, 3.8))
    for m in MOTORES:
        ax.fill_between(t, rbd.construir(m, nivel_taxa="min").F(t), rbd.construir(m, nivel_taxa="max").F(t),
                        color=COR[m], alpha=0.13, linewidth=0)
        f = rbd.construir(m).F(t)
        ax.plot(t, f, color=COR[m], linewidth=1.5 if artigo else 2, linestyle=TRACO[m] if artigo else "-")
        ax.annotate(ROTULO_MOTOR[m], (t[-1], f[-1]), xytext=(4 if artigo else 6, {"turbofan": 5, "turboelice": -5}.get(m, 0)),
                    textcoords="offset points", va="center",
                    fontsize=7 if artigo else 9, color=TINTA)
    for x, txt in ((1, "voo de 1 h"), (1000, "ano de 1000 h")):
        ax.axvline(x, color=TINTA2, linewidth=0.8, linestyle=(0, (2, 3)))
        ax.text(x * 1.12, 2.2e-7, txt, fontsize=6.5 if artigo else 8, color=TINTA2, va="bottom")
    ax.set(xscale="log", yscale="log", xlim=(1, 1e4), ylim=(2e-7, 1.5), xlabel="Tempo de operação t (h)",
           ylabel="P(falha do motor até t)" if artigo else "Probabilidade de falha do motor até t")
    ax.grid(True, which="major", axis="y")
    if artigo:
        fig.subplots_adjust(left=0.16, right=0.78, top=0.97, bottom=0.17)
    else:
        ax.set_title("Probabilidade de falha por tecnologia")
        fig.text(0.01, 0.005, "Linha: taxa nominal da literatura. Faixa: taxa mínima a máxima (Tabela I).",
                 fontsize=7, color=TINTA2)
        fig.subplots_adjust(left=0.11, right=0.86, top=0.9, bottom=0.17)
    salvar(fig, "fig_prob_falha_tempo", artigo)


def fig_pareto(par, artigo=False):
    fig, axs = plt.subplots(1, 3, figsize=(7.16, 2.55) if artigo else (11, 3.9))
    for ax, m in zip(axs, MOTORES):
        d = par[par["motor"] == m].iloc[::-1]
        y = np.arange(len(d))
        ax.barh(y, 100 * d["parcela"], height=0.62, color=COR[m])
        ax.errorbar(100 * d["parcela"], y, xerr=[100 * (d["parcela"] - d["parcela_min"]),
                    100 * (d["parcela_max"] - d["parcela"])], fmt="none", ecolor=TINTA2, elinewidth=0.9, capsize=2)
        for yi, (pv, pmax) in enumerate(zip(d["parcela"], d["parcela_max"])):
            ax.text(100 * pmax + 1.2, yi, f"{100 * pv:.0f}%", va="center", fontsize=6.5 if artigo else 8, color=TINTA)
        ax.set_yticks(y, [r.replace(", virabrequim", ",\nvirabrequim") for r in d["rotulo"]], fontsize=6.5 if artigo else 8)
        ax.set(xlim=(0, 100 * par["parcela_max"].max() + 9),
               xlabel="Parcela na falha (%)" if artigo else "Parcela na falha do motor (%)",
               title=ROTULO_MOTOR[m])
        ax.grid(True, axis="x")
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)
    if artigo:
        fig.tight_layout(pad=0.3, w_pad=0.6)
    else:
        nota_provisorio(fig, bool(par.loc[par["estrutura"] == "serie", "provisorio"].any()))  # pares: taxa assumida, não fração
        fig.text(0.99, 0.005, f"Frações: {FONTE_ROTULO[P['fonte_fracoes']]}", fontsize=7, color=TINTA2,
                 ha="right", va="bottom")
        fig.tight_layout(rect=(0, 0.03, 1, 1))
    salvar(fig, "fig_pareto_blocos", artigo)


def fig_bimotor(eq, artigo=False):
    t = 1.0
    betas = np.logspace(-3, np.log10(0.5), 120)
    lam = {m: float(rbd.construir(m).taxa_equivalente(t)) for m in MOTORES}
    fig, ax = plt.subplots(figsize=(3.5, 2.45) if artigo else (6.6, 3.9))
    lw, fs, dx = (1.5, 7, 4) if artigo else (2, None, 6)
    y2 = 1 - rbd.R_dois_motores(lam["pistao"], betas, t)
    ax.plot(betas, y2, color=COR["pistao"], linewidth=lw)
    ax.annotate("2 pistões" if artigo else "2 motores a pistão", (betas[-1], y2[-1]), xytext=(dx, 0),
                textcoords="offset points", va="center", fontsize=fs)
    ax.axhline(lam["pistao"] * t, color=COR["pistao"], linewidth=1.2, linestyle=(0, (5, 3)))
    ax.annotate("1 pistão" if artigo else "1 motor a pistão", (betas[-1], lam["pistao"] * t), xytext=(dx, 0),
                textcoords="offset points", va="center", fontsize=fs)
    for m in ("turboelice", "turbofan"):
        ax.axhline(lam[m] * t, color=COR[m], linewidth=lw, linestyle=TRACO[m] if artigo else "-")
        ax.annotate(f"1 {ROTULO_MOTOR[m].lower()}", (betas[-1], lam[m] * t), xytext=(dx, 5 if m == "turbofan" else -5),
                    textcoords="offset points", va="center", fontsize=fs)
    be = eq[(eq["dois_pistoes_contra"] == "1 Turboélice") & (eq["nivel_lambda_turbina"] == "nom")]["beta_equilibrio"].iloc[0]
    if np.isfinite(be) and be < 1:
        ax.plot([be], [lam["turboelice"] * t], "o", color=TINTA, markersize=5, zorder=5)
        ax.annotate(f"empate em β ≈ {be:.3f}".replace(".", ","), (be, lam["turboelice"] * t), xytext=(8, -14),
                    textcoords="offset points", fontsize=6.5 if artigo else 8)
    ax.set(xscale="log", yscale="log", xlim=(1e-3, 0.5),
           xlabel="β entre os dois motores" if artigo else "β entre os dois motores (fração de causa comum)",
           ylabel="P(perda total de propulsão em 1 h)")
    ax.grid(True, which="major", axis="y")
    if artigo:
        fig.subplots_adjust(left=0.17, right=0.77, top=0.97, bottom=0.17)
    else:
        ax.set_title("Dois motores a pistão × um motor a turbina")
        fig.text(0.01, 0.005, "Taxas nominais; o empate para as faixas da literatura está em bimotor_beta_equilibrio.csv.",
                 fontsize=7, color=TINTA2)
        fig.subplots_adjust(left=0.12, right=0.80, top=0.9, bottom=0.17)
    salvar(fig, "fig_bimotor", artigo)


def fig_sensibilidade(sen):
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.2), sharex=False)
    for ax, m in zip(axs, MOTORES):
        d = sen[sen["motor"] == m].sort_values("variacao_relativa")
        y = np.arange(len(d))
        lo, hi = d[["F_min", "F_max"]].min(axis=1), d[["F_min", "F_max"]].max(axis=1)
        ax.barh(y, hi - lo, left=lo, height=0.5, color=COR[m])
        ax.axvline(d["F_nominal"].iloc[0], color=TINTA, linewidth=1)
        rot = [p.split(" (/")[0].replace("taxa da unidade: ", "unidade: ") + f"\n{a:.3g} a {b:.3g}"
               for p, a, b in zip(d["parametro"], d["valor_min"], d["valor_max"])]
        ax.set_yticks(y, rot, fontsize=8)
        ax.set(xscale="log", xlabel="P(falha em 1 h)", title=ROTULO_MOTOR[m])
        todos_ = np.concatenate([lo.values, hi.values])
        ax.set_xlim(10 ** np.floor(np.log10(todos_.min())), 10 ** np.ceil(np.log10(todos_.max())))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_ylim(len(d) - 4.5, len(d) - 0.5)  # mesma espessura de barra nos três painéis
        ax.grid(True, axis="x", which="major")
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)
    fig.text(0.01, 0.005, "Barra: efeito de levar um parâmetro do mínimo ao máximo da faixa, os demais no nominal. "
             "Linha vertical: caso nominal."
             + (" Sem barra: com calibrar_total, β e unidades só redistribuem a taxa publicada." if P["calibrar_total"] else ""),
             fontsize=7, color=TINTA2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    salvar(fig, "fig_sensibilidade", False)


def fig_ntsb(artigo=False):
    arq = TABELAS / "ntsb_prob_fatal.csv"
    if not arq.exists():
        return
    d = pd.read_csv(arq)
    d = d[d["grupo"].isin(["monomotor", "multimotor"]) & (d["eventos"] >= 10)].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(3.5, 1.85) if artigo else (7.6, 3.0))
    y = np.arange(len(d))[::-1]
    for yi, r in zip(y, d.itertuples()):
        ax.plot([100 * r.ic95_inf, 100 * r.ic95_sup], [yi, yi], color=COR[r.motor], linewidth=2)
        ax.plot(100 * r.p_fatal, yi, "o", color=COR[r.motor], markersize=5 if artigo else 7,
                markeredgecolor="white" if artigo else FUNDO, markeredgewidth=1 if artigo else 1.5)
        ax.text(100 * r.ic95_sup + 2, yi, f"{100 * r.p_fatal:.0f}%  ({r.fatais}/{r.eventos})", va="center",
                fontsize=6.5 if artigo else 8)
    ax.set_yticks(y, [f"{ROTULO_MOTOR[r.motor]}, {r.grupo}" for r in d.itertuples()])
    ax.set(xlim=(0, 100), ylim=(-0.6, len(d) - 0.4),
           xlabel="Falhas com vítima fatal (%)" if artigo else "Falhas de motor em que houve vítima fatal (%)")
    ax.grid(True, axis="x")
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    if artigo:
        fig.tight_layout(pad=0.3)
    else:
        ax.set_title("Falha de motor com vítima fatal (NTSB, 2008–2026)")
        fig.text(0.01, 0.005, "Ponto: proporção; traço: intervalo de Wilson de 95%. Grupos com menos de 10 eventos "
                 "ficam fora (turbofan monomotor).", fontsize=7, color=TINTA2)
        fig.tight_layout(rect=(0, 0.04, 1, 1))
    salvar(fig, "fig_ntsb_prob_fatal", artigo)


def main():
    met, lam, comp, par, red = metricas(), lambda_blocos(), fracoes_por_fonte(), pareto(), redundancia_interna()
    bim, eq = bimotor()
    sen = sensibilidade()
    for nome, df in (("metricas_motores", met), ("lambda_blocos", lam), ("fracoes_ntsb_vs_sdrs", comp),
                     ("pareto_blocos", par), ("redundancia_interna", red),
                     ("bimotor_vs_monomotor", bim), ("bimotor_beta_equilibrio", eq), ("sensibilidade", sen)):
        df.to_csv(TABELAS / f"{nome}.csv", index=False)
    fig_prob_tempo(); fig_pareto(par); fig_bimotor(eq); fig_sensibilidade(sen); fig_ntsb()
    with plt.rc_context(RC_ARTIGO):  # versões em PDF para o artigo (saida/figuras/artigo/)
        fig_prob_tempo(True); fig_pareto(par, True); fig_bimotor(eq, True); fig_ntsb(True)
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.float_format", lambda v: f"{v:.4g}")
    print(f"Frações e taxa das unidades: {FONTE_ROTULO[P['fonte_fracoes']]} (fonte_fracoes = {P['fonte_fracoes']})")
    for titulo, df in (("Métricas por motor", met.T),
                       ("Lambda por bloco (por 1e5 h)", lam[["motor", "rotulo", "estrutura", "n", "fracao", "lambda_1e5h", "lambda_inf_1e5h", "lambda_sup_1e5h"]]),
                       ("Frações NTSB x SDRS", comp), ("Pareto (voo de 1 h)", par[["motor", "rotulo", "taxa_1e5h", "parcela", "parcela_min", "parcela_max"]]),
                       ("Redundância interna", red.T), ("Bimotor x monomotor", bim), ("Beta de equilíbrio", eq),
                       ("Sensibilidade", sen)):
        print(f"\n== {titulo}\n{df.to_string()}")


if __name__ == "__main__":
    main()
