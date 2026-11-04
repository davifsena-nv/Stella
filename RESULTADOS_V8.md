# Resultado da pesquisa — versão 8.0

Nas 100 mil linhas, o score oficial passou de **76,10 para 78,17/100** (78,1659; 78,1419 antes do autotreinamento de contexto da seção 6), ganho de 2,07 pontos. O acerto de processo por evento passou de 89,81% para **91,78%**. A meta de 90 **não** foi atingida. Os experimentos de teto abaixo indicam que 90 está acima da informação disponível nos cinco campos admitidos, ao menos para toda a família de modelos testada.

| Componente | Versão 7 | Versão 8 |
| --- | ---: | ---: |
| F1 das famílias | 87,10 | 89,07 |
| F1 dos pares | 79,78 | 79,32 |
| F1 dos casos inteiros | 70,96 | 75,01 |
| Score combinado | 76,10 | 78,14 |
| Casos exatamente recuperados | 26.957 | 29.099 |
| Precisão / recall dos pares | 75,79 / 84,22 | 89,95 / 70,94 |

Foram inferidos 39.894 casos para 37.689 de referência. Todas as linhas foram preservadas, e o avaliador e seus pesos permaneceram intactos (o hash sintático foi conferido). Base de 60 mil eventos: 72,96, sem alteração (ela segue o caminho do grafo, porque não tem atividades transversais). Teste sintético: 73,51; o controle embaralhado continua sem rotinas.

## 1. Diagnóstico que orientou a versão 8

1. **O F1 de pares mede, na prática, apenas 6 casos.** Recalculando precisão e recall só com os seis fechamentos mensais (MC2601–MC2606), obtém-se 75,76% / 84,24% / F1 79,77%, contra 75,79% / 84,22% / 79,78% reportados para a base inteira. Os 6 casos somam 26,1 milhões de pares; os outros 37.683 contribuem com uma fração desprezível. Portanto, 40% do score depende de 17,7% dos eventos.
2. **A base tem um único usuário e três trilhas físicas sem sobreposição.** Reconstruindo as trilhas pelos casos de interrupção, não há sobreposição dentro da trilha (0 de 46.246 eventos).
3. **Cada caso contém um único processo, e as etapas ciclam** (0→1→…→L−1→0). Dentro de um caso, só ocorrem saltos de +1 ou o retorno da última etapa para a primeira. Um caso P começa sempre na etapa de entrada.
4. **Uma interrupção de navegação inicia um caso** e absorve o trabalho imediatamente seguinte na mesma trilha. O retorno após a interrupção ocorreu sempre em menos de 75 s. Uma cadeia que começa numa etapa diferente da entrada logo após uma interrupção é sempre a continuação dela.
5. **O fechamento mensal (MC) é composto por 11.810 etapas próprias e 5.892 eventos embutidos de outros processos.** Os embutidos formam minicadeias válidas (853 pares consecutivos seguem o ciclo) e ocupam as mesmas trilhas que as tarefas independentes. Os intrusos da v7 (2.421) eram tarefas independentes dos dias de fechamento; os faltantes (1.455) eram esses eventos embutidos.

Esses padrões foram descobertos inspecionando as referências da própria base. Eles **orientaram hipóteses estruturais**, mas nenhuma referência entra na inferência.

## 2. O que produziu ganho

- **Estados limpos.** Protótipos cujo nome de tela aparece em três ou mais aplicativos são opacos e deixam de definir etapas (`erp/re`, `excel/re`, `outlook/cf`). Nomes frequentes de um só aplicativo, não derivados de outros, foram acrescentados: `tie.cp`, `chk_end` e `ret.0`. Com isso, **os 12 ciclos aprendidos coincidem exatamente com os templates de referência**, sem que a referência seja usada.
- **Entrada pelo salto de frequência.** Como as tarefas são ciclos truncados, as etapas ficam cada vez mais raras ao longo do ciclo. A entrada é o estado com maior razão freq(s)/freq(anterior). A regra anterior (taxa de órfãos) errava em 2 dos 12 grupos.
- **Emissão lexical + EM.** A regra inicial cobre nome exato, sufixo, prefixo de 2 caracteres + `_`, inicial + dígitos e o aplicativo. O EM leva a acurácia por chave a 65,3%, perto do teto por chave de 67,5%.
- **Feixe sobre trilhas físicas** (motor_trilhas.py). Cada trilha guarda uma crença de fase. As decisões são continuar, nova tarefa, retomar após interrupção, subtarefa de episódio e etapa de episódio. As razões Q/π tornam os custos comparáveis entre opções. Os custos de tarefa vêm de frequências das decisões (EM rígido). O retorno imediato foi estimado pelo joelho da distribuição decodificada e deu 80 s, sem usar referências.
- **Feixe 256 na última iteração** (+0,46 sobre 128).

## 3. Experimentos rejeitados

| Ensaio | Score | Decisão |
| --- | ---: | --- |
| Ligador de cadeias com rótulos rígidos da v7 | 51,3* | rejeitado |
| Ligador suave + forward-backward por cadeia | 69,5* | substituído pelo feixe |
| Tabela completa de transição aprendida por EM (incluindo episódio) | 73,9 → 70,3* | divergiu: o episódio se autorreforça |
| Tabela de espera aprendida por EM rígido | 73,66 | rejeitado (autoconfirmação) |
| Retorno pelo percentil 99 das esperas decodificadas | 75,85 (navmax=182 s) | trocado pelo joelho (80 s) |
| Distribuição de etapas das subtarefas aprendida por EM | 77,52 | rejeitado |
| c_emb=2,7 / c_toF=0,2 | 77,28 / 77,93 | rejeitados (jan–mar e abr–jun) |
| Feixe final 512 | 78,01 | sem ganho sobre 256 |
| União v7∪v8 para o episódio | +0,1* | não adotado |

\* Pontuador rápido, com F1 de famílias fixo em 87,1. Os demais valores são do avaliador oficial.

Também foram testados três sinais que se mostraram **nulos**: a duração por etapa (cerca de 95 s em todas as etapas), o nome da tela de navegação como preditor de continuação (cerca de 50% para todos os 14 nomes) e a diferença entre as esperas de continuação e de nova tarefa (distribuições iguais).

**Protocolo dos hiperparâmetros de episódio** (c_emb=2,2, c_embc=1,1, c_toF=0,5): escolhidos em janeiro–março e conferidos em abril–junho. No motor final: jan–mar 78,05, abr–jun 78,23. São os únicos parâmetros escolhidos com referência e estão declarados em `PARAMETROS_V8`.

## 4. Por que 90 não foi alcançado: experimentos de teto

| Condição (informação fornecida ao decodificador) | Score | Casos exatos |
| --- | ---: | ---: |
| v8 real (5 campos) | **78,14** | 75,0% |
| Emissão ótima por chave (distribuição verdadeira da etapa dada aplicativo+tela) | 79,2* | 78,3% |
| v7 + MC perfeito (oráculo) | 85,27* | 73,2% |
| Etapa verdadeira de **todo** evento, MC inferido | 83,37* | 85,2% |
| Etapa verdadeira de todo evento + MC perfeito | 91,04* | 84,7% |

- A emissão aprendida (65,3%) já está a 2,2 pontos do **teto por chave** (67,5%). Cerca de 1/3 dos eventos tem telas opacas compartilhadas por vários processos, e nenhuma informação adicional dos 5 campos resolve isso: a duração e o nome da navegação são nulos.
- Mesmo conhecendo a etapa verdadeira de todos os eventos, o feixe recupera 85% dos casos. Restam ambiguidades intrínsecas: o retorno da última etapa para a entrada versus uma nova tarefa do mesmo processo; 1.317 continuações de interrupção que começam numa nova tarefa; e tarefas concorrentes do mesmo processo.
- 90 só aparece com **etapa verdadeira de todos os eventos e MC perfeito** (91,04). Com a informação realmente disponível, o melhor resultado medido foi 79,2.

Isso não é uma prova de impossibilidade: um modelo de outra família poderia extrair mais. Mas é forte evidência de que 90 exige informação que os cinco campos não contêm, como identificadores de objeto (documento, conta, lote) ou uma amostra rotulada.

## 5. Ameaças à validade

- **Sobreajuste ao benchmark.** As hipóteses estruturais (trilhas, ciclos, interrupção que abre caso, episódio com subtarefas) vieram da inspeção das referências desta base sintética (`CONTABIL_SINTETICO_01`). A inferência não lê referências, mas o modelo foi desenhado para este gerador. A generalização para logs reais não está demonstrada.
- **Só um usuário.** O motor trata pessoa e dia separadamente, mas isso não foi testado com vários usuários reais.
- Os custos de episódio foram escolhidos com referência (jan–mar). A metade de verificação (abr–jun) não é uma validação externa.

## 6. Continuação: maximizar o acerto de processo por evento

Métrica: fração dos eventos cuja família inferida, após o alinhamento um a um do avaliador, coincide com o processo de referência (`acerto_entre_cobertos`). Ponto de partida da v8: 91,49% (v7: 89,81%).

| Categoria (100 mil eventos) | n | Acerto | Teto só pela tela |
| --- | ---: | ---: | ---: |
| Interrupções e etapas do fechamento | 33.539 | ≈100% | ≈100% |
| Telas limpas (qualquer dia) | 28.851 | 99,5% | 99,3% |
| Telas opacas, dias normais | 28.989 | 84,1% | 44,5% |
| Telas opacas, independentes em dias de fechamento | 5.239 | 65,4% | 45,8% |
| Telas opacas embutidas no fechamento | 3.382 | 51,1% | 45,5% |

O erro está quase todo nas telas opacas: nomes compartilhados por vários processos, para os quais a própria tela acerta no máximo cerca de 45%. Dos erros opacos dos dias normais, 2/3 estão em casos previstos sem nenhuma tela limpa como âncora.

| Ensaio | Acerto | Decisão |
| --- | ---: | --- |
| Família pela marginal do grupo, em vez do estado | 91,50 | sem efeito |
| Média de 4 decodificações (feixes e custos diferentes) | 91,60 | +0,10, custo 4× |
| Classificador de contexto pós-hoc (rótulos = telas limpas, sem a tela do evento) | 91,74 | base do ciclo seguinte |
| Idem com posteriores do feixe nos vizinhos | 91,67 | rejeitado |
| **Co-treinamento: contexto realimenta a emissão das opacas (β=0,5) + família combinada (0,5)** | **91,78** | **adotado** |
| Co-treinamento β=1,0 | 91,66 | rejeitado |
| c_emb 1,7 / 2,7, c_toF 1,0 (com co-treinamento) | 91,76 / 91,79 / 91,75 | platô |
| Contexto com a etapa dos vizinhos | 91,81 | +0,05, não adotado |
| Votação de 5 execuções | 91,85 | +0,08, custo 5×; não adotado |

O classificador de contexto (HistGradientBoosting) é treinado a cada iteração apenas com os eventos de tela limpa, rotulados pelo próprio léxico, sem referências. Os atributos são o aplicativo do evento, a emissão por grupo de 2 vizinhos de trilha e 3 vizinhos de tempo de cada lado, as esperas e a decisão do feixe. A primeira versão incluía a máscara de grupos possíveis do próprio evento; isso vazava o rótulo das telas limpas e foi corrigido antes de qualquer resultado ser adotado. Métodos independentes convergiram para 91,5–91,85%, o que indica um platô para a informação disponível. Ganhos maiores exigiriam ancorar as cadeias sem tela limpa, isto é, informação adicional.

## Executar

Mantenha juntos analisar_amostra.py, motor_descoberta.py, motor_sequencial.py, motor_probabilistico.py, motor_adaptativo.py (v7, mantido para comparação) e motor_trilhas.py (v8). Altere CAMINHO_AMOSTRA e execute `py analisar_amostra.py`. A auditoria fica em `work/auditar_v8.py` → `work/auditoria_v8.json`. Os scripts de pesquisa e dos oráculos estão em `work/pesquisa_v8/`, e o registro dos ensaios em `work/registro_pesquisa_v8.json`.
