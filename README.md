# Confiabilidade de motores aeronáuticos: pistão, turboélice e turbofan

Roteiro de execução do trabalho (Seção IV da proposta). Cada etapa é um script em `src/`;
parâmetros e hipóteses ficam em `config/`, e nada de numérico está escondido no código.
Duas bases: o NTSB (avall, 2008 a 2026) identifica as falhas de motor e dá gravidade e tempo de motor;
o SDRS da FAA (2008 a 2025) reparte a taxa total da literatura entre os blocos do diagrama.

```
uv run python src/executar_tudo.py        # etapas 2 a 5, com o que está em data/raw/ntsb/ e data/raw/sdrs/
```

## De onde vem cada número

| O quê | Fonte |
|-------|-------|
| Taxa total de cada motor (λ) | Literatura (`config/taxas_literatura.csv`) |
| λ de cada bloco (λ_i = λ × n_i/N) e taxa de cada unidade redundante | Contagens por bloco da fonte `fonte_fracoes` (`parametros.yaml`): `sdrs` (padrão, etapa 3) ou `ntsb` (etapa 2). A outra sai lado a lado em `fracoes_ntsb_vs_sdrs.csv` |
| Falhas de motor, P(fatal \| falha), combustível à parte | NTSB (etapa 2) |
| Forma de Weibull (taxa constante) | Horas do motor no NTSB (etapa 5) |

## Objetivos e onde cada um é respondido

| Objetivo | Onde |
|----------|------|
| 1. Arquitetura de cada motor em diagrama de blocos | `config/blocos_rbd.csv`, `rbd.py` |
| 2. λ, MTBF e R(t) de cada motor | `metricas_motores.csv`, λ de cada bloco em `lambda_blocos.csv`; hipótese de taxa constante testada em `weibull_tempo_motor.csv` |
| 3. Efeito das redundâncias (magnetos, FADEC, dois motores) | `redundancia_interna.csv`, `bimotor_*.csv`, `ntsb_prob_fatal.csv` |
| 4. Subsistemas que mais contribuem para a falha | `pareto_blocos.csv` |

## Etapas

| # | Script | O que faz | Depende de |
|---|--------|-----------|------------|
| 1 | `01_extrair_ntsb.py` | Baixa o `avall.zip` do NTSB e exporta para CSV as tabelas events, aircraft, engines, Findings e Events_Sequence (mdbtools) | internet |
| 2 | `02_tratar_ntsb.py` | Uma linha por avião-evento; falha de motor pelos códigos da Events_Sequence; falhas por bloco do RBD pelos findings; P(evento fatal \| falha), monomotor × multimotor; combustível à parte | etapa 1 |
| 3 | `03_tratar_sdrs.py` | Relatos do SDRS por bloco do RBD, pelo código JASC; filtros de período e de helicópteros | CSV em `data/raw/sdrs/` |
| 4 | `04_analise_confiabilidade.py` | λ de cada bloco, λ, MTBF, R(t), Pareto, redundâncias, dois pistões × uma turbina, sensibilidade; comparação NTSB × SDRS; figuras | etapas 2 e 3 e config |
| 5 | `05_bayes_weibull.py` | Gama–Poisson (pulado sem horas da frota), forma de Weibull pelo tempo de motor | etapas 2 e 4 |

`rbd.py` é o modelo (Eq. 1 da proposta), `estatistica.py` as rotinas estatísticas. O risco de voar com uma unidade redundante já inoperante sai do próprio RBD (`aumento_sem_este_par_pct` em `redundancia_interna.csv`), sem rede bayesiana.

## Tratamento da base do NTSB (etapa 2)

- **Universo.** Aviões (`acft_category = AIR`) com motor a pistão (`REC`), turboélice (`TP`) ou turbofan (`TF`, `GTFN`). Turbojato, turboeixo e elétrico ficam fora, e também os aviões com tipos de motor misturados. Construção amadora (`homebuilt = Y`, 3 258 aviões, motores Rotax, Jabiru e conversões automotivas) fica fora porque as taxas da literatura são de motores certificados (`excluir_construcao_amadora`). Eventos fora dos EUA ficam: são 107 das 161 falhas de turbofan.
- **Falha de motor.** A Events_Sequence tem um dos códigos de `eventos_falha_motor` (perda de potência total ou parcial, mau funcionamento do grupo motopropulsor, falha não contida, corte do motor). Se a mesma sequência tem um código de `eventos_combustivel` (pane seca, falta de alimentação, contaminação, combustível errado), a perda de potência é operacional e vai para `ntsb_combustivel_a_parte.csv`.
- **Número de motores.** `num_eng`; vazio ou zero vira o número de linhas da tabela engines. Turbofans com `num_eng = 1` que não são SF50 ou L-39 são erro de cadastro (há B747, 777 e A380 com 1 motor: o NTSB às vezes lista só o motor envolvido) e ficam com número de motores desconhecido.
- **Horas do motor.** `eng_time_total` (TSN) e `eng_time_overhaul` (TSO). Zero quer dizer "não informado". TSO maior que TSN é descartado. As horas só são usadas em monomotores, porque nos multimotores não se sabe qual motor falhou.
- **Blocos do RBD.** Findings de motopropulsor dos aviões com falha de motor, pelo código: `category_no = 01` (Aircraft) e `subcategory_no` 04 (hélice) ou 05 (grupo motopropulsor). O bloco vem de `section_no` + `subsection_no`, que seguem os capítulos ATA (ex.: 8530 cilindros, 7414 magneto, 7250 turbinas), pelo prefixo mais longo de `config/mapa_componentes.csv`, o mesmo mapa usado no SDRS. Um avião conta uma vez por bloco. Erro de uso do piloto (`modifier_no` 10 "Not used/operated" e 11 "Incorrect use/operation") não conta.

## Tratamento do SDRS (etapa 3)

- **O que é.** O Service Difficulty Reporting System reúne os relatos de dificuldade em serviço que oficinas e operadores enviam à FAA, com o código JASC do componente. Não há download em lote: os CSV de `data/raw/sdrs/` foram exportados do site, uma consulta por motor (Lycoming 540, PT6A-34, CFM56-7); a etapa 3 imprime o passo a passo se faltar um arquivo.
- **Filtros** (`sdrs` em `parametros.yaml`). Relatos de 2008 em diante, como o NTSB. Helicópteros que usam o O-540 (Robinson R22/R44, Bell 47G, Hiller UH-12E: 1 026 relatos) ficam fora, porque o NTSB só usa aviões.
- **Blocos.** O código JASC segue os mesmos capítulos ATA dos findings do NTSB, então vale o mesmo `config/mapa_componentes.csv`. A única linha só do SDRS é a 2822, bomba de combustível da célula, que é a bomba elétrica do pistão. Genéricos (7200, 7300, 8500) e componentes fora do RBD ficam fora.
- **Resultado.** 504 relatos nos blocos em série do pistão (magnetos 201, bombas 65), 77 no turboélice e 2 988 no turbofan (FADEC 105); `sdrs_contagens.csv` mostra quantos caem em cada filtro.

## O que é dado medido e o que é hipótese

| Item | Situação |
|------|----------|
| Falhas por bloco, P(fatal \| falha), horas do motor | Medidos no NTSB, 2008 a 2026 |
| Taxa total de cada motor | Literatura (`config/taxas_literatura.csv`). O NTSB não traz horas voadas da frota, então não dá taxa absoluta. A do turbofan (CFM56-7B) é fonte de fabricante, ref. [11] |
| Frações por subsistema | n_i/N dos relatos do SDRS por bloco (504 / 77 / 2 988 nos blocos em série). Com `fonte_fracoes: ntsb`, dos achados do NTSB (880 / 69 / 45) |
| Taxa das unidades redundantes | Estimada pelas contagens dos pares: no SDRS, magnetos 201, bombas 65, FADEC 105; no NTSB, 102, 12 e 1 (`taxa_unidade_medida` em `rbd.py`) |
| β | Faixa assumida, como previsto na proposta |
| Taxa constante | Testada pela forma de Weibull, caso-controle (etapa 4) |

## Decisões de modelagem que valem uma linha no relatório

- **Taxa total preservada.** `calibrar_total: true`: a taxa publicada de cada motor vale para um voo de 1 h, e os blocos em série recebem o que sobra depois da contribuição dos pares. Consequência: β e a taxa das unidades só redistribuem a taxa publicada entre os blocos e não mudam P(falha em 1 h); na sensibilidade, quem move o resultado é a taxa total.
- **Frações por contagem.** n_i/N supõe que a chance de um problema virar registro é a mesma para todos os blocos. As duas fontes medem coisas diferentes, e `fracoes_ntsb_vs_sdrs.csv` mostra a diferença:
  - **SDRS (padrão):** dificuldades em serviço, incluindo achados de manutenção em solo e falhas que a redundância tolerou. Por isso a taxa das unidades redundantes sai maior que no NTSB (magnetos: 201 relatos contra 102 achados), o que corrige a subestimativa que o NTSB tem nos pares. Viés: o turbofan é dominado por um operador (ASAA, 76% dos relatos com bloco), e os registros de fan são, na maioria, achados de manutenção (`data/raw/sdrs/amostra_fan_cfm56_7.json`). No turboélice há só 77 relatos. Os motores entram pelo modelo consultado (Lycoming 540, PT6A-34, CFM56-7).
  - **NTSB:** achados das falhas que levaram a acidente ou incidente investigado (no pistão, 2 529 das 2 562 falhas são acidentes). Poucos registros nas turbinas (69 e 45). Os motores entram por tipo (REC, TP, TF), não por modelo.
- **Blocos sem registro.** Ficam com fração 0 (arrefecimento do pistão no SDRS; lubrificação do turbofan e entrada de ar do turboélice no NTSB), e o limite superior do intervalo de Jeffreys mostra até onde podem ir.
- **Registros genéricos.** Códigos que não dizem o bloco ficam fora de n_i/N (números abaixo do NTSB; no SDRS, `sdrs_contagens.csv`): "(general)" de seções que cobrem vários blocos, como 8500 "Engine (reciprocating)", 7200 "Engine (turbine/turboprop)", 7300 "Engine fuel and control", 7100 "Power plant" e 0000. São 535 findings (478 no pistão, 287 deles 8500; 47 no turboélice, 30 deles 7200; 10 no turbofan). Antes, pela busca no texto, os 8500 caíam em `nucleo` e os 7200 em `turbinas`. Isso supõe que se distribuem entre os blocos na mesma proporção dos classificados. O "(general)" de uma seção que é um bloco só (7400 ignição, 7900 óleo, 8100 turbo, 6100 hélice) conta nesse bloco.
- **Fora do RBD.** Escapamento (78), partida (80), indicação (77), berço (7120), comandos do motor (76: manete, mistura, corte), anti-gelo, injeção de água e reversor não têm bloco. O controle de ar do compressor (753x: sangria, VSV/VBV) entra no compressor. Sistemas da célula (tanques, linhas) ficam fora, exceto a bomba elétrica do pistão (2822).
- **FADEC do turbofan.** O código 7321 ("Fuel control electronic") é atribuído ao FADEC (no CFM56-7B, a ECU de dois canais); no turboélice, que tem FCU hidromecânica, fica em `combustivel_fcu`.
- **Turbinas do turboélice num bloco só.** O NTSB não separa a turbina do compressor da turbina livre; o bloco `turbinas` soma as duas. Em série com taxa constante isso não muda λ, MTBF nem R(t), só tira a separação do Pareto.
- **Taxa das unidades redundantes.** λ_unidade = (n_par / 2) × λ_motor / N_série, com as contagens da `fonte_fracoes`: cada registro de bloco em série vale λ_motor / N_série, e o registro do par é de uma das duas unidades. Com zero registros, o nominal é a média da posteriori de Jeffreys, (0 + ½) / (N_série + 1), e a faixa vai de 0 ao limite de 97,5%: zero falhas não quer dizer taxa zero. No NTSB, o FADEC tem um registro só, e falhas que o próprio par tolera raramente viram acidente, o que subestima essa taxa; o SDRS registra essas falhas (FADEC 105), mas também achados de manutenção.
- **λ de cada bloco** (`lambda_blocos.csv`). Nominal: λ_série × n_i/N. Faixa: da taxa mínima da literatura com o limite inferior da fração até a máxima com o limite superior, como no `reparticao.py`.
- **Taxa constante (forma de Weibull).** Não há horas da frota, então o teste é caso-controle: casos são monomotores com falha de motor; controles são monomotores acidentados por outra causa (sem evento de motor, pane seca nem finding de motopropulsor), cujo TSO representa a idade dos motores em uso. Se h(t) ∝ t^(k−1) e os outros acidentes não dependem da idade do motor, a regressão logística da falha em ln t dá k − 1. No pistão, o TSO dá k = 0,99 (IC 95% 0,94 a 1,05; 903 falhas), compatível com taxa constante. O TSN dá k = 1,08 (1,02 a 1,13), um desgaste leve ao longo da vida do motor. No turboélice há pouco dado (32 falhas com TSO), e no turbofan quase nenhum monomotor tem horas. A hipótese falha se os controles forem sistematicamente mais novos ou mais velhos que a frota.
- **1000 h.** A Eq. 1 aplicada a t = 1000 h supõe que uma unidade falhada nunca é reparada. `R_1000h_redundancia_restaurada` supõe o par restaurado a cada voo de 1 h (cheque de magnetos antes da decolagem), que é o caso real.
- **MTBF.** Com pares, R(t) não é exponencial; `mtbf_sem_reparo_h` é a integral de R(t) e `mtbf_redundancia_restaurada_h` é 1/λ equivalente de um voo.
- **Dois motores.** Perda total de propulsão pela Eq. 1 com o motor no lugar da unidade. O modelo não trata a dificuldade de voar um bimotor com um motor parado. A medida empírica está em `ntsb_prob_fatal.csv`: nas falhas de motor, 43% dos pistões multimotores tiveram vítima fatal, contra 11% dos monomotores.
- **Fonte da taxa do turbofan.** 0,002 IFSD por 1000 h vem de comunicado da CFM (ref. [11]); não há estatística independente da FAA ou da EASA para o CFM56-7B.
