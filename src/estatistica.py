"""Estatística de apoio: atualização bayesiana (Dirichlet e Gama-Poisson) e teste da taxa constante."""
import numpy as np
import pandas as pd
from scipy import stats


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


def forma_por_caso_controle(t_falha, t_controle):
    """Forma de Weibull k a partir de acidentes (desenho caso-controle), sem horas voadas da frota.

    Casos: motores que falharam, no tempo t em que falharam. Controles: motores de aviões acidentados por
    outra causa, cujo t representa a idade dos motores em uso. Se a taxa de falha é h(t) = c t^(k-1) e a
    chance de um acidente por outra causa não depende de t, a chance de um acidentado ser caso é
    proporcional a h(t), e a regressão logística log-chance = a + b ln t dá b = k - 1.
    k = 1 é a taxa constante do RBD. Ajuste por mínimos quadrados reponderados (IRLS), IC e teste de Wald."""
    x = np.log(np.concatenate([np.asarray(t_falha, float), np.asarray(t_controle, float)]))
    y = np.concatenate([np.ones(len(t_falha)), np.zeros(len(t_controle))])
    X = np.column_stack([np.ones_like(x), x - x.mean()])
    w = np.zeros(2)
    for _ in range(50):
        p = 1 / (1 + np.exp(-X @ w))
        H = X.T @ (X * (p * (1 - p))[:, None])
        passo = np.linalg.solve(H, X.T @ (y - p))
        w += passo
        if np.abs(passo).max() < 1e-10:
            break
    ep = np.sqrt(np.linalg.inv(H)[1, 1])
    b = w[1]
    return dict(n_falhas=int(y.sum()), n_controles=int(len(y) - y.sum()), forma=1 + b,
                forma_ic95_inf=1 + b - 1.96 * ep, forma_ic95_sup=1 + b + 1.96 * ep,
                p_valor_taxa_constante=2 * stats.norm.sf(abs(b / ep)))
