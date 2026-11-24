# Confiabilidade de motores aeronáuticos: pistão, turboélice e turbofan

Roteiro de execução do trabalho (Seção IV da proposta). Cada etapa é um script em `src/`;
parâmetros e hipóteses ficam em `config/`, e nada de numérico está escondido no código.

```
pip install -r requirements.txt
python src/executar_tudo.py        # etapas 2 a 6, com o que houver em data/
```

## Etapas

| # | Script | O que faz | Depende de |
|---|--------|-----------|------------|
| 1 | `01_extrair_bases.py cenipa\|ntsb\|sdrs` | Baixa os dados abertos do CENIPA e o `avall.zip` do NTSB; para o SDRS, imprime o passo a passo da consulta | internet |
| 2 | `02_tratar_cenipa.py` | Uma linha por aeronave-ocorrência, filtro SCF-PP, tipo e número de motores; tabelas de contagem, P(acidente \| falha), origem e combustível à parte | etapa 1 |
| 3 | `03_amostra_relatorios.py [--baixar-pdfs]` | Sorteia 50 relatórios de pistão (semente em `parametros.yaml`), inclui todos os de turboélice e jato e cria `data/processed/planilha_relatorios.xlsx` | etapa 2 |
| 4 | `04_tratar_ntsb_sdrs.py` | Conta falhas por bloco do RBD no SDRS (código JASC) e no NTSB (findings) | etapa 1 |
| 5 | `05_analise_confiabilidade.py` | λ, MTBF, R(t), Pareto, redundâncias, dois pistões × uma turbina, sensibilidade; figuras | config |
| 6 | `06_bayes_weibull.py` | Rede bayesiana (diagnóstico e previsão), atualização das frações, Gama–Poisson, Weibull do TSO | planilha preenchida |

`rbd.py` é o modelo (Eq. 1 da proposta), `rede_bayesiana.py` a rede equivalente, `estatistica.py` as rotinas estatísticas.

## O que já é dado medido e o que ainda é hipótese

| Item | Situação |
|------|----------|
| Contagens, P(acidente \| falha), origem das falhas (CENIPA) | Medido na base aberta (2007 a 09/05/2026). A cópia usada veio de um repositório público, não do portal: ver `data/raw/cenipa/FONTE.txt` |
| Taxa total de cada motor | Literatura (`config/taxas_literatura.csv`). A do turbofan (CFM56-7B) é fonte de fabricante, ref. [11]: CFM International, *CFM56-7B Engine in Service with TUIfly Sets New First-Run World Record*, comunicado de imprensa, Hanover, 6 jun. 2012 |
| Frações por subsistema | Medidas: n_i/N somando planilha do CENIPA, SDRS e NTSB (etapa 4). Os valores de `config/blocos_rbd.csv` só voltam a valer se não houver contagens |
| Taxa das unidades redundantes | Estimada pelas contagens dos pares (`taxa_unidade_medida` em `rbd.py`); a faixa de `blocos_rbd.csv` só vale sem contagens |
| β | Faixa assumida, como previsto na proposta |
| Weibull, atualização bayesiana | Rodados com a planilha preenchida |

## Para fechar o trabalho

1. Rodar `python src/01_extrair_bases.py cenipa` em uma rede comum (ou baixar os 4 CSV do portal) e repetir a etapa 2.
2. Ler os 86 relatórios e preencher as colunas amarelas da planilha (aba `instrucoes`). `--baixar-pdfs` baixa os PDF e gera sugestões de modelo de motor, TSN, TSO e bloco para conferir na leitura.
3. Exportar as consultas do SDRS e baixar o NTSB (etapa 1), rodar a etapa 4.
4. Rodar de novo as etapas 5 e 6: as frações passam a ser as medidas e o aviso de "provisórias" some das figuras.

## Decisões de modelagem que valem uma linha no relatório

- **Taxa total preservada.** `calibrar_total: true`: a taxa publicada de cada motor vale para um voo de 1 h, e os blocos em série recebem o que sobra depois da contribuição dos pares. Consequência: β e a taxa das unidades só redistribuem a taxa publicada entre os blocos e não mudam P(falha em 1 h); na sensibilidade, quem move o resultado é a taxa total.
- **Frações por contagem de registros.** n_i/N supõe que a chance de um registro entrar no SDRS, no NTSB ou no CENIPA é a mesma para todos os blocos. As três fontes medem coisas diferentes (dificuldade em serviço na frota dos EUA, achados de acidentes nos EUA, ocorrências no Brasil) e são somadas sem peso. O NTSB entra com todos os motores do tipo (REC, TP, TF), não só os modelos escolhidos; o SDRS, só com Lycoming 540, PT6A-34 e CFM56-7.
- **SDRS registra dificuldades, não só falhas.** Leitura de 101 dos 883 registros de fan do CFM56-7 (`data/raw/sdrs/amostra_fan_cfm56_7.json`): 94 achados em inspeção ou manutenção, 84 de desgaste de itens trocados na lubrificação das pás (espaçadores, calços, revestimento, vedações), 7 em voo, 3 deles colisão com ave. 95% dos registros de fan e 68% de todos os do CFM56-7 vêm de um único operador (ASAA). As frações do turbofan medem achados de manutenção; o fan (28%) é o caso mais visível.
- **Registros genéricos.** Códigos que não dizem o componente (JASC 7200 e 8500, "Power plant (general)" no NTSB) e relatórios `indeterminado` ficam fora de n_i/N, o que supõe que eles se distribuem entre os blocos na mesma proporção dos classificados. No turbofan são 768 registros 7200, uma parte grande da amostra.
- **Fora do RBD.** Escapamento (78xx), partida (80xx), indicação (77xx), berço (7120), controles de cabine (7603) e ignição do turboélice não têm bloco; erro de operação do piloto (`so_operacional = S`, "Incorrect use/operation" no NTSB) não conta como falha de componente; no NTSB entram só aviões.
- **Turbinas do turboélice num bloco só.** O JASC 7250 e o NTSB não separam a turbina do compressor da turbina livre; o bloco `turbinas` soma as duas. Em série com taxa constante isso não muda λ, MTBF nem R(t), só tira a separação do Pareto.
- **Taxa das unidades redundantes.** λ_unidade = (n_par / 2) × λ_motor / N_série: cada registro de bloco em série vale λ_motor / N_série, e o registro do par é de uma das duas unidades. Supõe que o SDRS registra falha de magneto, bomba e FADEC na mesma proporção que as dos blocos em série; falhas do FADEC (19 registros) que o próprio sistema tolera podem não virar registro, o que subestimaria essa taxa. No pistão, o JASC 7314 cobre só a bomba acionada pelo motor.
- **Taxa constante.** O RBD supõe λ constante, mas o Weibull do TSO dos pistões que falharam (n = 10) dá forma ≈ 2,3 (IC 95% 1,4 a 6,0), sinal de desgaste. É indicativo: só entram motores que falharam, sem os que seguem voando (censura).
- **1000 h.** A Eq. 1 aplicada a t = 1000 h supõe que uma unidade falhada nunca é reparada. `R_1000h_redundancia_restaurada` supõe o par restaurado a cada voo de 1 h (cheque de magnetos antes da decolagem), que é o caso real.
- **MTBF.** Com pares, R(t) não é exponencial; `mtbf_sem_reparo_h` é a integral de R(t) e `mtbf_redundancia_restaurada_h` é 1/λ equivalente de um voo.
- **Dois motores.** Perda total de propulsão pela Eq. 1 com o motor no lugar da unidade. Não modela a dificuldade de voar um bimotor com um motor parado; a tabela do CENIPA dá a medida empírica disso.
- **Fonte da taxa do turbofan.** 0,002 IFSD por 1000 h vem de comunicado da CFM (ref. [11]); não há estatística independente da FAA ou da EASA para o CFM56-7B.

## Fontes que não foram testadas contra o site real

O ambiente em que o pipeline foi montado não alcançava cenipa.fab.mil.br, dados.gov.br, sdrs.faa.gov nem data.ntsb.gov.
Os endereços de download da etapa 1, o leitor de PDF da etapa 3 e os nomes de colunas do NTSB/SDRS na etapa 4 foram
escritos a partir da documentação e testados só com arquivos sintéticos; confira na primeira execução.
`config/mapa_jasc.csv` e as regras do NTSB também merecem revisão de quem conhece os manuais dos motores escolhidos.
