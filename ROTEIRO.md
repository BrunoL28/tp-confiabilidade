# Roteiro para a equipe

Como rodar a análise e o que cada um precisa fazer. Detalhes do modelo estão no [README](README.md).

## 1. Preparar o ambiente (uma vez)

Requisito: [uv](https://docs.astral.sh/uv/getting-started/installation/), que instala o Python 3.14 sozinho.

```bash
cd tp-confiabilidade
uv sync
```

Sem uv: `python3.14 -m venv .venv`, ative o ambiente e rode `pip install -r requirements.txt`.

**Sempre rode os scripts com `uv run python ...`** (ou com o `.venv` ativado), a partir da pasta raiz do projeto. O `python` do sistema não tem as bibliotecas e dá `ModuleNotFoundError: pandas`. Também não use `python -m src.xxx`: rode o arquivo direto, `python src/xxx.py`.

## 2. Os dados já estão extraídos

São duas bases, e os CSV já estão no projeto. Para o NTSB, a etapa 1 (`src/01_extrair_ntsb.py`) só é necessária para atualizar a base. Ela baixa o `avall.zip` (cerca de 100 MB) e precisa do mdbtools (`sudo apt install mdbtools`).

| Pasta | Conteúdo | Origem |
|---|---|---|
| `data/raw/ntsb/` | CSV exportados da base `avall`: events, aircraft, engines, Findings, Events_Sequence | NTSB, 2008 a 2026. O `avall.mdb` original (538 MB) não vai no repositório |
| `data/raw/sdrs/` | Uma consulta do SDRS por motor: `pistao_lycoming540.csv`, `turboelice_pt6a34.csv`, `turbofan_cfm56_7.csv` | FAA, exportados do site (não há download em lote; a etapa 3 explica como refazer) |

## 3. Rodar a análise

```bash
uv run python src/executar_tudo.py
```

O script leva cerca de 30 segundos, roda as etapas 2, 3, 4 e 5 em ordem e para no primeiro erro.

| O que sai | Onde |
|---|---|
| Base tratada (uma linha por avião-evento) e registros por bloco | `data/processed/ntsb_avioes.csv`, `data/processed/contagens_ntsb.csv`, `data/processed/contagens_sdrs.csv` |
| Tabelas (NTSB, SDRS, λ por bloco, métricas, Pareto, redundância, sensibilidade, Weibull) | `saida/tabelas/*.csv` |
| Figuras | `saida/figuras/*.png` e, em PDF para o artigo, `saida/figuras/artigo/` |

Conferências rápidas depois de rodar:

- **Aviso nas figuras:** o rodapé "frações provisórias" não deve aparecer. Se aparecer, a etapa da `fonte_fracoes` (3 para `sdrs`, 2 para `ntsb`) não gerou as contagens.
- **Etapa 2:** `ntsb_eventos.csv` tem uma linha para cada código de `eventos_falha_motor` (`config/parametros.yaml`).
- **Etapa 3:** `sdrs_contagens.csv` tem uma linha por motor.
- **Etapa 5:** `weibull_tempo_motor.csv` existe em `saida/tabelas/`.

## 4. Mudou alguma coisa? Rode só o que depende dela

| Mudança | Rodar |
|---|---|
| `eventos_falha_motor`, `eventos_combustivel` ou `excluir_construcao_amadora` em `parametros.yaml` | `02`, depois `04` e `05` |
| `config/mapa_componentes.csv` | `02` e `03`, depois `04` e `05` |
| `sdrs` em `parametros.yaml` ou um CSV novo em `data/raw/sdrs/` | `03`, depois `04` e `05` |
| `fonte_fracoes`, outros itens de `parametros.yaml`, `blocos_rbd.csv` ou `taxas_literatura.csv` | `04` e `05` |

Cada etapa se roda assim: `uv run python src/04_analise_confiabilidade.py`. Rodar `executar_tudo.py` de novo também funciona.

## 5. Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Está usando o Python do sistema. Use `uv run python ...` |
| `No module named 'comum'` | Rodou com `python -m src.xxx`. Rode `python src/xxx.py` |
| Etapa 2 diz "data/raw/ntsb/... não existe" | A pasta `data/` não veio junto. Peça a cópia completa do projeto ou rode a etapa 1 |
| Etapa 1 diz "Instale o mdbtools" | `sudo apt install mdbtools` (Linux/WSL) ou `brew install mdbtools` (macOS) |
