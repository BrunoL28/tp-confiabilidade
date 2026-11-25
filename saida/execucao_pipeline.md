# Execução do pipeline

Gerado por `src/executar_tudo.py` em 25/11/2026 12:31. Bases: NTSB (avall, 2008 a 2026) e SDRS (FAA, 2008 a 2025).

## 02_tratar_ntsb.py

> NTSB: 18735 avião-eventos (pistão, turboélice, turbofan), anos 2008 a 2026; 3258 de construção amadora excluídos; 86 com TSO > TSN descartados; 42 turbofans com num_eng = 1 tratados como número de motores desconhecido
> Findings de motopropulsor nos aviões com falha: 2069 (77 de operação descartados; sem bloco: 535 genéricos, sem componente, e 146 de componentes fora do modelo)

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
carburador_injecao     121           0         0
combustivel              0           0         8
combustivel_fcu          0          11         0
compressor               0          14         0
compressores             0           0        18
fadec                    0           0         1
fan                      0           0         1
helice_governador       36           7         0
lubrificacao           127           9         0
magnetos               102           0         0
nucleo                 532           0         0
turbinas                 0          22        12
```

## 03_tratar_sdrs.py

> SDRS: relatos de 2008 em diante, sem os modelos ^(R22|R44|R66|47G|UH12)

### Relatos por motor em cada filtro

```text
     motor                arquivo  relatos  duplicados  antes_de_ano_inicio  helicopteros  analisados  com_bloco  genericos  fora_do_modelo  ano_min  ano_max maior_operador  parcela_maior_operador
    pistao pistao_lycoming540.csv     2746           0                  252          1026        1468        770         58             640     2008     2025           YAXA                   0.030
turboelice  turboelice_pt6a34.csv      269           0                   14             0         255         77         46             132     2008     2025           AXSA                   0.026
  turbofan   turbofan_cfm56_7.csv     6855           0                   80             0        6775       3093        807            2875     2008     2025           ASAA                   0.764
```

### Relatos por bloco

```text
motor               pistao  turboelice  turbofan
bloco                                           
admissao                78           0         0
bombas                  65           0         0
caixa_acessorios         0           0        45
caixa_reducao            0           1         0
camara_combustao         0           4         2
carburador_injecao      61           0         0
combustivel              0           0      1005
combustivel_fcu          0          32         0
compressor               0          12         0
compressores             0           0       615
entrada_ar               0           2         0
fadec                    0           0       105
fan                      0           0       883
helice_governador       55           4         0
lubrificacao            51           5       330
magnetos               201           0         0
nucleo                 259           0         0
turbinas                 0          17       108
```

## 04_analise_confiabilidade.py

> Frações e taxa das unidades: relatos de dificuldade em serviço (SDRS, FAA) (fonte_fracoes = sdrs)

### Métricas por motor

```text
                                       0           1         2
motor                             pistao  turboelice  turbofan
lambda_literatura_1e5h              12.4        0.15       0.2
lambda_eq_1h_1e5h                   12.4        0.15       0.2
lambda_eq_1000h_1e5h               12.45        0.15       0.2
mtbf_sem_reparo_h                   7702   6.667e+05 4.998e+05
mtbf_redundancia_restaurada_h       8065   6.667e+05     5e+05
R_1h                              0.9999           1         1
F_1h                            0.000124     1.5e-06     2e-06
F_1h_lambda_min                   0.0001     1.5e-06     1e-06
F_1h_lambda_max                0.0009995       1e-05     2e-05
R_1000h_sem_reparo                0.8829      0.9985     0.998
R_1000h_redundancia_restaurada    0.8834      0.9985     0.998
F_1h_total_preservado           0.000124     1.5e-06     2e-06
fracoes_provisorias                False       False     False
razao_para_pistao                      1       82.66        62
```

### Lambda por bloco (por 1e5 h)

```text
         motor                                     rotulo       estrutura     n    fracao  lambda_1e5h  lambda_inf_1e5h  lambda_sup_1e5h
0       pistao                                   Admissão           serie    78    0.1548        1.868            1.225            18.23
1       pistao                       Carburador / injeção           serie    61     0.121        1.461           0.9267            14.68
2       pistao  Cilindros, válvulas, pistões, virabrequim           serie   259    0.5139        6.204              4.6            53.96
3       pistao                               Lubrificação           serie    51    0.1012        1.222           0.7546            12.57
4       pistao                              Arrefecimento           serie     0         0            0                0           0.4811
5       pistao                        Hélice e governador           serie    55    0.1091        1.317           0.8231            13.42
6       pistao       Bombas de combustível (cada unidade)  par redundante    65       NaN       0.7996           0.4949            8.297
7       pistao                    Magnetos (cada unidade)  par redundante   201       NaN        2.473            1.691            23.45
8   turboelice                              Entrada de ar           serie     2   0.02597     0.003896        0.0008154          0.08071
9   turboelice                                 Compressor           serie    12    0.1558      0.02338          0.01322           0.2489
10  turboelice                        Câmara de combustão           serie     4   0.05195     0.007792         0.002668           0.1188
11  turboelice              Turbinas (compressor e livre)           serie    17    0.2208      0.03312          0.02092           0.3226
12  turboelice                           Caixa de redução           serie     1   0.01299     0.001948        0.0002107          0.05909
13  turboelice                        Hélice e governador           serie     4   0.05195     0.007792         0.002668           0.1188
14  turboelice                          Combustível (FCU)           serie    32    0.4156      0.06234          0.04654           0.5271
15  turboelice                               Lubrificação           serie     5   0.06494      0.00974         0.003781           0.1365
16    turbofan                                        Fan           serie   883    0.2955        0.059           0.0279           0.6228
17    turbofan                       Compressores LP e HP           serie   615    0.2058      0.04109          0.01913           0.4403
18    turbofan                        Câmara de combustão           serie     2 0.0006693    0.0001336        1.389e-05         0.004282
19    turbofan                           Turbinas HP e LP           serie   108   0.03614     0.007216         0.002985           0.0864
20    turbofan                                Combustível           serie  1005    0.3363      0.06715          0.03191           0.7054
21    turbofan                               Lubrificação           serie   330    0.1104      0.02205         0.009944           0.2436
22    turbofan                        Caixa de acessórios           serie    45   0.01506     0.003007         0.001113          0.03973
23    turbofan                   FADEC A/B (cada unidade)  par redundante   105       NaN     0.003514          0.00144           0.0425
```

### Frações NTSB x SDRS

```text
         motor               bloco                                     rotulo  n_ntsb  fracao_ntsb  ic_inf_ntsb  ic_sup_ntsb  lambda_unidade_1e5h_ntsb  n_sdrs  fracao_sdrs  ic_inf_sdrs  ic_sup_sdrs  lambda_unidade_1e5h_sdrs
0       pistao            admissao                                   Admissão      60      0.06818      0.05293      0.08627                       NaN      78       0.1548       0.1252       0.1883                       NaN
1       pistao  carburador_injecao                       Carburador / injeção     121       0.1375       0.1159       0.1614                       NaN      61        0.121      0.09474       0.1517                       NaN
2       pistao              nucleo  Cilindros, válvulas, pistões, virabrequim     532       0.6045       0.5719       0.6365                       NaN     259       0.5139       0.4703       0.5573                       NaN
3       pistao        lubrificacao                               Lubrificação     127       0.1443       0.1223       0.1687                       NaN      51       0.1012      0.07715       0.1298                       NaN
4       pistao       arrefecimento                              Arrefecimento       4     0.004545     0.001536      0.01077                       NaN       0            0            0     0.004969                       NaN
5       pistao   helice_governador                        Hélice e governador      36      0.04091      0.02929      0.05554                       NaN      55       0.1091      0.08415       0.1386                       NaN
6       pistao              bombas                Bombas de combustível (par)      12          NaN          NaN          NaN                   0.08455      65          NaN          NaN          NaN                    0.7996
7       pistao            magnetos                             Magnetos (par)     102          NaN          NaN          NaN                    0.7186     201          NaN          NaN          NaN                     2.473
8   turboelice          entrada_ar                              Entrada de ar       0            0            0      0.03562                       NaN       2      0.02597     0.005436      0.08071                       NaN
9   turboelice          compressor                                 Compressor      14       0.2029       0.1213       0.3088                       NaN      12       0.1558      0.08812       0.2489                       NaN
10  turboelice    camara_combustao                        Câmara de combustão       1      0.01449     0.001568      0.06573                       NaN       4      0.05195      0.01779       0.1188                       NaN
11  turboelice            turbinas              Turbinas (compressor e livre)      22       0.3188        0.218       0.4345                       NaN      17       0.2208       0.1395       0.3226                       NaN
12  turboelice       caixa_reducao                           Caixa de redução       5      0.07246      0.02819       0.1515                       NaN       1      0.01299     0.001405      0.05909                       NaN
13  turboelice   helice_governador                        Hélice e governador       7       0.1014      0.04654       0.1889                       NaN       4      0.05195      0.01779       0.1188                       NaN
14  turboelice     combustivel_fcu                          Combustível (FCU)      11       0.1594      0.08776       0.2589                       NaN      32       0.4156       0.3103       0.5271                       NaN
15  turboelice        lubrificacao                               Lubrificação       9       0.1304      0.06655       0.2245                       NaN       5      0.06494      0.02521       0.1365                       NaN
16    turbofan                 fan                                        Fan       1      0.02222     0.002408      0.09919                       NaN     883       0.2955       0.2794       0.3121                       NaN
17    turbofan        compressores                       Compressores LP e HP      18          0.4       0.2667       0.5457                       NaN     615       0.2058       0.1916       0.2206                       NaN
18    turbofan    camara_combustao                        Câmara de combustão       2      0.04444     0.009349        0.135                       NaN       2    0.0006693    0.0001391     0.002146                       NaN
19    turbofan            turbinas                           Turbinas HP e LP      12       0.2667       0.1548       0.4075                       NaN     108      0.03614      0.02989      0.04329                       NaN
20    turbofan         combustivel                                Combustível       8       0.1778      0.08781       0.3076                       NaN    1005       0.3363       0.3196       0.3534                       NaN
21    turbofan        lubrificacao                               Lubrificação       0            0            0        0.054                       NaN     330       0.1104      0.09958       0.1221                       NaN
22    turbofan    caixa_acessorios                        Caixa de acessórios       4      0.08889      0.03075       0.1976                       NaN      45      0.01506      0.01115      0.01991                       NaN
23    turbofan               fadec                            FADEC A/B (par)       1          NaN          NaN          NaN                  0.002222     105          NaN          NaN          NaN                  0.003514
```

### Pareto (voo de 1 h)

```text
         motor                                     rotulo  taxa_1e5h   parcela  parcela_min  parcela_max
0       pistao  Cilindros, válvulas, pistões, virabrequim      6.204    0.5003       0.4579       0.5426
1       pistao                                   Admissão      1.868    0.1507       0.1219       0.1833
2       pistao                       Carburador / injeção      1.461    0.1178      0.09224       0.1477
3       pistao                        Hélice e governador      1.317    0.1062      0.08193       0.1349
4       pistao                               Lubrificação      1.222   0.09852      0.07511       0.1264
5       pistao                             Magnetos (par)     0.2473   0.01994      0.01691      0.02346
6       pistao                Bombas de combustível (par)    0.07997  0.006449     0.004949     0.008297
7       pistao                              Arrefecimento          0         0            0     0.004838
8   turboelice                          Combustível (FCU)    0.06234    0.4156       0.3103       0.5271
9   turboelice              Turbinas (compressor e livre)    0.03312    0.2208       0.1395       0.3226
10  turboelice                                 Compressor    0.02338    0.1558      0.08812       0.2489
11  turboelice                               Lubrificação    0.00974   0.06494      0.02521       0.1365
12  turboelice                        Câmara de combustão   0.007792   0.05195      0.01779       0.1188
13  turboelice                        Hélice e governador   0.007792   0.05195      0.01779       0.1188
14  turboelice                              Entrada de ar   0.003896   0.02597     0.005436      0.08071
15  turboelice                           Caixa de redução   0.001948   0.01299     0.001405      0.05909
16    turbofan                                Combustível    0.06715    0.3358        0.319       0.3528
17    turbofan                                        Fan      0.059     0.295       0.2789       0.3115
18    turbofan                       Compressores LP e HP    0.04109    0.2055       0.1913       0.2202
19    turbofan                               Lubrificação    0.02205    0.1102      0.09941       0.1218
20    turbofan                           Turbinas HP e LP   0.007216   0.03608      0.02984      0.04322
21    turbofan                        Caixa de acessórios   0.003007   0.01503      0.01113      0.01987
22    turbofan                            FADEC A/B (par)  0.0003514  0.001757      0.00144     0.002125
23    turbofan                        Câmara de combustão  0.0001336 0.0006682    0.0001389     0.002142
```

### Redundância interna

```text
                                                    0               1                2
motor                                          pistao          pistao         turbofan
par                       Bombas de combustível (par)  Magnetos (par)  FADEC A/B (par)
taxa_unidade_1e5h                              0.7996           2.473         0.003514
beta                                              0.1             0.1              0.1
F_unidade_unica                             7.996e-06       2.473e-05        3.514e-08
F_par                                       7.997e-07       2.473e-06        3.514e-09
ganho_do_par                                    9.999           9.998               10
parcela_causa_comum                            0.9999          0.9998                1
F_motor_com_par                              0.000124        0.000124            2e-06
F_motor_sem_este_par                        0.0001312       0.0001462        2.032e-06
aumento_sem_este_par_pct                        5.803           17.94            1.581
F_motor_sem_nenhum_par                      0.0001534       0.0001534        2.032e-06
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
2      pistao  taxa da unidade: Bombas de combustível (par) (/1e5 h)     0.6137      1.029 0.000124  0.000124   0.000124                  1
3      pistao               taxa da unidade: Magnetos (par) (/1e5 h)      2.097      2.908 0.000124  0.000124   0.000124                  1
4  turboelice                           taxa total do motor (/1e5 h)       0.15          1  1.5e-06     1e-05    1.5e-06              6.667
5    turbofan                           taxa total do motor (/1e5 h)        0.1          2    1e-06     2e-05      2e-06                 20
6    turbofan                                         beta dos pares       0.01        0.3    2e-06     2e-06      2e-06                  1
7    turbofan              taxa da unidade: FADEC A/B (par) (/1e5 h)    0.00288    0.00425    2e-06     2e-06      2e-06                  1
```

## 05_bayes_weibull.py

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
