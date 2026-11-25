"""Modelo de diagrama de blocos de confiabilidade (RBD) dos três motores.

Hipóteses da proposta: taxa de falha constante, blocos independentes, e nos pares redundantes
uma fração beta da taxa de cada unidade é de causa comum (Eq. 1):

    R_serie(t) = exp(-sum(lambda_i) t)
    R_par(t)   = [1 - (1 - exp(-(1-beta) lambda t))^2] * exp(-beta lambda t)
    R_motor(t) = R_serie(t) * prod(R_par(t))
"""
from dataclasses import dataclass, field
from itertools import product

import numpy as np
import pandas as pd

from comum import CONFIG, MOTORES, PROC, parametros


@dataclass
class Bloco:
    nome: str
    rotulo: str
    taxa: float  # falhas por hora


@dataclass
class Par:
    nome: str
    rotulo: str
    taxa_unidade: float  # falhas por hora de cada unidade
    beta: float
    medida: bool = False  # True: taxa estimada pelas contagens; False: faixa assumida de blocos_rbd.csv

    def nao_conf_independente(self, t):
        """P(as duas unidades falharem por causas independentes até t)."""
        return np.expm1(-(1 - self.beta) * self.taxa_unidade * np.asarray(t, float)) ** 2

    def menos_ln_R(self, t):
        t = np.asarray(t, float)
        return self.beta * self.taxa_unidade * t - np.log1p(-self.nao_conf_independente(t))

    def R(self, t):
        return np.exp(-self.menos_ln_R(t))


@dataclass
class Motor:
    nome: str
    serie: list = field(default_factory=list)
    pares: list = field(default_factory=list)
    fracoes_provisorias: bool = True

    @property
    def taxa_serie(self):
        return sum(b.taxa for b in self.serie)

    def menos_ln_R(self, t):
        t = np.asarray(t, float)
        return self.taxa_serie * t + sum(p.menos_ln_R(t) for p in self.pares)

    def R(self, t):
        return np.exp(-self.menos_ln_R(t))

    def F(self, t):
        """Probabilidade de falha até t (calculada sem perda de precisão quando é muito pequena)."""
        return -np.expm1(-self.menos_ln_R(t))

    def taxa_equivalente(self, t):
        """Taxa constante que daria a mesma confiabilidade em t: -ln R(t) / t."""
        return self.menos_ln_R(t) / np.asarray(t, float)

    def mtbf(self):
        """Integral de R(t) de 0 a infinito, sem reparo. Cada par vale 2e^{-lt} - e^{-(2-beta)lt};
        o produto com a parte em série é uma soma de exponenciais, integrada termo a termo."""
        termos = [[(2.0, p.taxa_unidade), (-1.0, (2 - p.beta) * p.taxa_unidade)] for p in self.pares]
        total = 0.0
        for combinacao in product(*termos):
            coef = np.prod([c for c, _ in combinacao]) if combinacao else 1.0
            taxa = self.taxa_serie + sum(r for _, r in combinacao)
            total += coef / taxa
        return total

    def contribuicoes(self, t=1.0):
        """Parcela de cada bloco em -ln R(t); para t pequeno é a parcela na probabilidade de falha."""
        linhas = [dict(bloco=b.nome, rotulo=b.rotulo, estrutura="serie", contrib=b.taxa * t) for b in self.serie]
        linhas += [dict(bloco=p.nome, rotulo=p.rotulo, estrutura="par redundante", contrib=float(p.menos_ln_R(t)))
                   for p in self.pares]
        df = pd.DataFrame(linhas)
        df["parcela"] = df["contrib"] / df["contrib"].sum()
        return df.sort_values("parcela", ascending=False).reset_index(drop=True)


def R_dois_motores(taxa_motor, beta_motores, t):
    """Aeronave com dois motores iguais: perde toda a propulsão se os dois falharem no mesmo voo.
    Mesma Eq. 1, com o motor no lugar da unidade e beta_motores como causa comum entre motores
    (combustível, manutenção repetida, gelo)."""
    par = Par("motores", "dois motores", taxa_motor, beta_motores)
    return par.R(t)


# ---------------------- montagem a partir da configuração ----------------------
ROTULO_PAR = {"bombas": "Bombas de combustível (par)", "magnetos": "Magnetos (par)", "fadec": "FADEC A/B (par)"}


def ler_config():
    return (pd.read_csv(CONFIG / "blocos_rbd.csv"), pd.read_csv(CONFIG / "taxas_literatura.csv").set_index("motor"))


FONTES = {"ntsb": "etapa 2", "sdrs": "etapa 3"}


def carregar_contagens(fonte=None):
    """Registros por bloco da fonte escolhida (padrão: fonte_fracoes em parametros.yaml): ntsb (etapa 2,
    contagens_ntsb.csv) ou sdrs (etapa 3, contagens_sdrs.csv). Vazio se a etapa ainda não rodou."""
    fonte = parametros()["fonte_fracoes"] if fonte is None else fonte
    if fonte not in FONTES:
        raise ValueError(f"fonte_fracoes = {fonte!r}; use uma de {list(FONTES)}")
    arq = PROC / f"contagens_{fonte}.csv"
    if not arq.exists():
        return pd.DataFrame(columns=["motor", "bloco", "n", "fonte"])
    return pd.read_csv(arq).assign(fonte=fonte)


def fracoes_serie(motor, blocos=None, contagens=None):
    """Frações dos blocos em série. Com contagens: n_i/N (fórmula da proposta). Sem contagens:
    valores provisórios de blocos_rbd.csv. Devolve (DataFrame bloco/rotulo/frac/frac_min/frac_max, provisorio)."""
    blocos = ler_config()[0] if blocos is None else blocos
    contagens = carregar_contagens() if contagens is None else contagens
    s = blocos[(blocos["motor"] == motor) & (blocos["estrutura"] == "serie")].copy()
    c = contagens[contagens["motor"] == motor].groupby("bloco")["n"].sum()
    n = s["bloco"].map(c).fillna(0)
    if n.sum() > 0:
        N = n.sum()
        s["n"] = n.astype(int).values
        s["frac"] = (n / N).values
        # faixa: intervalo de 95% da posteriori Beta(n_i + 1/2, N - n_i + 1/2) (Jeffreys)
        from scipy.stats import beta as _beta
        # n_i = 0: limite inferior 0 (Brown, Cai e DasGupta, 2001), senão a estimativa fica fora da faixa
        s["frac_min"] = np.where(n == 0, 0.0, _beta.ppf(0.025, n + 0.5, N - n + 0.5))
        s["frac_max"] = _beta.ppf(0.975, n + 0.5, N - n + 0.5)
        return s[["bloco", "rotulo", "n", "frac", "frac_min", "frac_max"]], False
    s["n"] = 0
    s["frac"] = s["frac_nom"] / s["frac_nom"].sum()
    return s[["bloco", "rotulo", "n", "frac", "frac_min", "frac_max"]], True


def taxa_unidade_medida(motor, grupo, taxa_total, nivel, blocos, contagens):
    """Taxa de cada unidade de um par estimada pelas contagens, na mesma escala das frações em série:
    cada registro de bloco em série vale taxa_total / N_serie, e o registro do par é de uma das duas
    unidades, daí o /2. Faixa: intervalo de Jeffreys de n_par / (n_par + N_serie). None sem contagens.
    Par sem nenhum registro (ex.: FADEC no NTSB): zero registros não quer dizer taxa zero; o nominal é a
    média da posteriori de Jeffreys, (0 + 1/2) / (N_serie + 1), e a faixa vai de 0 ao limite de 97,5%."""
    from scipy.stats import beta as _beta
    serie = blocos[(blocos["motor"] == motor) & (blocos["estrutura"] == "serie")]["bloco"]
    c = contagens[contagens["motor"] == motor]
    N = c[c["bloco"].isin(serie)]["n"].sum()
    n = c[c["bloco"] == grupo]["n"].sum()
    if N == 0:
        return None
    a, b = n + 0.5, N + 0.5
    p = {"nom": n / (n + N) if n else a / (a + b), "min": 0.0 if n == 0 else _beta.ppf(0.025, a, b), "max": _beta.ppf(0.975, a, b)}[nivel]
    # ponytail: usa a taxa total no lugar da taxa em série (diferença = contribuição dos pares, < 1% aqui)
    return p / (1 - p) / 2 * taxa_total


def construir(motor, taxa_total=None, beta=None, taxa_unidade=None, fracoes=None, calibrar=None,
              nivel_taxa="nom", nivel_unidade="nom", fonte=None):
    """Monta o Motor. Argumentos omitidos usam os valores nominais da configuração.
    taxa_total em falhas/hora; taxa_unidade = dict {grupo: taxa por hora}; fracoes = dict {bloco: fração};
    fonte = ntsb ou sdrs, de onde vêm as contagens (padrão: fonte_fracoes)."""
    par = parametros()
    blocos, lit = ler_config()
    if taxa_total is None:
        taxa_total = lit.loc[motor, f"lambda_{nivel_taxa}"] * par["unidade_taxa"]
    beta = par["beta"]["nom"] if beta is None else beta
    calibrar = par["calibrar_total"] if calibrar is None else calibrar

    contagens = carregar_contagens(fonte)
    b = blocos[blocos["motor"] == motor]
    pares = []
    for grupo, g in b[b["estrutura"] == "paralelo"].groupby("grupo", sort=False):
        medida = taxa_unidade_medida(motor, grupo, taxa_total, nivel_unidade, blocos, contagens)
        lu = (taxa_unidade or {}).get(grupo, g[f"lu_{nivel_unidade}"].mean() if medida is None else medida)
        pares.append(Par(grupo, ROTULO_PAR.get(grupo, grupo), float(lu), beta, medida is not None))

    fr, provisorio = fracoes_serie(motor, blocos, contagens)
    if fracoes is not None:
        fr = fr.assign(frac=fr["bloco"].map(fracoes))
        fr["frac"] = fr["frac"] / fr["frac"].sum()
    taxa_serie = taxa_total
    if calibrar:  # preserva a taxa publicada em um voo de 1 h
        taxa_serie = max(taxa_total - sum(float(p.menos_ln_R(1.0)) for p in pares), 0.0)
    serie = [Bloco(r.bloco, r.rotulo, taxa_serie * r.frac) for r in fr.itertuples()]
    return Motor(motor, serie, pares, provisorio)


def todos(**kw):
    return {m: construir(m, **kw) for m in MOTORES}


if __name__ == "__main__":  # conferência da estimativa dos pares: 25 registros do par para 100 em série
    _b = pd.DataFrame({"motor": "x", "bloco": ["s1", "s2", "p_a", "p_b"], "estrutura": ["serie", "serie", "paralelo", "paralelo"]})
    _c = pd.DataFrame({"motor": "x", "bloco": ["s1", "s2", "p"], "n": [60, 40, 25]})
    assert abs(taxa_unidade_medida("x", "p", 1.0, "nom", _b, _c) - 0.125) < 1e-12  # (25/125)/(100/125)/2
    assert taxa_unidade_medida("x", "p", 1.0, "nom", _b, _c.iloc[:0]) is None
    assert abs(taxa_unidade_medida("x", "p", 1.0, "nom", _b, _c.iloc[:2]) - 0.5 / 100.5 / 2) < 1e-12  # par sem registro: Jeffreys
    print("ok")
