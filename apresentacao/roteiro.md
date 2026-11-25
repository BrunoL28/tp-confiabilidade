# Roteiro da apresentação

**Tempo:** 10 min de apresentação e 5 min de arguição. 17 slides de conteúdo, 1 de encerramento e 1 de apoio (só para a arguição). Cada pessoa fala cerca de 2 min. Não é para ler: decorem só os números em **negrito**.

| Pessoa | Slides | Tema |
|---|---|---|
| 1. Ana | 1–4 | Abertura, problema, conceitos, Engenharia de Sistemas |
| 2. Bruno | 5–7 | Os três diagramas, o método e as duas bases |
| 3. Eduarda | 8–10 | Comparação entre motores, onde estão as falhas, NTSB × SDRS |
| 4. Mariana | 11–13 | O que a peça reserva esconde, ganho dos pares, dois motores |
| 5. Victor | 14–19 | Gravidade da falha, envelhecimento, limitações, conclusões, referências |

---

## 1. Ana (slides 1–4)
- **1. Título:** apresenta o tema e o grupo.
- **2. O problema:** num monomotor, se o motor para, o avião vira planador. A literatura diz **cerca de 12** falhas a cada 100 mil horas no pistão e **menos de 1** nas turbinas, mas é um número só para o motor inteiro. Objetivos: desenhar, calcular, medir a redundância, achar as peças críticas.
- **3. Conceitos:** taxa de falha, confiabilidade, MTBF (**não é vida útil**) e o diagrama de blocos: série são as lâmpadas de Natal; par só para se as duas falharem, exceto por causa comum.
- **4. Engenharia de Sistemas:** a confiabilidade **emerge da arquitetura**; um ou dois motores é um trade-off que depende da causa comum.

## 2. Bruno (slides 5–7)
- **5. Diagramas:** pistão com dois pares (bombas e magnetos), turboélice todo em série, turbofan com FADEC de dois canais.
- **6. Método:** a literatura diz **quanto** o motor falha; o SDRS diz **como dividir** entre as peças (exemplo: núcleo **50% de 12,4 = 6,2**); o diagrama junta tudo; o NTSB confere com falhas reais.
- **7. Bases:** NTSB é **o que derruba o avião** (2899 falhas); SDRS é **o que dá trabalho na oficina** (3940 relatos). Mesmo código de peça (ATA).

## 3. Eduarda (slides 8–10)
- **8. Resultado 1:** pistão falha **1 vez a cada 8 mil voos** de 1 h; turbinas, 1 a cada 500–670 mil. **62 a 83 vezes** mais. Em 1000 h, **12%** contra 0,2%. Turboélice × turbofan: empate.
- **9. Resultado 2:** no pistão, **metade** das falhas no núcleo mecânico, sem reserva. Magnetos: só **2%**, porque são dois.
- **10. NTSB × SDRS:** o núcleo do pistão lidera nas duas (**60% e 51%**): resultado mais robusto. No turbofan, o fan tem 1 caso no NTSB e 883 relatos no SDRS: **94 de 101** eram achados de inspeção, e **76%** vêm de uma só empresa.

## 4. Mariana (slides 11–13)
- **11. O que a reserva esconde:** magneto falha, o outro segura, avião pousa normal, o NTSB não vê, o SDRS vê. Por isso o SDRS registra **3,4 vezes** mais falhas de magneto.
- **12. Ganho dos pares:** **10 vezes**, porque quase toda falha do par é causa comum (ganho ≈ 1/β). Com um magneto só, o motor falharia **18%** mais; sem os dois pares, **24%**.
- **13. Dois motores:** independentes seriam **100 vezes** melhores que uma turbina, mas a causa comum domina. Empate quando **1,2 a 1,6** em cada 100 falhas atingem os dois; a literatura usa 1 a 30, então **a turbina ganha**.

## 5. Victor (slides 14–19)
- **14. Gravidade:** **11%** fatal no monomotor e **43%** no multimotor a pistão, mas é viés: o monomotor sempre entra na base, o bimotor só quando dá errado (**hospital × UTI**). Quando dá errado, é perda de controle com um motor puxando para o lado.
- **15. Envelhecimento:** curva da banheira; comparamos **903** motores que falharam com **4000** de acidentes por outro motivo. Desde a revisão, **k = 0,99**: não envelhece, e a hipótese do modelo vale.
- **16. Limitações:** viés de cada base, poucos dados no turboélice, β assumido, sem horas voadas.
- **17. Conclusões:** 62 a 83 vezes; metade no núcleo; pares ganham 10×; **redundância não compensa tecnologia**.
- **18–19. Referências e perguntas.**

**Slide de apoio (20):** sensibilidade, números das bases, pane seca (**1532** no pistão) e Weibull completo.

---

## Arguição (5 min)

O slide 20 fica depois do encerramento, como apoio: sensibilidade, números das bases, pane seca e Weibull. Cada pergunta tem um responsável, que pode passar a palavra.

| Pergunta provável | Quem responde | Resposta curta |
|---|---|---|
| Onde está a Engenharia de Sistemas no trabalho? | Ana | Na fronteira e no evento de falha (requisito), na decomposição em subsistemas, na confiabilidade como propriedade que emerge da arquitetura, no trade-off entre um e dois motores e no uso de dados de operação e manutenção para orientar o projeto (slide 4). |
| Um MTBF de 8 mil horas quer dizer que o motor dura 8 mil horas? | Ana | Não. É a média de horas entre falhas somando a frota: uma frota que voa 8 mil horas tem, em média, uma falha. A vida de cada motor é limitada pela revisão geral, que vem bem antes. |
| Por que a taxa total vem da literatura e não dos dados? | Bruno | Nenhuma das duas bases traz horas voadas da frota. Elas dizem como as falhas se dividem entre as peças, não quantas acontecem por hora. A literatura dá o total (12,4; 0,15; 0,20 por 10⁵ h) e as contagens só dividem esse total. |
| Por que usar o SDRS para dividir a taxa, e não o NTSB? | Bruno | O SDRS vê as falhas que a peça reserva segurou (3,4 vezes mais falhas de magneto que o NTSB) e tem mais dados (3940 relatos). O NTSB, que só vê acidentes, fica para conferir o modelo: gravidade e idade do motor. |
| Como um relato vira um bloco do diagrama? | Bruno | Pelo código da peça, que segue os capítulos ATA (8530 cilindros, 7414 magneto, 7250 turbinas), com o mesmo mapa nas duas bases. Registros que não dizem a peça ficam fora e supõe-se que se dividem como os demais. |
| Por que a pane seca ficou fora? | Bruno | É falha de operação, não do motor: o motor estava bom e faltou combustível. Fica contada à parte: 1532 panes no pistão, 174 fatais (slide 20). |
| Por que turboélice e turbofan empatam? | Eduarda | As faixas publicadas (0,15 a 1 e 0,10 a 2 por 10⁵ h) se sobrepõem quase por inteiro. |
| O Pareto do turbofan, com o fan em 30%, vale? | Eduarda | Ele mostra a manutenção, não a falha em voo: 94 de 101 relatos de fan eram achados de inspeção, e 76% dos relatos do turbofan vêm de uma empresa. No NTSB, o fan tem 1 caso. O resultado robusto é o núcleo do pistão (60% no NTSB, 51% no SDRS). |
| No turboélice, o combustível (FCU) lidera no SDRS e as turbinas no NTSB. Qual vale? | Eduarda | Nenhuma ordem é segura: são 77 relatos e 69 achados, com intervalos de 31% a 53% (FCU no SDRS) e de 22% a 43% (turbinas no NTSB). As duas bases concordam que FCU, turbinas e compressor somam a maior parte. |
| Como escolheram o β? | Mariana | Faixa assumida de 0,01 a 0,3, com 0,1 como nominal. Por isso a pergunta do bimotor foi respondida ao contrário: em vez de fixar β, calculamos o β de empate. |
| Por que β não muda a chance de falha do motor em 1 h? | Mariana | A taxa da literatura é mantida em 1 h. β e a taxa das unidades só redistribuem essa taxa entre as peças e mudam o Pareto (slide 20). |
| Os magnetos são só 2% do Pareto, mas com um magneto só o motor falha 18% mais. Como? | Mariana | Com o par, cada magneto (2,47 por 10⁵ h) só pesa pela causa comum, cerca de 0,25. Com um magneto só, a taxa inteira entra: 2,2 a mais sobre 12,4, cerca de 18%. |
| Por que o FADEC duplicado ajuda tão pouco? | Mariana | Cada canal falha 0,0035 por 10⁵ h, contra 0,2 do turbofan inteiro: o controle é parte pequena da falha do motor. Perder um canal aumenta a chance de falha em só 1,6%. |
| Que decisão de projeto o resultado orienta? | Mariana | No pistão, investir no núcleo mecânico, que tem metade das falhas e nenhuma reserva, rende mais que duplicar componentes. Entre arquiteturas, um bimotor a pistão só se justifica se a causa comum entre os motores ficar abaixo de cerca de 1%. |
| Por que o multimotor tem mais falhas fatais? | Victor | Seleção: no multimotor, a falha que termina em pouso normal quase não vira acidente nem entra no NTSB. Quando entra, a perda de controle com um motor puxando para o lado pesa. |
| A taxa constante vale? | Victor | No pistão, desde a revisão, sim: k = 0,99 (IC 0,94 a 1,05). Desde novo há desgaste leve (1,08). No turboélice, 1,28 com só 32 falhas e intervalo que inclui 1. O teste supõe que os motores dos aviões acidentados por outra causa tenham a idade da frota. |

## Antes do dia

- Ensaiar uma vez com cronômetro: são 17 slides de conteúdo em 10 min. Se passar de 10:30, encurtar primeiro os slides 3 (conceitos) e 10 (NTSB × SDRS).
- Combinar as passagens: cada pessoa termina chamando a próxima pelo nome.
