"""Rede bayesiana equivalente ao RBD (mapeamento de Bobbio et al., ref. [10]) com inferência exata.

Nós-raiz binários (1 = falhou até t):
  - um por bloco em série;
  - três por par redundante: unidade A e unidade B (falhas independentes) e CC (causa comum).
Nós determinísticos: par = CC OU (A E B); motor = OU de todos os blocos em série e pares.
Com no máximo ~12 raízes, a distribuição conjunta é enumerada por completo (2^n estados).
"""
from itertools import product

import numpy as np
import pandas as pd


def raizes(motor, t):
    """Lista (nome, rótulo, P(falha até t)) dos nós-raiz."""
    nos = [(b.nome, b.rotulo, -np.expm1(-b.taxa * t)) for b in motor.serie]
    for p in motor.pares:
        q = -np.expm1(-(1 - p.beta) * p.taxa_unidade * t)
        nos += [(f"{p.nome}:A", f"{p.rotulo} - unidade A", q), (f"{p.nome}:B", f"{p.rotulo} - unidade B", q),
                (f"{p.nome}:CC", f"{p.rotulo} - causa comum", -np.expm1(-p.beta * p.taxa_unidade * t))]
    return nos


def conjunta(motor, t):
    """Enumera os estados: devolve (matriz de estados, probabilidade de cada um, vetor motor_falhou, nós)."""
    nos = raizes(motor, t)
    nomes = [n for n, _, _ in nos]
    q = np.array([x for _, _, x in nos])
    estados = np.array(list(product([0, 1], repeat=len(nos))), dtype=bool)
    prob = np.prod(np.where(estados, q, 1 - q), axis=1)
    falhou = np.zeros(len(estados), dtype=bool)
    for b in motor.serie:
        falhou |= estados[:, nomes.index(b.nome)]
    for p in motor.pares:
        a, bb, cc = (estados[:, nomes.index(f"{p.nome}:{s}")] for s in ("A", "B", "CC"))
        falhou |= cc | (a & bb)
    return estados, prob, falhou, nos


def diagnostico(motor, t=1.0):
    """P(nó falhou | motor falhou em t): qual subsistema é a causa mais provável."""
    estados, prob, falhou, nos = conjunta(motor, t)
    pf = prob[falhou].sum()
    linhas = [dict(no=n, rotulo=r, p_priori=q, p_dado_falha=prob[falhou & estados[:, i]].sum() / pf)
              for i, (n, r, q) in enumerate(nos)]
    # para os pares, também a probabilidade de o par (como bloco) ser a causa
    nomes = [n for n, _, _ in nos]
    for p in motor.pares:
        a, bb, cc = (estados[:, nomes.index(f"{p.nome}:{s}")] for s in ("A", "B", "CC"))
        par = cc | (a & bb)
        linhas.append(dict(no=p.nome, rotulo=p.rotulo, p_priori=prob[par].sum(),
                           p_dado_falha=prob[falhou & par].sum() / pf))
    return pd.DataFrame(linhas).sort_values("p_dado_falha", ascending=False).reset_index(drop=True), pf


def previsao(motor, evidencia, t=1.0):
    """P(motor falhar em t | evidência), com evidência = {nome do nó-raiz: 0 ou 1}.
    Ex.: {'magnetos:A': 1} = voar com um magneto já inoperante."""
    estados, prob, falhou, nos = conjunta(motor, t)
    nomes = [n for n, _, _ in nos]
    ok = np.ones(len(estados), dtype=bool)
    for no, valor in evidencia.items():
        ok &= estados[:, nomes.index(no)] == bool(valor)
    return prob[ok & falhou].sum() / prob[ok].sum()
