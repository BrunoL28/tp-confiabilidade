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
| Tabelas (métricas, Pareto, redundância, CENIPA, sensibilidade, kappa, Weibull) | `saida/tabelas/*.csv` |
| Figuras | `saida/figuras/*.png` |
| Texto do relatório (resultados até limitações) | `saida/relatorio.md` |

Conferências rápidas depois de rodar:

- **Aviso nas figuras:** o rodapé "frações provisórias" não deve aparecer. Se aparecer, a etapa 4 não encontrou as contagens.
- **Tabelas da etapa 6:** `fracoes_posteriori.csv`, `weibull_tso.csv` e `consistencia_kappa.csv` precisam existir em `saida/tabelas/`.
- **Kappa:** o de `bloco_rbd` deve ficar acima de 0,6 (ver seção 5).

## 4. Mudou alguma coisa? Rode só o que depende dela

| Mudança | Rodar |
|---|---|
| `config/mapa_jasc.csv` ou regras do NTSB em `src/04_tratar_ntsb_sdrs.py` | `04`, depois `05` e `06` |
| `config/parametros.yaml`, `blocos_rbd.csv` ou `taxas_literatura.csv` | `05` e `06` |
| Planilha de relatórios (classificações, TSO, dupla classificação) | `05` e `06` |

Cada etapa se roda assim: `uv run python src/05_analise_confiabilidade.py`. Rodar `executar_tudo.py` de novo também funciona.

## 5. Tarefa pendente: dupla classificação para o kappa

O kappa mede se duas pessoas, lendo o mesmo relatório com os mesmos critérios, chegam ao mesmo bloco e à mesma origem. As colunas `bloco_rbd_2` e `origem_2` foram preenchidas pela mesma pessoa que fez a primeira classificação, então o kappa atual (0,79) ainda não vale. **Um membro da equipe que não participou da primeira classificação** precisa refazê-las.

### Passo a passo

1. **Não abra `data/processed/planilha_relatorios.xlsx`.** As colunas `componente`, `bloco_rbd`, `origem` e `observacoes` dela são a primeira classificação. Ver qualquer uma delas invalida o teste.
2. **Abra `data/processed/dupla_cega.xlsx`.** Ela tem só as 10 linhas da dupla classificação, sem a primeira resposta.
   - Aba `criterios`: leia antes de começar. São as mesmas regras usadas na primeira classificação.
   - Aba `classificar`: uma linha por relatório.
3. **Pule as 3 linhas marcadas "SEM PDF CORRETO"** (`A-010/CENIPA/2014`, `IG-522/CENIPA/2017` e `A - 060/CENIPA/2018`). Elas também não têm a primeira classificação. Se alguém achar o relatório certo no site do CENIPA pela matrícula, duas pessoas diferentes precisam classificá-lo, uma na planilha principal e outra aqui.
4. **Para cada uma das 7 linhas restantes:**
   - abra o PDF indicado em `arquivo_pdf` (ou o link de `pdf_pt` no navegador);
   - leia as seções de histórico do voo, exames do motor, análise e conclusões/fatores contribuintes;
   - preencha os três campos amarelos:
     - `bloco_rbd_2`: escolha na lista. Se o relatório só levanta hipótese, use `indeterminado`. Se a falha é só de operação ou de algo sem bloco, use `fora_do_modelo`.
     - `origem_2`: projeto, fabricação, manutenção, operação ou indeterminado.
     - `notas_2`: o trecho ou a página que justificou a escolha.
5. **Passe as respostas para a planilha principal.** Isso só pode ser feito depois de terminar as 7 linhas, e de preferência por outra pessoa.
   - Em `planilha_relatorios.xlsx`, aba `relatorios`, ache cada linha pelo `codigo_ocorrencia`.
   - Copie os valores para as colunas `bloco_rbd_2` (T) e `origem_2` (U), substituindo o que já está lá.
6. **Calcule o kappa:**
   ```bash
   uv run python src/06_bayes_weibull.py
   ```
   Abra `saida/tabelas/consistencia_kappa.csv` e veja o `kappa` da linha `bloco_rbd`.
7. **Avalie o resultado:**
   - **0,6 ou mais:** os critérios são consistentes. Rode `executar_tudo.py` de novo e anote o valor no relatório, com n = 7.
   - **Abaixo de 0,6:**
     - Reúnam-se e listem as linhas em que as duas classificações divergiram.
     - Para cada divergência, vejam qual critério ficou ambíguo.
     - **Não alterem a segunda classificação para coincidir com a primeira.** Isso invalida o kappa.
     - Se um critério mudar, reclassifiquem com o critério novo **todas** as 86 linhas da planilha.

Com n = 7, o kappa tem incerteza grande, e uma única divergência pesa muito. Vale dizer isso no relatório.

## 6. Problemas comuns

| Sintoma | Causa e solução |
|---|---|
| `ModuleNotFoundError: No module named 'pandas'` | Está usando o Python do sistema. Use `uv run python ...` |
| `No module named 'comum'` | Rodou com `python -m src.xxx`. Rode `python src/xxx.py` |
| `PermissionError` ao salvar a planilha | A planilha está aberta no Excel. Feche-a e rode de novo |
| Etapa 4 diz "nenhum arquivo em data/raw/sdrs" | A pasta `data/` não veio junto. Peça a cópia completa do projeto |
