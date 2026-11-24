# Roteiro da apresentação

**Tempo:** 10 min de apresentação e 5 min de arguição. Slides em `apresentacao/slides.pdf`: 13 slides de conteúdo, 1 de encerramento e 1 de apoio, só para a arguição.

A divisão segue a ordem dos autores, e cada pessoa fica com cerca de 2 min. Se quiserem trocar quem fala o quê, basta trocar os nomes: os blocos não dependem uns dos outros.

| Pessoa | Slides | Tema | Tempo | Acumulado |
|---|---|---|---|---|
| 1. Ana | 1–4 | Abertura, motivação, Engenharia de Sistemas, literatura | 2:05 | 2:05 |
| 2. Bruno | 5–6 | Sistema (RBD) e método | 2:00 | 4:05 |
| 3. Eduarda | 7–8 | Comparação entre tecnologias e subsistemas críticos | 1:55 | 6:00 |
| 4. Mariana | 9–10 | Redundância interna e dois pistões × uma turbina | 2:00 | 8:00 |
| 5. Victor | 11–14 | Dados do CENIPA, limitações, conclusões e encerramento | 2:00 | 10:00 |

As falas abaixo têm cerca de 250 palavras por pessoa, o que dá 2 min em ritmo calmo. Não é para ler: usem como guia e decorem só os números em **negrito**.

---

## 1. Ana: slides 1 a 4 (2:05)

**Slide 1: título (10 s)**
> Boa tarde. Nosso trabalho compara a confiabilidade de três tecnologias de motor aeronáutico: pistão, turboélice e turbofan. Sou a Ana, e apresento com Bruno, Eduarda, Mariana e Victor.

**Slide 2: motivação e objetivos (40 s)**
> Num monomotor, não existe propulsão de reserva. A literatura diz que motores a pistão falham entre **10 e 100 vezes a cada 100 mil horas**, e as turbinas, **menos de 1**. Só que esse número vem como uma taxa única para o motor inteiro: não diz onde estão as falhas nem se a redundância compensa uma tecnologia pior.
> Nossos objetivos: modelar cada motor, calcular taxa de falha, MTBF e confiabilidade, avaliar as redundâncias e achar os subsistemas críticos.

**Slide 3: Engenharia de Sistemas (45 s)**
> Esse é, antes de tudo, um problema de Engenharia de Sistemas. Começamos pela fronteira e pelo requisito: falha é não entregar a potência exigida, e tanques ou erro do piloto ficam de fora. Depois decompomos: aeronave, motor, subsistemas, componentes. A confiabilidade não está em nenhuma peça isolada: ela **emerge da arquitetura**, de como os blocos se arranjam em série ou em paralelo. A pergunta de um ou dois motores é um **trade-off de arquitetura**, e a resposta depende da dependência entre as partes. E fechamos o ciclo de vida: usamos dados de operação e manutenção para dizer onde o projeto deve intervir.

**Slide 4: literatura (30 s)**
> RBD, árvore de falhas e o fator beta já foram usados em propulsão. Mas, para turbinas, o que se publica costuma ser limite regulatório, que diz quanto o motor *pode* falhar, não quanto falha, e as bases de ocorrências não trazem horas voadas. Ninguém comparou as três tecnologias no mesmo modelo. O Bruno explica como fizemos isso.

---

## 2. Bruno: slides 5 e 6 (2:00)

**Slide 5: sistema e RBD (55 s)**
> Escolhemos um motor representativo de cada tecnologia: o Lycoming O-540, o PT6A-34 e o CFM56-7B, que equipa o Boeing 737. A falha que modelamos é a perda de potência que obriga a desligar o motor.
> No diagrama, todo bloco em série derruba o motor sozinho. Os blocos empilhados são pares redundantes. No pistão, são as duas bombas de combustível e os dois magnetos, que alimentam velas separadas em cada cilindro. No turbofan, é o FADEC, o computador de controle com dois canais. O turboélice não tem redundância: toda a vantagem dele precisa vir da baixa taxa de cada componente.

**Slide 6: método (65 s)**
> O modelo supõe taxa constante. Em série, as confiabilidades se multiplicam. Nos pares, uma fração beta das falhas é de causa comum, como combustível contaminado nas duas bombas, e essa parte derruba o par inteiro. É a equação do slide.
> A taxa total de cada motor vem da literatura: **12,4** para o pistão, **0,15** para o turboélice e **0,20** para o turbofan, por 100 mil horas. Essa taxa é distribuída entre os blocos pela fração de registros de cada um. Para isso, classificamos **6 432 registros**: 4 295 do SDRS, da FAA, 2 097 do NTSB e 40 de relatórios do CENIPA que lemos um a um, de um total de 86.
> As frações têm intervalo de confiança de Jeffreys. Também montamos uma rede bayesiana equivalente ao diagrama e ajustamos uma Weibull ao tempo desde a revisão. A Eduarda mostra o que saiu disso.

---

## 3. Eduarda: slides 7 e 8 (1:55)

**Slide 7: comparação entre tecnologias (50 s)**
> O primeiro resultado é a diferença de ordem de grandeza. Num voo de uma hora, o pistão tem probabilidade de falha de **1,24 por 10 mil**, que é **83 vezes** a do turboélice e **62 vezes** a do turbofan. Num ano de mil horas, a chance de pelo menos uma falha chega a **12%** no pistão, contra 0,15% a 0,20% nas turbinas.
> Mesmo no caso mais favorável ao pistão, ele ainda falha **5 vezes** mais. Entre turboélice e turbofan, as faixas se sobrepõem, e o modelo não consegue dizer qual é melhor.

**Slide 8: subsistemas (65 s)**
> Onde estão as falhas? No pistão, o núcleo mecânico, ou seja, cilindros, válvulas, pistões e virabrequim, responde por **57%**. Os cinco blocos em série sem redundância somam 98%. Os magnetos duplicados ficam com só 1%: a redundância protege bem uma parte que já falhava pouco.
> No turbofan, o fan apareceu com 28%, o que nos pareceu estranho. Lemos a ficha completa de 101 desses registros: **94** foram achados em solo, durante a manutenção programada, quase todos desgaste de peças trocadas na lubrificação das pás. E 68% dos registros do motor vêm de um único operador. Ou seja, no turbofan o Pareto mostra onde a manutenção encontra problemas, não onde o motor falha em voo. A Mariana fala agora da redundância.

---

## 4. Mariana: slides 9 e 10 (2:00)

**Slide 9: redundância interna (55 s)**
> Os pares redundantes reduzem em cerca de **10 vezes** a chance de perder a função. Esse número não é coincidência: com beta igual a 0,1, quase toda a falha do par vem da causa comum, e o ganho fica perto de 1 sobre beta. Ou seja, a causa comum limita o que a duplicação consegue entregar.
> Sem os dois pares, o motor a pistão falharia **12%** mais. A rede bayesiana confirma pelo outro lado: decolar com um magneto já inoperante aumenta o risco do voo em 9,4%. No FADEC, há só 19 registros, em parte porque o próprio sistema tolera falhas sem gerar notificação.

**Slide 10: dois pistões × uma turbina (65 s)**
> Agora a pergunta principal: dois motores menos confiáveis compensam um motor mais confiável? Se as falhas dos dois pistões fossem independentes, a perda total de propulsão seria de 1,5 em 100 milhões por hora, muito melhor que uma turbina.
> Mas existe causa comum entre os motores: o mesmo combustível, a mesma equipe de manutenção, o mesmo gelo. No gráfico, a linha azul sobe com o beta entre motores e cruza a do turboélice em **beta igual a 0,012**, ou 0,016 contra o turbofan. Ou seja, basta pouco mais de **1%** das falhas serem comuns para o bimotor a pistão perder a vantagem, e a faixa usual de beta vai de 1% a 30%. E o bimotor ainda dobra a chance de ter alguma falha de motor no voo. O Victor mostra o que os dados reais dizem sobre isso.

---

## 5. Victor: slides 11 a 14 (2:00)

**Slide 11: CENIPA (45 s)**
> O modelo só conta a perda total de propulsão. Ele não mede a dificuldade de voar com um motor parado. Para isso, usamos as ocorrências do CENIPA de 2007 a 2026. No turboélice, o segundo motor derruba a proporção de falhas que viram acidente de 40% para **4,8%**, 8 vezes menos. No pistão, cai de 62% para **38%**, só 1,6 vez. Nos jatos, nenhuma das 488 falhas virou acidente. Esses números são indicativos: há subnotificação de incidentes leves, e mono e multimotores fazem operações diferentes.

**Slide 12: limitações (30 s)**
> As principais limitações: as frações somam três bases que medem coisas diferentes; o SDRS registra dificuldades de manutenção, não só falhas em voo; a Weibull ajustada ao tempo desde a revisão tem forma 2,3, o que sugere desgaste e coloca em dúvida a taxa constante; e, sem horas voadas, não conseguimos estimar taxas absolutas.

**Slide 13: conclusões (40 s)**
> Concluindo: o pistão falha de **62 a 83 vezes** mais que as turbinas, e isso não depende do valor escolhido na literatura. Suas falhas estão no núcleo mecânico, onde não há redundância. E a redundância não compensa a tecnologia: dois pistões só superam uma turbina se a causa comum ficar abaixo de 1,2 a 1,6%, e os dados do CENIPA apontam na mesma direção. A lição de sistemas é que uma decisão de arquitetura só se avalia com as dependências entre as partes: quem ignora a causa comum superestima o ganho da redundância. Como próximos passos, propomos filtrar os eventos em voo, obter horas voadas e tratar os dados de tempo com censura.

**Slide 14: encerramento (5 s)**
> Obrigado. Ficamos à disposição para perguntas.

---

## Arguição (5 min)

O slide 15 fica depois do encerramento, como apoio, com sensibilidade, rede bayesiana e Weibull. Cada pergunta tem um responsável, que pode passar a palavra.

| Pergunta provável | Quem responde | Resposta curta |
|---|---|---|
| Por que a taxa total vem da literatura e não dos dados? | Bruno | As bases não têm horas voadas: dão a proporção entre subsistemas, não a taxa. A literatura dá o total, e as contagens dividem esse total entre os blocos. |
| Como escolheram o β? | Mariana | Faixa assumida de 0,01 a 0,3, com 0,1 como nominal. Por isso a pergunta do bimotor foi respondida ao contrário: em vez de fixar β, calculamos o β de empate. |
| Por que β não muda P(falha em 1 h)? | Mariana | A taxa publicada é preservada em 1 h. β só redistribui a taxa entre os blocos e muda o Pareto (slide 15). |
| O fan de 28% não invalida o Pareto do turbofan? | Eduarda | Invalida como distribuição de falhas em voo, e por isso tratamos como distribuição de achados de manutenção. Corrigir só o fan distorceria os outros blocos, que têm o mesmo viés. |
| A taxa constante vale? | Victor | A Weibull sugere desgaste (forma 2,3; p = 0,009), mas com n = 10 e sem os motores que seguem voando. Fica como trabalho futuro com dados censurados. |
| Por que turboélice e turbofan não têm ordem? | Eduarda | As faixas publicadas (0,15–1 e 0,10–2 por 10⁵ h) se sobrepõem quase por inteiro. |
| Onde está a Engenharia de Sistemas no trabalho? | Ana | Na fronteira e no evento de falha (requisito), na decomposição em subsistemas, na confiabilidade como propriedade emergente da arquitetura, no trade-off entre um e dois motores e no uso de dados de operação para orientar projeto e manutenção (slide 3). |
| Que decisão de projeto o resultado orienta? | Mariana | No pistão, investir na confiabilidade do núcleo mecânico rende mais que duplicar componentes. Entre arquiteturas, um bimotor a pistão só se justifica se a causa comum entre os motores ficar abaixo de cerca de 1%. |

## Antes do dia

- Ensaiar uma vez com cronômetro. Se passar de 10:30, pular primeiro o slide 4 (Ana resume a literatura em uma frase no fim do slide 3).
- Combinar as passagens: cada pessoa termina chamando a próxima pelo nome (já está nas falas).
