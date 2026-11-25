# Execução do pipeline

Gerado por `src/executar_tudo.py` em 24/11/2026 20:56. Base: NTSB (avall, 2008 a 2026).

## 02_tratar_ntsb.py

> NTSB: 18735 avião-eventos (pistão, turboélice, turbofan), anos 2008 a 2026; 3258 de construção amadora excluídos; 86 com TSO > TSN descartados; 42 turbofans com num_eng = 1 tratados como número de motores desconhecido
> Findings de motopropulsor nos aviões com falha: 2069 (77 de operação descartados, 328 sem bloco no modelo)

### Aviões e falhas de motor

```text
        motor  avioes  falhas  acidentes  monomotor  com_tso  com_tsn
0      pistao   16046    2562       2529       2377      903      977
1  turboelice    1420     176        158        141       32       56
2    turbofan    1269     161         16          1        1        1
```

### Tipo de evento nas falhas

```text
motor                           pistao  turboelice  turbofan
evento                                                      
Loss of engine power (total)      1530         100        25
Loss of engine power (partial)     976          52        34
Powerplant sys/comp malf/fail      325          34        99
Uncontained engine failure           2           2        21
Engine shutdown                     20           6        24
```

### P(evento fatal | falha de motor)

```text
         motor                         grupo  eventos  fatais  acidentes  p_fatal  ic95_inf  ic95_sup
0       pistao                falha de motor     2562     349       2529    0.136     0.123     0.150
1       pistao                     monomotor     2377     270       2346    0.114     0.101     0.127
2       pistao                    multimotor      185      79        183    0.427     0.358     0.499
3       pistao  qualquer evento (referência)    16046    2665      15913    0.166     0.160     0.172
4   turboelice                falha de motor      176      17        158    0.097     0.061     0.149
5   turboelice                     monomotor      141       4        137    0.028     0.011     0.071
6   turboelice                    multimotor       35      13         21    0.371     0.232     0.537
7   turboelice  qualquer evento (referência)     1420     354       1336    0.249     0.227     0.272
8     turbofan                falha de motor      161       6         16    0.037     0.017     0.079
9     turbofan                     monomotor        1       1          1    1.000     0.207     1.000
10    turbofan                    multimotor      136       4         13    0.029     0.011     0.073
11    turbofan  qualquer evento (referência)     1269      72        763    0.057     0.045     0.071
```

### Combustível, à parte

```text
        motor  ocorrencias  fatais
0      pistao         1532     174
1  turboelice           61       8
2    turbofan            5       0
```

### Falhas por bloco

```text
motor               pistao  turboelice  turbofan
bloco                                           
admissao                60           0         0
arrefecimento            4           0         0
bombas                  12           0         0
caixa_acessorios         0           0         4
caixa_reducao            0           5         0
camara_combustao         0           1         2
carburador_injecao     134           0         0
combustivel              0           0        12
combustivel_fcu          0          14         0
compressor               0          14         0
compressores             0           0        18
fan                      0           0         1
helice_governador       37           7         0
lubrificacao           127          10         0
magnetos               102           0         0
nucleo                 787           0         0
turbinas                 0          47        16
```

## 03_analise_confiabilidade.py

### Métricas por motor

```text
                                       0           1         2
motor                             pistao  turboelice  turbofan
lambda_literatura_1e5h              12.4        0.15       0.2
lambda_eq_1h_1e5h                   12.4        0.15       0.2
lambda_eq_1000h_1e5h                12.4        0.15       0.2
mtbf_sem_reparo_h                   8041   6.667e+05     5e+05
mtbf_redundancia_restaurada_h       8065   6.667e+05     5e+05
R_1h                              0.9999           1         1
F_1h                            0.000124     1.5e-06     2e-06
F_1h_lambda_min                   0.0001     1.5e-06     1e-06
F_1h_lambda_max                0.0009995       1e-05     2e-05
R_1000h_sem_reparo                0.8834      0.9985     0.998
R_1000h_redundancia_restaurada    0.8834      0.9985     0.998
F_1h_total_preservado           0.000124     1.5e-06     2e-06
fracoes_provisorias                False       False     False
razao_para_pistao                      1       82.66        62
```

### Pareto (voo de 1 h)

```text
         motor                                     rotulo  taxa_1e5h   parcela  parcela_min  parcela_max
0       pistao  Cilindros, válvulas, pistões, virabrequim      8.451    0.6815       0.6544       0.7078
1       pistao                       Carburador / injeção      1.439     0.116      0.09854       0.1355
2       pistao                               Lubrificação      1.364      0.11      0.09292        0.129
3       pistao                                   Admissão     0.6443   0.05196      0.04026       0.0659
4       pistao                        Hélice e governador     0.3973   0.03204      0.02303       0.0434
5       pistao                             Magnetos (par)    0.05504  0.004439      0.00361     0.005412
6       pistao                              Arrefecimento    0.04295  0.003464      0.00117     0.008215
7       pistao                Bombas de combustível (par)   0.006475 0.0005222    0.0002847    0.0008874
8   turboelice              Turbinas (compressor e livre)    0.07194    0.4796       0.3825       0.5779
9   turboelice                                 Compressor    0.02143    0.1429       0.0843       0.2221
10  turboelice                          Combustível (FCU)    0.02143    0.1429       0.0843       0.2221
11  turboelice                               Lubrificação    0.01531     0.102      0.05368       0.1734
12  turboelice                        Hélice e governador    0.01071   0.07143      0.03252       0.1351
13  turboelice                           Caixa de redução   0.007653   0.05102      0.01973       0.1082
14  turboelice                        Câmara de combustão   0.001531    0.0102     0.001103      0.04669
15  turboelice                              Entrada de ar          0         0            0      0.02524
16    turbofan                       Compressores LP e HP    0.06789    0.3395       0.2232       0.4727
17    turbofan                           Turbinas HP e LP    0.06035    0.3017       0.1912       0.4333
18    turbofan                                Combustível    0.04526    0.2263       0.1301       0.3515
19    turbofan                        Caixa de acessórios    0.01509   0.07544        0.026       0.1694
20    turbofan                        Câmara de combustão   0.007544   0.03772      0.00792       0.1155
21    turbofan                                        Fan   0.003772   0.01886     0.002042      0.08476
22    turbofan                            FADEC A/B (par)  9.346e-05 0.0004673            0     0.002415
23    turbofan                               Lubrificação          0         0            0      0.04605
```

### Redundância interna

```text
                                                    0               1                2
motor                                          pistao          pistao         turbofan
par                       Bombas de combustível (par)  Magnetos (par)  FADEC A/B (par)
taxa_unidade_1e5h                             0.06475          0.5504        0.0009346
beta                                              0.1             0.1              0.1
F_unidade_unica                             6.475e-07       5.504e-06        9.346e-09
F_par                                       6.475e-08       5.504e-07        9.346e-10
ganho_do_par                                       10              10               10
parcela_causa_comum                                 1               1                1
F_motor_com_par                              0.000124        0.000124            2e-06
F_motor_sem_este_par                        0.0001246       0.0001289        2.008e-06
aumento_sem_este_par_pct                       0.4699           3.995           0.4206
F_motor_sem_nenhum_par                      0.0001295       0.0001295        2.008e-06
```

### Bimotor x monomotor

```text
              configuracao       motor  n_motores  beta_motores  p_perda_total  p_alguma_falha_de_motor
0         1 motor - Pistão      pistao          1           NaN       0.000124                 0.000124
1     1 motor - Turboélice  turboelice          1           NaN        1.5e-06                  1.5e-06
2       1 motor - Turbofan    turbofan          1           NaN          2e-06                    2e-06
3       2 motores - Pistão      pistao          2             0      1.537e-08                 0.000248
4       2 motores - Pistão      pistao          2          0.01      1.255e-06                0.0002467
5       2 motores - Pistão      pistao          2          0.05      6.214e-06                0.0002418
6       2 motores - Pistão      pistao          2           0.1      1.241e-05                0.0002356
7       2 motores - Pistão      pistao          2           0.2      2.481e-05                0.0002232
8       2 motores - Pistão      pistao          2           0.3      3.721e-05                0.0002108
9   2 motores - Turboélice  turboelice          2             0       2.25e-12                    3e-06
10  2 motores - Turboélice  turboelice          2          0.01        1.5e-08                2.985e-06
11  2 motores - Turboélice  turboelice          2          0.05        7.5e-08                2.925e-06
12  2 motores - Turboélice  turboelice          2           0.1        1.5e-07                 2.85e-06
13  2 motores - Turboélice  turboelice          2           0.2          3e-07                  2.7e-06
14  2 motores - Turboélice  turboelice          2           0.3        4.5e-07                 2.55e-06
15    2 motores - Turbofan    turbofan          2             0          4e-12                    4e-06
16    2 motores - Turbofan    turbofan          2          0.01          2e-08                 3.98e-06
17    2 motores - Turbofan    turbofan          2          0.05          1e-07                  3.9e-06
18    2 motores - Turbofan    turbofan          2           0.1          2e-07                  3.8e-06
19    2 motores - Turbofan    turbofan          2           0.2          4e-07                  3.6e-06
20    2 motores - Turbofan    turbofan          2           0.3          6e-07                  3.4e-06
```

### Beta de equilíbrio

```text
  dois_pistoes_contra nivel_lambda_turbina  lambda_turbina_1e5h  beta_equilibrio
0        1 Turboélice                  min                 0.15          0.01198
1        1 Turboélice                  nom                 0.15          0.01198
2        1 Turboélice                  max                    1          0.08054
3          1 Turbofan                  min                  0.1         0.007942
4          1 Turbofan                  nom                  0.2          0.01601
5          1 Turbofan                  max                    2           0.1612
```

### Sensibilidade

```text
        motor                                              parametro  valor_min  valor_max    F_min     F_max  F_nominal  variacao_relativa
0      pistao                           taxa total do motor (/1e5 h)         10        100   0.0001 0.0009995   0.000124              9.996
1      pistao                                         beta dos pares       0.01        0.3 0.000124  0.000124   0.000124                  1
2      pistao  taxa da unidade: Bombas de combustível (par) (/1e5 h)    0.03531       0.11 0.000124  0.000124   0.000124                  1
3      pistao               taxa da unidade: Magnetos (par) (/1e5 h)     0.4476     0.6711 0.000124  0.000124   0.000124                  1
4  turboelice                           taxa total do motor (/1e5 h)       0.15          1  1.5e-06     1e-05    1.5e-06              6.667
5    turbofan                           taxa total do motor (/1e5 h)        0.1          2    1e-06     2e-05      2e-06                 20
6    turbofan                                         beta dos pares       0.01        0.3    2e-06     2e-06      2e-06                  1
7    turbofan              taxa da unidade: FADEC A/B (par) (/1e5 h)          0    0.00483    2e-06     2e-06      2e-06                  1
```

## 04_bayes_weibull.py

### Diagnóstico: P(subsistema falhou | motor falhou em 1 h), três mais prováveis

```text
     motor                                    rotulo  p_dado_falha
    pistao Cilindros, válvulas, pistões, virabrequim         0.682
    pistao                      Carburador / injeção         0.116
    pistao                              Lubrificação         0.110
turboelice             Turbinas (compressor e livre)         0.480
turboelice                         Combustível (FCU)         0.143
turboelice                                Compressor         0.143
  turbofan                      Compressores LP e HP         0.339
  turbofan                          Turbinas HP e LP         0.302
  turbofan                               Combustível         0.226
```

### Previsão com evidência

```text
   motor                                                evidencia  p_falha_1h_sem_evidencia  p_falha_1h_com_evidencia  fator
  pistao uma unidade de Bombas de combustível (par) já inoperante                  0.000124                  0.000125      1
  pistao              uma unidade de Magnetos (par) já inoperante                  0.000124                  0.000129   1.04
turbofan             uma unidade de FADEC A/B (par) já inoperante                     2e-06                  2.01e-06      1
```

### Frações: prior (provisório) x posteriori

```text
 prior   n  posteriori  ic95_inf  ic95_sup      motor              bloco
  0.08  60       0.053     0.041     0.066     pistao           admissao
  0.22 134       0.118     0.101     0.138     pistao carburador_injecao
  0.42 787       0.680     0.653     0.707     pistao             nucleo
  0.15 127       0.111     0.094     0.130     pistao       lubrificacao
  0.03   4       0.004     0.001     0.008     pistao      arrefecimento
  0.10  37       0.033     0.024     0.044     pistao  helice_governador
  0.03   0       0.005     0.000     0.023 turboelice         entrada_ar
  0.15  14       0.144     0.087     0.213 turboelice         compressor
  0.05   1       0.017     0.002     0.047 turboelice   camara_combustao
  0.30  47       0.449     0.361     0.539 turboelice           turbinas
  0.12   5       0.063     0.027     0.113 turboelice      caixa_reducao
  0.12   7       0.080     0.038     0.135 turboelice  helice_governador
  0.15  14       0.144     0.087     0.213 turboelice    combustivel_fcu
  0.08  10       0.098     0.052     0.158 turboelice       lubrificacao
  0.08   1       0.036     0.006     0.088   turbofan                fan
  0.20  18       0.301     0.202     0.411   turbofan       compressores
  0.05   2       0.041     0.009     0.097   turbofan   camara_combustao
  0.20  16       0.274     0.179     0.381   turbofan           turbinas
  0.20  12       0.219     0.133     0.320   turbofan        combustivel
  0.17   0       0.047     0.011     0.105   turbofan       lubrificacao
  0.10   4       0.082     0.031     0.155   turbofan   caixa_acessorios
```

> Gama-Poisson das taxas: exposicao_horas não informada em parametros.yaml - pulada (o NTSB não traz horas voadas da frota).

> Tempo de motor: turbofan, tso_h: 1 falhas com horas - pulado (mínimo 20).

> Tempo de motor: turbofan, tsn_h: 1 falhas com horas - pulado (mínimo 20).

### Forma de Weibull pelo tempo de motor (monomotores; k = 1 é taxa constante)

```text
     motor                       tempo  n_falhas  n_controles  forma  forma_ic95_inf  forma_ic95_sup  p_valor_taxa_constante  mediana_falhas_h  mediana_controles_h
    pistao TSO (desde a revisão geral)       903         4000  0.992           0.936           1.049                   0.786             833.0                725.0
    pistao            TSN (desde novo)       977         4689  1.076           1.023           1.130                   0.005            2274.0               2085.0
turboelice TSO (desde a revisão geral)        32          177  1.278           0.970           1.586                   0.077            3518.5               2162.0
turboelice            TSN (desde novo)        56          345  1.131           0.930           1.332                   0.202            6884.5               3990.0
```

### Chance relativa de falha por quartil de tempo (1º quartil = 1)

```text
     motor tempo     faixa_h  falhas  controles  chance_relativa
    pistao tso_h     0 a 307     210       1001             1.00
    pistao tso_h   307 a 725     210       1001             1.00
    pistao tso_h  725 a 1293     242        999             1.15
    pistao tso_h  1293 a inf     241        999             1.15
    pistao tsn_h     0 a 828     184       1173             1.00
    pistao tsn_h  828 a 2085     274       1172             1.49
    pistao tsn_h 2085 a 3896     253       1172             1.38
    pistao tsn_h  3896 a inf     266       1172             1.45
turboelice tso_h     0 a 680       7         45             1.00
turboelice tso_h  680 a 2162       6         44             0.88
turboelice tso_h 2162 a 4065       6         44             0.88
turboelice tso_h  4065 a inf      13         44             1.90
turboelice tsn_h    0 a 1529      12         87             1.00
turboelice tsn_h 1529 a 3990       3         86             0.25
turboelice tsn_h 3990 a 9254      19         86             1.60
turboelice tsn_h  9254 a inf      22         86             1.85
```
