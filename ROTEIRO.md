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

## 2. Os dados já estão extraídos: não rode a etapa 1

Os sites do CENIPA e do SDRS bloqueiam download automático (desafio anti-robô do Cloudflare). Por isso a extração foi feita uma vez, pelo navegador, e os arquivos já estão no projeto. **Não rodem `src/01_extrair_bases.py`.**

| Pasta | Conteúdo | Origem |
|---|---|---|
| `data/raw/cenipa/` | 4 CSV de ocorrências (2007 a 09/05/2026) e `links_relatorios.csv` | Cópia dos dados abertos do CENIPA no GitHub (ver `FONTE.txt`) |
| `data/raw/cenipa/relatorios/` | 80 PDF de relatórios finais | Site do CENIPA, baixados pelo navegador |
| `data/raw/sdrs/` | 3 CSV: Lycoming 540 (2.746 registros), PT6A-34 (269), CFM56-7 (6.855) | Consulta no SDRS da FAA, 2007 a 2025, ano a ano |
| `data/raw/ntsb/` | CSV exportados da base `avall` (events, aircraft, engines, Findings, Occurrences) | NTSB. O `avall.mdb` original (538 MB) não vai no repositório |
| `data/processed/planilha_relatorios.xlsx` | 86 relatórios do CENIPA, 75 classificados à mão | Etapa 3 e leitura dos PDF |

## 3. Rodar a análise

```bash
uv run python src/executar_tudo.py
```

O script leva cerca de 20 segundos, roda as etapas 2 a 6 em ordem e para no primeiro erro. A planilha preenchida não é sobrescrita: a etapa 3 só sorteia uma amostra nova se o arquivo não existir.

| O que sai | Onde |
|---|---|
| Tabelas (métricas, Pareto, redundância, CENIPA, sensibilidade, Weibull) | `saida/tabelas/*.csv` |
| Figuras | `saida/figuras/*.png` |
| Texto do relatório (resultados até limitações) | `saida/relatorio.md` |

Conferências rápidas depois de rodar:

- **Aviso nas figuras:** o rodapé "frações provisórias" não deve aparecer. Se aparecer, a etapa 4 não encontrou as contagens.
- **Tabelas da etapa 6:** `fracoes_posteriori.csv` e `weibull_tso.csv` precisam existir em `saida/tabelas/`.

## 4. Mudou alguma coisa? Rode só o que depende dela

| Mudança | Rodar |
|---|---|
| `config/mapa_jasc.csv` ou regras do NTSB em `src/04_tratar_ntsb_sdrs.py` | `04`, depois `05` e `06` |
| `config/parametros.yaml`, `blocos_rbd.csv` ou `taxas_literatura.csv` | `05` e `06` |
| Planilha de relatórios (classificações, TSO) | `05` e `06` |

Cada etapa se roda assim: `uv run python src/05_analise_confiabilidade.py`. Rodar `executar_tudo.py` de novo também funciona.

## 5. Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Está usando o Python do sistema. Use `uv run python ...` |
| `No module named 'comum'` | Rodou com `python -m src.xxx`. Rode `python src/xxx.py` |
| `PermissionError` ao salvar a planilha | A planilha está aberta no Excel. Feche-a e rode de novo |
| Etapa 4 diz "nenhum arquivo em data/raw/sdrs" | A pasta `data/` não veio junto. Peça a cópia completa do projeto |
