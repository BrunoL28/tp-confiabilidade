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
