# Estudo de descoberta de processos a partir de logs sem identificadores

## Problema e objetivo

Recebemos sequências de observações de tela com usuário, aplicativo, início, fim e contadores de interação. Queremos descobrir padrões recorrentes, associar eventos às suas execuções e apresentar as etapas, a repetição no calendário e a intensidade de interação manual.

A versão atual aprende separadamente em cada amostra. Os nomes de processo e os identificadores de referência participam apenas da avaliação. Os cinco atributos admitidos na inferência são usuário, aplicativo, tela, início e fim. Os contadores alimentam a apresentação da manualidade.

Há três unidades diferentes a observar. Uma tela é uma atividade registrada. Uma sequência local é uma execução candidata de tarefa. Um episódio de vários dias pode reunir tarefas relacionadas, mas sua equivalência a um processo de negócio precisa de confirmação.

## Dificuldades encontradas

- A mesma tela pode participar de tarefas diferentes. Por isso, a identidade da tela não determina a classificação de todas as suas ocorrências.
- Execuções podem se intercalar. A próxima linha do CSV pode pertencer a outra execução.
- Interrupções e retornos aparecem entre atividades relevantes.
- Atividades e nomes de tela mudam entre amostras. Parte dos nomes da segunda amostra é opaca ou rara.
- As escalas variam de um evento a milhares de eventos ao longo de vários dias.
- A referência pode misturar categorias em um mesmo ID. Na segunda base, 10.898 casos contêm mais de um tipo entre suas linhas.
- Os CSVs não trazem documentos, contas, pedidos ou outros objetos que distingam execuções parecidas.
- Somar durações sobrepostas ou tratar contadores como percentual de trabalho manual produziria interpretações incorretas.

Se duas execuções têm observações indistinguíveis, várias partições podem ser igualmente compatíveis com os dados. Um algoritmo precisa reconhecer essa ambiguidade. Classificar todas as linhas com alta confiança esconderia a falta de informação.

## O que a academia oferece

Leno e colaboradores estudam a descoberta de rotinas recorrentes em logs de interface ainda sem segmentação e com ruído. Essa linha motiva aprender padrões antes de exigir casos prontos. A nossa implementação usa comunidades de associações temporais, enquanto o trabalho investiga outra estratégia de descoberta de rotinas. [Artigo de 2020](https://arxiv.org/abs/2008.05782)

Rebmann e van der Aa distinguem a identificação de tarefas, sua categorização e sua relação com processos. O trabalho combina fluxo, semântica e identificação de objetos. Aproveitamos a distinção das unidades e a comparação contextual. A extração de objetos depende de atributos que estes CSVs não oferecem. [Artigo de 2024](https://doi.org/10.1016/j.is.2024.102404)

Bayomie, Di Ciccio e Mendling formulam a correlação de eventos como otimização com restrições. O método recebe um modelo de processo e restrições de dados. Aproveitamos o princípio de atribuir eventos sob restrições, com um modelo de transições aprendido da própria amostra. [Artigo de 2022](https://arxiv.org/abs/2206.10009)

## O que o mercado efetivamente faz

A documentação da UiPath para Unassisted Task Mining, na versão 2023.4, descreve a descoberta de sequências frequentes e consistentes. Também registra resultados que capturam apenas parte da tarefa ou dividem uma tarefa em vários candidatos, exigindo análise dos resultados. [Guia de análise](https://docs.uipath.com/task-mining/automation-suite/2023.4/user-guide/unassisted-task-mining-analysis-guide)

A documentação atual do Task Mining da UiPath apresenta outro escopo, centrado em coletar e combinar variações de uma tarefa já conhecida. Essa distinção impede assumir que todo produto chamado task mining resolve descoberta aberta de processos. [Documentação atual](https://docs.uipath.com/task-mining/automation-cloud/latest/user-guide/introduction-as)

A Microsoft descreve task mining como captura e análise de ações de desktop. Seus tutoriais trabalham com gravações e processos preparados para a análise. Isso reforça a necessidade de avaliar separadamente a captura, a reconstrução das execuções e a interpretação do fluxo. [Microsoft Learn](https://learn.microsoft.com/en-us/power-automate/task-mining-overview)

## Algoritmo próprio implementado

### 1. Barreira de entrada e representação

O motor copia somente os cinco atributos permitidos para suas observações. Campos de referência, execucao_id e quaisquer colunas adicionais ficam fora dessa cópia.

Cada atividade é representada por aplicativo e tela. Um sufixo é agregado à tela-base somente quando a base também existe no arquivo e ocorre pelo menos três vezes mais. Não há listas de nomes de tarefas ou telas contábeis.

Essa normalização é uma hipótese linguística simples. Uma nova convenção de nomes pode exigir revisão, mesmo que o algoritmo aceite o arquivo.

### 2. Associações acima do esperado

Para cada pessoa, contamos pares próximos em janelas de até cinco eventos e vinte minutos. A contribuição de um par é inversamente proporcional à distância entre as observações.

Chamamos essa contagem ponderada de C(a,b). O grau ponderado da atividade a é d(a). A referência de associação por frequência é

    E(a,b) = d(a) × d(b) / soma dos graus

O grafo mantém pares repetidos com razão C/E suficientemente alta e atividades com suporte mínimo. A contribuição ao agrupamento cresce com a raiz do suporte e com o quadrado do logaritmo da razão C/E.

O algoritmo Louvain encontra comunidades nesse grafo. A quantidade de comunidades emerge dos dados. [Documentação do método](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html)

### 3. Contexto por ocorrência

Para evitar que telas muito comuns dominem os votos, calculamos um excesso regularizado

    R(a,b) = máximo de 0 e C(a,b) − E(a,b) − 2 × raiz de E(a,b)

Esse desconto é uma regularização aproximada. Ele não é um teste formal de significância.

As atividades têm vetores de afinidade com as comunidades. Uma tela pode ter afinidade com vários grupos. Para classificar uma ocorrência, usamos evidências dos dois lados da sequência e reforçamos a concordância entre eles.

Um núcleo recorrente pode fornecer a atribuição quando sua afinidade com o próprio grupo é de pelo menos 0,8. Nos demais casos, exigimos apoio contextual de pelo menos 0,6. Os valores são índices relativos do modelo, sem calibração probabilística externa. Eventos sem apoio suficiente permanecem identificados como contexto insuficiente.

### 4. Pausas, sessões e fronteiras

Ajustamos misturas de uma a quatro distribuições normais a log(1 + espera), usando EM. Escolhemos o número de componentes pelo BIC.

O componente de maior espera propõe uma hipótese de fronteira. Os componentes mais curtos propõem continuidade. Quando não há separação suficiente ou há poucas observações, usamos uma regra robusta baseada na mediana e no desvio absoluto mediano.

As pausas globais da pessoa também ajudam a separar sessões da escala local. Uma interrupção forte impede ligar automaticamente tarefas de sessões distintas nessa escala.

A seleção por BIC ajusta a complexidade da distribuição de pausas. Ela não prova que as fronteiras correspondam a casos de negócio.

### 5. Correlação com competição entre alternativas

Criamos candidatos a vínculo entre eventos da mesma pessoa e rotina. A pontuação de cada vínculo combina

    log da razão de densidades de continuidade e fronteira
    + evidência da transição entre as atividades
    − penalização pela quantidade de continuações concorrentes

Resolvemos uma cobertura de caminhos em um grafo acíclico. Cada evento admite no máximo um predecessor e um sucessor. A solução usa atribuição bipartida esparsa de custo mínimo e permite alternância entre execuções simultâneas.

O algoritmo considera até 32 próximos eventos da mesma rotina na busca de candidatos. Essa é uma aproximação computacional. Casos com muitas execuções concorrentes podem exigir ampliar a busca.

### 6. Episódios em várias datas

A concentração de uma rotina em várias datas consecutivas, comparada à sua distribuição usual, propõe episódios longos.

O CSV mantém as duas escalas. caso_local identifica a execução local, episodio_longo identifica o agrupamento temporal mais amplo e caso_inferido incorpora os episódios longos quando presentes.

O HTML avalia as duas escalas contra a mesma referência. Essa comparação revela quando o score depende principalmente dos casos grandes.

### 7. Diagnósticos sem rótulos

O relatório apresenta cobertura, modularidade do grafo e estabilidade ARI sob uma perturbação de 10% dos pesos. Esses números ajudam a inspecionar estrutura e sensibilidade. Um grupo incorreto também pode ser estável.

A evidência de acerto vem da comparação com referências disponíveis, de testes controlados e da revisão de exemplos concretos.

## Avaliação e critérios de sucesso

Mantivemos a composição do score anterior para permitir acompanhamento do estudo.

    Score = 0,10 × F1 das famílias + 0,40 × F1 dos pares + 0,50 × F1 dos casos inteiros

As famílias descobertas são alinhadas às referências um a um pelo maior F1. Grupos excedentes recebem zero. Eventos sem contexto contam como erros de família.

O F1 de pares pesa fortemente casos grandes. Por isso, apresentamos também F1 B³, acerto de famílias entre eventos cobertos, cobertura e casos exatamente recuperados. Esses indicadores devem ser lidos juntos.

As duas bases fornecidas foram usadas durante o desenvolvimento. Seus resultados são descritivos, sem representar um teste externo independente. O novo cenário sintético é um teste funcional controlado, sem representar uma amostra operacional real.

## Resultados

| Amostra | Versão 2 | Versão 3 | Cobertura v3 | F1 famílias v3 | F1 casos inteiros v3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 60,000 eventos | 70,88 | 72,96 | 100,00% | 100,00% | 65,87% |
| 100,000 eventos | 38,22 | 37,66 | 33,84% | 30,93% | 25,77% |


Na primeira base, o F1 de casos inteiros passou de 54,56% para 65,87%. A precisão dos pares caiu para 61,37%, indicando mais fusões incorretas, enquanto a sensibilidade ficou em 96,62%. A mudança melhora uma parte da reconstrução e piora outra.

Na segunda base, a versão 3 obteve score de 37,66 e deixou 66.157 eventos sem contexto suficiente. Entre os eventos cobertos, o acerto de família após alinhamento foi de 73,66%. A precisão dos pares ficou em 55,99%. O desempenho ainda é insuficiente para considerar a reconstrução correta de forma autônoma.

A diferença entre escalas nessa base é grande. O F1 de pares na escala local é de aproximadamente 0,39%, enquanto a escala que incorpora episódios longos chega a 54,22%. Isso mostra quanto os seis casos grandes influenciam essa métrica. O F1 B³ da escala com episódios é de 62,32%.

Em um cenário sintético novo com 3.200 eventos, três tarefas de nomes opacos, duas execuções intercaladas por usuário e uma tela compartilhada, o modelo encontrou os três grupos. O F1 de famílias foi 93,60%, o F1 de casos inteiros foi 29,73% e o score foi 52,47. Reconhecer a família continua mais fácil que reconstruir cada execução.

No controle negativo, embaralhamos telas e aplicativos entre os mesmos horários. O algoritmo não encontrou rotinas e deixou os eventos sem contexto. Esse teste verifica se o método distingue estrutura repetida de uma sequência sem a mesma organização.

As verificações de remoção de referências confirmam a independência da inferência. A comparação de todas as linhas também verifica sua preservação no CSV classificado.


## O que ainda precisa melhorar

A principal limitação continua sendo a cobertura da amostra mais ambígua. O modelo ainda deixa muitas ocorrências sem associação e erra fronteiras de execuções. A separação de episódios longos melhora a leitura de uma escala do trabalho, mas não resolve a tarefa local.

Os nomes das comunidades são exemplos de telas. Nomear um grupo como conciliação, revisão ou atendimento exige evidência de negócio adicional ou validação humana.

Uma avaliação operacional deve usar uma amostra nova, com um pequeno conjunto de execuções revisadas de ponta a ponta. O motor pode continuar aprendendo sem essas referências. A revisão é necessária para medir se os grupos e as fronteiras têm o significado desejado.


## Continuação experimental — versão 5.0

A auditoria dos horários encontrou concorrência máxima de três intervalos em cada um dos 122 dias da amostra de 100 mil eventos. Os casos curtos de referência não continham sobreposição temporal interna; as sobreposições dentro dos casos de referência estavam concentradas nos seis episódios extensos. Essa constatação motivou uma restrição física de trilhas, cuja concorrência é recalculada para cada entrada. A referência motivou o experimento e avalia o resultado, mas não fornece atributos ao modelo.

O novo correlacionador usa três componentes: afinidade lexical das telas com os protótipos, transições entre fases e uma densidade de espera. Para uma atribuição de fase s e predecessor a, minimiza aproximadamente a energia

    E = soma[-log afinidade(tela,s)
             - 0,5 log(0,8 T(fase_anterior,s) + 0,2 prior(s))
             - log densidade(inicio - fim_anterior)]

O primeiro evento de uma trilha paga um custo de abertura log(duração observada do dia). A espera utiliza 0,9 Laplace(40,40) + 0,1 Laplace(40,180), em segundos. Esperas negativas são proibidas na mesma trilha. A busca mantém os 128 estados de menor energia após cada evento. Não é inferência exata nem produz probabilidades calibradas de acerto.

A matriz T combina 90% de um sucessor cíclico e 10% das transições empíricas suavizadas. Os sucessores são estimados por atribuição húngara e união de ciclos, usando apenas ocorrências com maior afinidade. A suposição de ciclos é restritiva: tarefas com ramificações e retornos não são totalmente representadas.

O detector de atividades transversais escolhe frequências elevadas fora do núcleo do grafo por mistura gaussiana e BIC, sem lista de aplicativos. Uma atividade transversal preserva a fase de trabalho, mas abre um novo caso candidato. Períodos concentrados podem estabelecer um contexto de episódio, mantido até a próxima atividade transversal. A decisão de usar esse correlacionador depende desse detector; arquivos sem esse sinal mantêm a cobertura de caminhos anterior.

### Experimentos e crítica

No recorte de janeiro, a primeira restrição sem sobreposição atingiu 60,07. Aprender uma densidade gaussiana de espera produziu 60,36; aumentar o feixe para 512 produziu 60,40. Reaprender emissões a partir das próprias atribuições não trouxe ganho consistente e foi descartado. Reduzir o peso das transições de 1,5 para 0,5 produziu 61,75. Manter o contexto de episódio até uma atividade transversal produziu 63,33 nesse recorte. A primeira avaliação completa da restrição simples produziu 59,17.

O correlacionador sequencial isolado piorou a base limpa de 60 mil eventos para 54,44 e o cenário sintético para 23,03. Portanto, não foi adotado universalmente. O critério automático de presença de atividades transversais preserva o método anterior nos dois cenários. Essa seleção ainda precisa ser testada em novas bases com e sem interrupções; os dois resultados não garantem que o detector sempre escolherá o melhor método.

Os ensaios usaram referências para comparar erros e escolher parâmetros. Isso é ajuste no conjunto estudado, mesmo sem uso de rótulos como atributos de inferência. Janeiro não constitui uma validação externa, e os demais meses também foram inspecionados anteriormente. Não existe garantia de atingir 80, nem prova de impossibilidade de atingi-lo. A recuperação exata das fronteiras e dos eventos pertencentes a episódios extensos continua sendo o principal problema.

O avaliador permanece intacto: 10% F1 de famílias, 40% F1 de pares e 50% F1 de casos completos, com todas as linhas. Nenhuma pontuação foi substituída por cobertura ou confiança interna. O relatório da execução completa é a fonte do resultado final; pontuações de janeiro não devem ser apresentadas como pontuação das 100 mil linhas.


### Resultado completo selecionado

Na amostra de 100 mil linhas, a versão 5.0 obteve **63,6973642570/100**, com 37.974 casos candidatos: F1 das famílias 79,8172%, F1 dos pares 73,1042% e F1 dos casos completos 52,9479%. Foram recuperados exatamente 20.031 dos 37.689 casos de referência. A precisão dos pares foi 62,1606% e o recall 88,7244%: ainda há excesso de vínculos, especialmente ao expandir episódios extensos. O F1 B³ foi 81,7147%, mas não substitui o score combinado nem representa o cumprimento da meta de 80.

O ganho sobre a versão 4.0 foi de aproximadamente 16,60 pontos. Todas as linhas foram classificadas; isso significa cobertura, não 100% de acerto. A meta de 80 pontos continua não atingida. A avaliação da escala local permanece separada e é mais baixa, porque não reúne os episódios extensos que dominam a contagem de pares da referência.

A última correção mudou a continuidade dos períodos concentrados: datas selecionadas podem ter no máximo uma data observada intermediária sem concentração. A comparação usa posições no calendário observado de cada pessoa, em vez do intervalo fixo de quatro dias corridos. Com isso, o episódio de fevereiro passou a incluir suas duas datas iniciais, separadas das demais por um intervalo sem registros. O score completo passou de 62,53 para 63,70. Não foi fornecida uma lista de feriados. Arquivos com lacunas de captura ainda podem confundir ausência de trabalho e ausência de coleta.

A inferência final recebeu objetos que expõem exclusivamente os cinco atributos permitidos e bloqueiam acesso a qualquer outro campo. Referências foram reintroduzidas somente depois da inferência para avaliar e gerar o relatório. Todas as 100 mil linhas e os valores originais foram reconciliados. O corpo sintático do avaliador foi comparado com seu hash anterior e permaneceu intacto. A auditoria está em work/auditoria_v5.json; a iteração anterior também foi repetida integralmente com e sem referências, com resultado idêntico.

A ordem de etapas e as transições do relatório representam adjacência cronológica na hipótese de caso. Episódios extensos podem reunir trilhas simultâneas; a tabela não demonstra causalidade entre todas as etapas.


## Continuação de 3 de novembro de 2026 — versão 6.0

### Hipóteses e pesquisa consultada

A versão anterior fixava cedo duas fases candidatas por evento. Quando um nome opaco é ambíguo, a fase correta pode não estar entre essas duas alternativas, mesmo que uma etapa posterior pudesse identificá-la. A nova estratégia retém uma distribuição sobre fases enquanto explora os fluxos físicos.

A inspiração é a marginalização de uma parte do estado em modelos dinâmicos. Doucet, de Freitas, Murphy e Russell mostram essa ideia em filtros de partículas Rao-Blackwellizados. Nossa implementação usa um feixe determinístico, sem amostragem; não é uma implementação literal do filtro daquele artigo. [Artigo original, UAI 2000](https://people.eecs.berkeley.edu/~pabbeel/cs287-fa12/optreadings/DoucetdeFreitasMurphyRussell_RaoBlackwellizedParticleFilters.pdf).

O problema de correlação continua distinto da classificação de atividades. O método de Bayomie, Di Ciccio e Mendling recebe um modelo de processo e restrições; aqui as transições são estimadas na própria amostra. [EC-SA-Data](https://arxiv.org/abs/2206.10009). Rebmann e van der Aa incluem objetos de negócio na correlação de tarefas; a ausência desses objetos neste CSV continua sendo uma diferença material. [Artigo de 2024](https://doi.org/10.1016/j.is.2024.102404).

### Modelo matemático implementado

Seja e_t(s) a afinidade lexical da observação t com a fase s, T a matriz de sucessores aprendida e pi a frequência das fases. O filtro utiliza

    P0(s,j) = 0,8 T(s,j) + 0,2 pi(j)
    A(s,j)  = P0(s,j)^0,5 / soma_k P0(s,k)^0,5
    u(j)    = soma_s b(s) A(s,j)
    Z_t     = soma_j u(j) e_t(j)
    b_nova(j) = u(j) e_t(j) / Z_t

A distribuição b acompanha cada trilha física candidata. O custo de associar o próximo evento é -log(Z_t) - log(w(espera)). O feixe preserva os 128 candidatos de menor custo. Atividades transversais e âncoras de episódios preservam a distribuição de fase. Afinidades lexicais de pelo menos 0,98 são aproximadas por uma âncora pontual, portanto essa etapa também contém uma aproximação.

A quantidade de trilhas utilizada é a concorrência máxima dos intervalos em cada pessoa e dia. Matematicamente, isso é o número mínimo necessário para acomodar os intervalos sem sobreposição, não uma prova de que corresponde ao número real de fluxos. Amostras esparsas podem ter mais fluxos do que essa estatística indica.

Depois da escolha das trilhas, Viterbi maximiza, para cada trilha, a soma das afinidades logarítmicas com 0,5 vezes o log das transições P0 e do prior inicial. A decodificação é exata condicional às trilhas e às hipóteses do modelo; a descoberta global das trilhas permanece aproximada. Forward-backward calcula o apoio posterior da fase escolhida. Esse apoio é condicionado ao modelo e não foi calibrado como probabilidade de acerto no mundo real.

O peso temporal w é aprendido a partir das transições entre fases de alta afinidade lexical. Comparamos seu histograma de esperas com a média de oito permutações de fases dentro de pessoa e data. O excesso positivo é suavizado em bins de cinco segundos, com horizonte de trinta minutos. Um piso de 0,005 e uma cauda evitam custo infinito fora do suporte. Trata-se de um potencial temporal de associação, não de uma estimativa comprovada dos tempos reais entre eventos do mesmo caso. Sem excesso, usamos a espera padrão da versão anterior.

O corte de suporte das atividades no grafo passou de teto(raiz(N)/3) para teto(raiz(N)/6), mantendo o filtro estatístico das associações. A mudança admite atividades mais raras; não introduz nomes conhecidos de etapas. Em janeiro, isso acrescentou duas fases ao modelo e melhorou a recuperação dos casos. O filtro usa uma aproximação de contagens e dependências; seu parâmetro de 1% não garante uma taxa real de falsos agrupamentos de 1%.

### Experimentos rejeitados e controles

A separação explícita do modo de episódio e da fase não superou a regra anterior. Encerrar episódios ao encontrar duas etapas coerentes melhorou a precisão dos pares, mas perdeu recall e score. Modelos de tempo com permutação condicionada à família, maior regularização e transições mais flexíveis também não superaram a combinação selecionada.

Reaprender emissões por realimentação de posteriors não melhorou os resultados. Um classificador de contexto, treinado com famílias inferidas e a própria tela mascarada, teve sinal preditivo em controle interno, mas não melhorou a decodificação. Os contadores de interação não mostraram ganho consistente sobre a frequência das classes no controle por datas. Nenhum desses classificadores foi incluído no motor final.

Uma otimização local de trocas de sufixos reduziu o custo interno do modelo. O ganho no score de referência foi pequeno, demonstrando que minimizar o objetivo interno não equivale a maximizar a recuperação verdadeira dos casos. Ela também não foi incluída no motor final.

Os experimentos intermediários têm escopo registrado em work/registro_pesquisa_v6.json. Valores de janeiro não são apresentados como resultados da base completa. Os CSVs foram consultados durante a seleção de alternativas e parâmetros; estes resultados não constituem validação externa. Não usamos identificadores, campos de referência ou um catálogo de processos como atributos de inferência.

O método é offline: utiliza observações futuras para revisar as fases e aprende o modelo com o arquivo inteiro. O critério de seleção entre correlacionadores continua sendo a detecção de atividades transversais, sem condição por nome de arquivo, número de linhas ou identificação de processo.


### Resultado completo da versão 6

A execução final obteve **69,2512755090/100**, com 36.817 casos inferidos e 23.083 casos exatamente recuperados, entre 37.689 de referência. F1 das famílias: 84,443354%; pares: 74,563857%; casos inteiros: 61,962795%. Precisão dos pares: 65,411198%; recall: 86,694592%. O F1 B³ de 85,443757% permanece uma métrica auxiliar, sem substituir o score.

A evolução completa foi: versão 5, 63,70; espera empírica, 65,32; revisão por Viterbi, 67,51; marginalização das fases durante a escolha dos fluxos, 68,30; admissão das duas fases mais raras, 69,25. As três últimas comparações foram conferidas na base completa; janeiro foi usado para comparar alternativas, não como validação externa.

A auditoria final bloqueou acesso a atributos além dos cinco permitidos, confirmou preservação dos 100 mil eventos e verificou o hash sintático do avaliador. As atribuições, famílias e etapas de janeiro coincidiram com o experimento correspondente. O apoio posterior permaneceu entre zero e um. Os resultados de 60 mil eventos e do controle sintético foram preservados.

A meta de 80 permanece aberta. Há 5.781 casos de referência fragmentados e 8.825 contidos em um único agrupamento que também incorpora eventos de outra execução. Esses dois grupos são exclusivos, juntamente com os 23.083 casos exatos. A diferença entre bom ajuste interno e recuperação verdadeira, além da falta de objetos de negócio para distinguir situações concorrentes, continua relevante. Não demonstramos um limite superior de acurácia para os dados nem uma garantia de que mais busca atingirá 80.


## Continuação experimental — versão 7.0

### Entradas de tarefa sem catálogo

O prior de frequência de fases não é a mesma coisa que a distribuição das etapas que iniciam uma tarefa. A versão 7 estima essa distribuição em trilhas preliminares. Usa mudanças de grupo entre observações de afinidade de pelo menos 0,8 e a primeira atividade normal de uma trilha. Eventos transversais são ignorados nessa contagem. Os dias de episódios concentrados ficam fora do ajuste das entradas para reduzir contaminação por atividades sobrepostas.

Para um grupo g e fase j, seja C_j a soma do apoio lexical dos inícios observados. Mantemos a massa original do grupo pi_g e estimamos

    theta_j = (C_j + 5 pi_j/pi_g) / (soma_{k em g} C_k + 5)
    pi_entrada(j) = pi_g theta_j

Grupos com menos de cinco observações de entrada mantêm o prior anterior. Não são fornecidos nomes de processos, telas de início ou ordens de etapas. Os índices de fase são aprendidos a partir das atividades do próprio arquivo.

### Três passagens

A primeira usa as representações da versão anterior para encontrar trilhas preliminares. A segunda distingue prefixos até oito caracteres, estima entradas e correlaciona novamente. A terceira refaz a estimativa de entradas com essas trilhas e ajusta os tempos antes da correlação final.

A distribuição de transição do filtro final é proporcional a

    (0,8 T(s,j) + 0,2 pi_entrada(j))^0,75

com normalização por estado de origem. O feixe mantém 128 hipóteses físicas. A distribuição de fase só é aproximada por uma âncora pontual quando o próprio posterior chega a 0,98. Uma boa correspondência textual que conflita com o fluxo pode, portanto, permanecer ambígua. Viterbi e forward-backward revisam as fases nas trilhas finais com peso 0,5. As temperaturas diferem entre as etapas de inferência; a implementação é um modelo híbrido aproximado, sem garantia de ótimo global.

### Espera e fronteiras

O modelo refinado de espera usa somente arestas adjacentes de trilhas preliminares cujas duas atividades tenham afinidade de pelo menos 0,8, pertençam ao mesmo grupo não transversal e apresentem uma transição de pelo menos 0,5. Atividades de grupos episódicos são excluídas dessa coleta quando estão nos períodos concentrados.

O histograma em bins de cinco segundos é segmentado por programação dinâmica. A função de ajuste é, a menos de constantes comuns,

    soma_blocos [n_b log(n_b / largura_b)] - K log(N)

onde K é o número de blocos e N a quantidade de arestas selecionadas. O potencial final combina 90% do histograma segmentado e 10% da espera inicial. Com menos de vinte amostras, mantém a espera inicial. Na base estudada, o ajuste encontrou automaticamente faixas curtas e longas de espera; esses limites não foram inseridos no código como conhecimento do fechamento contábil.

### Preservação da tarefa local

Uma tarefa candidata pode ser reconhecida dentro da vizinhança de um episódio maior. Se sua primeira atividade de trabalho corresponde à entrada mais provável do grupo, tem apoio posterior de pelo menos 0,98 e o grupo possui evidência suficiente de entrada, as atividades dessa tarefa podem ser mantidas no caso local. A proteção é aplicada apenas a grupos cuja entrada dominante reúne pelo menos metade do apoio estimado.

O mecanismo preserva os eventos centrais do episódio e restitui os eventos locais selecionados à hipótese de tarefa. Não elimina linhas. O CSV usa criterio=tarefa_local_preservada para as 2.190 atividades restituídas na execução final. Tanto essa proteção quanto a própria unidade de episódio são hipóteses; não confirmam o significado de negócio dos agrupamentos.

### Resultados e crítica

A evolução na base completa foi 69,25 na versão 6; 73,65 com entradas aprendidas e nova correlação; 74,53 após refinamento das entradas, espera e âncoras; 76,10 após preservar tarefas locais. O resultado final sem arredondamento foi 76,1017338300. F1 das famílias: 87,101070%; pares: 79,781384%; casos inteiros: 70,958147%. Foram recuperados exatamente 26.957 dos 37.689 casos, com 38.291 casos candidatos e todos os 100 mil eventos.

A precisão dos pares foi 75,788659% e o recall 84,218196%. Persistem 4.802 casos de referência fragmentados e 5.930 unidos a eventos de outra execução. Os seis casos extensos continuam sem igualdade exata com suas referências.

Modelos de episódio explícito, emissões categóricas reestimadas, dicionários obtidos com a própria tela mascarada, filtros de presença diária e vários consensos não superaram o conjunto escolhido. Um consenso apresentou F1 interno esperado próximo de 94%, enquanto seu F1 de casos de referência ficou em aproximadamente 69%. Esse resultado reforçou a decisão de manter o avaliador externo original. Aumentar o feixe para 512 produziu ganho inferior a 0,01 ponto em janeiro, com tempo aproximadamente três vezes maior; não foi adotado.

O registro desta continuação contém 149 saídas experimentais, separando janeiro da amostra completa e saídas antes/depois de refinamentos. As referências foram consultadas para diagnosticar erros e selecionar alternativas, mas nenhum desses atributos entrou na inferência. Isso é desenvolvimento sobre o conjunto estudado, não validação externa.

A execução final bloqueou acesso a qualquer atributo além dos cinco permitidos. Casos, famílias e etapas coincidiram integralmente com o experimento completo. O hash sintático do avaliador permaneceu igual, todas as linhas e seus valores originais foram preservados e o apoio das fases ficou entre zero e um. A base de 60 mil eventos e os controles sintéticos mantiveram seus resultados anteriores.

A meta de 80 continua não atingida. O F1 B³ de 88,628128% é auxiliar e não equivale ao cumprimento dessa meta. O estudo não prova uma impossibilidade de chegar a 80 nem uma garantia de que mais ajustes irão alcançá-lo. A ausência de objetos que distingam execuções, os nomes ambíguos e as hipóteses de ciclo, início de tarefa e escala de episódio continuam limitando a interpretação. As trilhas locais são tratadas por pessoa e data, o que também restringe casos que atravessam a meia-noite.
