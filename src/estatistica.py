"""Estatística de apoio: atualização bayesiana (Dirichlet e Gama-Poisson) e Weibull."""
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import brentq


def atualizar_fracoes(frac_prior, contagens, forca_prior):
    """Prior Dirichlet(forca_prior * frac_prior) + contagens multinomiais -> posteriori Dirichlet.
    É o modelo Gama-Poisson por bloco com exposição comum, condicionado ao total de falhas:
    não precisa das horas voadas. Devolve média e intervalo de 95% de cada fração."""
    a0 = forca_prior * np.asarray(frac_prior, float)
    a = a0 + np.asarray(contagens, float)
    A = a.sum()
    return pd.DataFrame({"prior": a0 / a0.sum(), "n": np.asarray(contagens, int), "posteriori": a / A,
                         "ic95_inf": stats.beta.ppf(0.025, a, A - a), "ic95_sup": stats.beta.ppf(0.975, a, A - a)})


def gama_poisson(taxa_prior, cv_prior, n_falhas, horas):
    """Taxa absoluta: prior Gama com média taxa_prior e coeficiente de variação cv_prior;
    dados: n_falhas em 'horas' de exposição. Posteriori Gama(a + n, b + horas)."""
    a = 1.0 / cv_prior ** 2
    b = a / taxa_prior
    a1, b1 = a + n_falhas, b + horas
    return dict(media_prior=taxa_prior, media_post=a1 / b1, ic95_inf=stats.gamma.ppf(0.025, a1, scale=1 / b1),
                ic95_sup=stats.gamma.ppf(0.975, a1, scale=1 / b1), peso_dados=horas / b1)


def ajustar_weibull(tempos, n_boot=2000, semente=0):
    """Ajuste de Weibull de 2 parâmetros por máxima verossimilhança aos tempos até a falha (ex.: TSO).
    Testa forma = 1 (taxa constante) por razão de verossimilhança e dá IC de 95% por bootstrap.
    Atenção: só há motores que falharam (sem censura), então o ajuste é apenas indicativo."""
    x = np.asarray([v for v in tempos if v and v > 0], float)
    if len(x) < 8:
        return None

    def forma_mv(v):
        lv = np.log(v)
        g = lambda k: (v ** k * lv).sum() / (v ** k).sum() - 1 / k - lv.mean()
        return brentq(g, 0.02, 50)

    v = x / x.mean()  # normaliza para evitar overflow em x**k
    k = forma_mv(v)
    escala = x.mean() * (v ** k).mean() ** (1 / k)
    ll_w = stats.weibull_min.logpdf(x, k, scale=escala).sum()
    ll_e = stats.expon.logpdf(x, scale=x.mean()).sum()
    rv = 2 * (ll_w - ll_e)
    rng = np.random.default_rng(semente)
    ks = []
    for _ in range(n_boot):
        try:
            ks.append(forma_mv(rng.choice(v, len(v))))
        except ValueError:
            pass
    return dict(n=len(x), forma=k, escala_h=escala, forma_ic95_inf=np.percentile(ks, 2.5),
                forma_ic95_sup=np.percentile(ks, 97.5), razao_verossimilhanca=rv, p_valor=stats.chi2.sf(rv, 1))

