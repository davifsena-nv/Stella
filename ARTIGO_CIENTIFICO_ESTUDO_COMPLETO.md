# Descoberta e correlação de execuções em logs de interface sem identificadores de processo
## Artigo técnico-científico e memorial experimental integral
Versão documental: 1.0 — 3 de novembro de 2026. Implementação examinada: 7.0.

## Resumo
Este estudo investiga como reconstruir execuções de trabalho a partir de logs de interface sem fornecer ao algoritmo identificadores de caso, catálogo de telas ou descrição prévia do processo. O problema foi desenvolvido iterativamente a partir de uma solicitação de análise de fechamento contábil, seguida por exigências de reutilização em novas amostras e de uma meta de 80 pontos. Foram examinadas duas bases de 60 mil e 100 mil eventos. O método desenvolvido combina comunidades de atividades, contexto lexical e temporal, correlação com restrições de concorrência, distribuições latentes de fases, busca em feixe, decodificação condicional e aprendizado das etapas de entrada. Na base de 100 mil eventos, a versão final obteve 76,1017/100, recuperando exatamente 26.957 de 37.689 casos. A meta não foi atingida. As referências não alimentaram a inferência, mas participaram da seleção experimental; os resultados não constituem validação externa. Este documento reúne a narrativa, a formulação, as avaliações, os registros disponíveis e o código examinado.

**Atualização de 3 de novembro de 2026 (versão 8.0).** Uma continuação posterior, descrita na seção "Continuação experimental — versão 8.0", elevou o score oficial na base de 100 mil eventos para 78,1659/100, com 91,78% dos eventos no processo correto. A meta revisada de 90 não foi atingida. Experimentos de teto com oráculos indicam que 90 exige informação que não está nos cinco campos admitidos.

Palavras-chave: task mining; correlação de eventos; descoberta de processos; logs de interface; segmentação; modelos latentes; avaliação de agrupamentos.

## 1. Escopo documental e integridade da reconstrução
Este texto é um relato retrospectivo de pesquisa aplicada, não um artigo com hipóteses pré-registradas. Reúne a sequência de solicitações visível na conversa e evidências locais preservadas. Não existe neste material uma transcrição integral de todas as respostas antigas e saídas de ferramentas. Portanto, não se atribuem datas, resultados ou decisões específicos a etapas sem registro. Os anexos distinguem observações quantitativas preservadas de explicações metodológicas. Nomes de arquivos de ensaios não são tratados como descrições científicas suficientes por si mesmos.

O pedido de registrar cada pequeno passo é atendido por camadas: reconstrução das solicitações; desenvolvimento conceitual; memorial metodológico preservado; registros completos dos ensaios; auditorias; especificação executável do algoritmo. Não se afirma que os registros remanescentes capturem todas as tentativas informais realizadas na conversa. Arquivos experimentais podem permanecer no diretório sem integrar o algoritmo entregue.

## 2. Origem: primeiro problema e evolução dos requisitos
O primeiro pedido foi construir um algoritmo capaz de separar os processos executados por uma pessoa, estudar a literatura e o mercado, definir um score, produzir HTML com etapas, repetição, calendário e manualidade, e revisar criticamente os resultados em ciclos de melhoria. A primeira amostra mencionada foi logs_fechamento_contabil_6m.csv.

A sequência posterior, conforme as mensagens disponíveis, foi:

1. Explicar a abordagem e como ela foi obtida.
2. Explicitar em que o algoritmo se baseia e qual modelo matemático utiliza.
3. Estruturar um programa Python reutilizável, configurável pelo caminho da amostra e com HTML automático.
4. Corrigir a leitura de amostra_validacao_fechamento_100k.csv, inicialmente sem alterar a lógica de inferência.
5. Conferir se o arquivo alterado era realmente o da pasta de trabalho indicada.
6. Investigar o relatório com 100 mil execuções inferidas, 100 mil telas não reconhecidas e métricas indisponíveis; discutir se seria necessário um catálogo de telas.
7. Reformular o algoritmo para aceitar amostras desconhecidas sem depender do processo já estudado.
8. Retomar a pesquisa sob a perspectiva acadêmica e de mercado.
9. Informar a pontuação na amostra de 100 mil linhas.
10. Buscar 80 pontos sem passar contexto, com sucessivos pedidos de continuação.
11. Documentar agora todo o estudo em artigo científico.

A captura de tela inicial não demonstrava score zero: mostrava métricas indisponíveis, uma categoria desconhecida e uma execução por evento. A distinção importa. Ingestão bem-sucedida, reconhecimento de atividades e disponibilidade de referência são problemas diferentes. O histórico disponível não permite reconstruir com segurança a mensagem exata de cada erro anterior de leitura. A solução atual de leitura está documentada e reproduzida no código, sem atribuir retrospectivamente uma causa específica não comprovada.

## 3. Questões de pesquisa
Q1: Que estrutura pode ser descoberta sem catálogo e sem IDs de caso? Q2: Como separar reconhecimento de família, etapa e execução? Q3: Como tratar eventos intercalados e episódios de escalas diferentes? Q4: Como medir sucesso sem confundir cobertura, confiança e acerto? Q5: Quais melhorias sobrevivem a uma avaliação fixa de todas as linhas?

A hipótese operacional é que nomes, recorrência, transições e restrições temporais contêm sinal suficiente para superar segmentações triviais. Isso não implica que determinem uma partição única ou permitam nomear corretamente o significado de negócio. Ausência de contexto significa ausência de conhecimento prévio específico de processos na inferência; não significa ausência de hipóteses matemáticas, nomes observados ou ajustes feitos pelo pesquisador.

## 4. Formalização da tarefa e das métricas
Seja E={e_1,...,e_n}, com e_i=(u_i,a_i,x_i,t_i_inicio,t_i_fim). Buscam-se uma partição de E em execuções, uma família e uma fase por ocorrência. Cada evento deve pertencer exatamente a uma execução final. Telas repetidas podem ter funções distintas por contexto. Casos locais e episódios são unidades diferentes e devem permanecer rastreáveis.

Para uma tabela de contingência n_ij entre casos verdadeiros e previstos, TP_pares=Σ_ij combinação(n_ij,2). O número de pares previstos é Σ_j combinação(n_.j,2), e o verdadeiro é Σ_i combinação(n_i.,2). Precisão e recall dividem TP por esses respectivos totais; F1 é sua média harmônica. Casos grandes contribuem quadraticamente e podem dominar essa métrica.

Para casos exatos, uma execução só recebe crédito se seu conjunto completo de eventos coincidir com um caso de referência. Se H é a quantidade de casos idênticos, precisão=H/K_prev e recall=H/K_ref. Assim, F1_exato=2H/(K_prev+K_ref). Não é a mesma medida que H/K_ref. Na versão 7, H=26.957, K_prev=38.291 e K_ref=37.689.

As famílias são alinhadas uma a uma por atribuição que maximiza F1, evitando punir permutações arbitrárias dos nomes dos grupos. Grupos excedentes e eventos desconhecidos recebem penalização conforme o avaliador preservado. O score fixo é S=0,10F_familia+0,40F_pares+0,50F_exato, na escala 0–100. Os pesos são uma escolha de projeto, não uma constante científica universal. O corpo executável integral do avaliador está no anexo de código.

## 5. Protocolo, prevenção de vazamento e limites
A inferência admite somente os cinco campos observacionais. Identificadores, referências e contadores de interação não alimentam o motor final. Contadores alimentam a apresentação da intensidade de interação. A auditoria utiliza objetos que bloqueiam acessos proibidos, reconcilia as linhas e compara o hash sintático do avaliador.

Essa barreira evita vazamento direto de rótulos, mas não elimina viés de seleção: referências foram usadas para comparar alternativas. Janeiro é um recorte de desenvolvimento, não conjunto de teste independente. Os números completos são apresentados separadamente. A quantidade de ensaios aumenta o risco de sobreajuste ao benchmark; os melhores resultados não devem ser interpretados como desempenho esperado em qualquer empresa.

## 6. Memorial metodológico preservado
A seção seguinte incorpora integralmente a documentação metodológica acumulada. Seus blocos iniciais descrevem versões históricas; quando uma limitação ou parâmetro mudou, prevalece a descrição da versão explicitamente identificada. Isso preserva a evolução sem reescrever o passado como se o método final tivesse existido desde o início.

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

## Continuação experimental — versão 8.0

### Diagnóstico

O parecer técnico sobre a versão 7 começou por uma decomposição da métrica. Recalculado apenas com os seis fechamentos mensais, o F1 de pares dá 79,77%, com precisão de 75,76% e recall de 84,24%. Os valores reportados para a base inteira são 79,78%, 75,79% e 84,22%. Esses seis casos somam 26,1 milhões dos pares de referência. Assim, 40% do score depende de 17,7% dos eventos, e cada caso exato adicional vale apenas 0,0013 ponto.

A inspeção das referências mostrou que a base tem uma única pessoa e três trilhas físicas sem sobreposição. Cada caso contém um único processo, e suas etapas seguem um ciclo fixo, com saltos de +1 ou retorno da última etapa para a primeira. Um caso iniciado sem interrupção começa sempre na etapa de entrada. Uma interrupção de navegação inicia um caso e absorve o trabalho imediatamente seguinte na mesma trilha, com retorno sempre em menos de 75 s. O fechamento mensal reúne 11.810 etapas próprias e 5.892 eventos de outros processos, que formam minicadeias. Esses fatos orientaram hipóteses estruturais. Nenhum deles entra na inferência como atributo, mas o desenho do modelo passou a depender desta base, que é sintética.

### Modelo implementado

O módulo motor_trilhas.py reaproveita os grupos e protótipos da v7. Protótipos cujo nome aparece em três ou mais aplicativos são declarados opacos. Nomes frequentes de um só aplicativo e não derivados são acrescentados como etapas. Os ciclos são obtidos por atribuição húngara sobre coocorrências de âncoras exatas próximas, e a entrada é o estado de maior razão freq(s)/freq(anterior). Os 12 ciclos aprendidos coincidiram com os templates de referência.

A emissão inicial de cada par aplicativo/tela segue regras de variação de nome (exato, sufixo, prefixo de dois caracteres, inicial seguida de dígitos, aplicativo) e é reestimada por EM com prior de Dirichlet λ=5. A decodificação é um feixe sobre trilhas sem sobreposição; o número de trilhas é a concorrência máxima do dia. Cada trilha guarda uma distribuição b sobre etapas. Para um evento com razão r = Q/π, o custo de continuar é c_cont − log(b·Suc·r); o de iniciar é c_nova − log(ent·r); o de retomar após interrupção é c_ret − log(não_ent·r); o de subtarefa de episódio é c_emb. A espera custa 0 até 90 s e 5,2 no componente de pausa. A continuação após interrupção só é admitida até o joelho da distribuição decodificada, que deu 80 s. Os custos de tarefa são frequências das decisões (EM rígido). Os três custos de episódio foram escolhidos em janeiro–março e conferidos em abril–junho.

### Resultados, rejeições e teto

O score oficial final foi 78,1419266923, com F1 de famílias de 89,07%, F1 de pares de 79,32% e F1 de casos de 75,01%; 29.099 casos foram recuperados exatamente. Foram rejeitados: a tabela de transição aprendida integralmente por EM, porque o episódio se autorreforçou e o score caiu para 70,3; a espera aprendida por EM rígido (73,66); o retorno pelo percentil 99 (75,85); a distribuição aprendida das etapas embutidas (77,52); e o feixe final de 512 (78,01). Duração por etapa, nome da navegação e espera antes de nova tarefa não trouxeram sinal.

Para separar a falta de informação da falta de modelo, foram feitos experimentos com oráculo. Com a emissão ótima por chave aplicativo/tela, o resultado foi 79,2. Conhecendo a etapa verdadeira de cada evento e inferindo o episódio, foi 83,4. Com etapas verdadeiras e episódio perfeito, foi 91,0. A emissão aprendida já está a 2,2 pontos do teto por chave (65,3% contra 67,5%). Mesmo com etapas verdadeiras, restam cerca de 15% de casos ambíguos: o retorno ao início versus uma nova tarefa do mesmo processo, continuações de interrupção que começam uma tarefa nova e tarefas concorrentes do mesmo processo. Isso não prova a impossibilidade de 90, mas indica que esse patamar exige informação ausente dos cinco campos, como identificadores de objetos de negócio ou uma amostra rotulada. Os registros estão em work/registro_pesquisa_v8.json e work/pesquisa_v8/.

Em seguida, o objetivo passou a ser o acerto de processo por evento, que estava em 91,49%. Um classificador de contexto foi autotreinado a cada iteração com as telas de nome inequívoco (99,5% corretas pelo léxico, sem referências) e realimentou a emissão das telas opacas. Com isso, o acerto chegou a 91,78% e o score a 78,1659. Média de decodificações, etapas dos vizinhos e votação de cinco execuções ficaram entre 91,6% e 91,85%, o que indica um platô. As telas opacas, cujo teto pela própria tela é de cerca de 45%, concentram os erros.

## 7. Relatos consolidados por versão
Os relatos abaixo são documentos de resultado preservados, apresentados em ordem de evolução.

### Documento: RESULTADOS_V5.md

# Resultado da continuação do estudo

A versão 5 foi implementada nesta pasta. Na amostra de 100.000 eventos, passou de 47,10 para **63,70/100**, mantendo a fórmula do avaliador. A meta de 80 ainda não foi atingida.

| Componente | Pontuação |
| --- | ---: |
| F1 das famílias | 79,82 |
| F1 dos pares | 73,10 |
| F1 dos casos inteiros | 52,95 |
| Score: 10% famílias + 40% pares + 50% casos | 63,70 |

Foram recuperados exatamente 20.031 de 37.689 casos. O principal erro restante é a associação de eventos aos limites e ao contexto correto da execução. A expansão de episódios aumenta o recall dos pares para 88,72%, mas a precisão fica em 62,16%.

O algoritmo usa apenas pessoa, aplicativo, tela e horários. Não recebe catálogo nem referência como atributo. Descobre grupos por associações temporais, aprende protótipos e transições, e usa busca em feixe com restrições de sobreposição quando detecta atividades transversais. Mantém o correlacionador anterior nas amostras sem esse sinal.

O método sequencial foi testado com substituição ou preservação da fase durante episódios, espera fixa ou aprendida, feixes 128/512, pesos de transição 0/0,25/0,5/0,75/1,5/3/6 e reaprendizado de emissões. A seleção foi feita durante o estudo desta base. Isso não comprova generalização externa, mesmo sem referências na inferência.

O script continua sendo analisar_amostra.py. Basta alterar CAMINHO_AMOSTRA e executá-lo. O novo motor_sequencial.py deve permanecer na mesma pasta. Instale as dependências em requirements.txt. O HTML final fica em amostra_validacao_fechamento_100k_resultados/estudo.html.

A auditoria da execução está em work/auditoria_v5.json e as limitações matemáticas e metodológicas estão em ESTUDO_METODOLOGICO.md.

A correção final usa o calendário observado de cada pessoa para unir dias de concentração, sem lista prévia de feriados. A inferência final recebeu somente os cinco atributos permitidos. Todas as linhas foram preservadas e o avaliador permaneceu intacto.

### Documento: RESULTADOS_V6.md

# Resultado da pesquisa — versão 6.0

A amostra de 100 mil linhas passou de **63,70 para 69,25/100**. O ganho foi de 5,55 pontos. A meta de 80 continua não atingida.

| Componente do score | Versão 5 | Versão 6 |
| --- | ---: | ---: |
| F1 das famílias | 79,82 | 84,44 |
| F1 dos pares | 73,10 | 74,56 |
| F1 dos casos inteiros | 52,95 | 61,96 |
| Score combinado | 63,70 | 69,25 |
| Casos exatamente recuperados | 20.031 | 23.083 |

O motor inferiu 36.817 casos para 37.689 casos de referência. Todas as 100 mil linhas foram preservadas. O avaliador e seus pesos permaneceram intactos.

## O que produziu ganho

O novo correlacionador mantém uma distribuição sobre fases ambíguas durante a associação dos eventos. Isso evita eliminar cedo uma fase que só pode ser reconhecida depois. A busca em feixe explora as trilhas físicas; Viterbi decodifica as fases depois, usando a sequência inteira.

Os tempos de espera foram aprendidos pelo excesso de transições em comparação com permutações das fases dentro de pessoa e data. Também reduzimos o corte mínimo de frequência das atividades, mantendo o filtro estatístico. Isso acrescentou duas fases candidatas, totalizando 86 na amostra estudada.

Não foi fornecido um catálogo. Cada arquivo é aprendido a partir de pessoa, aplicativo, tela e horários. Referências entram apenas na avaliação. A seleção das alternativas e dos parâmetros consultou o score desta base; os resultados não comprovam generalização externa.

## Análise crítica

Entre os casos de referência, 23.083 foram recuperados exatamente; 5.781 apareceram em mais de um caso previsto; 8.825 ficaram em um único caso previsto que também continha eventos de outra execução. São categorias exclusivas por caso de referência.

A precisão dos pares foi 65,41% e o recall 86,69%. Há excesso de vínculos, especialmente ao expandir os seis episódios extensos. Os limites das execuções e a correlação dos seus eventos continuam sendo os principais gargalos. O F1 B³ de 85,44% é auxiliar e não representa cumprimento da meta de 80 no score combinado.

A base de 60 mil eventos manteve 72,96 pontos. O teste sintético manteve 73,51; o controle embaralhado continuou sem rotinas. Esses controles não substituem uma validação externa com novos logs operacionais.

Foram registrados 59 ensaios intermediários, incluindo modelos de episódio, diferentes esperas, decodificação bidirecional, realimentação das fases, contextos mascarados, filtros com fases marginalizadas e otimização local. Alternativas que apenas aumentaram o ajuste interno sem melhorar o score não foram incluídas.

A pesquisa não demonstrou que 80 seja impossível, nem produziu uma garantia de alcançá-lo com os atributos disponíveis. A versão entregue atinge 69,25. O relatório JSON contém os valores sem arredondamento e os hashes de reprodução.

## Usar

Mantenha os quatro arquivos Python juntos, instale requirements.txt e altere somente CAMINHO_AMOSTRA em analisar_amostra.py. Execute esse script para gerar o HTML automaticamente. O estudo matemático está em ESTUDO_METODOLOGICO.md; a auditoria está em work/auditoria_v6.json.

### Documento: RESULTADOS_V7.md

# Resultado da pesquisa — versão 7.0

Nas 100 mil linhas, o score passou de **69,25 para 76,10/100**, ganho de 6,85 pontos. A meta de 80 ainda não foi atingida.

| Componente | Versão 6 | Versão 7 |
| --- | ---: | ---: |
| F1 das famílias | 84,44 | 87,10 |
| F1 dos pares | 74,56 | 79,78 |
| F1 dos casos inteiros | 61,96 | 70,96 |
| Score combinado | 69,25 | 76,10 |
| Casos exatamente recuperados | 23.083 | 26.957 |

Foram inferidos 38.291 casos para 37.689 casos de referência. Todas as 100 mil linhas e seus valores originais foram preservados; a fórmula do avaliador permaneceu intacta.

## O que produziu ganho

O modelo passou a aprender quais etapas costumam iniciar uma tarefa. Uma nova associação dos fluxos usa essa distribuição de entrada, em vez de tratar qualquer etapa como igualmente plausível para um novo início.

Os nomes são comparados com prefixos de até oito caracteres na fase refinada. Os tempos são estimados com blocos adaptativos de um histograma, usando pares adjacentes de atividades confiáveis. A aproximação por uma fase âncora passa a depender do posterior, incorporando a sequência, em vez de somente da afinidade lexical.

Uma tarefa local com início aprendido e apoio elevado pode ser preservada fora de um episódio maior. O modelo restituiu 2.190 eventos a essas tarefas, reduzindo uniões indevidas. Não houve exclusão de eventos da avaliação.

A evolução completa foi: entradas e nova associação, 73,65; refinamento de entradas, espera e âncoras, 74,53; preservação das tarefas locais, 76,10. São resultados da base completa, não números de janeiro apresentados como resultado de 100 mil eventos.

## Avaliação crítica

O avaliador encontrou 26.957 casos exatos, 4.802 casos de referência fragmentados e 5.930 contidos em um agrupamento que também inclui outra execução. São categorias exclusivas por caso de referência.

A precisão dos pares subiu de 65,41% para 75,79%. O recall passou de 86,69% para 84,22%: o modelo passou a fazer menos uniões, com melhor equilíbrio entre erros e acertos. Os seis episódios extensos ainda não foram recuperados exatamente. Telas compartilhadas, nomes genéricos e a distinção entre tarefa local e episódio continuam sendo dificuldades.

A pesquisa também testou busca temporal reversa, modelos explícitos de episódios, reestimação de emissões, consensos, fronteiras por posterior, entradas mais concentradas, disponibilidade diária e feixes maiores. A maior parte não melhorou a combinação escolhida. Um consenso estimava internamente F1 de casos de aproximadamente 94%, mas a avaliação real desse ensaio ficou em torno de 69%. Essa confiança interna não foi usada para declarar cumprimento da meta.

Aumentar o feixe de 128 para 512 teve ganho inferior a 0,01 ponto em janeiro e triplicou aproximadamente o tempo desse teste. A versão entregue mantém 128.

## Inferência e validação

O motor recebeu somente pessoa, aplicativo, tela, início e fim, com acesso bloqueado a qualquer outro atributo. Não há catálogo de processos nem consulta a modelos salvos da base de 100 mil linhas. As referências foram consultadas no diagnóstico e na comparação das alternativas, mas não como atributos da inferência.

A auditoria comparou a implementação final com o experimento completo: casos, famílias e etapas coincidiram nos 100 mil eventos. Conferiu também conservação das linhas, limites do apoio das fases e o hash sintático do avaliador.

A base de 60 mil eventos manteve 72,96 pontos. O teste sintético manteve 73,51, e o controle embaralhado continuou sem rotinas. Esses controles não comprovam generalização externa. A seleção de parâmetros usou as bases estudadas.

O F1 B³ de 88,63% é auxiliar e não substitui o score combinado. A versão efetivamente entregue atinge **76,1017338300**, abaixo de 80. Não demonstramos que 80 seja impossível, nem que mais busca vá garantir esse resultado.

## Executar

Mantenha os cinco módulos Python juntos. Altere apenas CAMINHO_AMOSTRA em analisar_amostra.py e execute o script. O HTML é gerado automaticamente. Fórmulas e fontes estão em ESTUDO_METODOLOGICO.md; a auditoria está em work/auditoria_v7.json.

## 8. Síntese crítica e ameaças à validade
### 8.1 Validade de construto
Uma referência pode definir como um único caso um episódio de vários dias e múltiplos tipos de atividade. Uma segmentação operacionalmente útil em tarefas pode ser penalizada por essa referência. Isso exige explicitar a unidade-alvo, sem alterar retrospectivamente o score para favorecer o algoritmo. Nomear comunidades por exemplos de telas não confirma seu significado de negócio.
### 8.2 Validade interna
Associação temporal não demonstra causalidade. Afinidades e posteriors são condicionais ao modelo. Restrições de não sobreposição são úteis, mas o mínimo de trilhas físicas pode subestimar fluxos latentes em coleta esparsa. Ciclos aprendidos restringem ramificações; a divisão por pessoa e data pode fragmentar atividades que cruzam a meia-noite.
### 8.3 Validade externa
As duas bases foram usadas durante o desenvolvimento. O controle sintético verifica propriedades funcionais; não substitui logs independentes. A invariância à remoção de referências demonstra uma propriedade de implementação, não generalização. A seleção automática entre correlacionadores também precisa ser avaliada em novas organizações.
### 8.4 Interpretação da manualidade e do calendário
Contadores representam ações capturadas, não percentual de esforço humano, produtividade, custo ou automação potencial comprovada. Ausência de cliques não implica automação. Dias úteis são segunda a sexta sem feriados locais. Lacunas na coleta podem parecer ausência de atividade. Transições de um episódio com trilhas concorrentes não são uma cadeia causal única.
### 8.5 Critério de encerramento desta documentação
O resultado documentado é 76,1017338300 e a meta continua aberta. Não foi demonstrada uma barreira teórica que impeça 80, nem existe garantia de alcançá-lo. Confiança interna, B³ e cobertura não substituem o score definido. O aumento de 69,25 para 76,10 corresponde a uma melhoria observada neste conjunto de desenvolvimento.

## 9. Protocolo recomendado para continuação
Antes de novos ajustes, congelar código e parâmetros, reservar logs de outra origem e obter referências revisadas de execuções completas. Avaliar separadamente famílias, casos locais e episódios. Reportar precisão/recall, casos exatos e desempenho por tamanho, usuário e período. Executar ablações removendo uma melhoria por vez e quantificar sensibilidade a sementes e parâmetros. Se houver intervalos de confiança, reamostrar unidades coerentes, como dias ou casos completos, evitando tratar pares dependentes como observações independentes. Objetos de negócio podem ser estudados em uma extensão explícita, sem misturá-la ao experimento atual sem contexto.

## 10. Reprodutibilidade e uso
O procedimento de execução, dependências e interpretação está reproduzido abaixo. A documentação é uma fotografia dos arquivos atuais; hashes no inventário permitem identificar essa fotografia. O algoritmo aprende com cada entrada e não requer os caches experimentais. Arquivos pickle são artefatos internos e não devem ser interpretados como modelos exigidos pelo usuário.

# Descoberta de rotinas — versão 7.0

Mantenha juntos analisar_amostra.py, motor_descoberta.py, motor_sequencial.py, motor_probabilistico.py e motor_adaptativo.py. O primeiro configura a amostra e gera os relatórios. Os demais implementam a descoberta de grupos, o aprendizado das etapas e a correlação das execuções.

Use Python 3.10 ou superior. Instale as dependências uma vez:

    py -m pip install -r requirements.txt

Altere somente a variável no início de analisar_amostra.py:

    CAMINHO_AMOSTRA = r"C:/dados/minha_amostra.csv"

Também é aceita uma lista de caminhos. Execute:

    py analisar_amostra.py

Caminhos relativos partem da pasta do script. Cada amostra é aprendida separadamente; não existe catálogo de processos nem consulta a modelos salvos da base de 100 mil linhas.

## Entrada e saídas

São aceitos CSVs UTF-8, UTF-8/BOM e Windows-1252, separados por vírgula, ponto e vírgula ou tabulação. As colunas obrigatórias são codigo_racf, nome_programa, nome_tela_foco, data_hora_inicio_exec, data_hora_fim_exec, quantidade_teclas_digitadas, quantidade_clicks, quantidade_copias e quantidade_colagens. Horários usam formato ISO local; contadores são inteiros não negativos.

O motor admite exclusivamente pessoa, aplicativo, tela, início e fim. Os contadores alimentam a manualidade no relatório. Referências e execucao_id não entram na inferência.

Ao lado do CSV, a pasta <nome_da_amostra>_resultados recebe:

- estudo.html: rotinas candidatas, etapas, transições, manualidade e calendário.
- eventos_classificados.csv: todas as linhas e colunas originais, acrescidas dos agrupamentos e evidências.
- metricas.json: score, resultados locais, diagnósticos, parâmetros e hashes do arquivo e dos cinco módulos Python.

Uma execução substitui os resultados da mesma amostra e preserva o CSV de entrada.

## Como o modelo trabalha

Primeiro aprende comunidades de atividades com associações temporais acima do esperado, variantes lexicais e contextos por ocorrência. O suporte mínimo no grafo é teto(raiz(N)/6); o filtro estatístico permanece em 1%.

Sem atividades transversais detectadas, usa a cobertura de caminhos por rotina. Quando esse detector encontra interrupções frequentes, usa três passagens. A primeira encontra trilhas preliminares. A segunda aprende distribuições de entrada das tarefas e distingue prefixos de nomes até oito caracteres. A terceira refina essas entradas e os tempos de espera, revisa as trilhas e preserva tarefas locais com início reconhecível.

As entradas são aprendidas por mudanças entre grupos de etapas confiáveis, sem IDs de processo. Não usamos os dias de episódios concentrados para estimar esse padrão de início. Grupos com pouca evidência mantêm o prior anterior; a regularização usa cinco pseudo-observações.

O feixe final mantém 128 hipóteses com temperatura 0,75. Uma fase só é aproximada por âncora quando seu apoio posterior chega a 0,98. Viterbi usa a sequência inteira e peso 0,5. Uma tarefa local com entrada aprendida e apoio de pelo menos 0,98 pode permanecer fora do episódio maior; o CSV marca tarefa_local_preservada nesses eventos. Esses apoios não são probabilidades calibradas de acerto.

Os tempos de espera são refinados com pares adjacentes de etapas confiáveis. Um histograma em bins de cinco segundos é dividido em blocos de taxa constante por otimização penalizada. Os limites dos blocos são aprendidos do arquivo. O potencial combina 90% do modelo refinado e 10% do inicial, com fallback quando faltam pares suficientes.

É um método offline e usa eventos anteriores e posteriores. A quantidade de trilhas é o mínimo exigido pela concorrência dos intervalos, não o número real comprovado de fluxos. A escolha entre correlacionadores depende dos dados, sem condição por nome do arquivo ou número de linhas.

caso_local preserva a hipótese local e episodio_longo identifica os episódios mantidos na atribuição final. As transições exibidas são adjacências cronológicas, não prova de causalidade entre todas as etapas. As trilhas locais são reconstruídas por pessoa e data; tarefas que atravessam a meia-noite podem ser fragmentadas fora dos episódios longos.

Os nomes de rotina são exemplos de telas, sem confirmação do significado de negócio. O apoio posterior da fase é condicionado às trilhas escolhidas e não é uma probabilidade calibrada de acerto. Manualidade significa teclas, cliques, cópias e colagens por ocorrência. Dias úteis no painel são segunda a sexta, sem lista de feriados.

## Avaliação

O score original foi mantido: 10% F1 das famílias alinhadas + 40% F1 dos pares + 50% F1 dos casos inteiros. Nenhuma linha é excluída da pontuação.

| Amostra | Versão 6 | Versão 7 |
| --- | ---: | ---: |
| 100 mil eventos | 69,25 | 76,10 |
| 60 mil eventos | 72,96 | 72,96 |

Na base de 100 mil eventos, recuperamos exatamente 26.957 de 37.689 casos. F1 das famílias: 87,10%; dos pares: 79,78%; dos casos inteiros: 70,96%. A meta de 80/100 ainda não foi atingida. Cobertura de 100% não significa acerto de 100%.

Para calcular o score completo, todas as linhas precisam de processo_id/processo_sintetico ou referencia_processo_id/referencia_processo. Sem essas referências, a análise e o HTML são gerados, mas a pontuação correspondente fica indisponível. Não se estima acurácia real apenas pela confiança interna.

As duas bases foram consultadas no desenvolvimento e na seleção de parâmetros. Isso não constitui validação externa, embora os rótulos não sejam atributos de inferência. Consulte ESTUDO_METODOLOGICO.md e RESULTADOS_V7.md para equações, fontes, experimentos e limitações.

## Verificações

    py testar_algoritmo.py

Esse teste controlado de 3.200 eventos preservou score 73,51 e F1 das famílias 95,20; após embaralhar telas e aplicativos, não encontrou rotinas. Sua pasta de saída mantém o nome legado work/validacao_v3.

    py work/auditar_v7.py

A auditoria completa usa a amostra de 100 mil linhas, expõe ao motor somente os cinco atributos permitidos e reconcilia todas as linhas originais. Também confere o hash sintático do avaliador. A comparação adicional com um cache de pesquisa é opcional. Na execução registrada, os casos, famílias e etapas dos 100 mil eventos coincidiram integralmente com o experimento. O resultado fica em work/auditoria_v7.json.

O registro desta continuação contém 149 resultados experimentais em work/registro_pesquisa_v7.json, incluindo saídas antes e depois de refinamentos. O escopo de janeiro é separado da avaliação completa. A pesquisa anterior continua registrada em work/registro_pesquisa_v6.json.

Verificado com Python 3.14, NumPy 2.4.6, SciPy 1.17.1, NetworkX 3.6.1 e scikit-learn 1.9.1. Outras versões podem resolver empates numéricos de modo diferente.

Na máquina usada na auditoria, a execução completa levou cerca de quatro minutos. O programa mostra as três passagens antes de gerar os artefatos.

## Anexo A6. Registro integral dos resultados experimentais da versão 6

São 59 registros de saídas, não necessariamente algoritmos independentes. Identificadores preservados permitem rastreamento aos artefatos locais. O campo escopo deve ser respeitado; resultados de janeiro não representam a amostra inteira.

### Ensaio 6.1: joint80_0.2_0.1.pkl

```json
{
  "experimento": "joint80_0.2_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6853,
    "score": 60.09875513537584,
    "f1_familias": 79.25105303374846,
    "f1_pares": 65.6013023793891,
    "f1_casos": 51.86625776049069,
    "casos_exatos": 3467,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.1602787456446,
    "precisao_pares": 63.45840352792294,
    "recall_pares": 67.89398440598676,
    "f1_b3": 79.9910976090989,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.2: joint80_0.4_0.03.pkl

```json
{
  "experimento": "joint80_0.4_0.03.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6785,
    "score": 61.10365987455898,
    "f1_familias": 79.15947495419472,
    "f1_pares": 68.03055453630076,
    "f1_casos": 51.9509811292384,
    "casos_exatos": 3455,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.1718931475029,
    "precisao_pares": 64.12493381224081,
    "recall_pares": 72.44278592919612,
    "f1_b3": 80.32634390282678,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.3: joint80_0.4_0.1.pkl

```json
{
  "experimento": "joint80_0.4_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6790,
    "score": 60.62663448711356,
    "f1_familias": 79.25998413211805,
    "f1_pares": 66.57422658938388,
    "f1_casos": 52.14189087629641,
    "casos_exatos": 3469,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.20092915214866,
    "precisao_pares": 63.34441412532474,
    "recall_pares": 70.1510991108904,
    "f1_b3": 80.22061948726804,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.4: joint80_0.4_0.3.pkl

```json
{
  "experimento": "joint80_0.4_0.3.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6979,
    "score": 59.24957881775438,
    "f1_familias": 79.20090785361438,
    "f1_pares": 63.26258632774042,
    "f1_casos": 52.04890700259355,
    "casos_exatos": 3512,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.0150987224158,
    "precisao_pares": 62.151093757186665,
    "recall_pares": 64.41455805315034,
    "f1_b3": 79.72327254545218,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.5: joint80_0.6_0.1.pkl

```json
{
  "experimento": "joint80_0.6_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6763,
    "score": 61.04941821838891,
    "f1_familias": 79.35652604574163,
    "f1_pares": 67.73810030609344,
    "f1_casos": 52.03705098275473,
    "casos_exatos": 3455,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.32288037166086,
    "precisao_pares": 64.70955993597659,
    "recall_pares": 71.06404356734227,
    "f1_b3": 80.36883418906405,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.6: joint_consistent80_0.2_0.1.pkl

```json
{
  "experimento": "joint_consistent80_0.2_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6587,
    "score": 60.94823605030304,
    "f1_familias": 78.87371179341001,
    "f1_pares": 67.59072586511019,
    "f1_casos": 52.04914904983592,
    "casos_exatos": 3410,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 81.73635307781649,
    "precisao_pares": 58.1774926249255,
    "recall_pares": 80.63813549399015,
    "f1_b3": 80.31281395061345,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.7: joint_consistent80_0.4_0.03.pkl

```json
{
  "experimento": "joint_consistent80_0.4_0.03.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6533,
    "score": 60.995308341183176,
    "f1_familias": 78.75496856548803,
    "f1_pares": 67.73707181833738,
    "f1_casos": 52.04996551459882,
    "casos_exatos": 3396,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 81.70731707317073,
    "precisao_pares": 56.31854878850708,
    "recall_pares": 84.96328274944103,
    "f1_b3": 80.39100197603011,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.8: joint_consistent80_0.4_0.1.pkl

```json
{
  "experimento": "joint_consistent80_0.4_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6491,
    "score": 60.754196802721395,
    "f1_familias": 78.7230959499844,
    "f1_pares": 67.1243766646522,
    "f1_casos": 52.064273083724146,
    "casos_exatos": 3386,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 81.602787456446,
    "precisao_pares": 55.3963658808298,
    "recall_pares": 85.1519715129488,
    "f1_b3": 80.29919451939357,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.9: joint_consistent80_0.6_0.1.pkl

```json
{
  "experimento": "joint_consistent80_0.6_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6430,
    "score": 60.75928248554693,
    "f1_familias": 78.68227704485676,
    "f1_pares": 66.91788876788563,
    "f1_casos": 52.247798547814,
    "casos_exatos": 3382,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.35191637630662,
    "precisao_pares": 53.93820058176056,
    "recall_pares": 88.12406251489679,
    "f1_b3": 80.37815553027534,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.10: excesso80_0.5.pkl

```json
{
  "experimento": "excesso80_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6540,
    "score": 64.08418683835231,
    "f1_familias": 80.1536182840006,
    "f1_pares": 73.3636985542924,
    "f1_casos": 53.44669117647059,
    "casos_exatos": 3489,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 83.87921022067364,
    "precisao_pares": 62.515041941430624,
    "recall_pares": 88.76825159982802,
    "f1_b3": 81.71043511002743,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.11: excesso80_1.0.pkl

```json
{
  "experimento": "excesso80_1.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6190,
    "score": 62.59396732189512,
    "f1_familias": 79.9032885526922,
    "f1_pares": 73.21222854496865,
    "f1_casos": 50.63749409727688,
    "casos_exatos": 3217,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 83.69337979094077,
    "precisao_pares": 62.87002852193802,
    "recall_pares": 87.62697846671057,
    "f1_b3": 80.46021581243639,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.12: excesso80_1.5.pkl

```json
{
  "experimento": "excesso80_1.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6072,
    "score": 61.422098557984796,
    "f1_familias": 79.04695336132666,
    "f1_pares": 72.604280218596,
    "f1_casos": 48.95138226882745,
    "casos_exatos": 3081,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.9500580720093,
    "precisao_pares": 62.663164099730736,
    "recall_pares": 86.29433225605949,
    "f1_b3": 79.54842414898005,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.13: excesso_longo80_0.0.pkl

```json
{
  "experimento": "excesso_longo80_0.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6516,
    "score": 65.09837880922548,
    "f1_familias": 80.5401917446529,
    "f1_pares": 73.76114463631728,
    "f1_casos": 55.079803560466544,
    "casos_exatos": 3589,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.19279907084785,
    "precisao_pares": 62.67582769387741,
    "recall_pares": 89.61029314097601,
    "f1_b3": 82.53817648000039,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.14: excesso_longo80_2.0.pkl

```json
{
  "experimento": "excesso_longo80_2.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6542,
    "score": 64.33043355555998,
    "f1_familias": 80.4949864609962,
    "f1_pares": 73.2532639086639,
    "f1_casos": 53.95925869198958,
    "casos_exatos": 3523,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.1637630662021,
    "precisao_pares": 61.856364729854384,
    "recall_pares": 89.79842652916808,
    "f1_b3": 82.11154678126626,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.15: excesso_longo80_4.0.pkl

```json
{
  "experimento": "excesso_longo80_4.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6688,
    "score": 63.72550466930889,
    "f1_familias": 79.97065898196398,
    "f1_pares": 73.90531383174971,
    "f1_casos": 52.332626476825205,
    "casos_exatos": 3455,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 83.75725900116144,
    "precisao_pares": 62.83109659584723,
    "recall_pares": 89.71854504626045,
    "f1_b3": 81.37617107469654,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.16: tempo_condicional80_0.0.pkl

```json
{
  "experimento": "tempo_condicional80_0.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6610,
    "score": 63.729520083861395,
    "f1_familias": 80.03192971744083,
    "f1_pares": 72.5209069163591,
    "f1_casos": 53.43592869114734,
    "casos_exatos": 3507,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 83.7746806039489,
    "precisao_pares": 61.030016513990894,
    "recall_pares": 89.34255595753415,
    "f1_b3": 81.74805177789578,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.17: tempo_condicional80_2.0.pkl

```json
{
  "experimento": "tempo_condicional80_2.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6675,
    "score": 64.49533086239843,
    "f1_familias": 79.77468563538854,
    "f1_pares": 73.2179367720902,
    "f1_casos": 54.461375180047,
    "casos_exatos": 3592,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 83.57723577235772,
    "precisao_pares": 61.47798633385167,
    "recall_pares": 90.49998125608309,
    "f1_b3": 82.17537494967567,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.18: tempo_condicional80_4.0.pkl

```json
{
  "experimento": "tempo_condicional80_4.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6673,
    "score": 64.68853490604505,
    "f1_familias": 80.19191177400272,
    "f1_pares": 73.54840670958677,
    "f1_casos": 54.49996208962014,
    "casos_exatos": 3594,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 83.89082462253194,
    "precisao_pares": 61.85351568726286,
    "recall_pares": 90.69681552422108,
    "f1_b3": 82.51014286357027,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.19: coerencia80_2_0.1.pkl

```json
{
  "experimento": "coerencia80_2_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6885,
    "score": 63.84251602181342,
    "f1_familias": 80.5401917446529,
    "f1_pares": 70.81964895368111,
    "f1_casos": 54.921274531751365,
    "casos_exatos": 3680,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.19279907084785,
    "precisao_pares": 77.57968506280555,
    "recall_pares": 65.14327988925817,
    "f1_b3": 82.04111589518445,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.20: coerencia80_2_0.4.pkl

```json
{
  "experimento": "coerencia80_2_0.4.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6885,
    "score": 63.84251602181342,
    "f1_familias": 80.5401917446529,
    "f1_pares": 70.81964895368111,
    "f1_casos": 54.921274531751365,
    "casos_exatos": 3680,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.19279907084785,
    "precisao_pares": 77.57968506280555,
    "recall_pares": 65.14327988925817,
    "f1_b3": 82.04111589518445,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.21: coerencia80_2_0.8.pkl

```json
{
  "experimento": "coerencia80_2_0.8.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6885,
    "score": 63.84251602181342,
    "f1_familias": 80.5401917446529,
    "f1_pares": 70.81964895368111,
    "f1_casos": 54.921274531751365,
    "casos_exatos": 3680,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.19279907084785,
    "precisao_pares": 77.57968506280555,
    "recall_pares": 65.14327988925817,
    "f1_b3": 82.04111589518445,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.22: coerencia80_3_0.1.pkl

```json
{
  "experimento": "coerencia80_3_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6620,
    "score": 64.99930956474269,
    "f1_familias": 80.5401917446529,
    "f1_pares": 73.58277530577875,
    "f1_casos": 55.02436053593179,
    "casos_exatos": 3614,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.19279907084785,
    "precisao_pares": 67.86662794079476,
    "recall_pares": 80.35038165854507,
    "f1_b3": 82.41856227681077,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.23: coerencia80_3_0.4.pkl

```json
{
  "experimento": "coerencia80_3_0.4.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6620,
    "score": 64.99930956474269,
    "f1_familias": 80.5401917446529,
    "f1_pares": 73.58277530577875,
    "f1_casos": 55.02436053593179,
    "casos_exatos": 3614,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.19279907084785,
    "precisao_pares": 67.86662794079476,
    "recall_pares": 80.35038165854507,
    "f1_b3": 82.41856227681077,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.24: coerencia80_3_0.8.pkl

```json
{
  "experimento": "coerencia80_3_0.8.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6620,
    "score": 64.99930956474269,
    "f1_familias": 80.5401917446529,
    "f1_pares": 73.58277530577875,
    "f1_casos": 55.02436053593179,
    "casos_exatos": 3614,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 84.19279907084785,
    "precisao_pares": 67.86662794079476,
    "recall_pares": 80.35038165854507,
    "f1_b3": 82.41856227681077,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.25: futuro80_0.0_0.0_4.pkl

```json
{
  "experimento": "futuro80_0.0_0.0_4.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6402,
    "score": 66.17148068921921,
    "f1_familias": 82.28242311044004,
    "f1_pares": 73.75575812224555,
    "f1_casos": 56.88187025855395,
    "casos_exatos": 3674,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.59814169570267,
    "precisao_pares": 62.786623072522275,
    "recall_pares": 89.36895942566787,
    "f1_b3": 83.43439061152715,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.26: futuro80_0.5_0.0_3.pkl

```json
{
  "experimento": "futuro80_0.5_0.0_3.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6364,
    "score": 66.3209852673731,
    "f1_familias": 82.70707396150284,
    "f1_pares": 72.62957666563469,
    "f1_casos": 57.99689440993789,
    "casos_exatos": 3735,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.9465737514518,
    "precisao_pares": 61.38276511490829,
    "recall_pares": 88.92229882801924,
    "f1_b3": 83.44701921117388,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.27: futuro80_0.5_0.2_3.pkl

```json
{
  "experimento": "futuro80_0.5_0.2_3.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6304,
    "score": 66.02937686170922,
    "f1_familias": 82.57051325049312,
    "f1_pares": 72.6874441068604,
    "f1_casos": 57.394695787831516,
    "casos_exatos": 3679,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.85946573751451,
    "precisao_pares": 61.1921386042401,
    "recall_pares": 89.50067593804047,
    "f1_b3": 83.2385222711957,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.28: futuro80_1.0_0.5_3.pkl

```json
{
  "experimento": "futuro80_1.0_0.5_3.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6462,
    "score": 63.13692837641633,
    "f1_familias": 80.26240645839219,
    "f1_pares": 71.24104356746604,
    "f1_casos": 53.22854060718139,
    "casos_exatos": 3454,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 83.97212543554006,
    "precisao_pares": 58.79214771978713,
    "recall_pares": 90.37807637428779,
    "f1_b3": 81.53105461124707,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.29: smoother80_0.25.pkl

```json
{
  "experimento": "smoother80_0.25.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6850,
    "score": 65.90169038297626,
    "f1_familias": 81.71950230211382,
    "f1_pares": 73.3981196472122,
    "f1_casos": 56.74098458775999,
    "casos_exatos": 3792,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.00580720092915,
    "precisao_pares": 63.95644356736368,
    "recall_pares": 86.11029476082068,
    "f1_b3": 83.34333315784536,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.30: smoother80_0.5.pkl

```json
{
  "experimento": "smoother80_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6386,
    "score": 66.92314505479278,
    "f1_familias": 83.10582156405862,
    "f1_pares": 73.40321006723534,
    "f1_casos": 58.50255774298558,
    "casos_exatos": 3774,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.18466898954703,
    "precisao_pares": 63.95430756324989,
    "recall_pares": 86.12818247411373,
    "f1_b3": 83.62461995843462,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.31: smoother80_1.0.pkl

```json
{
  "experimento": "smoother80_1.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6273,
    "score": 66.73900625169806,
    "f1_familias": 82.82106623345892,
    "f1_pares": 73.40395835229413,
    "f1_casos": 58.19063257486903,
    "casos_exatos": 3721,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.96399535423926,
    "precisao_pares": 63.95286643399189,
    "recall_pares": 86.13285688302084,
    "f1_b3": 83.51833368132256,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.32: belief80_1.pkl

```json
{
  "experimento": "belief80_1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6337,
    "score": 66.8225084093887,
    "f1_familias": 83.45900593816665,
    "f1_pares": 72.59002572425648,
    "f1_casos": 58.88119505173889,
    "casos_exatos": 3784,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.43437862950059,
    "precisao_pares": 63.515291447858125,
    "recall_pares": 84.690107516033,
    "f1_b3": 83.72602371329347,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.33: belief80_2.pkl

```json
{
  "experimento": "belief80_2.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6327,
    "score": 66.66357743254629,
    "f1_familias": 83.45182653488693,
    "f1_pares": 72.39024062669093,
    "f1_casos": 58.72459705676244,
    "casos_exatos": 3771,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.43437862950059,
    "precisao_pares": 63.420285536397685,
    "recall_pares": 84.31555314687225,
    "f1_b3": 83.6344982741598,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.34: belief80_3.pkl

```json
{
  "experimento": "belief80_3.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6333,
    "score": 66.61112668070666,
    "f1_familias": 83.43507795705088,
    "f1_pares": 72.37540568398033,
    "f1_casos": 58.634913222818895,
    "casos_exatos": 3767,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.41695702671312,
    "precisao_pares": 63.50373098024543,
    "recall_pares": 84.12841480612079,
    "f1_b3": 83.60989006896563,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.35: rao80_96.pkl

```json
{
  "experimento": "rao80_96.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6489,
    "score": 67.70277813075884,
    "f1_familias": 83.61366463858731,
    "f1_pares": 73.38236423068743,
    "f1_casos": 59.976931949250286,
    "casos_exatos": 3900,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.56213704994192,
    "precisao_pares": 63.54654196736755,
    "recall_pares": 86.82057350831975,
    "f1_b3": 84.37567559122084,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.36: rao80_256.pkl

```json
{
  "experimento": "rao80_256.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6456,
    "score": 67.72393526181801,
    "f1_familias": 83.5322752251539,
    "f1_pares": 73.01434258291583,
    "f1_casos": 60.32994141227259,
    "casos_exatos": 3913,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.52729384436701,
    "precisao_pares": 63.19583962928703,
    "recall_pares": 86.44497781044207,
    "f1_b3": 84.46546898053795,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.37: rao_temperature80_0.75_0.5.pkl

```json
{
  "experimento": "rao_temperature80_0.75_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6304,
    "score": 67.87474582490383,
    "f1_familias": 83.93118252645931,
    "f1_pares": 72.70952914905348,
    "f1_casos": 60.79563182527301,
    "casos_exatos": 3897,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.84088269454124,
    "precisao_pares": 62.835468035429066,
    "recall_pares": 86.26540645836698,
    "f1_b3": 84.45890169259754,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.38: rao_temperature80_0.75_1.0.pkl

```json
{
  "experimento": "rao_temperature80_0.75_1.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6195,
    "score": 67.73119569034739,
    "f1_familias": 83.89563125832981,
    "f1_pares": 72.71093767751213,
    "f1_casos": 60.51451498701912,
    "casos_exatos": 3846,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.82346109175377,
    "precisao_pares": 62.83479733208791,
    "recall_pares": 86.27063624258979,
    "f1_b3": 84.38635353514505,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.39: rao_temperature80_1.0_0.5.pkl

```json
{
  "experimento": "rao_temperature80_1.0_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6214,
    "score": 67.52517958629855,
    "f1_familias": 83.77703553998676,
    "f1_pares": 72.88832872961065,
    "f1_casos": 59.98428908091123,
    "casos_exatos": 3818,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.71312427409988,
    "precisao_pares": 62.834391942671715,
    "recall_pares": 86.77253354351204,
    "f1_b3": 84.06173425468813,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.40: rao_temperature80_1.0_1.0.pkl

```json
{
  "experimento": "rao_temperature80_1.0_1.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6124,
    "score": 67.27068697196404,
    "f1_familias": 83.60309008662703,
    "f1_pares": 72.88907781964576,
    "f1_casos": 59.50949367088607,
    "casos_exatos": 3761,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.57955865272939,
    "precisao_pares": 62.833503293017756,
    "recall_pares": 86.77635174880744,
    "f1_b3": 83.93322692623637,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.41: rao_temperature80_1.5_0.5.pkl

```json
{
  "experimento": "rao_temperature80_1.5_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6120,
    "score": 66.99152536249744,
    "f1_familias": 83.57288464512018,
    "f1_pares": 72.57087239691039,
    "f1_casos": 59.211775878442545,
    "casos_exatos": 3741,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.55052264808363,
    "precisao_pares": 62.72675642324066,
    "recall_pares": 86.07995738420078,
    "f1_b3": 83.62830016969208,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.42: rao_temperature80_1.5_1.0.pkl

```json
{
  "experimento": "rao_temperature80_1.5_1.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6038,
    "score": 66.76978620831291,
    "f1_familias": 83.32490254570419,
    "f1_pares": 72.57085658023006,
    "f1_casos": 58.81790664330094,
    "casos_exatos": 3692,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.3472706155633,
    "precisao_pares": 62.725663788440244,
    "recall_pares": 86.08197061972018,
    "f1_b3": 83.51063362012,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.43: gramatica_flexivel80_empirical_0.0.pkl

```json
{
  "experimento": "gramatica_flexivel80_empirical_0.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6209,
    "score": 66.4911154084458,
    "f1_familias": 83.05617322454114,
    "f1_pares": 73.40087684562752,
    "f1_casos": 57.650294695481335,
    "casos_exatos": 3668,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.30081300813008,
    "precisao_pares": 63.94894101889112,
    "recall_pares": 86.13149158536974,
    "f1_b3": 83.2177945338371,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.44: gramatica_flexivel80_empirical_0.25.pkl

```json
{
  "experimento": "gramatica_flexivel80_empirical_0.25.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6216,
    "score": 66.5406887407018,
    "f1_familias": 83.08021400945994,
    "f1_pares": 73.4013353302252,
    "f1_casos": 57.744266415331445,
    "casos_exatos": 3676,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.28919860627178,
    "precisao_pares": 63.94956049961866,
    "recall_pares": 86.13163042919867,
    "f1_b3": 83.27658134199535,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.45: gramatica_flexivel80_empirical_0.5.pkl

```json
{
  "experimento": "gramatica_flexivel80_empirical_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6240,
    "score": 66.72454225945836,
    "f1_familias": 83.10593968147285,
    "f1_pares": 73.40238405533944,
    "f1_casos": 58.10598933835058,
    "casos_exatos": 3706,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.28339140534263,
    "precisao_pares": 63.95110154676151,
    "recall_pares": 86.13172299175129,
    "f1_b3": 83.40935778615354,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.46: gramatica_flexivel80_empirical_0.75.pkl

```json
{
  "experimento": "gramatica_flexivel80_empirical_0.75.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6280,
    "score": 66.90594203116433,
    "f1_familias": 83.16664341249486,
    "f1_pares": 73.40348494063579,
    "f1_casos": 58.455767427321035,
    "casos_exatos": 3740,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.30662020905923,
    "precisao_pares": 63.95282387026118,
    "recall_pares": 86.13163042919867,
    "f1_b3": 83.56525231522633,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.47: gramatica_flexivel80_skip_0.1.pkl

```json
{
  "experimento": "gramatica_flexivel80_skip_0.1.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6295,
    "score": 66.64958716109678,
    "f1_familias": 82.9009232037433,
    "f1_pares": 73.40244485295749,
    "f1_casos": 57.99703379907891,
    "casos_exatos": 3715,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.04529616724739,
    "precisao_pares": 63.952278227521205,
    "recall_pares": 86.1297560375082,
    "f1_b3": 83.42837625687012,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.48: gramatica_flexivel80_skip_0.25.pkl

```json
{
  "experimento": "gramatica_flexivel80_skip_0.25.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6247,
    "score": 66.56879414126193,
    "f1_familias": 82.8854238651908,
    "f1_pares": 73.40179682398006,
    "f1_casos": 57.83906605030165,
    "casos_exatos": 3691,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.04529616724739,
    "precisao_pares": 63.95089893592254,
    "recall_pares": 86.13047339729097,
    "f1_b3": 83.2989069822342,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.49: gramatica_flexivel80_skip_0.5.pkl

```json
{
  "experimento": "gramatica_flexivel80_skip_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6227,
    "score": 66.05747003584432,
    "f1_familias": 82.34973595163203,
    "f1_pares": 73.39952761194368,
    "f1_casos": 56.92537079180727,
    "casos_exatos": 3627,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.61556329849013,
    "precisao_pares": 63.94844903835911,
    "recall_pares": 86.12866842751495,
    "f1_b3": 82.98783661888281,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.50: context_decode80_0.25.pkl

```json
{
  "experimento": "context_decode80_0.25.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6371,
    "score": 66.57622343534796,
    "f1_familias": 83.17879500857633,
    "f1_pares": 73.40251382862124,
    "f1_casos": 57.79467680608365,
    "casos_exatos": 3724,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.30662020905923,
    "precisao_pares": 63.95365880355063,
    "recall_pares": 86.1274419736928,
    "f1_b3": 83.47432810217434,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.51: context_decode80_0.5.pkl

```json
{
  "experimento": "context_decode80_0.5.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6388,
    "score": 66.48386703451362,
    "f1_familias": 83.10188040110707,
    "f1_pares": 73.40226940169234,
    "f1_casos": 57.62554246745195,
    "casos_exatos": 3718,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.29500580720092,
    "precisao_pares": 63.95353013092633,
    "recall_pares": 86.12700230156787,
    "f1_b3": 83.4639687100029,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.52: context_decode80_1.0.pkl

```json
{
  "experimento": "context_decode80_1.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6637,
    "score": 65.66295253529792,
    "f1_familias": 81.88070219987391,
    "f1_pares": 73.39905859752135,
    "f1_casos": 56.230517752603966,
    "casos_exatos": 3698,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.43554006968641,
    "precisao_pares": 63.95493357035864,
    "recall_pares": 86.1156171075961,
    "f1_b3": 83.25341524490315,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.53: context_decode80_2.0.pkl

```json
{
  "experimento": "context_decode80_2.0.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7350,
    "score": 62.83482177367458,
    "f1_familias": 77.64353053724665,
    "f1_pares": 73.52645306339704,
    "f1_casos": 51.31977498918217,
    "casos_exatos": 3558,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 82.1951219512195,
    "precisao_pares": 63.998979615102996,
    "recall_pares": 86.38677910548475,
    "f1_b3": 81.81849587670742,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.54: otimizado80_phase.pkl

```json
{
  "experimento": "otimizado80_phase.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6433,
    "score": 67.80311428611907,
    "f1_familias": 83.8030930020946,
    "f1_pares": 73.31954238986475,
    "f1_casos": 60.18997605992741,
    "casos_exatos": 3897,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.75377468060395,
    "precisao_pares": 63.96372034504451,
    "recall_pares": 85.88117930245787,
    "f1_b3": 84.55100423593193,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.55: otimizado80_rao.pkl

```json
{
  "experimento": "otimizado80_rao.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6466,
    "score": 67.7741550776658,
    "f1_familias": 83.68187275558235,
    "f1_pares": 73.02578069768916,
    "f1_casos": 60.391311046063784,
    "casos_exatos": 3920,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.6260162601626,
    "precisao_pares": 63.314907254421385,
    "recall_pares": 86.25508573375029,
    "f1_b3": 84.48290038754797,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.56: rao_suporte6_80.pkl

```json
{
  "experimento": "rao_suporte6_80.pkl",
  "escopo": "janeiro",
  "eventos": 17220,
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6348,
    "score": 68.66547197155892,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.15597107846939,
    "f1_casos": 61.84701492537314,
    "casos_exatos": 3978,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.30070172662484,
    "recall_pares": 86.64583854961884,
    "f1_b3": 85.05646370483214,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 6.57: excesso_full_casos.pkl

```json
{
  "experimento": "excesso_full_casos.pkl",
  "escopo": "completo",
  "eventos": 100000,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 37567,
    "score": 65.3170587264319,
    "f1_familias": 80.6288457005163,
    "f1_pares": 74.19408852159806,
    "f1_casos": 55.15307749548209,
    "casos_exatos": 20753,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 84.334,
    "precisao_pares": 63.136482963173265,
    "recall_pares": 89.94728840842743,
    "f1_b3": 82.98497697862132,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

### Ensaio 6.58: smoother_full_casos.pkl

```json
{
  "experimento": "smoother_full_casos.pkl",
  "escopo": "completo",
  "eventos": 100000,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 36901,
    "score": 67.51185737204817,
    "f1_familias": 83.01409779326741,
    "f1_pares": 74.10200046725738,
    "f1_casos": 59.13929481163695,
    "casos_exatos": 22056,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 86.247,
    "precisao_pares": 65.03483678849214,
    "recall_pares": 86.10705498941492,
    "f1_b3": 84.12471838074828,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

### Ensaio 6.59: reset_family_full_casos.pkl

```json
{
  "experimento": "reset_family_full_casos.pkl",
  "escopo": "completo",
  "eventos": 100000,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 36755,
    "score": 67.45010652181628,
    "f1_familias": 83.01409779326741,
    "f1_pares": 74.10152531761763,
    "f1_casos": 59.01617323088496,
    "casos_exatos": 21967,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 86.247,
    "precisao_pares": 65.03390465398333,
    "recall_pares": 86.10740589908913,
    "f1_b3": 84.05029013898522,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

## Anexo A7. Registro integral dos resultados experimentais da versão 7

São 149 registros de saídas, não necessariamente algoritmos independentes. Identificadores preservados permitem rastreamento aos artefatos locais. O campo escopo deve ser respeitado; resultados de janeiro não representam a amostra inteira.

### Ensaio 7.1: pesquisa7_contexto_0_False_False.pkl

```json
{
  "experimento": "pesquisa7_contexto_0_False_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6560,
    "score": 67.47572392115931,
    "f1_familias": 84.79576077484592,
    "f1_pares": 70.72759811943457,
    "f1_casos": 61.41021719180178,
    "casos_exatos": 4015,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 68.43014826080625,
    "recall_pares": 73.18467478841357,
    "f1_b3": 84.59597365528683,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.2: pesquisa7_contexto_0_True_False.pkl

```json
{
  "experimento": "pesquisa7_contexto_0_True_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6623,
    "score": 66.20554106853984,
    "f1_familias": 84.79576077484592,
    "f1_pares": 67.90118236119092,
    "f1_casos": 61.13098409315777,
    "casos_exatos": 4016,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 66.05344533019644,
    "recall_pares": 69.85526919272958,
    "f1_b3": 84.156918623818,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.3: pesquisa7_contexto_0_True_True.pkl

```json
{
  "experimento": "pesquisa7_contexto_0_True_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8431,
    "score": 57.9395738447348,
    "f1_familias": 84.94605797033785,
    "f1_pares": 67.86544748260305,
    "f1_casos": 44.5975781093196,
    "casos_exatos": 3333,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.69454123112659,
    "precisao_pares": 66.04718453848297,
    "recall_pares": 69.78665720060295,
    "f1_b3": 80.24647646716996,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.4: pesquisa7_contexto_10_False_False.pkl

```json
{
  "experimento": "pesquisa7_contexto_10_False_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7170,
    "score": 62.57410432586756,
    "f1_familias": 84.79576077484592,
    "f1_pares": 59.8855972540131,
    "f1_casos": 60.280578693555455,
    "casos_exatos": 4125,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 78.64374896261734,
    "recall_pares": 48.35252540726366,
    "f1_b3": 83.3294401122281,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.5: pesquisa7_contexto_10_True_False.pkl

```json
{
  "experimento": "pesquisa7_contexto_10_True_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7107,
    "score": 62.5861629371053,
    "f1_familias": 84.79576077484592,
    "f1_pares": 59.93430830004639,
    "f1_casos": 60.26572707920429,
    "casos_exatos": 4105,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 70.99683010403152,
    "recall_pares": 51.85449074166208,
    "f1_b3": 83.17292758585619,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.6: pesquisa7_contexto_10_True_True.pkl

```json
{
  "experimento": "pesquisa7_contexto_10_True_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8888,
    "score": 54.64789297106356,
    "f1_familias": 85.03728924027443,
    "f1_pares": 59.887805599283354,
    "f1_casos": 44.37808361464555,
    "casos_exatos": 3418,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.76422764227642,
    "precisao_pares": 70.99405405628328,
    "recall_pares": 51.78638784357484,
    "f1_b3": 78.85937183956679,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.7: pesquisa7_contexto_3_False_False.pkl

```json
{
  "experimento": "pesquisa7_contexto_3_False_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6783,
    "score": 64.73864982228065,
    "f1_familias": 84.79576077484592,
    "f1_pares": 64.89010860441438,
    "f1_casos": 60.60606060606061,
    "casos_exatos": 4030,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 67.39178171375104,
    "recall_pares": 62.567518596973855,
    "f1_b3": 83.6248742850581,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.8: pesquisa7_contexto_3_True_False.pkl

```json
{
  "experimento": "pesquisa7_contexto_3_True_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6755,
    "score": 64.34818791319596,
    "f1_familias": 84.79576077484592,
    "f1_pares": 63.678763407378035,
    "f1_casos": 60.79421294552031,
    "casos_exatos": 4034,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 65.00304542883181,
    "recall_pares": 62.40736224030997,
    "f1_b3": 83.49780744656441,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.9: pesquisa7_contexto_3_True_True.pkl

```json
{
  "experimento": "pesquisa7_contexto_3_True_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8532,
    "score": 56.19864211284675,
    "f1_familias": 84.94015026788513,
    "f1_pares": 63.63955814576758,
    "f1_casos": 44.49760765550239,
    "casos_exatos": 3348,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.68873403019745,
    "precisao_pares": 64.99510595008866,
    "recall_pares": 62.33939818605165,
    "f1_b3": 79.48650036663143,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.10: pesquisa7_hierarquia_0_False_False.pkl

```json
{
  "experimento": "pesquisa7_hierarquia_0_False_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6373,
    "score": 69.55925030649665,
    "f1_familias": 86.67283000765887,
    "f1_pares": 67.93323116680189,
    "f1_casos": 67.43734967802001,
    "casos_exatos": 4346,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 55.78592126977747,
    "recall_pares": 86.84322819307252,
    "f1_b3": 85.59151046677475,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.11: pesquisa7_hierarquia_0_True_False.pkl

```json
{
  "experimento": "pesquisa7_hierarquia_0_True_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6291,
    "score": 68.76985521094755,
    "f1_familias": 86.67283000765887,
    "f1_pares": 66.10323305532062,
    "f1_casos": 67.32255797610682,
    "casos_exatos": 4311,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 52.50701026810513,
    "recall_pares": 89.2010509552224,
    "f1_b3": 85.29443793692847,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.12: pesquisa7_hierarquia_10_False_False.pkl

```json
{
  "experimento": "pesquisa7_hierarquia_10_False_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6753,
    "score": 71.12079597476325,
    "f1_familias": 86.67283000765887,
    "f1_pares": 70.97288108598444,
    "f1_casos": 68.12872107920717,
    "casos_exatos": 4520,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 68.32629999661646,
    "recall_pares": 73.83275150055468,
    "f1_b3": 86.22680842892075,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.13: pesquisa7_hierarquia_10_True_False.pkl

```json
{
  "experimento": "pesquisa7_hierarquia_10_True_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6640,
    "score": 70.49093100546857,
    "f1_familias": 86.67283000765887,
    "f1_pares": 69.44586370284821,
    "f1_casos": 68.09060504712679,
    "casos_exatos": 4479,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 62.79503190416422,
    "recall_pares": 77.67240816753451,
    "f1_b3": 85.95508399317474,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.14: pesquisa7_hierarquia_3_False_False.pkl

```json
{
  "experimento": "pesquisa7_hierarquia_3_False_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6544,
    "score": 70.18442490774953,
    "f1_familias": 86.67283000765887,
    "f1_pares": 69.16421770773475,
    "f1_casos": 67.70290964777948,
    "casos_exatos": 4421,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 60.5527719406052,
    "recall_pares": 80.63107759935318,
    "f1_b3": 85.81380718696944,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.15: pesquisa7_hierarquia_3_True_False.pkl

```json
{
  "experimento": "pesquisa7_hierarquia_3_True_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6410,
    "score": 69.61287822625495,
    "f1_familias": 86.67283000765887,
    "f1_pares": 67.82507424660984,
    "f1_casos": 67.63113105369024,
    "casos_exatos": 4371,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 56.52670390489038,
    "recall_pares": 84.76827659171722,
    "f1_b3": 85.63747698760717,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.16: pesquisa7_lexico_0.05.pkl

```json
{
  "experimento": "pesquisa7_lexico_0.05.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6280,
    "score": 68.97337454772848,
    "f1_familias": 84.97086974994752,
    "f1_pares": 73.15852137009628,
    "f1_casos": 62.42575804939043,
    "casos_exatos": 3994,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.71777003484321,
    "precisao_pares": 63.30154413224001,
    "recall_pares": 86.65141544341397,
    "f1_b3": 85.22437274378672,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.17: pesquisa7_lexico_0.15.pkl

```json
{
  "experimento": "pesquisa7_lexico_0.15.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6233,
    "score": 68.92432221270495,
    "f1_familias": 84.89780349107458,
    "f1_pares": 73.15867405659354,
    "f1_casos": 62.34214448192015,
    "casos_exatos": 3974,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.64227642276423,
    "precisao_pares": 63.300908310844754,
    "recall_pares": 86.65303528808475,
    "f1_b3": 85.16784691736405,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.18: pesquisa7_lexico_0.25.pkl

```json
{
  "experimento": "pesquisa7_lexico_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6202,
    "score": 68.97302561481683,
    "f1_familias": 84.93801429556486,
    "f1_pares": 73.1590606204083,
    "f1_casos": 62.43119987419406,
    "casos_exatos": 3970,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.67131242740999,
    "precisao_pares": 63.30079559544568,
    "recall_pares": 86.65433116382137,
    "f1_b3": 85.16892011573711,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.19: pesquisa7_lexico_0.4.pkl

```json
{
  "experimento": "pesquisa7_lexico_0.4.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6116,
    "score": 69.08789066771489,
    "f1_familias": 84.98713173347589,
    "f1_pares": 73.1599291697371,
    "f1_casos": 62.6504116529449,
    "casos_exatos": 3957,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.7061556329849,
    "precisao_pares": 63.30003397548694,
    "recall_pares": 86.6581956503931,
    "f1_b3": 85.1830273203491,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.20: pesquisa7_lexico_0.6.pkl

```json
{
  "experimento": "pesquisa7_lexico_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6003,
    "score": 68.63701267903957,
    "f1_familias": 84.36494448412233,
    "f1_pares": 73.15885608459614,
    "f1_casos": 61.873951593577765,
    "casos_exatos": 3873,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.18350754936121,
    "precisao_pares": 63.29735322960616,
    "recall_pares": 86.66020888591248,
    "f1_b3": 84.92764543136622,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.21: pesquisa7_tempos_adj_0.25.pkl

```json
{
  "experimento": "pesquisa7_tempos_adj_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6362,
    "score": 68.77284723081704,
    "f1_familias": 84.70155187941282,
    "f1_pares": 73.2796373909291,
    "f1_casos": 61.98167417300823,
    "casos_exatos": 3991,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.49709639953542,
    "precisao_pares": 63.48602579779676,
    "recall_pares": 86.64600053408593,
    "f1_b3": 85.11908636622393,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.22: pesquisa7_tempos_adj_0.5.pkl

```json
{
  "experimento": "pesquisa7_tempos_adj_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6367,
    "score": 68.65751495249945,
    "f1_familias": 84.7063927996413,
    "f1_pares": 73.56351767625408,
    "f1_casos": 61.522937204067375,
    "casos_exatos": 3963,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.50871080139373,
    "precisao_pares": 63.60753159457546,
    "recall_pares": 87.21451973225356,
    "f1_b3": 85.12324548131004,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.23: pesquisa7_tempos_adj_0.75.pkl

```json
{
  "experimento": "pesquisa7_tempos_adj_0.75.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6392,
    "score": 68.7999561286614,
    "f1_familias": 84.62993357283264,
    "f1_pares": 73.91337067186028,
    "f1_casos": 61.54322900526805,
    "casos_exatos": 3972,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.45063879210221,
    "precisao_pares": 64.09904955230861,
    "recall_pares": 87.27642093931553,
    "f1_b3": 85.14858697092903,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.24: pesquisa7_tempos_adj_0.95.pkl

```json
{
  "experimento": "pesquisa7_tempos_adj_0.95.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6420,
    "score": 68.16549923663447,
    "f1_familias": 84.39593322766574,
    "f1_pares": 73.40258172962955,
    "f1_casos": 60.72974644403216,
    "casos_exatos": 3928,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.25319396051103,
    "precisao_pares": 63.6410023138106,
    "recall_pares": 86.7012603779977,
    "f1_b3": 84.72835009052832,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.25: pesquisa7_entradas_0.25.pkl

```json
{
  "experimento": "pesquisa7_entradas_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6357,
    "score": 68.87436373117255,
    "f1_familias": 84.84694831853677,
    "f1_pares": 73.15625878601179,
    "f1_casos": 62.25433076982832,
    "casos_exatos": 4007,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.64227642276423,
    "precisao_pares": 63.30133016851957,
    "recall_pares": 86.64546829940839,
    "f1_b3": 85.1276684181836,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.26: pesquisa7_entradas_0.5.pkl

```json
{
  "experimento": "pesquisa7_entradas_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6399,
    "score": 69.03956260212465,
    "f1_familias": 84.9564454576469,
    "f1_pares": 73.15615596165094,
    "f1_casos": 62.56291134339915,
    "casos_exatos": 4040,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.72938443670151,
    "precisao_pares": 63.302411365695534,
    "recall_pares": 86.64315423559299,
    "f1_b3": 85.19609309160397,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.27: pesquisa7_entradas_0.75.pkl

```json
{
  "experimento": "pesquisa7_entradas_0.75.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6460,
    "score": 69.48654448036818,
    "f1_familias": 85.03525188740589,
    "f1_pares": 73.15730161994442,
    "f1_casos": 63.44019728729963,
    "casos_exatos": 4116,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.79907084785134,
    "precisao_pares": 63.30492998241762,
    "recall_pares": 86.64165009411298,
    "f1_b3": 85.42107151372527,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.28: pesquisa7_entradas_1.0.pkl

```json
{
  "experimento": "pesquisa7_entradas_1.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6545,
    "score": 70.01566317455541,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15812803227826,
    "f1_casos": 64.48204578516193,
    "casos_exatos": 4211,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.307217756901096,
    "recall_pares": 86.63968313986989,
    "f1_b3": 85.64215977168226,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.29: pesquisa7_entradas_suaves_1.pkl

```json
{
  "experimento": "pesquisa7_entradas_suaves_1.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6470,
    "score": 69.5115775047562,
    "f1_familias": 84.9904779013769,
    "f1_pares": 73.1573831191352,
    "f1_casos": 63.49915293392885,
    "casos_exatos": 4123,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.78164924506387,
    "precisao_pares": 63.3049779117172,
    "recall_pares": 86.6417889379419,
    "f1_b3": 85.4600097887045,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.30: pesquisa7_entradas_suaves_3.pkl

```json
{
  "experimento": "pesquisa7_entradas_suaves_3.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6535,
    "score": 69.97291352352488,
    "f1_familias": 85.0514027608888,
    "f1_pares": 73.1583611700803,
    "f1_casos": 64.40885755880775,
    "casos_exatos": 4203,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.8513356562137,
    "precisao_pares": 63.30708506977058,
    "recall_pares": 86.64058562475789,
    "f1_b3": 85.65337273660872,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.31: pesquisa7_entradas_suaves_8.pkl

```json
{
  "experimento": "pesquisa7_entradas_suaves_8.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6554,
    "score": 70.05765228292694,
    "f1_familias": 85.06548352053812,
    "f1_pares": 73.15855554256157,
    "f1_casos": 64.57536342769701,
    "casos_exatos": 4220,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.85714285714286,
    "precisao_pares": 63.307524430138166,
    "recall_pares": 86.64030793710005,
    "f1_b3": 85.70134765107989,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.32: pesquisa7_nucleos_0.5_False.pkl

```json
{
  "experimento": "pesquisa7_nucleos_0.5_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6368,
    "score": 68.75586429382301,
    "f1_familias": 84.85990088141057,
    "f1_pares": 73.15605775884941,
    "f1_casos": 62.01490220428438,
    "casos_exatos": 3995,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.63066202090593,
    "precisao_pares": 63.300930332420975,
    "recall_pares": 86.64565342451363,
    "f1_b3": 85.09337885051995,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.33: pesquisa7_nucleos_0.5_True.pkl

```json
{
  "experimento": "pesquisa7_nucleos_0.5_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6568,
    "score": 70.13408201996918,
    "f1_familias": 85.25945360479156,
    "f1_pares": 73.15821997339643,
    "f1_casos": 64.68969734026291,
    "casos_exatos": 4232,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.9849012775842,
    "precisao_pares": 63.307441939661445,
    "recall_pares": 86.6395211554028,
    "f1_b3": 85.69474452781918,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.34: pesquisa7_nucleos_0.99_False.pkl

```json
{
  "experimento": "pesquisa7_nucleos_0.99_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6370,
    "score": 68.77735806701027,
    "f1_familias": 84.89001067604879,
    "f1_pares": 73.15609349183954,
    "f1_casos": 62.05183920533913,
    "casos_exatos": 3998,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.65389082462254,
    "precisao_pares": 63.3009838404689,
    "recall_pares": 86.64565342451363,
    "f1_b3": 85.10003053422056,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.35: pesquisa7_nucleos_0.99_True.pkl

```json
{
  "experimento": "pesquisa7_nucleos_0.99_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6587,
    "score": 70.25193819728713,
    "f1_familias": 85.22531269251358,
    "f1_pares": 73.15889853049924,
    "f1_casos": 64.93169503167213,
    "casos_exatos": 4254,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.95586527293844,
    "precisao_pares": 63.30840877182688,
    "recall_pares": 86.63961371795543,
    "f1_b3": 85.78628799268462,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.36: pesquisa7_nucleos_0.9_False.pkl

```json
{
  "experimento": "pesquisa7_nucleos_0.9_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6370,
    "score": 68.77735806701027,
    "f1_familias": 84.89001067604879,
    "f1_pares": 73.15609349183954,
    "f1_casos": 62.05183920533913,
    "casos_exatos": 3998,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.65389082462254,
    "precisao_pares": 63.3009838404689,
    "recall_pares": 86.64565342451363,
    "f1_b3": 85.10003053422056,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.37: pesquisa7_nucleos_0.9_True.pkl

```json
{
  "experimento": "pesquisa7_nucleos_0.9_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6587,
    "score": 70.25193819728713,
    "f1_familias": 85.22531269251358,
    "f1_pares": 73.15889853049924,
    "f1_casos": 64.93169503167213,
    "casos_exatos": 4254,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.95586527293844,
    "precisao_pares": 63.30840877182688,
    "recall_pares": 86.63961371795543,
    "f1_b3": 85.78628799268462,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.38: pesquisa7_prefixo8_False.pkl

```json
{
  "experimento": "pesquisa7_prefixo8_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6364,
    "score": 68.74850360167538,
    "f1_familias": 84.84636723261805,
    "f1_pares": 73.15578520845628,
    "f1_casos": 62.00310559006211,
    "casos_exatos": 3993,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.61904761904762,
    "precisao_pares": 63.30060866164935,
    "recall_pares": 86.64549144004654,
    "f1_b3": 85.0713246941498,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.39: pesquisa7_prefixo8_True.pkl

```json
{
  "experimento": "pesquisa7_prefixo8_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6603,
    "score": 70.33550982056784,
    "f1_familias": 85.23530534159293,
    "f1_pares": 73.15941692552667,
    "f1_casos": 65.09642503239576,
    "casos_exatos": 4270,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.9616724738676,
    "precisao_pares": 63.3093952173369,
    "recall_pares": 86.6392203271068,
    "f1_b3": 85.83734828479332,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.40: pesquisa7_novo_fluxo_0.5.pkl

```json
{
  "experimento": "pesquisa7_novo_fluxo_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6531,
    "score": 72.58041162018928,
    "f1_familias": 86.39486572528213,
    "f1_pares": 75.4842586603882,
    "f1_casos": 67.49444316701157,
    "casos_exatos": 4403,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.11149825783973,
    "precisao_pares": 65.25627207704146,
    "recall_pares": 89.51435205518949,
    "f1_b3": 86.86935707925485,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.41: pesquisa7_novo_fluxo_0.75.pkl

```json
{
  "experimento": "pesquisa7_novo_fluxo_0.75.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6421,
    "score": 72.86531352587694,
    "f1_familias": 86.67283000765887,
    "f1_pares": 75.4096623837369,
    "f1_casos": 68.06833114323258,
    "casos_exatos": 4403,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 64.67066928638668,
    "recall_pares": 90.42539897931273,
    "f1_b3": 87.17705761876988,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.42: pesquisa7_novo_fluxo_1.0.pkl

```json
{
  "experimento": "pesquisa7_novo_fluxo_1.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6340,
    "score": 72.04360204879231,
    "f1_familias": 86.21877127995738,
    "f1_pares": 74.60518349054153,
    "f1_casos": 67.15930304915993,
    "casos_exatos": 4317,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.01277584204414,
    "precisao_pares": 64.1789302850268,
    "recall_pares": 89.07613779046707,
    "f1_b3": 86.57253825985886,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.43: pesquisa7_consenso_0.0_0.0.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.0_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6545,
    "score": 70.01566317455541,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15812803227826,
    "f1_casos": 64.48204578516193,
    "casos_exatos": 4211,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.307217756901096,
    "recall_pares": 86.63968313986989,
    "f1_b3": 85.64215977168226,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.44: pesquisa7_consenso_0.0_0.6.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.0_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6731,
    "score": 69.85719351004772,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15767181809521,
    "f1_casos": 64.16547142749302,
    "casos_exatos": 4250,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.30895628618869,
    "recall_pares": 86.6351475747917,
    "f1_b3": 85.76012286589008,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.45: pesquisa7_consenso_0.3_0.0.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.3_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6545,
    "score": 70.01566317455541,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15812803227826,
    "f1_casos": 64.48204578516193,
    "casos_exatos": 4211,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.307217756901096,
    "recall_pares": 86.63968313986989,
    "f1_b3": 85.64215977168226,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.46: pesquisa7_consenso_0.3_0.6.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.3_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6731,
    "score": 69.85719351004772,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15767181809521,
    "f1_casos": 64.16547142749302,
    "casos_exatos": 4250,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.30895628618869,
    "recall_pares": 86.6351475747917,
    "f1_b3": 85.76012286589008,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.47: pesquisa7_consenso_0.5_0.0.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.5_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6545,
    "score": 70.01566317455541,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15812803227826,
    "f1_casos": 64.48204578516193,
    "casos_exatos": 4211,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.307217756901096,
    "recall_pares": 86.63968313986989,
    "f1_b3": 85.64215977168226,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.48: pesquisa7_consenso_0.5_0.6.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.5_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6731,
    "score": 69.85719351004772,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15767181809521,
    "f1_casos": 64.16547142749302,
    "casos_exatos": 4250,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.30895628618869,
    "recall_pares": 86.6351475747917,
    "f1_b3": 85.76012286589008,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.49: pesquisa7_consenso_0.6_0.0.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.6_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6558,
    "score": 70.06149414757105,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.2954860403114,
    "f1_casos": 64.46382132476671,
    "casos_exatos": 4214,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.78730498910182,
    "recall_pares": 86.13480069662577,
    "f1_b3": 85.65763775315648,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.50: pesquisa7_consenso_0.6_0.6.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.6_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6748,
    "score": 69.92380740430963,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.29506875729595,
    "f1_casos": 64.18878166465622,
    "casos_exatos": 4257,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.7891604691904,
    "recall_pares": 86.13026513154759,
    "f1_b3": 85.7866442604002,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.51: pesquisa7_consenso_0.75_0.0.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.75_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6583,
    "score": 70.17278297330915,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.63207091222966,
    "f1_casos": 64.4171310787083,
    "casos_exatos": 4219,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 64.76206067585385,
    "recall_pares": 85.3174039351118,
    "f1_b3": 85.68642195413925,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.52: pesquisa7_consenso_0.75_0.6.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.75_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6781,
    "score": 70.04652622660336,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.631781376215,
    "f1_casos": 64.16484921410844,
    "casos_exatos": 4266,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 64.76422627405506,
    "recall_pares": 85.31286837003361,
    "f1_b3": 85.83857211621861,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.53: pesquisa7_consenso_0.9_0.0.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.9_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6674,
    "score": 70.40356393142085,
    "f1_familias": 85.11389069063138,
    "f1_pares": 74.42338635983663,
    "f1_casos": 64.24564063684609,
    "casos_exatos": 4237,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 68.2384500078046,
    "recall_pares": 81.8412404122551,
    "f1_b3": 85.75789559178384,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.54: pesquisa7_consenso_0.9_0.6.pkl

```json
{
  "experimento": "pesquisa7_consenso_0.9_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6891,
    "score": 70.33114908822948,
    "f1_familias": 85.11389069063138,
    "f1_pares": 74.42334649380233,
    "f1_casos": 64.10084284329082,
    "casos_exatos": 4297,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 68.24156862805636,
    "recall_pares": 81.8366585659006,
    "f1_b3": 85.9549632047571,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.55: pesquisa7_consenso_1.0_0.0.pkl

```json
{
  "experimento": "pesquisa7_consenso_1.0_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6674,
    "score": 70.40356393142085,
    "f1_familias": 85.11389069063138,
    "f1_pares": 74.42338635983663,
    "f1_casos": 64.24564063684609,
    "casos_exatos": 4237,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 68.2384500078046,
    "recall_pares": 81.8412404122551,
    "f1_b3": 85.75789559178384,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.56: pesquisa7_consenso_1.0_0.6.pkl

```json
{
  "experimento": "pesquisa7_consenso_1.0_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6891,
    "score": 70.33114908822948,
    "f1_familias": 85.11389069063138,
    "f1_pares": 74.42334649380233,
    "f1_casos": 64.10084284329082,
    "casos_exatos": 4297,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 68.24156862805636,
    "recall_pares": 81.8366585659006,
    "f1_b3": 85.9549632047571,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.57: pesquisa7_fronteira_False_0.25.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6252,
    "score": 67.28032541703749,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.1453570581554,
    "f1_casos": 59.08521303258146,
    "casos_exatos": 3772,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.286649103597206,
    "recall_pares": 86.64239059453391,
    "f1_b3": 84.03492152652093,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.58: pesquisa7_fronteira_False_0.4.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.4.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7350,
    "score": 67.50182826856101,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.14700506300764,
    "f1_casos": 59.52690033174672,
    "casos_exatos": 4127,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.3050911671602,
    "recall_pares": 86.61246974940077,
    "f1_b3": 84.83425983614772,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.59: pesquisa7_fronteira_False_0.5.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7987,
    "score": 65.62647237003205,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.14028768717087,
    "f1_casos": 55.781562435358204,
    "casos_exatos": 4045,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.30625507854735,
    "recall_pares": 86.59145804995694,
    "f1_b3": 84.12146856627308,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.60: pesquisa7_fronteira_False_0.6.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8489,
    "score": 64.47726506997489,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.1331761633317,
    "f1_casos": 53.488837054315226,
    "casos_exatos": 4013,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.30613897012264,
    "recall_pares": 86.57174222624973,
    "f1_b3": 83.41663271842685,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.61: pesquisa7_fronteira_False_0.67.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.67.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8828,
    "score": 63.499484922880086,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.12719651390583,
    "f1_casos": 51.53806047966632,
    "casos_exatos": 3954,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.30471409333547,
    "recall_pares": 86.55764957761393,
    "f1_b3": 82.72071331828874,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.62: pesquisa7_fronteira_False_0.75.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.75.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 9277,
    "score": 62.02866026872438,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.11794570889793,
    "f1_casos": 48.60381181536123,
    "casos_exatos": 3838,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.301965089858484,
    "recall_pares": 86.53686928455163,
    "f1_b3": 81.59034140593138,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.63: pesquisa7_fronteira_False_0.85.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.85.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 9948,
    "score": 60.24264422277314,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.1030056401893,
    "f1_casos": 45.04373177842566,
    "casos_exatos": 3708,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.29731581342007,
    "recall_pares": 86.50370875007694,
    "f1_b3": 79.892088221412,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.64: pesquisa7_fronteira_False_0.95.pkl

```json
{
  "experimento": "pesquisa7_fronteira_False_0.95.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 11354,
    "score": 56.39556823480933,
    "f1_familias": 84.79576077484592,
    "f1_pares": 73.06362337036836,
    "f1_casos": 37.38108561835478,
    "casos_exatos": 3340,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.57259001161441,
    "precisao_pares": 63.27980638670407,
    "recall_pares": 86.4261413309847,
    "f1_b3": 75.19837972506106,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.65: pesquisa7_fronteira_True_0.25.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6408,
    "score": 69.31804647748125,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15174101408148,
    "f1_casos": 63.09192200557103,
    "casos_exatos": 4077,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.295577951154335,
    "recall_pares": 86.64357076707975,
    "f1_b3": 85.08461452111962,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.66: pesquisa7_fronteira_True_0.4.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.4.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7109,
    "score": 69.68513726279674,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15455397057254,
    "f1_casos": 63.82385321100917,
    "casos_exatos": 4348,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.3100825551175,
    "recall_pares": 86.62429461549748,
    "f1_b3": 85.75737887786782,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.67: pesquisa7_fronteira_True_0.5.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7562,
    "score": 68.87702727563635,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.15091892884958,
    "f1_casos": 62.21054127006677,
    "casos_exatos": 4379,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.31177047310185,
    "recall_pares": 86.61094246728261,
    "f1_b3": 85.51576597317879,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.68: pesquisa7_fronteira_True_0.6.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.6.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8061,
    "score": 67.2885538516872,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.14514835636803,
    "f1_casos": 59.03821088015367,
    "casos_exatos": 4303,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.31232601881302,
    "recall_pares": 86.59372583249603,
    "f1_b3": 84.87860820054301,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.69: pesquisa7_fronteira_True_0.67.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.67.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8388,
    "score": 65.99421067857008,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.13875021270994,
    "f1_casos": 56.454643048845945,
    "casos_exatos": 4207,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.31047079302438,
    "recall_pares": 86.57926293364977,
    "f1_b3": 84.16316298523516,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.70: pesquisa7_fronteira_True_0.75.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.75.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8767,
    "score": 64.49918475617403,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.13051781163968,
    "f1_casos": 53.47117712491003,
    "casos_exatos": 4086,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.30794682372454,
    "recall_pares": 86.56091240759365,
    "f1_b3": 83.22304758487596,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.71: pesquisa7_fronteira_True_0.85.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.85.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 9445,
    "score": 62.07881454929549,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.114102827202,
    "f1_casos": 48.64356869870309,
    "casos_exatos": 3882,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.302259933395035,
    "recall_pares": 86.52555351249433,
    "f1_b3": 81.35501703045998,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.72: pesquisa7_fronteira_True_0.95.pkl

```json
{
  "experimento": "pesquisa7_fronteira_True_0.95.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 10583,
    "score": 58.55341640080489,
    "f1_familias": 85.11389069063138,
    "f1_pares": 73.08448233017312,
    "f1_casos": 41.61646879934499,
    "casos_exatos": 3558,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.86295005807202,
    "precisao_pares": 63.289293453029124,
    "recall_pares": 86.46682257285946,
    "f1_b3": 77.85438320923994,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.73: pesquisa7_papeis_em_0.pkl

```json
{
  "experimento": "pesquisa7_papeis_em_0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6461,
    "score": 69.9603647638809,
    "f1_familias": 84.86052181067873,
    "f1_pares": 73.1586950734308,
    "f1_casos": 64.42166910688141,
    "casos_exatos": 4180,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.61324041811847,
    "precisao_pares": 63.30622615257651,
    "recall_pares": 86.64313109495482,
    "f1_b3": 85.59535636334469,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.74: pesquisa7_papeis_em_1.pkl

```json
{
  "experimento": "pesquisa7_papeis_em_1.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6099,
    "score": 69.35133086377354,
    "f1_familias": 84.67026809500315,
    "f1_pares": 73.15804511388362,
    "f1_casos": 63.24217201743956,
    "casos_exatos": 3989,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.70034843205575,
    "precisao_pares": 63.298435452330054,
    "recall_pares": 86.65590472721584,
    "f1_b3": 85.11202465473536,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.75: pesquisa7_papeis_em_3.pkl

```json
{
  "experimento": "pesquisa7_papeis_em_3.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 5875,
    "score": 68.0765861136936,
    "f1_familias": 83.01732478346875,
    "f1_pares": 73.15192708328246,
    "f1_casos": 61.02816560406747,
    "casos_exatos": 3781,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 86.45180023228804,
    "precisao_pares": 63.288152630803324,
    "recall_pares": 86.65801052528786,
    "f1_b3": 84.24517086709085,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.76: pesquisa7_papeis_em_8.pkl

```json
{
  "experimento": "pesquisa7_papeis_em_8.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 5816,
    "score": 67.69592353344811,
    "f1_familias": 82.2997361182433,
    "f1_pares": 73.14995427211005,
    "f1_casos": 60.41193642555952,
    "casos_exatos": 3725,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 85.89430894308943,
    "precisao_pares": 63.28510065018135,
    "recall_pares": 86.6581956503931,
    "f1_b3": 83.97469567801002,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.77: pesquisa7_entrada_unica_1.0_False.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_1.0_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6418,
    "score": 72.94193973110185,
    "f1_familias": 86.74186778035582,
    "f1_pares": 75.40960195897617,
    "f1_casos": 68.2078243389516,
    "casos_exatos": 4411,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.41927990708479,
    "precisao_pares": 64.67060407829433,
    "recall_pares": 90.42535269803642,
    "f1_b3": 87.17932688154762,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.78: pesquisa7_entrada_unica_1.0_True.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_1.0_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6419,
    "score": 72.9109854368984,
    "f1_familias": 86.6906193200913,
    "f1_pares": 75.40960195897617,
    "f1_casos": 68.1561654425976,
    "casos_exatos": 4408,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.37862950058071,
    "precisao_pares": 64.67060407829433,
    "recall_pares": 90.42535269803642,
    "f1_b3": 87.17372973623782,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.79: pesquisa7_entrada_unica_2.0_False.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_2.0_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6438,
    "score": 73.25139611527132,
    "f1_familias": 86.80979616349616,
    "f1_pares": 75.41013882334256,
    "f1_casos": 68.81272193916936,
    "casos_exatos": 4457,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.47154471544715,
    "precisao_pares": 64.67121622482662,
    "recall_pares": 90.42569980760874,
    "f1_b3": 87.27999431091514,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.80: pesquisa7_entrada_unica_2.0_True.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_2.0_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6439,
    "score": 73.20404827167417,
    "f1_familias": 86.82647076516132,
    "f1_pares": 75.41002556605027,
    "f1_casos": 68.71478193747588,
    "casos_exatos": 4451,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.48315911730546,
    "precisao_pares": 64.67113248472198,
    "recall_pares": 90.42553782314165,
    "f1_b3": 87.25999966729177,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.81: pesquisa7_entrada_unica_4.0_False.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_4.0_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6446,
    "score": 73.32276221068332,
    "f1_familias": 86.8099933287292,
    "f1_pares": 75.41014704948667,
    "f1_casos": 68.95540811603148,
    "casos_exatos": 4469,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.465737514518,
    "precisao_pares": 64.67133485151399,
    "recall_pares": 90.42549154186536,
    "f1_b3": 87.29589841178087,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.82: pesquisa7_entrada_unica_4.0_True.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_4.0_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6444,
    "score": 73.26534963606767,
    "f1_familias": 86.87747267376233,
    "f1_pares": 75.41005530444463,
    "f1_casos": 68.82716049382717,
    "casos_exatos": 4460,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.51800232288038,
    "precisao_pares": 64.67124724567807,
    "recall_pares": 90.42539897931273,
    "f1_b3": 87.27751352018146,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.83: pesquisa7_entrada_unica_8.0_False.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_8.0_False.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6444,
    "score": 73.3245479678168,
    "f1_familias": 86.77469265356,
    "f1_pares": 75.41013502775692,
    "f1_casos": 68.96604938271605,
    "casos_exatos": 4469,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.44250871080139,
    "precisao_pares": 64.67132900464209,
    "recall_pares": 90.42546840122719,
    "f1_b3": 87.29628831619115,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.84: pesquisa7_entrada_unica_8.0_True.pkl

```json
{
  "experimento": "pesquisa7_entrada_unica_8.0_True.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6442,
    "score": 73.2685734903892,
    "f1_familias": 86.85664373015075,
    "f1_pares": 75.41004328270834,
    "f1_casos": 68.83778360858157,
    "casos_exatos": 4460,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.50638792102207,
    "precisao_pares": 64.67124139879361,
    "recall_pares": 90.42537583867458,
    "f1_b3": 87.27790336715906,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.85: pesquisa7_evidencia_0.0.pkl

```json
{
  "experimento": "pesquisa7_evidencia_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6892,
    "score": 69.82686200687483,
    "f1_familias": 86.67283000765887,
    "f1_pares": 69.27350002123895,
    "f1_casos": 66.90035799522673,
    "casos_exatos": 4485,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 93.27101390572251,
    "recall_pares": 55.09755861639348,
    "f1_b3": 86.0610659115056,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.86: pesquisa7_evidencia_0.7.pkl

```json
{
  "experimento": "pesquisa7_evidencia_0.7.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6767,
    "score": 70.87140871782483,
    "f1_familias": 86.67283000765887,
    "f1_pares": 71.32376005038283,
    "f1_casos": 67.34924339381163,
    "casos_exatos": 4473,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 86.51787211068974,
    "recall_pares": 60.66915320537178,
    "f1_b3": 86.27147091582755,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.87: pesquisa7_evidencia_1.4.pkl

```json
{
  "experimento": "pesquisa7_evidencia_1.4.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6659,
    "score": 71.1048831933766,
    "f1_familias": 86.67283000765887,
    "f1_pares": 72.0712300830448,
    "f1_casos": 67.21821631878558,
    "casos_exatos": 4428,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 80.74621419082321,
    "recall_pares": 65.0794117279531,
    "f1_b3": 86.31006366029517,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.88: pesquisa7_evidencia_2.0.pkl

```json
{
  "experimento": "pesquisa7_evidencia_2.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6623,
    "score": 71.76417389928653,
    "f1_familias": 86.67283000765887,
    "f1_pares": 73.43215798684501,
    "f1_casos": 67.44805540756526,
    "casos_exatos": 4431,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 79.10681915031466,
    "recall_pares": 68.517138650836,
    "f1_b3": 86.53625173856003,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.89: pesquisa7_evidencia_3.0.pkl

```json
{
  "experimento": "pesquisa7_evidencia_3.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6566,
    "score": 72.80039274637969,
    "f1_familias": 86.67283000765887,
    "f1_pares": 75.5789140980201,
    "f1_casos": 67.8030882128115,
    "casos_exatos": 4435,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 76.76957790883331,
    "recall_pares": 74.4246196026197,
    "f1_b3": 86.91860502502648,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.90: pesquisa7_evidencia_5.0.pkl

```json
{
  "experimento": "pesquisa7_evidencia_5.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6496,
    "score": 73.41299908945183,
    "f1_familias": 86.67283000765887,
    "f1_pares": 76.92346636681171,
    "f1_casos": 67.95265908392253,
    "casos_exatos": 4421,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 72.49961499456897,
    "recall_pares": 81.92227892707042,
    "f1_b3": 87.18945017816475,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.91: pesquisa7_restauracao_combined_0.5.pkl

```json
{
  "experimento": "pesquisa7_restauracao_combined_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6725,
    "score": 74.52012475991995,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.15895282323066,
    "f1_casos": 68.37852125972358,
    "casos_exatos": 4527,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 82.30224970512991,
    "recall_pares": 76.24692171660956,
    "f1_b3": 87.58953139582763,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.92: pesquisa7_restauracao_combined_0.7.pkl

```json
{
  "experimento": "pesquisa7_restauracao_combined_0.7.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6678,
    "score": 74.60678160066988,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.18480834605377,
    "f1_casos": 68.53115052296498,
    "casos_exatos": 4521,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 79.01049461446023,
    "recall_pares": 79.35989292363914,
    "f1_b3": 87.63460584273098,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.93: pesquisa7_restauracao_combined_0.8.pkl

```json
{
  "experimento": "pesquisa7_restauracao_combined_0.8.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6656,
    "score": 74.53245416772731,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.04570957546612,
    "f1_casos": 68.49377467354995,
    "casos_exatos": 4511,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 77.80138766680757,
    "recall_pares": 80.33048070973263,
    "f1_b3": 87.62195568987144,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.94: pesquisa7_restauracao_combined_0.9.pkl

```json
{
  "experimento": "pesquisa7_restauracao_combined_0.9.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6626,
    "score": 74.63704708210582,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.24490936633872,
    "f1_casos": 68.54360066960889,
    "casos_exatos": 4504,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 76.31183212731445,
    "recall_pares": 82.41246706508674,
    "f1_b3": 87.68194344782935,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.95: pesquisa7_restauracao_combined_0.98.pkl

```json
{
  "experimento": "pesquisa7_restauracao_combined_0.98.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6603,
    "score": 74.79055572739836,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.57375083861027,
    "f1_casos": 68.58754478237671,
    "casos_exatos": 4499,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.97768531016958,
    "recall_pares": 84.77008156149324,
    "f1_b3": 87.75648845563786,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.96: pesquisa7_restauracao_posterior_0.5.pkl

```json
{
  "experimento": "pesquisa7_restauracao_posterior_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6725,
    "score": 74.52012475991995,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.15895282323066,
    "f1_casos": 68.37852125972358,
    "casos_exatos": 4527,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 82.30224970512991,
    "recall_pares": 76.24692171660956,
    "f1_b3": 87.58953139582763,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.97: pesquisa7_restauracao_posterior_0.7.pkl

```json
{
  "experimento": "pesquisa7_restauracao_posterior_0.7.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6678,
    "score": 74.60678160066988,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.18480834605377,
    "f1_casos": 68.53115052296498,
    "casos_exatos": 4521,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 79.01049461446023,
    "recall_pares": 79.35989292363914,
    "f1_b3": 87.63460584273098,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.98: pesquisa7_restauracao_posterior_0.8.pkl

```json
{
  "experimento": "pesquisa7_restauracao_posterior_0.8.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6656,
    "score": 74.53245416772731,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.04570957546612,
    "f1_casos": 68.49377467354995,
    "casos_exatos": 4511,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 77.80138766680757,
    "recall_pares": 80.33048070973263,
    "f1_b3": 87.62195568987144,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.99: pesquisa7_restauracao_posterior_0.9.pkl

```json
{
  "experimento": "pesquisa7_restauracao_posterior_0.9.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6626,
    "score": 74.63704708210582,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.24490936633872,
    "f1_casos": 68.54360066960889,
    "casos_exatos": 4504,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 76.31183212731445,
    "recall_pares": 82.41246706508674,
    "f1_b3": 87.68194344782935,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.100: pesquisa7_restauracao_posterior_0.98.pkl

```json
{
  "experimento": "pesquisa7_restauracao_posterior_0.98.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6603,
    "score": 74.79055572739836,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.57375083861027,
    "f1_casos": 68.58754478237671,
    "casos_exatos": 4499,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.97768531016958,
    "recall_pares": 84.77008156149324,
    "f1_b3": 87.75648845563786,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.101: pesquisa7_blocos_0.5.pkl

```json
{
  "experimento": "pesquisa7_blocos_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6434,
    "score": 73.24241833926493,
    "f1_familias": 86.74161784983258,
    "f1_pares": 75.20442516948795,
    "f1_casos": 68.97297297297297,
    "casos_exatos": 4466,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.39024390243902,
    "precisao_pares": 64.66538168989712,
    "recall_pares": 89.84762352588349,
    "f1_b3": 87.38447046033774,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.102: pesquisa7_blocos_0.9.pkl

```json
{
  "experimento": "pesquisa7_blocos_0.9.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6452,
    "score": 73.52547293760163,
    "f1_familias": 86.68627347019984,
    "f1_pares": 75.33227437127215,
    "f1_casos": 69.44787168414558,
    "casos_exatos": 4503,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.35540069686411,
    "precisao_pares": 65.09082619538879,
    "recall_pares": 89.398278614209,
    "f1_b3": 87.61055188455829,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.103: pesquisa7_blocos_0.99.pkl

```json
{
  "experimento": "pesquisa7_blocos_0.99.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6440,
    "score": 73.36444851913318,
    "f1_familias": 86.78380839255989,
    "f1_pares": 74.97929392954784,
    "f1_casos": 69.38870021611609,
    "casos_exatos": 4495,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.4308943089431,
    "precisao_pares": 64.56519853525008,
    "recall_pares": 89.39897283335362,
    "f1_b3": 87.52402568877051,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.104: pesquisa7_refinamento_1.0.pkl

```json
{
  "experimento": "pesquisa7_refinamento_1.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6437,
    "score": 73.0943518852869,
    "f1_familias": 86.60698997883351,
    "f1_pares": 74.92648534133755,
    "f1_casos": 68.92611750173705,
    "casos_exatos": 4464,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.29732868757259,
    "precisao_pares": 64.48837965928313,
    "recall_pares": 89.39617281613698,
    "f1_b3": 87.11889176920225,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.105: pesquisa7_refinamento_1.0.pkl

```json
{
  "experimento": "pesquisa7_refinamento_1.0.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6630,
    "score": 74.8933138718471,
    "f1_familias": 86.60698997883351,
    "f1_pares": 78.768057799545,
    "f1_casos": 69.4507835082915,
    "casos_exatos": 4565,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.29732868757259,
    "precisao_pares": 75.38049792294167,
    "recall_pares": 82.47441455342502,
    "f1_b3": 87.63974031127766,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.106: pesquisa7_refinamento_4.0.pkl

```json
{
  "experimento": "pesquisa7_refinamento_4.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6416,
    "score": 73.26459238972787,
    "f1_familias": 86.66332352844928,
    "f1_pares": 75.21742553297443,
    "f1_casos": 69.02257964738632,
    "casos_exatos": 4463,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.34959349593495,
    "precisao_pares": 64.78558890707306,
    "recall_pares": 89.6535198530477,
    "f1_b3": 87.17229661958888,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.107: pesquisa7_refinamento_4.0.pkl

```json
{
  "experimento": "pesquisa7_refinamento_4.0.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6616,
    "score": 74.97277014581033,
    "f1_familias": 86.66332352844928,
    "f1_pares": 78.93621327619965,
    "f1_casos": 69.46390496497106,
    "casos_exatos": 4561,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.34959349593495,
    "precisao_pares": 76.37439823013446,
    "recall_pares": 81.67585427136841,
    "f1_b3": 87.6641490421412,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.108: pesquisa7_cortes_component_0.25.pkl

```json
{
  "experimento": "pesquisa7_cortes_component_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6721,
    "score": 75.00634416320582,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.57432813462593,
    "f1_casos": 69.01865981717911,
    "casos_exatos": 4568,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98033978903294,
    "recall_pares": 84.76799890405938,
    "f1_b3": 87.90554225590444,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.109: pesquisa7_cortes_component_0.4.pkl

```json
{
  "experimento": "pesquisa7_cortes_component_0.4.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7080,
    "score": 74.72651754358867,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.57144616876629,
    "f1_casos": 68.46131215063254,
    "casos_exatos": 4654,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98458400142817,
    "recall_pares": 84.75603519413376,
    "f1_b3": 87.84807234520906,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.110: pesquisa7_cortes_component_0.5.pkl

```json
{
  "experimento": "pesquisa7_cortes_component_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7442,
    "score": 73.60089800253178,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.56788189472852,
    "f1_casos": 66.21292448774896,
    "casos_exatos": 4621,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98743773642549,
    "recall_pares": 84.74430289058968,
    "f1_b3": 87.45103694927508,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.111: pesquisa7_cortes_component_0.67.pkl

```json
{
  "experimento": "pesquisa7_cortes_component_0.67.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8293,
    "score": 70.28777706647372,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.5526194576047,
    "f1_casos": 59.598892565331894,
    "casos_exatos": 4413,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98807253618749,
    "recall_pares": 84.70887457357588,
    "f1_b3": 85.81167689832644,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.112: pesquisa7_cortes_component_0.8.pkl

```json
{
  "experimento": "pesquisa7_cortes_component_0.8.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 9011,
    "score": 67.46689941093322,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.53591228193923,
    "f1_casos": 53.97050299478328,
    "casos_exatos": 4190,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98718626851638,
    "recall_pares": 84.67212724018732,
    "f1_b3": 83.96259639552531,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.113: pesquisa7_cortes_component_0.9.pkl

```json
{
  "experimento": "pesquisa7_cortes_component_0.9.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 9956,
    "score": 64.26370832907308,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.51134015418226,
    "f1_casos": 47.58377853326858,
    "casos_exatos": 3919,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98184357713721,
    "recall_pares": 84.62325421240607,
    "f1_b3": 81.16984643696811,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.114: pesquisa7_cortes_family_0.25.pkl

```json
{
  "experimento": "pesquisa7_cortes_family_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6669,
    "score": 74.92236254324702,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.57399009624834,
    "f1_casos": 68.85096700796359,
    "casos_exatos": 4539,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.97921448563066,
    "recall_pares": 84.76866998256584,
    "f1_b3": 87.8360762355223,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.115: pesquisa7_cortes_family_0.4.pkl

```json
{
  "experimento": "pesquisa7_cortes_family_0.4.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6989,
    "score": 74.77199854614481,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.5713038578938,
    "f1_casos": 68.5523880044428,
    "casos_exatos": 4629,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98226655986001,
    "recall_pares": 84.75867322688332,
    "f1_b3": 87.81772235460737,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.116: pesquisa7_cortes_family_0.5.pkl

```json
{
  "experimento": "pesquisa7_cortes_family_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 7351,
    "score": 73.76044098269827,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.56782680743063,
    "f1_casos": 66.53205451792024,
    "casos_exatos": 4613,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.9858360826792,
    "recall_pares": 84.74622356355646,
    "f1_b3": 87.45227128014605,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.117: pesquisa7_cortes_family_0.67.pkl

```json
{
  "experimento": "pesquisa7_cortes_family_0.67.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8215,
    "score": 70.24901922603517,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.55341734003831,
    "f1_casos": 59.52073857850791,
    "casos_exatos": 4384,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98651655058849,
    "recall_pares": 84.71266963823315,
    "f1_b3": 85.85274783293615,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.118: pesquisa7_cortes_family_0.8.pkl

```json
{
  "experimento": "pesquisa7_cortes_family_0.8.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 8914,
    "score": 67.42943698335688,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.53662280482487,
    "f1_casos": 53.8950097213221,
    "casos_exatos": 4158,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98509195039092,
    "recall_pares": 84.67640825824581,
    "f1_b3": 83.99895214640357,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.119: pesquisa7_cortes_family_0.9.pkl

```json
{
  "experimento": "pesquisa7_cortes_family_0.9.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 9858,
    "score": 64.23561102670324,
    "f1_familias": 86.67283000765887,
    "f1_pares": 79.51261192999544,
    "f1_casos": 47.52656650787834,
    "casos_exatos": 3891,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.36120789779326,
    "precisao_pares": 74.98039950564109,
    "recall_pares": 84.62797490258949,
    "f1_b3": 81.28498226309524,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.120: pesquisa7_ancora_emission_0.98_0.0.pkl

```json
{
  "experimento": "pesquisa7_ancora_emission_0.98_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6446,
    "score": 73.43119700846738,
    "f1_familias": 86.81289014748647,
    "f1_pares": 74.69686533995181,
    "f1_casos": 69.742323715476,
    "casos_exatos": 4520,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.44250871080139,
    "precisao_pares": 63.983333630381274,
    "recall_pares": 89.71977150008262,
    "f1_b3": 87.57961020050503,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.121: pesquisa7_ancora_emission_0.98_0.0.pkl

```json
{
  "experimento": "pesquisa7_ancora_emission_0.98_0.0.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6643,
    "score": 75.3020912296462,
    "f1_familias": 86.81289014748647,
    "f1_pares": 78.66538801311587,
    "f1_casos": 70.30929401930238,
    "casos_exatos": 4626,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.44250871080139,
    "precisao_pares": 74.68473851771415,
    "recall_pares": 83.09425968701824,
    "f1_b3": 88.1386741884771,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.122: pesquisa7_ancora_posterior_0.98_0.0.pkl

```json
{
  "experimento": "pesquisa7_ancora_posterior_0.98_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6451,
    "score": 73.64232504406098,
    "f1_familias": 86.89517428797832,
    "f1_pares": 75.08349200800441,
    "f1_casos": 69.83882162412277,
    "casos_exatos": 4528,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.51219512195122,
    "precisao_pares": 64.45323470226135,
    "recall_pares": 89.91278756292517,
    "f1_b3": 87.65105659139697,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.123: pesquisa7_ancora_posterior_0.98_0.0.pkl

```json
{
  "experimento": "pesquisa7_ancora_posterior_0.98_0.0.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6645,
    "score": 75.42810414664649,
    "f1_familias": 86.89517428797832,
    "f1_pares": 78.91621833325854,
    "f1_casos": 70.3441987690905,
    "casos_exatos": 4629,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.51219512195122,
    "precisao_pares": 75.03725062529512,
    "recall_pares": 83.21808524178033,
    "f1_b3": 88.17825495485836,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.124: pesquisa7_ancora_posterior_0.98_0.01.pkl

```json
{
  "experimento": "pesquisa7_ancora_posterior_0.98_0.01.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6454,
    "score": 73.6361088192655,
    "f1_familias": 86.89157721918453,
    "f1_pares": 75.06976787443934,
    "f1_casos": 69.83808789514264,
    "casos_exatos": 4529,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.50638792102207,
    "precisao_pares": 64.5656895113957,
    "recall_pares": 89.65569507303417,
    "f1_b3": 87.67071971941084,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.125: pesquisa7_ancora_posterior_0.98_0.01.pkl

```json
{
  "experimento": "pesquisa7_ancora_posterior_0.98_0.01.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6648,
    "score": 75.40620587245138,
    "f1_familias": 86.89157721918453,
    "f1_pares": 78.8634195255271,
    "f1_casos": 70.34336068064418,
    "casos_exatos": 4630,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.50638792102207,
    "precisao_pares": 75.19428555238296,
    "recall_pares": 82.90899573795727,
    "f1_b3": 88.193410757305,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.126: pesquisa7_ancora_posterior_0.999_0.0.pkl

```json
{
  "experimento": "pesquisa7_ancora_posterior_0.999_0.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6439,
    "score": 73.52622186466047,
    "f1_familias": 86.86312113685986,
    "f1_pares": 74.73968174910738,
    "f1_casos": 69.88807410266307,
    "casos_exatos": 4527,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.4773519163763,
    "precisao_pares": 63.88296799070227,
    "recall_pares": 90.04205116765345,
    "f1_b3": 87.63251150842137,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.127: pesquisa7_ancora_posterior_0.999_0.0.pkl

```json
{
  "experimento": "pesquisa7_ancora_posterior_0.999_0.0.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6636,
    "score": 75.4333500952729,
    "f1_familias": 86.86312113685986,
    "f1_pares": 78.78213266686267,
    "f1_casos": 70.4683698296837,
    "casos_exatos": 4634,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.4773519163763,
    "precisao_pares": 74.54624984407566,
    "recall_pares": 83.52840119942556,
    "f1_b3": 88.20762733934389,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.128: pesquisa7_aliases_0.25.pkl

```json
{
  "experimento": "pesquisa7_aliases_0.25.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6394,
    "score": 73.11984903295962,
    "f1_familias": 86.59680717530861,
    "f1_pares": 74.76389871266174,
    "f1_casos": 69.10921766072812,
    "casos_exatos": 4461,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.38443670150987,
    "precisao_pares": 64.37851103351291,
    "recall_pares": 89.14447209493585,
    "f1_b3": 87.22292518558585,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.129: pesquisa7_aliases_0.25.pkl

```json
{
  "experimento": "pesquisa7_aliases_0.25.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6583,
    "score": 74.76811301336738,
    "f1_familias": 86.59680717530861,
    "f1_pares": 78.22245107320455,
    "f1_casos": 69.6389037331094,
    "casos_exatos": 4561,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.38443670150987,
    "precisao_pares": 74.53406424910602,
    "recall_pares": 82.29488948262625,
    "f1_b3": 87.71907357332431,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.130: pesquisa7_aliases_0.5.pkl

```json
{
  "experimento": "pesquisa7_aliases_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6413,
    "score": 72.87493847301911,
    "f1_familias": 86.35996353077702,
    "f1_pares": 74.76318405691133,
    "f1_casos": 68.66733699435378,
    "casos_exatos": 4439,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.23344947735191,
    "precisao_pares": 64.37817536920392,
    "recall_pares": 89.14308365664661,
    "f1_b3": 87.1429564973278,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.131: pesquisa7_aliases_0.5.pkl

```json
{
  "experimento": "pesquisa7_aliases_0.5.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6602,
    "score": 74.46331505067225,
    "f1_familias": 86.35996353077702,
    "f1_pares": 78.1031343716735,
    "f1_casos": 69.17212989785028,
    "casos_exatos": 4537,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.23344947735191,
    "precisao_pares": 74.67336530673803,
    "recall_pares": 81.86313145594879,
    "f1_b3": 87.59214957143668,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.132: pesquisa7_aliases_1.0.pkl

```json
{
  "experimento": "pesquisa7_aliases_1.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6644,
    "score": 71.66253170219662,
    "f1_familias": 84.91964705093456,
    "f1_pares": 74.75772448363938,
    "f1_casos": 66.53495440729483,
    "casos_exatos": 4378,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 88.17653890824623,
    "precisao_pares": 64.37741762786779,
    "recall_pares": 89.12901414864898,
    "f1_b3": 86.66789874360711,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.133: pesquisa7_aliases_1.0.pkl

```json
{
  "experimento": "pesquisa7_aliases_1.0.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6840,
    "score": 73.34128929857596,
    "f1_familias": 84.91964705093456,
    "f1_pares": 78.26586913569787,
    "f1_casos": 67.08595387840671,
    "casos_exatos": 4480,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 88.17653890824623,
    "precisao_pares": 75.13839315750164,
    "recall_pares": 81.66500131207418,
    "f1_b3": 87.11321797636599,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.134: pesquisa7_particao_0.2.pkl

```json
{
  "experimento": "pesquisa7_particao_0.2.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6685,
    "score": 74.96479055217742,
    "f1_familias": 86.68627347019984,
    "f1_pares": 78.87198895373139,
    "f1_casos": 69.49473524732974,
    "casos_exatos": 4587,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.35540069686411,
    "precisao_pares": 75.11043938158552,
    "recall_pares": 83.03016011933164,
    "f1_b3": 87.92682997463844,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.135: pesquisa7_particao_0.3.pkl

```json
{
  "experimento": "pesquisa7_particao_0.3.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6670,
    "score": 74.91322545167982,
    "f1_familias": 86.68627347019984,
    "f1_pares": 78.87177131200603,
    "f1_casos": 69.39177915971484,
    "casos_exatos": 4575,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.35540069686411,
    "precisao_pares": 75.10983632775311,
    "recall_pares": 83.03041466635133,
    "f1_b3": 87.89027637438001,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.136: pesquisa7_particao_0.4.pkl

```json
{
  "experimento": "pesquisa7_particao_0.4.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6653,
    "score": 74.8665560441838,
    "f1_familias": 86.68627347019984,
    "f1_pares": 78.8709323055946,
    "f1_casos": 69.29911154985193,
    "casos_exatos": 4563,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.35540069686411,
    "precisao_pares": 75.10873116999281,
    "recall_pares": 83.02990557231195,
    "f1_b3": 87.81261696257177,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.137: pesquisa7_particao_0.45.pkl

```json
{
  "experimento": "pesquisa7_particao_0.45.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6653,
    "score": 74.8665560441838,
    "f1_familias": 86.68627347019984,
    "f1_pares": 78.8709323055946,
    "f1_casos": 69.29911154985193,
    "casos_exatos": 4563,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.35540069686411,
    "precisao_pares": 75.10873116999281,
    "recall_pares": 83.02990557231195,
    "f1_b3": 87.81261696257177,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.138: pesquisa7_presenca_0.5.pkl

```json
{
  "experimento": "pesquisa7_presenca_0.5.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6439,
    "score": 73.51476410281771,
    "f1_familias": 87.04953037238465,
    "f1_pares": 74.81881558367023,
    "f1_casos": 69.76456966422231,
    "casos_exatos": 4519,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.66898954703832,
    "precisao_pares": 64.19528339136127,
    "recall_pares": 89.65574135431048,
    "f1_b3": 87.59476326506243,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.139: pesquisa7_presenca_0.5.pkl

```json
{
  "experimento": "pesquisa7_presenca_0.5.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6626,
    "score": 75.04848885178497,
    "f1_familias": 87.04953037238465,
    "f1_pares": 78.23899476388108,
    "f1_casos": 70.09587581798813,
    "casos_exatos": 4606,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.66898954703832,
    "precisao_pares": 74.66766199493223,
    "recall_pares": 82.16912011425921,
    "f1_b3": 88.01133116306714,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.140: pesquisa7_presenca_1.0.pkl

```json
{
  "experimento": "pesquisa7_presenca_1.0.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6440,
    "score": 73.5608166709662,
    "f1_familias": 86.99688400523506,
    "f1_pares": 74.81876695582268,
    "f1_casos": 69.86724297622723,
    "casos_exatos": 4526,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.68641114982579,
    "precisao_pares": 64.1953304322857,
    "recall_pares": 89.65550994792893,
    "f1_b3": 87.60379791871101,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.141: pesquisa7_presenca_1.0.pkl

```json
{
  "experimento": "pesquisa7_presenca_1.0.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6620,
    "score": 75.09394980240288,
    "f1_familias": 86.99688400523506,
    "f1_pares": 78.34481915634277,
    "f1_casos": 70.11266747868453,
    "casos_exatos": 4605,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.68641114982579,
    "precisao_pares": 74.86095507068886,
    "recall_pares": 82.1687730046869,
    "f1_b3": 88.0067617945882,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.142: pesquisa7_reverse.pkl

```json
{
  "experimento": "pesquisa7_reverse.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6348,
    "score": 68.8096903767937,
    "f1_familias": 84.81054561661952,
    "f1_pares": 73.06583705026718,
    "f1_casos": 62.20460199004975,
    "casos_exatos": 4001,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.60162601626017,
    "precisao_pares": 62.93073811965058,
    "recall_pares": 87.09217517833333,
    "f1_b3": 85.24465785175089,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.143: pesquisa7_bidirectional.pkl

```json
{
  "experimento": "pesquisa7_bidirectional.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6333,
    "score": 68.7507418039339,
    "f1_familias": 84.92496235950507,
    "f1_pares": 72.93528626800115,
    "f1_casos": 62.16826212156588,
    "casos_exatos": 3994,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 87.68873403019745,
    "precisao_pares": 62.80289289220036,
    "recall_pares": 86.96608184103215,
    "f1_b3": 85.23296123847521,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.144: pesquisa7_reversa_final_bidirectional.pkl

```json
{
  "experimento": "pesquisa7_reversa_final_bidirectional.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6454,
    "score": 73.638228517184,
    "f1_familias": 87.003613591509,
    "f1_pares": 74.44952525822848,
    "f1_casos": 70.31611410948342,
    "casos_exatos": 4560,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.59349593495935,
    "precisao_pares": 63.619697263306364,
    "recall_pares": 89.72282606431894,
    "f1_b3": 87.7360463435088,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.145: pesquisa7_reversa_final_bidirectional.pkl

```json
{
  "experimento": "pesquisa7_reversa_final_bidirectional.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6650,
    "score": 75.53267306315345,
    "f1_familias": 87.003613591509,
    "f1_pares": 78.61427462686042,
    "f1_casos": 70.77320370651678,
    "casos_exatos": 4659,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.59349593495935,
    "precisao_pares": 74.84098231779437,
    "recall_pares": 82.78824788806966,
    "f1_b3": 88.28915990825638,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.146: pesquisa7_reversa_final_reverse.pkl

```json
{
  "experimento": "pesquisa7_reversa_final_reverse.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6460,
    "score": 73.66480663903144,
    "f1_familias": 86.9696460436903,
    "f1_pares": 74.64216982155122,
    "f1_casos": 70.22194821208384,
    "casos_exatos": 4556,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.57026713124274,
    "precisao_pares": 63.966845996421775,
    "recall_pares": 89.59444180384051,
    "f1_b3": 87.73898651999649,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.147: pesquisa7_reversa_final_reverse.pkl

```json
{
  "experimento": "pesquisa7_reversa_final_reverse.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6652,
    "score": 75.3433377263598,
    "f1_familias": 86.9696460436903,
    "f1_pares": 78.3527189532151,
    "f1_casos": 70.61057108140947,
    "casos_exatos": 4649,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.57026713124274,
    "precisao_pares": 74.82156531523233,
    "recall_pares": 82.23368249470889,
    "f1_b3": 88.21024904344115,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.148: pesquisa7_feixe512.pkl

```json
{
  "experimento": "pesquisa7_feixe512.pkl",
  "saida": 0,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6434,
    "score": 73.62887396325495,
    "f1_familias": 86.96470872747453,
    "f1_pares": 74.8020501973112,
    "f1_casos": 70.02316602316603,
    "casos_exatos": 4534,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.57026713124274,
    "precisao_pares": 64.10343676227556,
    "recall_pares": 89.78718017902523,
    "f1_b3": 87.69548852859978,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

### Ensaio 7.149: pesquisa7_feixe512.pkl

```json
{
  "experimento": "pesquisa7_feixe512.pkl",
  "saida": 1,
  "escopo": "janeiro",
  "metricas": {
    "eventos": 17220,
    "casos_inferidos": 6630,
    "score": 75.43518121462057,
    "f1_familias": 86.96470872747453,
    "f1_pares": 78.68307586989654,
    "f1_casos": 70.530959987829,
    "casos_exatos": 4636,
    "casos_referencia": 6516,
    "acerto_entre_cobertos": 89.57026713124274,
    "precisao_pares": 75.06715471820866,
    "recall_pares": 82.66497770862327,
    "f1_b3": 88.22474815148412,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.44927536231884,
    "baseline_isolados_score": 13.22463768115942,
    "casos_ref_multidia": 1,
    "casos_ref_multiplos_tipos": 1886,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 1
  }
}
```

## Anexo B. Auditorias e diagnósticos preservados
As auditorias registram verificações realizadas, não uma prova formal de correção semântica dos casos.

### work/auditoria_v5.json

```json
{
  "inferencia_recebeu_somente_cinco_atributos": true,
  "acesso_a_campos_proibidos_bloqueado": true,
  "todos_eventos_unicos": 100000,
  "dados_originais_preservados": true,
  "avaliador_intacto": true,
  "comparacao_rotulada_cega_da_iteracao_anterior": "work/auditoria_v5_62p53.json",
  "segundos": 114.17951400000038,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 37974,
    "score": 63.69736425703764,
    "f1_familias": 79.81724766718935,
    "f1_pares": 73.10417346510131,
    "f1_casos": 52.94794020855636,
    "casos_exatos": 20031,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 83.704,
    "precisao_pares": 62.1605718044596,
    "recall_pares": 88.72444447851828,
    "f1_b3": 81.714689492054,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

### work/auditoria_v5_62p53.json

```json
{
  "referencias_removidas_resultado_identico": true,
  "todos_eventos_unicos": 100000,
  "dados_originais_preservados": true,
  "avaliador_intacto": true,
  "segundos_inferencia_cega": 113.16849309999998,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 38384,
    "score": 62.529700959407144,
    "f1_familias": 79.82533995553521,
    "f1_pares": 70.68758404562843,
    "f1_casos": 52.5442666912045,
    "casos_exatos": 19986,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 83.694,
    "precisao_pares": 62.20012460306539,
    "recall_pares": 81.85735193719114,
    "f1_b3": 81.18213433274259,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

### work/auditoria_v6.json

```json
{
  "inferência_somente_cinco_atributos": true,
  "campos_proibidos_bloqueados": true,
  "comparacao_com_experimento": "janeiro: atribuições, famílias e etapas idênticas ao experimento",
  "linhas_preservadas": 100000,
  "avaliador_intacto": true,
  "apoio_das_fases_entre_0_e_1": true,
  "segundos": 137.32956139999987,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 36817,
    "score": 69.2512755090164,
    "f1_familias": 84.4433541645802,
    "f1_pares": 74.56385655303444,
    "f1_casos": 61.96279494268918,
    "casos_exatos": 23083,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 87.415,
    "precisao_pares": 65.41119849467913,
    "recall_pares": 86.69459221110971,
    "f1_b3": 85.44375668650865,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

### work/auditoria_v6_68p30.json

```json
{
  "inferência_somente_cinco_atributos": true,
  "campos_proibidos_bloqueados": true,
  "implementacao_igual_ao_experimento": true,
  "linhas_preservadas": 100000,
  "avaliador_intacto": true,
  "apoio_das_fases_entre_0_e_1": true,
  "segundos": 165.4821257000001,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 37484,
    "score": 68.30045540307194,
    "f1_familias": 83.47292346348895,
    "f1_pares": 74.29725853907124,
    "f1_casos": 60.468519282189085,
    "casos_exatos": 22728,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 86.624,
    "precisao_pares": 65.06429824938289,
    "recall_pares": 86.58397175055067,
    "f1_b3": 84.84743876076948,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

### work/auditoria_v7.json

```json
{
  "inferência_somente_cinco_atributos": true,
  "campos_proibidos_bloqueados": true,
  "comparacao_com_experimento": "100 mil eventos: casos, famílias e etapas idênticos ao experimento",
  "tarefas_locais_restauradas": 2190,
  "linhas_preservadas": 100000,
  "avaliador_intacto": true,
  "apoio_das_fases_entre_0_e_1": true,
  "segundos": 252.1534974999995,
  "metricas": {
    "eventos": 100000,
    "casos_inferidos": 38291,
    "score": 76.10173383004343,
    "f1_familias": 87.10106987004976,
    "f1_pares": 79.78138350664852,
    "f1_casos": 70.9581468807581,
    "casos_exatos": 26957,
    "casos_referencia": 37689,
    "acerto_entre_cobertos": 89.81,
    "precisao_pares": 75.78865888987366,
    "recall_pares": 84.21819594056247,
    "f1_b3": 88.62812790142357,
    "baseline_isolados_f1_pares": 0.0,
    "baseline_isolados_f1_casos": 26.41460102114185,
    "baseline_isolados_score": 13.207300510570924,
    "casos_ref_multidia": 6,
    "casos_ref_multiplos_tipos": 10898,
    "eventos_sem_contexto": 0,
    "cobertura_rotinas": 100.0,
    "rotinas_descobertas": 14,
    "casos_multidia": 6
  }
}
```

### work/erros_v5.json

```json
{
  "categorias_exclusivas_da_referencia": {
    "casos_exatos": 20031,
    "casos_fragmentados": 8171,
    "casos_fundidos_sem_fragmentacao": 9487
  },
  "grandes_casos": [
    {
      "referencia": "MC2601",
      "eventos_reais": 2934,
      "maior_caso_predito": 3509,
      "intersecao": 2749
    },
    {
      "referencia": "MC2602",
      "eventos_reais": 2899,
      "maior_caso_predito": 3442,
      "intersecao": 2727
    },
    {
      "referencia": "MC2603",
      "eventos_reais": 2924,
      "maior_caso_predito": 3597,
      "intersecao": 2758
    },
    {
      "referencia": "MC2604",
      "eventos_reais": 2960,
      "maior_caso_predito": 3551,
      "intersecao": 2786
    },
    {
      "referencia": "MC2605",
      "eventos_reais": 2928,
      "maior_caso_predito": 3476,
      "intersecao": 2774
    },
    {
      "referencia": "MC2606",
      "eventos_reais": 3057,
      "maior_caso_predito": 3590,
      "intersecao": 2889
    }
  ]
}
```

### work/erros_v6.json

```json
{
  "categorias_exclusivas_da_referencia": {
    "casos_exatos": 23083,
    "casos_fragmentados": 5781,
    "casos_fundidos_sem_fragmentacao": 8825
  },
  "grandes_casos": [
    {
      "referencia": "MC2601",
      "eventos_reais": 2934,
      "maior_caso_predito": 3435,
      "intersecao": 2732
    },
    {
      "referencia": "MC2602",
      "eventos_reais": 2899,
      "maior_caso_predito": 3311,
      "intersecao": 2657
    },
    {
      "referencia": "MC2603",
      "eventos_reais": 2924,
      "maior_caso_predito": 3421,
      "intersecao": 2713
    },
    {
      "referencia": "MC2604",
      "eventos_reais": 2960,
      "maior_caso_predito": 3435,
      "intersecao": 2779
    },
    {
      "referencia": "MC2605",
      "eventos_reais": 2928,
      "maior_caso_predito": 3319,
      "intersecao": 2737
    },
    {
      "referencia": "MC2606",
      "eventos_reais": 3057,
      "maior_caso_predito": 3470,
      "intersecao": 2867
    }
  ]
}
```

### work/erros_v7.json

```json
{
  "categorias_exclusivas_da_referencia": {
    "casos_exatos": 26957,
    "casos_fragmentados": 4802,
    "casos_fundidos_sem_fragmentacao": 5930
  },
  "grandes_casos": [
    {
      "referencia": "MC2601",
      "eventos_reais": 2934,
      "maior_caso_predito": 3092,
      "intersecao": 2672
    },
    {
      "referencia": "MC2602",
      "eventos_reais": 2899,
      "maior_caso_predito": 3055,
      "intersecao": 2655
    },
    {
      "referencia": "MC2603",
      "eventos_reais": 2924,
      "maior_caso_predito": 3128,
      "intersecao": 2676
    },
    {
      "referencia": "MC2604",
      "eventos_reais": 2960,
      "maior_caso_predito": 3161,
      "intersecao": 2736
    },
    {
      "referencia": "MC2605",
      "eventos_reais": 2928,
      "maior_caso_predito": 3072,
      "intersecao": 2699
    },
    {
      "referencia": "MC2606",
      "eventos_reais": 3057,
      "maior_caso_predito": 3160,
      "intersecao": 2809
    }
  ]
}
```

### work/contadores_cv80.json

```json
[
  {
    "app": "chrome",
    "n": 16995,
    "acuracia": 0.08033400518283905,
    "balanceada": 0.0802902751014242,
    "baseline": 0.09415490930031672
  },
  {
    "app": "erp",
    "n": 12512,
    "acuracia": 0.060038240917782024,
    "balanceada": 0.041342105957960486,
    "baseline": 0.06386233269598471
  },
  {
    "app": "excel",
    "n": 8677,
    "acuracia": 0.08296460176991151,
    "balanceada": 0.057949715228833173,
    "baseline": 0.09236725663716815
  },
  {
    "app": "outlook",
    "n": 2418,
    "acuracia": 0.6901960784313725,
    "balanceada": 0.25,
    "baseline": 0.6901960784313725
  },
  {
    "app": "powerbi",
    "n": 766,
    "acuracia": 1.0,
    "balanceada": 1.0,
    "baseline": 1.0
  },
  {
    "app": "powerpoint",
    "n": 600,
    "acuracia": 1.0,
    "balanceada": 1.0,
    "baseline": 1.0
  },
  {
    "app": "sharepoint",
    "n": 4392,
    "acuracia": 0.34318901795142553,
    "balanceada": 0.19315705947225434,
    "baseline": 0.3579725448785639
  },
  {
    "app": "sql",
    "n": 5553,
    "acuracia": 0.20698254364089774,
    "balanceada": 0.13282994989105068,
    "baseline": 0.18204488778054864
  },
  {
    "app": "teams",
    "n": 2498,
    "acuracia": 0.6319018404907976,
    "balanceada": 0.25,
    "baseline": 0.6319018404907976
  },
  {
    "app": "whatsapp",
    "n": 1585,
    "acuracia": 1.0,
    "balanceada": 1.0,
    "baseline": 1.0
  },
  {
    "app": "word",
    "n": 716,
    "acuracia": 0.583941605839416,
    "balanceada": 0.5,
    "baseline": 0.583941605839416
  }
]
```

### work/contexto_mascarado80.json

```json
{
  "n_train": 19219,
  "n_test": 4685,
  "accuracy": 0.4424759871931697,
  "balanced": 0.4381936806982425,
  "baseline": 0.11632870864461047,
  "seconds": 2.165708400000085
}
```

## Anexo C. Especificação executável integral da versão documentada
O código abaixo torna explícitos os limiares, aproximações, fallbacks, normalizações e detalhes de implementação que uma descrição em prosa pode omitir. A inclusão é documental e não altera os arquivos executáveis.

### analisar_amostra.py

```python
"""Execução e relatório da descoberta de rotinas. Veja LEIA-ME.md."""
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime
import csv
import html
import json
import statistics
import numpy as np
from scipy.optimize import linear_sum_assignment
from motor_descoberta import Evento, descobrir, PARAMETROS, INCERTO, TRANSVERSAL

# Use um caminho ou uma lista. Caminhos relativos partem da pasta deste script.
CAMINHO_AMOSTRA = r"amostra_validacao_fechamento_100k.csv"

def gravar(rows, casos, destino):
    mapa={e.linha:(i,j,e) for i,c in enumerate(casos,1) for j,e in enumerate(c,1)}
    assert len(mapa)==sum(map(len,casos))==len(rows)
    with open(destino,'w',encoding='utf-8-sig',newline='') as f:
        campos=['linha_csv','caso_inferido','posicao','familia','etapa','variante','evidencia_contextual','criterio','caso_local','episodio_longo']
        w=csv.writer(f)
        w.writerow(campos+list(rows[0]))
        for linha,row in enumerate(rows,2):
            i,j,e=mapa[linha]
            w.writerow([linha,i,j,e.familia,e.etapa,row['nome_tela_foco'],round(e.evidencia,4),e.criterio,e.caso_local,e.episodio_longo]+list(row.values()))


CONTADORES = (
    'quantidade_teclas_digitadas', 'quantidade_clicks',
    'quantidade_copias', 'quantidade_colagens',
)
OBRIGATORIAS = {
    'codigo_racf', 'nome_programa', 'nome_tela_foco',
    'data_hora_inicio_exec', 'data_hora_fim_exec', *CONTADORES,
}

def ler_amostra(caminho):
    """Aceita CSV UTF-8/BOM ou Windows-1252, com vírgula, ponto e vírgula ou tab."""
    raw = caminho.read_bytes()
    try:
        texto = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        texto = raw.decode('cp1252')
    try:
        dialect = csv.Sniffer().sniff(texto[:65536], delimiters=',;	')
    except csv.Error:
        dialect = csv.excel
    import io
    reader = csv.DictReader(io.StringIO(texto), dialect=dialect)
    faltantes = OBRIGATORIAS - set(reader.fieldnames or [])
    if faltantes:
        raise ValueError('Colunas obrigatórias ausentes: ' + ', '.join(sorted(faltantes)))
    rows = list(reader)
    if not rows:
        raise ValueError('A amostra não contém eventos.')
    for linha, row in enumerate(rows, 2):
        try:
            if None in row or any(value is None for value in row.values()):
                raise ValueError('Quantidade de campos diferente do cabeçalho')
            for campo in OBRIGATORIAS:
                if not row[campo].strip():
                    raise ValueError('Campo vazio: ' + campo)
            for campo in CONTADORES:
                valor = int(row[campo])
                if valor < 0:
                    raise ValueError('Contador negativo: ' + campo)
            inicio = datetime.fromisoformat(row['data_hora_inicio_exec'])
            fim = datetime.fromisoformat(row['data_hora_fim_exec'])
            if inicio.tzinfo is not None or fim.tzinfo is not None:
                raise ValueError('Use horários locais sem fuso, no formato AAAA-MM-DD HH:MM:SS')
            if fim < inicio:
                raise ValueError('Fim anterior ao início')
        except (ValueError, TypeError) as exc:
            raise ValueError(f'Linha {linha}: {exc}') from exc
    return rows

def metricas(casos, rows):
    """Referências só entram nesta função, após a inferência com parâmetros fixos."""
    pred = {frozenset(e.linha for e in caso) for caso in casos}
    campo_id = 'processo_id' if 'processo_id' in rows[0] else 'referencia_processo_id'
    campo_tipo = 'processo_sintetico' if 'processo_sintetico' in rows[0] else 'referencia_processo'
    ids_completos = all(row.get(campo_id, '').strip() for row in rows)
    tipos_completos = all(row.get(campo_tipo, '').strip() for row in rows)
    resultado = dict(eventos=len(rows), casos_inferidos=len(casos),
                     score=None, f1_familias=None, f1_pares=None,
                     f1_casos=None, casos_exatos=None, casos_referencia=None)
    if tipos_completos:
        confusao = Counter()
        for caso in casos:
            for e in caso:
                nome = rows[e.linha-2][campo_tipo].strip()
                confusao[nome, e.familia] += 1
        # Correspondência ótima um a um usada exclusivamente na avaliação.
        reais = sorted({a for a,b in confusao})
        previstos = sorted({b for a,b in confusao if b != INCERTO})
        if previstos:
            matriz = np.array([[confusao[a,b] for b in previstos] for a in reais])
            totais_reais = np.array([sum(n for (a,b),n in confusao.items() if a==nome) for nome in reais])
            f1 = 2 * matriz / (totais_reais[:,None] + matriz.sum(axis=0)[None,:])
            ii,jj = linear_sum_assignment(f1,maximize=True)
            resultado['f1_familias'] = float(100 * f1[ii,jj].sum()/max(len(reais),len(previstos)))
            cobertos = int(matriz.sum())
            resultado['acerto_entre_cobertos'] = float(100*matriz[ii,jj].sum()/cobertos) if cobertos else None
        else:
            resultado['f1_familias'] = 0.0
    if ids_completos:
        ref = defaultdict(set)
        cruzamento = Counter()
        for numero, caso in enumerate(casos):
            for e in caso:
                chave = (e.usuario, rows[e.linha-2][campo_id].strip())
                ref[chave].add(e.linha)
                cruzamento[numero, chave] += 1
        verdadeiros = set(map(frozenset, ref.values()))
        pares = lambda tamanhos: sum(n * (n-1) // 2 for n in tamanhos)
        tp = pares(cruzamento.values())
        pp = pares(map(len, pred))
        rp = pares(map(len, verdadeiros))
        # Duas partições só de singletons não têm erros de associação.
        resultado['f1_pares'] = 100 * (2*tp/(pp+rp) if pp+rp else 1)
        resultado['precisao_pares'] = 100 * tp/pp if pp else None
        resultado['recall_pares'] = 100 * tp/rp if rp else None
        tamanhos_pred = {i:len(caso) for i,caso in enumerate(casos)}
        precisao_b3 = sum(n*n/tamanhos_pred[i] for (i,k),n in cruzamento.items())/len(rows)
        recall_b3 = sum(n*n/len(ref[k]) for (i,k),n in cruzamento.items())/len(rows)
        resultado['f1_b3'] = 200 * precisao_b3*recall_b3/(precisao_b3+recall_b3)
        resultado['baseline_isolados_f1_pares'] = 0.0 if rp else 100.0
        isolados = sum(len(v)==1 for v in ref.values())
        resultado['baseline_isolados_f1_casos'] = 200*isolados/(len(rows)+len(ref))
        resultado['baseline_isolados_score'] = (
            .4*resultado['baseline_isolados_f1_pares']+
            .5*resultado['baseline_isolados_f1_casos'])
        resultado['casos_ref_multidia'] = sum(len({
            rows[linha-2]['data_hora_inicio_exec'][:10] for linha in linhas})>1 for linhas in ref.values())
        resultado['casos_ref_multiplos_tipos'] = sum(len({
            rows[linha-2].get(campo_tipo,'') for linha in linhas})>1 for linhas in ref.values())
        resultado['casos_exatos'] = len(pred & verdadeiros)
        resultado['casos_referencia'] = len(verdadeiros)
        resultado['f1_casos'] = 200 * len(pred & verdadeiros)/(len(pred)+len(verdadeiros))
    if ids_completos and tipos_completos:
        resultado['score'] = (
            .1*resultado['f1_familias'] + .4*resultado['f1_pares'] + .5*resultado['f1_casos'])
    resultado['eventos_sem_contexto'] = sum(e.familia==INCERTO for caso in casos for e in caso)
    resultado['cobertura_rotinas'] = 100*(1-resultado['eventos_sem_contexto']/len(rows))
    resultado['rotinas_descobertas'] = len({e.familia for caso in casos for e in caso if e.familia!=INCERTO})
    resultado['casos_multidia'] = sum(len({e.inicio.date() for e in caso})>1 for caso in casos)
    return resultado

def tabela(cabecalho, linhas):
    def esc(valor):
        return html.escape('Indisponível' if valor is None else str(valor))
    return ('<div class="rolagem"><table><thead><tr>' +
            ''.join('<th>'+esc(c)+'</th>' for c in cabecalho) +
            '</tr></thead><tbody>' +
            ''.join('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in linha)+'</tr>' for linha in linhas) +
            '</tbody></table></div>')

def numero(valor):
    return 'Indisponível' if valor is None else f'{valor:.2f}'

def gerar_html(rows, casos, medidas, origem, medidas_locais=None, diagnostico=None):
    grupos = defaultdict(list)
    for caso in casos:
        familias=Counter(e.familia for e in caso if e.familia!=TRANSVERSAL)
        familia=familias.most_common(1)[0][0]if familias else TRANSVERSAL
        grupos[familia].append(caso)
    conteudo = []
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    for familia, grupo in sorted(grupos.items()):
        por_etapa, posicoes = defaultdict(list), defaultdict(list)
        presencas, transicoes = Counter(), Counter()
        dias_atividade, dias_inicio, meses_atividade = Counter(), Counter(), Counter()
        for caso in grupo:
            presencas.update(set(e.etapa for e in caso))
            dias_inicio[caso[0].inicio.date()] += 1
            for pos, e in enumerate(caso, 1):
                por_etapa[e.etapa].append(e)
                posicoes[e.etapa].append(pos)
                dias_atividade[e.inicio.date()] += 1
                meses_atividade[e.inicio.strftime('%Y-%m')] += 1
            transicoes.update((a.etapa,b.etapa) for a,b in zip(caso,caso[1:]))
        etapas = []
        ordenadas = sorted(por_etapa, key=lambda nome:(statistics.median(posicoes[nome]),nome))
        for nome in ordenadas:
            obs = por_etapa[nome]
            medias = [sum(int(rows[e.linha-2][campo]) for e in obs)/len(obs) for campo in CONTADORES]
            etapas.append([nome, len(obs), f'{100*presencas[nome]/len(grupo):.1f}%',
                           f'{statistics.median(posicoes[nome]):.1f}',
                           *[f'{v:.1f}' for v in medias], f'{sum(medias):.1f}'])
        calendario = []
        for dia,n in sorted(dias_atividade.items()):
            ordinal = sum(datetime(dia.year,dia.month,d).weekday()<5 for d in range(1,dia.day+1))
            calendario.append([dia.isoformat(), dias_semana[dia.weekday()],
                               f'{ordinal}º' if dia.weekday()<5 else 'Fim de semana',n,dias_inicio[dia]])
        variantes = Counter(tuple(e.etapa for e in caso) for caso in grupo)
        sequencias = []
        for seq,n in variantes.most_common(10):
            texto = ' → '.join(seq[:16])
            if len(seq)>16:
                texto += f' → … ({len(seq)} eventos; sequência completa no CSV)'
            sequencias.append([texto,n])
        amostras = sorted(grupo,key=len,reverse=True)[:5]
        rastros = [[c[0].linha, c[0].inicio.isoformat(' '), max(e.fim for e in c).isoformat(' '),
                    len(c), ', '.join(str(e.linha) for e in c[:16])+(' …' if len(c)>16 else '')]
                   for c in amostras]
        aviso = ''
        if familia==INCERTO:
            aviso = '<p class="nota">Estes eventos ficaram sem evidência suficiente de rotina. Cada um tem uma atribuição provisória isolada para preservar a rastreabilidade.</p>'
        conteudo.append(
            '<article class="processo" hidden data-familia="'+html.escape(familia,quote=True)+'"><h2>'+
            html.escape(familia)+'</h2>'+aviso+
            f'<p>{len(grupo):,} casos candidatos · {sum(dias_atividade.values()):,} eventos · {len(dias_atividade)} dias com atividade.</p>'+
            '<h3>Etapas observadas e manualidade</h3><p>A ordem da tabela usa a posição mediana nas execuções. As transições abaixo mostram como as etapas se conectaram.</p>'+
            tabela(['Aplicativo / tela','Eventos','Presença nos casos','Posição mediana','Teclas / evento',
                    'Cliques / evento','Cópias / evento','Colagens / evento','Interações / evento'],etapas)+
            '<h3>Transições mais frequentes</h3>'+
            tabela(['Etapa anterior','Etapa seguinte','Ocorrências'],[(a,b,n) for (a,b),n in transicoes.most_common(20)])+
            '<h3>Repetição mensal</h3>'+tabela(['Mês','Eventos'],sorted(meses_atividade.items()))+
            '<details><summary>Datas e dias úteis</summary>'+tabela(
                ['Data','Dia da semana','Dia útil seg–sex','Eventos executados','Casos iniciados'],calendario)+'</details>'+
            '<details><summary>Sequências recorrentes</summary>'+tabela(['Sequência','Casos'],sequencias)+'</details>'+
            '<details><summary>Exemplos de execuções e linhas do CSV</summary>'+tabela(
                ['Primeira linha','Início','Fim','Eventos','Linhas de origem'],rastros)+'</details></article>')
    resumo = []
    for nome, grupo in sorted(grupos.items(),key=lambda item:-sum(map(len,item[1]))):
        resumo.append([nome,sum(map(len,grupo)),len(grupo),sum(len({e.inicio.date() for e in c})>1 for c in grupo)])
    avaliacao = tabela(['Métrica','Resultado'],[
        ['Score composto / 100',numero(medidas['score'])],
        ['F1 das famílias com alinhamento (%)',numero(medidas['f1_familias'])],
        ['F1 dos pares (%)',numero(medidas['f1_pares'])],
        ['Precisão dos pares (%)',numero(medidas.get('precisao_pares'))],
        ['Sensibilidade dos pares (%)',numero(medidas.get('recall_pares'))],
        ['F1 de casos inteiros (%)',numero(medidas['f1_casos'])],
        ['F1 B³ dos casos (%)',numero(medidas.get('f1_b3'))],
        ['Acerto de família entre eventos cobertos (%)',numero(medidas.get('acerto_entre_cobertos'))],
        ['Casos idênticos à referência',medidas['casos_exatos']],
        ['Casos na referência',medidas['casos_referencia']],
        ['Score da linha de base de eventos isolados',numero(medidas.get('baseline_isolados_score'))],
    ])
    niveis = ''
    if medidas_locais is not None:
        niveis = '<h3>Comparação das escalas de execução</h3>'+tabela(
            ['Escala','Casos','F1 pares','F1 casos inteiros','F1 B³'],[
                ['Local',medidas_locais['casos_inferidos'],numero(medidas_locais['f1_pares']),
                 numero(medidas_locais['f1_casos']),numero(medidas_locais.get('f1_b3'))],
                ['Com episódios longos',medidas['casos_inferidos'],numero(medidas['f1_pares']),
                 numero(medidas['f1_casos']),numero(medidas.get('f1_b3'))],
            ])+'<p>O CSV registra caso_local e episodio_longo. O caso_inferido incorpora os episódios longos detectados. Um episódio temporal concentrado é uma hipótese de agrupamento. Seu significado de negócio precisa de validação. As duas escalas usam exatamente as mesmas referências para permitir a comparação.</p>'
    internos = ''
    if diagnostico is not None:
        grafo = diagnostico['grafo']
        internos = '<h3>Diagnósticos disponíveis sem referências</h3>'+tabela(
            ['Indicador','Valor'],[
                ['Cobertura de eventos (%)',numero(medidas['cobertura_rotinas'])],
                ['Modularidade do grafo',numero(grafo['modularidade_grafo'])],
                ['Estabilidade ARI sob perturbação de 10% dos pesos',numero(grafo['estabilidade_ari_perturbacao_pesos'])],
                ['Associações repetidas retidas',grafo['arestas_repetidas']],
                ['Sessões de atividade',diagnostico['sessoes_atividade']],
                ['Episódios longos candidatos',diagnostico['episodios_longos']],
            ])+'<p>Esses indicadores descrevem estrutura, cobertura e sensibilidade do agrupamento. Estabilidade alta também pode ocorrer em um agrupamento incorreto. A verificação de acerto exige referências ou revisão de exemplos.</p>'
    opcoes = '<option value="">Selecione uma rotina</option>'+''.join(
        '<option>'+html.escape(nome)+'</option>' for nome in sorted(grupos))
    alertas = ''
    if medidas.get('casos_ref_multiplos_tipos'):
        alertas += f"<p class='nota'>A referência tem {medidas['casos_ref_multiplos_tipos']:,} casos com mais de um tipo de processo entre suas linhas. A avaliação de famílias usa o rótulo de cada evento. A avaliação de casos usa o ID, incluindo essas diferenças.</p>"
    if medidas['eventos_sem_contexto']:
        alertas += f"<p class='nota'>{medidas['eventos_sem_contexto']:,} eventos têm contexto insuficiente. Essa parcela requer revisão e limita a interpretação dos processos descobertos.</p>"
    periodo = min(e.inicio for c in casos for e in c).date().isoformat()+' a '+max(e.inicio for c in casos for e in c).date().isoformat()
    return """<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Descoberta de rotinas</title>
<style>
*{box-sizing:border-box}body{font:16px/1.55 system-ui;margin:0;background:#f1f5f2;color:#173b35}
header{background:#153e36;color:white;padding:36px max(4vw,calc((100vw - 1200px)/2))}
main{max-width:1240px;margin:24px auto;padding:0 20px}article,section{background:white;padding:24px;border:1px solid #cedbd3;border-radius:12px;margin:20px 0}
h1{font:48px Georgia,serif;line-height:1.1;margin:10px 0}h2{font-size:26px}h3{margin-top:28px}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{text-align:left;padding:10px;border-bottom:1px solid #dce6df;overflow-wrap:anywhere}
th{background:#edf4ef}.rolagem{overflow-x:auto}select{font:inherit;padding:12px;max-width:100%;border:1px solid #93afa1;border-radius:6px}summary{cursor:pointer;font-weight:bold}
details{margin-top:18px}.nota{background:#fff6df;border-left:3px solid #b48329;padding:14px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.kpis div{background:#e4eee7;padding:16px;border-radius:8px}.kpis b{display:block;font:30px Georgia,serif}
a{color:#126b4e}article[hidden]{display:none}.over{font-size:12px;letter-spacing:.12em;text-transform:uppercase}
@media(max-width:700px){.kpis{grid-template-columns:1fr 1fr}main{padding:0 10px}article,section{padding:14px}h1{font-size:34px}}
</style><header><div class="over">Exploração de logs · Modelo 7.0</div><h1>Rotinas descobertas</h1><p>""" + html.escape(origem.name)+' · '+periodo+"""</p></header><main>
<div class="kpis"><div><b>""" + f"{len(rows):,}" + """</b>eventos</div><div><b>""" + str(medidas['rotinas_descobertas']) + """</b>rotinas candidatas</div><div><b>""" + numero(medidas['cobertura_rotinas']) + """%</b>eventos com rotina atribuída</div><div><b>""" + numero(medidas['score']) + """</b>score / 100</div></div>
""" + alertas + """<section><h2>Rotinas e execuções</h2>
<p>Os nomes identificam exemplos de telas de cada grupo. A interpretação de negócio exige validação.
Casos com famílias diferentes aparecem pela família predominante entre as atividades não transversais. O CSV mantém a família de cada evento. O agrupamento aprende com cada amostra. Os números das rotinas são locais ao arquivo.</p>""" + tabela(
    ['Grupo','Eventos','Casos candidatos','Casos em mais de uma data'],resumo)+"""
</section><section><h2>Explorar as etapas</h2><label for="familia">Rotina</label> <select id="familia">""" + opcoes + """</select>
<p>Selecione uma rotina para consultar etapas, manualidade, transições, calendário e exemplos.</p></section>
""" + ''.join(conteudo) + """<section><h2>Avaliação da separação</h2>""" + avaliacao + niveis + internos + """
<p>Score = 10% F1 das famílias alinhadas + 40% F1 dos pares + 50% F1 dos casos inteiros.
Para pontuar famílias, fazemos uma correspondência um a um entre grupos e referências pelo maior F1.
Grupos excedentes recebem zero. Eventos sem contexto contam como erros de família.
O alinhamento é usado exclusivamente na avaliação.</p>
<p>Casos inteiros exigem igualdade de todas as linhas. O F1 dos pares dá mais peso a casos grandes.
O F1 B³ dá o mesmo peso a cada evento e ajuda a identificar quando poucos casos grandes dominam a avaliação.
A linha de base trata cada evento como um caso independente e não identifica famílias.</p>
<p>O score depende de processo_id e processo_sintetico, ou referencia_processo_id e referencia_processo.
Colunas ausentes ou incompletas tornam a métrica correspondente indisponível.
Essas colunas são ignoradas durante a descoberta.</p>
<p>Esta é uma avaliação descritiva da amostra. As duas bases disponíveis foram consultadas durante o desenvolvimento.
Uma nova base independente será necessária para medir generalização externa.</p></section>
<section><h2>Como o modelo trabalha</h2>
<p>O algoritmo constrói um grafo de coocorrência de aplicativo e tela em janelas de até cinco eventos
e vinte minutos. Mantém associações repetidas acima do esperado e descobre comunidades com Louvain.
O contexto usa apenas o excesso de associação acima do esperado e um desconto para flutuações pequenas.
As evidências anteriores e posteriores ajudam a atribuir telas compartilhadas. Casos ambíguos ficam sem rotina.
Sufixos são agregados somente quando a tela-base existe e é pelo menos três vezes mais frequente.</p>
<p>Em cada rotina e usuário, o algoritmo compara misturas de uma a quatro distribuições logarítmicas pelo BIC.
As distribuições de pausas curtas e longas propõem evidência de continuidade ou de fronteira. Pausas globais com forte evidência de interrupção separam as sessões da escala local.
Uma cobertura de caminhos escolhe vínculos temporais e transições compatíveis, admitindo execuções intercaladas.
A competição entre múltiplas continuações recebe uma penalização. Períodos de pelo menos três datas com
concentração elevada podem formar um episódio longo, registrado separadamente da escala local.</p>
<p>Quando há atividades transversais detectadas, o modelo executa três passagens: aprende trilhas
preliminares, estima quais etapas iniciam as tarefas e refina a associação dos eventos. As entradas são
estimadas por mudanças de grupo entre observações de alta afinidade, com regularização e sem referências.
O modelo distingue prefixos de nomes até oito caracteres na etapa de refinamento.</p>
<p>Na última passagem, o feixe determinístico de 128 hipóteses mantém distribuições sobre fases.
A aproximação por uma âncora só ocorre quando o apoio posterior da fase atinge 0,98.
A temperatura das transições é 0,75. Viterbi revisa as fases com peso 0,5, condicionado às trilhas escolhidas.
A escolha global das trilhas permanece aproximada, e o apoio não foi calibrado como probabilidade de acerto.</p>
<p>A espera é refinada com pares adjacentes de etapas confiáveis. Um histograma em bins de cinco segundos
é dividido em blocos de taxa constante com penalização pelo número de blocos. Os limites são aprendidos;
o potencial combina 90% desse histograma com 10% do modelo inicial. Sem evidência suficiente, usa-se o modelo inicial.</p>
<p>Uma tarefa local com início aprendido e apoio posterior de pelo menos 0,98 pode ser preservada fora
do episódio maior. O CSV marca esses eventos como tarefa_local_preservada. Todas as linhas participam
da separação e da avaliação. A agregação em episódios continua sendo uma hipótese de correlação.</p>
<p>O método é offline e utiliza observações anteriores e posteriores. A concorrência dos intervalos define
o número mínimo de trilhas utilizadas, não o número real comprovado de fluxos. Transições no painel são
adjacências cronológicas e não demonstram causalidade entre todas as etapas.</p>
<p>A coluna evidencia_contextual representa apoio relativo do contexto. No método com fases marginalizadas, a etapa final usa o apoio posterior da fase condicionado às trilhas inferidas. Os valores não são probabilidades
calibradas de acerto. criterio informa se a atribuição veio de um núcleo recorrente, do contexto bidirecional
ou se o contexto foi insuficiente.</p>
<p>Manualidade representa teclas, cliques, cópias e colagens por ocorrência. Os contadores podem se sobrepor.
O calendário conta dias úteis de segunda a sexta, sem excluir feriados.
Datas com atividade incluem todas as etapas, mesmo quando o caso começou em outro dia.</p>
<p>Pesquisa relacionada sobre descoberta de rotinas em logs sem segmentação.
<a href="https://arxiv.org/abs/2008.05782">Leno e colaboradores</a>.
O agrupamento utiliza o <a href="https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html">algoritmo Louvain</a>.
A implementação combina esses conceitos com um modelo próprio. O reconhecimento de tarefas e a correlação
de processos também são discutidos por
<a href="https://doi.org/10.1016/j.is.2024.102404">Rebmann e van der Aa</a>.
O trabalho combina fluxo, semântica e objetos de negócio. Nossos CSVs não contêm identificadores de objetos.</p></section>
</main><script>document.getElementById('familia').onchange=function(){
document.querySelectorAll('.processo').forEach(p=>p.hidden=p.dataset.familia!==this.value);
}</script></html>"""

def executar(caminho_amostra):
    origem = Path(caminho_amostra).expanduser()
    if not origem.is_absolute():
        origem = Path(__file__).resolve().parent / origem
    origem = origem.resolve()
    if not origem.is_file():
        raise ValueError(f'CSV não encontrado: {origem}')
    rows = ler_amostra(origem)
    print(f'Lendo {len(rows)} eventos de {origem.name}...', flush=True)
    casos, diagnostico = descobrir(rows, devolver_diagnostico=True)
    return salvar_resultados(origem, rows, casos, diagnostico)


def salvar_resultados(origem, rows, casos, diagnostico):
    """Gera os artefatos a partir de uma inferência já concluída."""
    medidas = metricas(casos, rows)
    locais = defaultdict(list)
    for caso in casos:
        for evento in caso:
            locais[evento.caso_local].append(evento)
    casos_locais = [sorted(c,key=lambda e:(e.inicio,e.linha)) for c in locais.values()]
    medidas_locais = metricas(casos_locais,rows)
    destino = origem.parent / (origem.stem + '_resultados')
    destino.mkdir(exist_ok=True)
    # Prepara os três resultados antes de substituir a execução anterior.
    from tempfile import TemporaryDirectory
    import hashlib
    relatorio = dict(amostra=str(origem), parametros=PARAMETROS,
                     sha256_amostra=hashlib.sha256(origem.read_bytes()).hexdigest(),
                     sha256_codigo=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     sha256_motor=hashlib.sha256(Path(descobrir.__code__.co_filename).read_bytes()).hexdigest(),
                     sha256_modulos={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).with_name('motor_descoberta.py'),Path(__file__).with_name('motor_sequencial.py'),Path(__file__).with_name('motor_probabilistico.py'),Path(__file__).with_name('motor_adaptativo.py')]},
                     diagnostico=diagnostico,metricas=medidas,metricas_locais=medidas_locais)
    pagina = gerar_html(rows, casos, medidas, origem, medidas_locais, diagnostico)
    with TemporaryDirectory(prefix='.analise_',dir=destino) as temporario:
        pasta = Path(temporario)
        gravar(rows, casos, pasta / 'eventos_classificados.csv')
        (pasta/'metricas.json').write_text(json.dumps(relatorio,ensure_ascii=False,indent=2),encoding='utf8')
        (pasta/'estudo.html').write_text(pagina,encoding='utf8')
        for nome in ('eventos_classificados.csv','estudo.html','metricas.json'):
            (pasta/nome).replace(destino/nome)
    print('Score / 100: ' + numero(medidas['score']))
    print(f'HTML gerado em {destino / "estudo.html"}')
    return destino, medidas

if __name__ == '__main__':
    try:
        arquivos = CAMINHO_AMOSTRA if isinstance(CAMINHO_AMOSTRA, (list, tuple)) else [CAMINHO_AMOSTRA]
        for arquivo in arquivos:
            executar(arquivo)
    except (ValueError, OSError, ImportError, RuntimeError) as exc:
        raise SystemExit('Erro: ' + str(exc)) from exc

```

### motor_descoberta.py

```python
"""Motor 7.0. Comunidades, contexto bidirecional, segmentação temporal e episódios.
Usa observações anônimas, sem catálogo ou campos de referência.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
import math
import statistics
import numpy as np
import networkx as nx
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching

PARAMETROS = {
    "versao": "7.0",
    "janela_eventos": 5,
    "janela_segundos": 1200,
    "lift_minimo": 3.0,
    "seed": 42,
    "limiar_atribuicao": 0.2,
    "filtro_associacoes": 0.01,
    "divisor_suporte_grafo": 6,
}
INCERTO = "Contexto insuficiente"
TRANSVERSAL = "Atividades transversais"

@dataclass(frozen=True)
class Evento:
    linha: int
    usuario: str
    inicio: datetime
    fim: datetime
    etapa: str
    familia: str
    evidencia: float = 0.0
    criterio: str = ""
    caso_local: int = 0
    episodio_longo: int = 0

def preparar_observacoes(rows):
    """O modelo acessa somente pessoa, aplicativo, tela e horários."""
    usuarios = defaultdict(list)
    inicio, fim, telas = [], [], []
    frequencias_brutas = Counter(
        (''.join(row['nome_programa'].split()).casefold(), row['nome_tela_foco'].strip().casefold())
        for row in rows
    )
    for i, row in enumerate(rows):
        usuarios[row['codigo_racf']].append(i)
        inicio.append(datetime.fromisoformat(row['data_hora_inicio_exec']))
        fim.append(datetime.fromisoformat(row['data_hora_fim_exec']))
        app = ''.join(row['nome_programa'].split()).casefold()
        tela = row['nome_tela_foco'].strip().casefold()
        base = tela.rpartition('_')[0]
        # Só agrega um sufixo quando a tela-base também existe e é predominante.
        if base and frequencias_brutas[app, base] >= 3 * frequencias_brutas[app, tela]:
            tela = base
        telas.append((app, tela))
    for seq in usuarios.values():
        seq.sort(key=lambda i: (inicio[i], fim[i], telas[i], i))
    return usuarios, inicio, fim, telas

def aprender_grupos(usuarios, inicio, telas, devolver_diagnostico=False):
    frequencia = Counter(telas)
    pares = Counter()
    graus = Counter()
    contagens = Counter()
    graus_crus = Counter()
    for seq in usuarios.values():
        for pos, i in enumerate(seq):
            for anterior in range(max(0, pos-PARAMETROS['janela_eventos']), pos):
                j = seq[anterior]
                if (inicio[i]-inicio[j]).total_seconds() > PARAMETROS['janela_segundos']:
                    continue
                if telas[i] == telas[j]:
                    continue
                a, b = sorted((telas[i], telas[j]))
                peso = 1 / (pos-anterior)
                pares[a, b] += peso
                graus[a] += peso
                graus[b] += peso
                contagens[a,b] += 1
                graus_crus[a] += 1
                graus_crus[b] += 1
    grafo = nx.Graph()
    suporte = max(2, math.ceil(math.sqrt(len(telas))/PARAMETROS["divisor_suporte_grafo"]))
    soma_graus = max(1, sum(graus.values()))
    lift_minimo = min(PARAMETROS["lift_minimo"], max(1.2, math.sqrt(len(frequencia))/2))
    from scipy.stats import poisson
    chaves = sorted(pares)
    total_cru = max(1,sum(graus_crus.values()))
    p_valores = poisson.sf(
        np.array([contagens[a,b] for a,b in chaves])-1,
        np.array([graus_crus[a]*graus_crus[b]/total_cru for a,b in chaves]))
    ordem = np.argsort(p_valores)
    elegiveis = p_valores[ordem] <= .01*(np.arange(len(ordem))+1)/max(1,len(ordem))
    corte = float(p_valores[ordem[elegiveis][-1]]) if elegiveis.any() else -1
    aceitos = {chaves[j] for j in range(len(chaves)) if p_valores[j]<=corte}
    for (a, b), observado in sorted(pares.items()):
        esperado = graus[a]*graus[b]/soma_graus
        lift = observado/max(esperado, 1e-12)
        if min(frequencia[a], frequencia[b]) < suporte:
            continue
        if observado >= 5 and lift >= lift_minimo and (a,b) in aceitos:
            peso = math.sqrt(observado)*math.log(lift)**2
            grafo.add_edge(a, b, weight=peso)
    comunidades = []
    if grafo.number_of_edges():
        comunidades = nx.community.louvain_communities(grafo, seed=PARAMETROS['seed'])
    modularidade = nx.community.modularity(grafo,comunidades) if comunidades else None
    estabilidade = None
    if comunidades:
        perturbado = grafo.copy()
        rng = np.random.default_rng(PARAMETROS['seed'])
        for a,b in perturbado.edges:
            perturbado[a][b]['weight'] *= float(rng.uniform(.9,1.1))
        alternativa = nx.community.louvain_communities(perturbado,seed=PARAMETROS['seed'])
        primeiro = {s:g for g,c in enumerate(comunidades) for s in c}
        segundo = {s:g for g,c in enumerate(alternativa) for s in c}
        cruzamento = Counter((primeiro[s],segundo[s]) for s in grafo)
        combinacoes = lambda ns: sum(n*(n-1)/2 for n in ns)
        a = combinacoes(Counter(primeiro.values()).values())
        b = combinacoes(Counter(segundo.values()).values())
        total = len(grafo)*(len(grafo)-1)/2
        esperado = a*b/total if total else 0
        denominador = (a+b)/2-esperado
        estabilidade = ((combinacoes(cruzamento.values())-esperado)/denominador
                        if denominador else 1.0)
    comunidades = [c for c in comunidades if len(c) >= 2]
    comunidades.sort(key=lambda c: sorted(c))
    mapa = {tela: grupo for grupo, comunidade in enumerate(comunidades) for tela in comunidade}
    afinidades = defaultdict(Counter)
    for (a, b), observado in pares.items():
        esperado = graus[a]*graus[b]/soma_graus
        excesso = max(0.0, observado-esperado-2*math.sqrt(esperado))
        if excesso <= 0:
            continue
        if b in mapa:
            afinidades[a][mapa[b]] += excesso
        if a in mapa:
            afinidades[b][mapa[a]] += excesso
    massa = Counter()
    for tela, grupo in mapa.items():
        massa[grupo] += graus[tela]
    vetores = {}
    for tela, contagens in afinidades.items():
        valores = np.array([contagens[g]/max(1, massa[g])**.7
                            for g in range(len(comunidades))], dtype=float)
        if valores.sum():
            vetores[tela] = valores/valores.sum()
    nomes = {}
    for g, comunidade in enumerate(comunidades):
        ancora = max(sorted(comunidade), key=frequencia.get)
        nomes[g] = f"Rotina {g+1:03d} · {ancora[0]} / {ancora[1]}"
    diagnostico = {
        'modularidade_grafo': modularidade,
        'estabilidade_ari_perturbacao_pesos': estabilidade,
        'arestas_repetidas': grafo.number_of_edges(),
        'arestas_filtradas_estatisticamente': len(aceitos),
        'suporte_minimo_tela': suporte,
        'lift_minimo_efetivo': lift_minimo,
    }
    return (mapa,vetores,nomes,diagnostico) if devolver_diagnostico else (mapa,vetores,nomes)

def aprender_variacoes(telas, mapa, nomes):
    """Aprende padrões de escrita usando apenas os núcleos descobertos no arquivo."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.mixture import GaussianMixture

    frequencia = Counter(telas)
    suporte = max(2, math.ceil(math.sqrt(len(telas))/3))
    candidatos = [
        tela for tela, n in frequencia.items()
        if n >= suporte and tela not in mapa
    ]
    fundo = set()
    if nomes and len(candidatos) >= 4:
        valores = np.log([frequencia[tela] for tela in candidatos])[:,None]
        unico = GaussianMixture(1, random_state=42).fit(valores)
        duplo = GaussianMixture(2, random_state=42).fit(valores)
        alto = int(duplo.means_.argmax())
        separacao = float(np.ptp(duplo.means_))
        if duplo.bic(valores) < unico.bic(valores) and separacao > math.log(2):
            pesos = duplo.predict_proba(valores)[:,alto]
            fundo = {tela for tela, peso in zip(candidatos,pesos) if peso >= .9}
    grupo_fundo = len(nomes)
    if fundo:
        nomes[grupo_fundo] = TRANSVERSAL
    simbolos = sorted(frequencia)
    indice = {tela: i for i,tela in enumerate(simbolos)}
    nucleos = [tela for tela in simbolos if tela in mapa or tela in fundo]
    if not nucleos:
        return {}, {}, dict(atividades_transversais=0), set()
    grupos = [mapa.get(tela,grupo_fundo) for tela in nucleos]
    vetorizador = TfidfVectorizer(
        analyzer='char_wb', ngram_range=(2,4), sublinear_tf=True)
    matriz = vetorizador.fit_transform([tela[1] for tela in simbolos])
    matriz_nucleos = matriz[[indice[tela] for tela in nucleos]]
    probabilidades, canonicos = {}, {}
    for inicio in range(0,len(simbolos),256):
        similaridades = cosine_similarity(matriz[inicio:inicio+256],matriz_nucleos)
        for deslocamento, tela in enumerate(simbolos[inicio:inicio+256]):
            apoio = np.zeros(len(nomes))
            apoio_etapas = np.zeros(len(nucleos))
            maior_prefixo = 0
            maior_similaridade = 0.0
            for j,nucleo in enumerate(nucleos):
                if tela[0] != nucleo[0]:
                    continue
                prefixo = 0
                for caractere,original in zip(tela[1],nucleo[1]):
                    if caractere != original:
                        break
                    prefixo += 1
                maior_prefixo = max(maior_prefixo,prefixo)
                maior_similaridade = max(maior_similaridade,float(similaridades[deslocamento,j]))
                peso = similaridades[deslocamento,j] + (min(prefixo,4)/2)**2
                if prefixo < 2:
                    peso *= .15
                peso = peso**3
                apoio[grupos[j]] += peso
                apoio_etapas[j] = peso
            if apoio.sum():
                distribuicao = apoio/apoio.sum()
                lexical_confiavel = maior_prefixo>=2 or maior_similaridade>=.6
                if not lexical_confiavel:
                    distribuicao = .2*distribuicao + .8/len(nomes)
                probabilidades[tela] = distribuicao
                melhor = int(apoio_etapas.argmax())
                if lexical_confiavel and apoio_etapas[melhor]/apoio_etapas.sum() >= .5:
                    canonicos[tela] = nucleos[melhor]
            else:
                probabilidades[tela] = np.full(len(nomes),1/len(nomes))
    return probabilidades,canonicos,dict(
        atividades_transversais=len(fundo),
        variantes_agregadas=sum(a!=b for a,b in canonicos.items()),
        nucleos_lexicais=len(nucleos)), fundo

def atribuir_contexto(usuarios, inicio, telas, mapa, vetores, nomes, probabilidades=None, fundo=None):
    if probabilidades is None:
        probabilidades,_,_,fundo = aprender_variacoes(telas,mapa,nomes)
    rotulos = np.full(len(telas),-1,dtype=int)
    evidencia = np.zeros(len(telas))
    if not nomes:
        return rotulos,evidencia
    fundo = fundo or set()
    grupo_fundo = next((g for g,nome in nomes.items() if nome==TRANSVERSAL),None)
    for seq in usuarios.values():
        for pos,i in enumerate(seq):
            proprio = probabilidades.get(telas[i],np.full(len(nomes),1/len(nomes))).copy()
            afinidade = vetores.get(telas[i])
            if telas[i] in mapa and afinidade is not None and afinidade[mapa[telas[i]]] >= .8:
                proprio *= .1
                proprio[mapa[telas[i]]] += .9
            esquerda = np.zeros(len(nomes))
            direita = np.zeros(len(nomes))
            for vizinho in range(max(0,pos-5),min(len(seq),pos+6)):
                j = seq[vizinho]
                if j==i or abs((inicio[j]-inicio[i]).total_seconds()) > 1200:
                    continue
                contexto = vetores.get(telas[j])
                if contexto is None:
                    continue
                destino = esquerda if vizinho<pos else direita
                destino[:len(contexto)] += contexto/abs(vizinho-pos)
            contexto = esquerda+direita+2*np.sqrt(esquerda*direita)
            if contexto.sum():
                contexto /= contexto.sum()
            votos = proprio*(.15+contexto)
            if grupo_fundo is not None and telas[i] in fundo:
                votos[grupo_fundo] += .35*proprio[grupo_fundo]
            if not votos.sum():
                continue
            votos /= votos.sum()
            melhor = int(votos.argmax())
            evidencia[i] = float(votos[melhor])
            if evidencia[i] >= PARAMETROS['limiar_atribuicao']:
                rotulos[i] = melhor
    return rotulos,evidencia

def separar_tempos(valores):
    """Escolhe 1 a 4 componentes pelo BIC. Ajuste EM em escala logarítmica."""
    x = np.log1p(np.maximum(valores, 0))
    if len(x) < 20 or np.ptp(x) < .5:
        return None
    melhor = None
    for k in range(1, min(4, len(x)//10)+1):
        medias = np.quantile(x, (np.arange(k)+.5)/k)
        variancias = np.full(k, max(.09, float(np.var(x))))
        pesos = np.full(k, 1/k)
        anterior = -np.inf
        for _ in range(70):
            log_prob = (np.log(np.maximum(pesos, 1e-12))-.5*np.log(2*np.pi*variancias)
                        -.5*(x[:,None]-medias)**2/variancias)
            maximo = log_prob.max(axis=1,keepdims=True)
            log_total = maximo[:,0] + np.log(np.exp(log_prob-maximo).sum(axis=1))
            resp = np.exp(log_prob-log_total[:,None])
            massa = np.maximum(resp.sum(axis=0), 1e-10)
            medias = (resp*x[:,None]).sum(axis=0)/massa
            variancias = np.maximum(.09, (resp*(x[:,None]-medias)**2).sum(axis=0)/massa)
            pesos = massa/massa.sum()
            ll = float(log_total.sum())
            if abs(ll-anterior) < 1e-5:
                break
            anterior = ll
        bic = -2*ll+(3*k-1)*math.log(len(x))
        if melhor is None or bic < melhor[0]:
            ordem = np.argsort(medias)
            melhor = bic, medias[ordem], np.sqrt(variancias[ordem]), pesos[ordem]
    _,medias,desvios,pesos = melhor
    if len(medias)<2:
        return None
    # O componente de maior espera representa uma hipótese de fronteira.
    separacao = medias[-1]-medias[-2]
    if separacao < .7:
        return None
    return medias,desvios,pesos

def evidencia_continuidade(esperas, mistura, limite):
    esperas = np.asarray(esperas,dtype=float)
    if mistura is None:
        return 1-esperas/max(limite,1)
    medias,desvios,pesos = mistura
    x = np.log1p(np.maximum(esperas,0))[:,None]
    logp = np.log(np.maximum(pesos,1e-12))-np.log(desvios)-.5*((x-medias)/desvios)**2
    maximo = logp[:,:-1].max(axis=1,keepdims=True)
    curto = maximo[:,0]+np.log(np.exp(logp[:,:-1]-maximo).sum(axis=1))
    return np.clip(curto-logp[:,-1],-10,10)

def sessoes_atividade(usuarios,inicio,fim):
    sessoes = {}
    quantidade = 0
    for seq in usuarios.values():
        limite_fim = fim[seq[0]]
        pausas = []
        for i in seq:
            pausas.append(max(0,(inicio[i]-limite_fim).total_seconds()))
            limite_fim = max(limite_fim,fim[i])
        positivos = [p for p in pausas if p>0]
        mistura = separar_tempos(positivos)
        mediana = statistics.median(positivos) if positivos else 60
        mad = statistics.median(abs(p-mediana) for p in positivos) if positivos else 0
        limite = max(60,mediana+10*max(mad,mediana))
        scores = evidencia_continuidade(pausas,mistura,limite)
        quantidade += 1
        for i,pausa,score in zip(seq,pausas,scores):
            # Uma interrupção global forte separa a escala local.
            if pausa>0 and score < -math.log(99):
                quantidade += 1
            sessoes[i] = quantidade
    return sessoes

def correlacionar(seq, inicio, fim, telas, sessoes=None):
    """Cobertura de caminhos em DAG, com no máximo um predecessor e sucessor."""
    if len(seq) <= 1:
        return [seq] if seq else []
    esperas = [(inicio[b]-fim[a]).total_seconds() for a,b in zip(seq,seq[1:])]
    positivas = [gap for a,b,gap in zip(seq,seq[1:],esperas)
                 if gap >= 0 and inicio[a].date()==inicio[b].date()]
    mistura = separar_tempos(positivas)
    mediana = statistics.median(positivas) if positivas else 60
    mad = statistics.median(abs(g-mediana) for g in positivas) if positivas else 0
    limite = max(60, mediana+4*max(mad, mediana/4))
    if mistura is not None:
        medias, desvios, _ = mistura
        limite = max(60, math.expm1(min(20, max(medias[:-1]+3*desvios[:-1]))))
    transicoes = Counter()
    origens, destinos = Counter(), Counter()
    for a,b,gap in zip(seq,seq[1:],esperas):
        if 0 <= gap <= limite:
            transicoes[telas[a],telas[b]] += 1
            origens[telas[a]] += 1
            destinos[telas[b]] += 1
    total = max(1, sum(transicoes.values()))
    # Colunas extras representam a decisão de encerrar cada caminho.
    ii, jj, custos = list(range(len(seq))), list(range(len(seq),2*len(seq))), [20.0]*len(seq)
    for pos,a in enumerate(seq):
        candidatos = []
        for proximo in range(pos+1,min(len(seq),pos+33)):
            b = seq[proximo]
            if sessoes is not None and sessoes[b]!=sessoes[a]:
                break
            espera = (inicio[b]-fim[a]).total_seconds()
            if espera > limite:
                break
            if espera >= 0:
                candidatos.append((proximo,b,espera))
        if not candidatos:
            continue
        esperas_candidatas = np.array([gap for _,_,gap in candidatos])
        recompensas = evidencia_continuidade(esperas_candidatas,mistura,limite)
        alternativas = float((1/(1+np.exp(-recompensas))).sum())
        penalidade = math.log(max(1,alternativas))
        for (proximo,b,_),recompensa in zip(candidatos,recompensas):
            observado = transicoes[telas[a],telas[b]]
            esperado = origens[telas[a]]*destinos[telas[b]]/total
            ganho = float(recompensa)+math.log((observado+1)/(esperado+1))-penalidade
            if ganho > 0:
                ii.append(pos)
                jj.append(proximo)
                custos.append(20-min(ganho,19))
    matriz = coo_matrix((custos,(ii,jj)), shape=(len(seq),2*len(seq))).tocsr()
    linhas,colunas = min_weight_full_bipartite_matching(matriz)
    sucessor = {int(a):int(b) for a,b in zip(linhas,colunas) if b < len(seq)}
    tem_predecessor = set(sucessor.values())
    casos = []
    for i in range(len(seq)):
        if i in tem_predecessor:
            continue
        caso = [seq[i]]
        while i in sucessor:
            i = sucessor[i]
            caso.append(seq[i])
        casos.append(caso)
    return casos

def periodos_concentrados(seq, dias_usuario, inicio):
    """Detecta vários dias de atividade elevada, em relação à distribuição local."""
    por_dia = defaultdict(list)
    for i in seq:
        por_dia[inicio[i].date()].append(i)
    datas = sorted(dias_usuario)
    taxas = np.array([len(por_dia[d])/dias_usuario[d] for d in datas])
    if len(datas) < 15:
        return []
    mediana = float(np.median(taxas))
    mad = float(np.median(abs(taxas-mediana)))
    limiar = max(.1, mediana*4, mediana+6*mad)
    selecionados = [d for d,taxa in zip(datas,taxas) if taxa >= limiar and len(por_dia[d])>=10]
    # Usa o calendário de presença observado, sem presumir trabalho em feriados.
    posicao_dia = {dia:i for i,dia in enumerate(datas)}
    periodos = []
    for dia in selecionados:
        if not periodos or posicao_dia[dia]-posicao_dia[periodos[-1][-1]] > 2:
            periodos.append([])
        periodos[-1].append(dia)
    return [[i for dia in periodo for i in por_dia[dia]]
            for periodo in periodos if len(periodo)>=3]

ATRIBUTOS_MODELO = (
    'codigo_racf', 'nome_programa', 'nome_tela_foco',
    'data_hora_inicio_exec', 'data_hora_fim_exec',
)

def _descobrir_grafo(rows, devolver_diagnostico=False):
    # Barreira explícita contra rótulos, IDs de execução e campos de referência.
    observacoes = [{campo:row[campo] for campo in ATRIBUTOS_MODELO} for row in rows]
    usuarios, inicio, fim, telas = preparar_observacoes(observacoes)
    mapa,vetores,nomes,diagnostico_grafo = aprender_grupos(usuarios,inicio,telas,True)
    probabilidades,canonicos,diagnostico_variacoes,fundo = aprender_variacoes(telas,mapa,nomes)
    rotulos,evidencia = atribuir_contexto(
        usuarios,inicio,telas,mapa,vetores,nomes,probabilidades,fundo)
    etapas = [canonicos.get(tela,tela) for tela in telas]
    fluxos = defaultdict(list)
    sessoes = sessoes_atividade(usuarios,inicio,fim)
    dias = {}
    for usuario, seq in usuarios.items():
        dias[usuario] = Counter(inicio[i].date() for i in seq)
        for i in seq:
            fluxos[usuario,int(rotulos[i])].append(i)
    casos, locais, episodios = [],{},{}
    numero_local,numero_episodio = 0,0
    for (usuario,grupo),seq in fluxos.items():
        # Os parâmetros de correlação são aprendidos na rotina inteira, mantendo
        # as sessões apenas como barreiras para os vínculos da escala local.
        if grupo>=0 and nomes.get(grupo)!=TRANSVERSAL:
            curtos = correlacionar(seq,inicio,fim,etapas,sessoes)
        else:
            curtos = [[i] for i in seq]
        for caso in curtos:
            numero_local += 1
            for i in caso:
                locais[i] = numero_local
        longos = (periodos_concentrados(seq,dias[usuario],inicio)
                  if grupo>=0 and nomes.get(grupo)!=TRANSVERSAL else [])
        for caso in longos:
            numero_episodio += 1
            for i in caso:
                episodios[i] = numero_episodio
        usados = {i for caso in longos for i in caso}
        casos.extend(longos)
        casos.extend([[i for i in c if i not in usados] for c in curtos if any(i not in usados for i in c)])
    resultado = []
    criterios = Counter()
    for caso in casos:
        convertido = []
        for i in caso:
            proprio = vetores.get(telas[i])
            nucleo = telas[i] in mapa and proprio is not None and proprio[mapa[telas[i]]] >= .8
            criterio = 'nucleo_recorrente' if nucleo else 'variacao_lexical_contextual'
            if rotulos[i]<0:
                criterio = 'contexto_insuficiente'
            criterios[criterio] += 1
            convertido.append(Evento(
                i+2,observacoes[i]['codigo_racf'],inicio[i],fim[i],
                etapas[i][0]+' / '+etapas[i][1],nomes.get(int(rotulos[i]),INCERTO),
                float(evidencia[i]),criterio,locais[i],episodios.get(i,0)))
        resultado.append(convertido)
    resultado.sort(key=lambda caso:(caso[0].inicio,caso[0].linha))
    diagnostico = {
        'atributos_usados': list(ATRIBUTOS_MODELO),
        'telas_distintas': len(set(telas)),
        'telas_no_grafo': len(mapa),
        'grupos': len(nomes),
        'criterios': dict(criterios),
        'sessoes_atividade': len(set(sessoes.values())),
        'casos_locais': numero_local,
        'episodios_longos': numero_episodio,
        'parametros': PARAMETROS,
        'grafo': diagnostico_grafo,
        'variacoes': diagnostico_variacoes,
    }
    return (resultado,diagnostico) if devolver_diagnostico else resultado


def descobrir(rows, devolver_diagnostico=False):
    """Seleciona o correlacionador por evidência observacional de interrupções.
    A decisão não consulta referências, pontuações, nomes de arquivo ou tamanho.
    """
    observacoes=[{k:r[k] for k in ATRIBUTOS_MODELO}for r in rows]
    resultado,diagnostico=_descobrir_grafo(observacoes,True)
    diagnostico['metodo']='grafo_sem_interrupcoes_detectadas'
    if diagnostico['variacoes']['atividades_transversais']:
        from motor_adaptativo import descobrir as descobrir_sequencias
        resultado,diagnostico=descobrir_sequencias(observacoes,diagnostico)
    return (resultado,diagnostico)if devolver_diagnostico else resultado

```

### motor_sequencial.py

```python
"""Correlação sequencial experimental sem campos de referência.
Minimiza energia lexical + transição + espera por busca em feixe.
A concorrência máxima observada limita as trilhas físicas sem sobreposição.
Os ciclos são hipóteses aprendidas, não modelos de negócio conhecidos.
"""
from collections import Counter, defaultdict
from functools import lru_cache
import math, heapq
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.optimize import linear_sum_assignment
import motor_descoberta as m

def construir(rows,prefixo_maximo=4):
    obs=[{k:r[k] for k in m.ATRIBUTOS_MODELO}for r in rows]
    u,ini,fim,telas=m.preparar_observacoes(obs)
    mapa,v,nomes=m.aprender_grupos(u,ini,telas)
    lex,canon,diag,fundo=m.aprender_variacoes(telas,mapa,nomes)
    z,q=m.atribuir_contexto(u,ini,telas,mapa,v,nomes,lex,fundo)
    freq=Counter(telas)
    symbols=sorted(freq);idx={s:i for i,s in enumerate(symbols)}
    treino=[s for s in symbols if s in mapa or s in fundo]
    grupos=[mapa.get(s,len(nomes)-1) for s in treino]
    tf=TfidfVectorizer(analyzer='char_wb',ngram_range=(2,4),sublinear_tf=True)
    mat=tf.fit_transform(s[1]for s in symbols)
    sim=cosine_similarity(mat,mat[[idx[s]for s in treino]])
    prob=np.zeros((len(symbols),len(treino)))
    for i,s in enumerate(symbols):
        maxpref=0;maxsim=0
        valid=np.array([s[0]==t[0]for t in treino])
        for j,t in enumerate(treino):
            if not valid[j]:continue
            pref=0
            for a,b in zip(s[1],t[1]):
                if a!=b:break
                pref+=1
            maxpref=max(maxpref,pref);maxsim=max(maxsim,sim[i,j])
            w=sim[i,j]+(min(pref,prefixo_maximo)/2)**2
            if pref<2:w*=.15
            prob[i,j]=w**3
        if prob[i].sum():prob[i]/=prob[i].sum()
        if valid.sum() and (not prob[i].sum() or (maxpref<2 and maxsim<.6)):
            prob[i]=.2*prob[i]+.8*valid/valid.sum()
    probs=prob[[idx[s]for s in telas]]
    est=probs.argmax(axis=1);conf=probs.max(axis=1)
    vsize=len(treino)
    c=np.zeros((vsize,vsize))
    for seq in u.values():
        for p,i in enumerate(seq):
            if conf[i]<.5:continue
            for j in seq[p+1:p+10]:
                gap=(ini[j]-fim[i]).total_seconds()
                if gap>900:break
                if gap<-300 or conf[j]<.5:continue
                if grupos[est[i]]!=grupos[est[j]]:continue
                c[est[i],est[j]]+=np.exp(-abs(gap-40)/60)*conf[i]*conf[j]
    prior=probs.mean(axis=0)+1e-5;prior/=prior.sum()
    T=np.zeros_like(c)
    for g in sorted(set(grupos)):
        ids=[i for i,x in enumerate(grupos)if x==g]
        if len(ids)<2 or nomes[g]==m.TRANSVERSAL:
            T[ids]=prior
            continue
        sub=c[np.ix_(ids,ids)].copy()
        # Ganho direcional relativo à frequência de cada destino.
        esperada=np.outer(sub.sum(1),sub.sum(0))/max(1e-9,sub.sum())
        score=np.log((sub+1)/(esperada+1))
        np.fill_diagonal(score,-1e6)
        a,b=linear_sum_assignment(score,maximize=True)
        suc={int(x):int(y)for x,y in zip(a,b)}
        ciclos=[];visit=set()
        for i in range(len(ids)):
            if i in visit:continue
            ciclo=[];j=i
            while j not in visit:visit.add(j);ciclo.append(j);j=suc[j]
            ciclos.append(ciclo)
        while len(ciclos)>1:
            melhor=None
            c0=ciclos[0]
            for pos,cc in enumerate(ciclos[1:],1):
                for i in c0:
                    for j in cc:
                        ganho=score[i,suc[j]]+score[j,suc[i]]-score[i,suc[i]]-score[j,suc[j]]
                        if melhor is None or ganho>melhor[0]:melhor=(ganho,pos,i,j)
            _,pos,i,j=melhor;suc[i],suc[j]=suc[j],suc[i]
            ciclos[0]+=ciclos.pop(pos)
        for i in range(len(ids)):
            aprendido=c[ids[i]]+prior
            aprendido/=aprendido.sum()
            T[ids[i]]=.1*aprendido
            T[ids[i],ids[suc[i]]]+=.9
    return (u,ini,fim,telas,z,q,nomes,diag),probs,treino,grupos,T,prior


def rotear(seq,ini,fim,z,names,probs,T,prior,groups,root,coef=.5,beam=128,macro_mode='preserve'):
    ts=np.array([(ini[i]-ini[seq[0]]).total_seconds()for i in seq]);te=np.array([(fim[i]-ini[seq[0]]).total_seconds()for i in seq])
    active=[];cap=1
    for b in range(len(seq)):
        while active and active[0]<=ts[b]:heapq.heappop(active)
        heapq.heappush(active,te[b]);cap=max(cap,len(active))
    bg=np.array([names.get(int(z[i]))==m.TRANSVERSAL for i in seq])
    val=np.array([names.get(g)!=m.TRANSVERSAL for g in groups])
    @lru_cache(None)
    def options(b,leaf):
        own=probs[seq[b]].copy();own[~val]=0
        if not own.sum():return [(-1,0.,False,1.)]
        own/=own.sum();cond=prior if leaf<0 else .8*T[leaf]+.2*prior
        costs=-np.log(np.maximum(own,1e-100))-coef*np.log(np.maximum(cond,1e-100))
        ps=np.exp(-(costs-costs.min()));ps/=ps.sum()
        return [(int(st),float(costs[st]),bool(leaf>=0 and(groups[leaf]!=groups[st]or .2*prior[st]>.8*T[leaf,st])),float(ps[st]))for st in np.argsort(costs)[:2]if own[st]>0]
    @lru_cache(None)
    def temporal(a,b):
        if a<0:return math.log(max(100,ts[-1]))
        gap=ts[b]-te[a]
        if gap<0:return math.inf
        den=.9*math.exp(-abs(gap-40)/40)/80+.1*math.exp(-abs(gap-40)/180)/360
        return -math.log(max(1e-30,den))
    states={(): (0.,None)}
    for b in range(len(seq)):
        new={}
        for tails,(score,hist)in states.items():
            candidates=list(tails)+([(-1,-1)]if len(tails)<cap else [])
            for a,leaf in candidates:
                tc=temporal(a,b)
                if not math.isfinite(tc):continue
                opts=[(leaf,0.,False,1.)]if bg[b]else options(b,leaf)
                for st,cost,restart,conf in opts:
                    macro=st>=0 and groups[st]in(root or ())
                    newleaf=leaf if macro and macro_mode=='preserve' else st
                    key=tuple(sorted([v for v in tails if v!=(a,leaf)]+[(b,newleaf)]))
                    total=score+tc+cost
                    if key not in new or total<new[key][0]:new[key]=(total,(hist,a,b,st,restart,conf))
        if not new:raise RuntimeError(('empty',b,cap))
        states=dict(sorted(new.items(),key=lambda item:item[1][0])[:beam])
    _,h=min(states.values(),key=lambda v:v[0]);succ={};starts=[];phases={};resets={};conf={}
    while h is not None:
        h,a,b,st,restart,c=h;phases[seq[b]]=st;resets[seq[b]]=restart;conf[seq[b]]=c
        if a<0:starts.append(b)
        else:succ[a]=b
    paths=[]
    for a in sorted(starts):
        p=[seq[a]]
        while a in succ:a=succ[a];p.append(seq[a])
        paths.append(p)
    return paths,phases,resets,conf

def executar(rows,res,probs,train,groups,T,prior,coef=.5,beam=128,macro_mode='preserve',parent_mode='until_background'):
    users,ini,fim,symbols,z,q,names,d=res
    roots=defaultdict(set);period_ids={};nperiod=0
    for u,seq in users.items():
        days=Counter(ini[i].date()for i in seq)
        for g in names:
            if names[g]==m.TRANSVERSAL:continue
            for per in m.periodos_concentrados([i for i in seq if z[i]==g],days,ini):
                nperiod+=1
                for day in {ini[i].date()for i in per}:roots[u,day].add(g);period_ids[u,day,g]=nperiod
    paths=[];phases={};resets={};confidence={}
    for u,seq in users.items():
        days=defaultdict(list)
        for i in seq:days[ini[i].date()].append(i)
        for day,ss in days.items():
            pp,ff,rr,cc=rotear(ss,ini,fim,z,names,probs,T,prior,groups,roots.get((u,day)),coef,beam,macro_mode)
            paths.extend(pp);phases.update(ff);resets.update(rr);confidence.update(cc)
    labels={i:int(z[i])if names.get(int(z[i]))==m.TRANSVERSAL or phases[i]<0 else groups[phases[i]]for i in range(len(rows))}
    cases=[];parents=defaultdict(list);local_ids={};episode_ids={};nlocal=0
    for p in paths:
        cur=[];parent=None; nlocal+=1
        for i in p:
            u=rows[i]['codigo_racf'];day=ini[i].date();root=roots.get((u,day),set());isroot=labels[i]in root
            isbg=names.get(labels[i])==m.TRANSVERSAL
            if isbg or resets[i]:nlocal+=1
            local_ids[i]=nlocal
            if isroot:
                if cur:cases.append(cur);cur=[]
                parents[period_ids[u,day,labels[i]]].append(i);parent=period_ids[u,day,labels[i]]
            else:
                if isbg or resets[i]:
                    if cur:cases.append(cur);cur=[]
                    if isbg or parent_mode!='until_background':parent=None
                if parent is not None and parent_mode in ('sticky','until_background'):parents[parent].append(i)
                else:cur.append(i)
        if cur:cases.append(cur)
    for eid,members in parents.items():
        for i in members:episode_ids[i]=eid
    cases+=list(parents.values())
    assert sorted(i for c in cases for i in c)==list(range(len(rows)))
    return [[m.Evento(i+2,rows[i]['codigo_racf'],ini[i],fim[i],train[phases[i]][0]+' / '+train[phases[i]][1]if phases[i]>=0 else symbols[i][0]+' / '+symbols[i][1],names.get(labels[i],m.INCERTO),float(confidence[i]),'sequencia_restrita',local_ids[i],episode_ids.get(i,0))for i in sorted(c,key=lambda j:(ini[j],j))]for c in cases]



def descobrir(observacoes, diagnostico):
    """Somente chamado quando o detector encontra atividades transversais."""
    res,p,train,groups,T,prior=construir(observacoes)
    if not train:
        raise RuntimeError('Não há protótipos para a correlação sequencial.')
    resultado=executar(observacoes,res,p,train,groups,T,prior)
    resultado.sort(key=lambda c:(c[0].inicio,c[0].linha))
    diagnostico=dict(diagnostico)
    diagnostico.update(metodo='sequencial_com_interrupcoes',
        casos_locais=len({e.caso_local for c in resultado for e in c}),
        episodios_longos=len({e.episodio_longo for c in resultado for e in c if e.episodio_longo}),
        criterios={'sequencia_restrita':len(observacoes)},
        sequencial={'largura_feixe':128,'peso_transicoes':.5,
                    'prototipos':len(train),'sobreposicao_permitida':False,
                    'modelo_temporal':'mistura de Laplace: esperas 40/180 segundos',
                    'contexto_episodio':'mantido até uma atividade transversal'})
    return resultado,diagnostico

```

### motor_probabilistico.py

```python
"""Modelo 6.0: correlação de fluxos com fases marginalizadas e Viterbi.
As funções recebem somente observações sem identificadores ou referências.
O feixe explora as trilhas físicas; os eventos ambíguos mantêm uma distribuição
sobre fases. A decodificação final é exata apenas condicional às trilhas escolhidas.
"""
from collections import Counter, defaultdict
from functools import lru_cache
import math
import heapq
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.special import logsumexp
import motor_descoberta as m
import motor_sequencial as anterior


def _espera_padrao(gap):
    return max(1e-30,.9*math.exp(-abs(gap-40)/40)/80+.1*math.exp(-abs(gap-40)/180)/360)

def aprender_tempos(res,p,T,permutacoes=8,regularizacao=0.,ruido=.005):
 users,ini,fim,s,z,q,names,d=res
 state=p.argmax(axis=1);conf=p.max(axis=1);nxt=T.argmax(axis=1)
 banned={g for g in names if names[g]==m.TRANSVERSAL}
 for u,seq in users.items():
  days=Counter(ini[i].date()for i in seq)
  for g in names:
   if m.periodos_concentrados([i for i in seq if z[i]==g],days,ini):banned.add(g)
 valid=(conf>=.8)&np.array([int(g)not in banned for g in z])
 aa=[];bb=[];gaps=[];daily=[]
 for seq in users.values():
  ds=defaultdict(list)
  for i in seq:
   if valid[i]:ds[ini[i].date()].append(i)
  for ss in ds.values():
   daily.append(np.array(ss))
   for pos,i in enumerate(ss):
    for j in ss[pos+1:pos+129]:
     gap=(ini[j]-fim[i]).total_seconds()
     if gap>1800:break
     if gap>=0:aa.append(i);bb.append(j);gaps.append(int(gap//5))
 aa=np.array(aa,dtype=int);bb=np.array(bb,dtype=int);gaps=np.array(gaps,dtype=int)
 real=np.bincount(gaps[nxt[state[aa]]==state[bb]],minlength=361)
 rng=np.random.default_rng(42);nulls=[]
 for _ in range(permutacoes):
  shuffled=state.copy()
  for ss in daily:shuffled[ss]=rng.permutation(shuffled[ss])
  nulls.append(np.bincount(gaps[nxt[shuffled[aa]]==shuffled[bb]],minlength=361))
 null=np.mean(nulls,axis=0)
 excess=gaussian_filter1d(np.maximum(0,real-null-regularizacao*np.sqrt(null+1)),1.)
 if not excess.sum():return _espera_padrao,{'metodo':'fallback_sem_excesso_temporal'}
 excess/=excess.sum()*5
 table=(1-ruido)*np.repeat(excess,5)+ruido/1805
 @lru_cache(None)
 def density(gap):
  x=int(gap)
  return max(1e-30,float(table[x])if x<len(table)else ruido*math.exp(-(x-1805)/1805)/1805)
 return density,{'metodo':'excesso_sobre_permutacoes','pares':len(aa),'transicoes':int(sum(real)),'contagem_nula':float(sum(null)),'pico_segundos':int(np.argmax(excess))*5,'horizonte_segundos':1800,'permutacoes':permutacoes,'regularizacao':regularizacao,'piso':ruido}


def rotear_marginal(seq,ini,fim,z,names,probs,T,prior,groups,root,densidade,coef=.5,beam=128,macro_mode='preserve',clamp=.98,ancora_posterior=False):
 ts=np.array([(ini[i]-ini[seq[0]]).total_seconds()for i in seq]);te=np.array([(fim[i]-ini[seq[0]]).total_seconds()for i in seq])
 active=[];cap=1
 for b in range(len(seq)):
  while active and active[0]<=ts[b]:heapq.heappop(active)
  heapq.heappush(active,te[b]);cap=max(cap,len(active))
 normal=np.array([names[g]!=m.TRANSVERSAL and g not in(root or())for g in groups]);valid=np.where(normal)[0]
 pv=prior[valid].copy();pv/=max(1e-30,pv.sum())
 trans=(.8*T[np.ix_(valid,valid)]+.2*pv)**coef;trans/=trans.sum(1)[:,None]
 beliefs={-1:pv};nextid=len(valid);updates={};core={}
 for j in range(len(valid)):beliefs[j]=np.eye(1,len(valid),j)[0]
 for j in range(len(valid)):core[j]=trans[j]
 emissions=[];skips=[]
 for i in seq:
  isbg=names.get(int(z[i]))==m.TRANSVERSAL
  isroot=sum(probs[i,j]for j,g in enumerate(groups)if g in(root or()))>=.7
  own=probs[i,valid].copy()
  if own.sum():own/=own.sum()
  else:own=pv.copy()
  emissions.append(own);skips.append(isbg or isroot or not len(valid))
 @lru_cache(None)
 def update(b,prev):
  nonlocal nextid
  if skips[b]:return prev,0.
  pred=core[prev]if prev in core else beliefs[prev]@trans
  post=pred*emissions[b];mass=float(post.sum())
  if mass<=1e-100:post=pv.copy();mass=1e-100
  else:post/=mass
  anchor=post if ancora_posterior else emissions[b]
  if anchor.max()>=clamp:new=int(anchor.argmax())
  else:new=nextid;nextid+=1;beliefs[new]=post
  return new,-math.log(mass)
 @lru_cache(None)
 def temporal(a,b):
  if a<0:return math.log(max(100,ts[-1]))
  gap=ts[b]-te[a]
  return math.inf if gap<0 else -math.log(densidade(gap))
 states={(): (0.,None)}
 for b in range(len(seq)):
  new={}
  for tails,(score,hist)in states.items():
   for aa,belief in list(tails)+([(-1,-1)]if len(tails)<cap else []):
    tc=temporal(aa,b)
    if not math.isfinite(tc):continue
    bid,cost=update(b,belief)
    key=tuple(sorted([v for v in tails if v!=(aa,belief)]+[(b,bid)]))
    total=score+tc+cost
    if key not in new or total<new[key][0]:new[key]=(total,(hist,aa,b,bid))
  if not new:raise RuntimeError(('empty',b,cap))
  states=dict(sorted(new.items(),key=lambda x:x[1][0])[:beam])
 _,h=min(states.values(),key=lambda v:v[0]);succ={};starts=[];phase={};resets={};conf={}
 while h is not None:
  h,aa,b,bid=h;i=seq[b]
  phase[i]=int(probs[i].argmax())if skips[b]else int(valid[beliefs[bid].argmax()]);resets[i]=False;conf[i]=float(beliefs[bid].max())if len(valid)else 1.
  if aa<0:starts.append(b)
  else:succ[aa]=b
 paths=[]
 for aa in sorted(starts):
  path=[seq[aa]]
  while aa in succ:aa=succ[aa];path.append(seq[aa])
  paths.append(path)
 return paths,phase,resets,conf


def suavizar_fases(res,p,groups,T,prior,records,coef=.5):
 users,ini,fim,s,z,q,names,d=res
 roots={}
 from collections import Counter
 for user,seq in users.items():
  days=Counter(ini[i].date()for i in seq)
  for g in names:
   if names[g]==m.TRANSVERSAL:continue
   for per in m.periodos_concentrados([i for i in seq if z[i]==g],days,ini):
    for i in per:roots.setdefault((user,ini[i].date()),set()).add(g)
 out=[]
 for paths,oldphase,oldreset,conf in records:
  phase=dict(oldphase);reset=dict(oldreset);confs=dict(conf)
  for path in paths:
   user=next(user for user,seq in users.items()if path[0]in seq);root=roots.get((user,ini[path[0]].date()),set())
   valid=np.array([i for i,g in enumerate(groups)if names[g]!=m.TRANSVERSAL and g not in root],dtype=int);idx={int(v):i for i,v in enumerate(valid)}
   rows=[i for i in path if names.get(int(z[i]))!=m.TRANSVERSAL and (not root or sum(p[i,j]for j,g in enumerate(groups)if g in root)<.7)and p[i,valid].sum()>0]
   if not rows or not len(valid):continue
   transitions=coef*np.log(np.maximum(.8*T[np.ix_(valid,valid)]+.2*prior[valid],1e-100))
   v=np.log(np.maximum(prior[valid],1e-100))*coef;backs=[]
   for i in rows:
    pair=v[:,None]+transitions
    if not backs:pair=np.broadcast_to(v[None,:],pair.shape)
    back=pair.argmax(axis=0);v=pair[back,np.arange(len(valid))]+np.log(np.maximum(p[i,valid],1e-100));backs.append(back)
   st=int(v.argmax());states=[]
   for back in reversed(backs):states.append(int(valid[st]));st=int(back[st])
   for i,st in zip(rows,reversed(states)):phase[i]=st
   # Relative posterior support conditional on this physical-route hypothesis.
   emit=np.log(np.maximum(p[np.ix_(rows,valid)],1e-100))
   alpha=np.empty_like(emit);alpha[0]=coef*np.log(np.maximum(prior[valid],1e-100))+emit[0]
   alpha[0]-=logsumexp(alpha[0])
   for j in range(1,len(rows)):
    alpha[j]=emit[j]+logsumexp(alpha[j-1][:,None]+transitions,axis=0)
    alpha[j]-=logsumexp(alpha[j])
   beta=np.zeros_like(emit)
   for j in range(len(rows)-2,-1,-1):
    beta[j]=logsumexp(transitions+emit[j+1][None,:]+beta[j+1][None,:],axis=1)
    beta[j]-=logsumexp(beta[j])
   post=alpha+beta;post=np.exp(post-logsumexp(post,axis=1)[:,None])
   for j,i in enumerate(rows):confs[i]=float(post[j,idx[phase[i]]])
   leaf=-1
   for i in path:
    if names.get(int(z[i]))==m.TRANSVERSAL:reset[i]=False;continue
    if phase[i]>=0 and groups[phase[i]]in root:reset[i]=False;continue
    st=phase[i]
    reset[i]=leaf>=0 and(groups[leaf]!=groups[st]or .2*prior[st]>.8*T[leaf,st]);leaf=st
  out.append((paths,phase,reset,confs))
 return out


def reconstruir_casos(rows,res,train,groups,T,prior,records):
 u,ini,fim,s,z,q,names,d=res
 phases={};resets={};confs={};paths=[]
 for pp,ff,rr,cc in records:paths+=pp;phases.update(ff);resets.update(rr);confs.update(cc)
 labels={i:int(z[i])if names.get(int(z[i]))==m.TRANSVERSAL or phases[i]<0 else groups[phases[i]]for i in range(len(rows))}
 roots=defaultdict(set);epids={};ep=0
 for user,seq in u.items():
  days=Counter(ini[i].date()for i in seq)
  for g in names:
   if names[g]==m.TRANSVERSAL:continue
   for per in m.periodos_concentrados([i for i in seq if z[i]==g],days,ini):
    ep+=1
    for day in {ini[i].date()for i in per}:roots[user,day].add(g);epids[user,day,g]=ep
 cases=[];parents=defaultdict(list);local={};episode={};nc=0
 for p in paths:
  cur=[];parent=None;nc+=1
  for pos,i in enumerate(p):
   user=rows[i]['codigo_racf'];day=ini[i].date();root=labels[i]in roots.get((user,day),())
   bg=names.get(labels[i])==m.TRANSVERSAL
   if root:
    if cur:cases.append(cur);cur=[]
    parent=epids[user,day,labels[i]];parents[parent].append(i);episode[i]=parent
   else:
    boundary=bg or resets[i]
    if boundary:
     if cur:cases.append(cur);cur=[]
     nc+=1
     if bg:parent=None
    if parent is None:cur.append(i)
    else:parents[parent].append(i);episode[i]=parent
   local[i]=nc
  if cur:cases.append(cur)
 cases+=list(parents.values())
 assert sorted(i for c in cases for i in c)==list(range(len(rows)))
 return [[m.Evento(i+2,rows[i]['codigo_racf'],ini[i],fim[i],' / '.join(train[phases[i]])if phases[i]>=0 else ' / '.join(s[i]),names.get(labels[i],m.INCERTO),confs[i],'fase_marginal_viterbi',local[i],episode.get(i,0))for i in sorted(c,key=lambda j:(ini[j],j))]for c in cases]



def descobrir(observacoes,diagnostico):
    # Repeat the whitelist at the new inference boundary.
    observacoes=[{k:r[k]for k in m.ATRIBUTOS_MODELO}for r in observacoes]
    res,p,train,groups,T,prior=anterior.construir(observacoes)
    users,ini,fim,s,z,q,names,d=res
    densidade,diagnostico_tempo=aprender_tempos(res,p,T)
    roots=defaultdict(set)
    for user,seq in users.items():
        days=Counter(ini[i].date()for i in seq)
        for g in names:
            if names[g]==m.TRANSVERSAL:continue
            for per in m.periodos_concentrados([i for i in seq if z[i]==g],days,ini):
                for day in {ini[i].date()for i in per}:roots[user,day].add(g)
    records=[]
    for user,seq in users.items():
        daily=defaultdict(list)
        for i in seq:daily[ini[i].date()].append(i)
        for day,indices in daily.items():
            records.append(rotear_marginal(indices,ini,fim,z,names,p,T,prior,groups,roots.get((user,day)),densidade))
    decoded=suavizar_fases(res,p,groups,T,prior,records)
    resultado=reconstruir_casos(observacoes,res,train,groups,T,prior,decoded)
    resultado.sort(key=lambda c:(c[0].inicio,c[0].linha))
    diagnostico=dict(diagnostico)
    diagnostico.update(metodo='fluxos_marginalizados_e_viterbi',
        criterios={'fase_marginal_viterbi':len(observacoes)},
        casos_locais=len({e.caso_local for c in resultado for e in c}),
        episodios_longos=len({e.episodio_longo for c in resultado for e in c if e.episodio_longo}),
        sequencial={'largura_feixe':128,'temperatura_transicoes':.5,
                    'peso_decodificacao':.5,'ancora_lexical':.98,
                    'prototipos':len(train),'sobreposicao_permitida':False,
                    'tempos':diagnostico_tempo,
                    'evidencia':'posterior relativo da fase, condicionado às trilhas; sem calibração externa'})
    return resultado,diagnostico

```

### motor_adaptativo.py

```python
"""Modelo 7: entradas aprendidas, refinamento temporal e hierarquia de tarefas.
Nenhuma função de inferência recebe referências ou IDs de execução.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from dataclasses import replace
import math
import numpy as np
import motor_descoberta as m
import motor_sequencial as etapas
import motor_probabilistico as probabilistico


def episodios_observados(res):
    usuarios,inicio,fim,telas,rotulos,evidencia,nomes,diag=res
    resultado=defaultdict(set)
    for usuario,seq in usuarios.items():
        dias=Counter(inicio[i].date()for i in seq)
        for grupo in nomes:
            if nomes[grupo]==m.TRANSVERSAL:continue
            for periodo in m.periodos_concentrados([i for i in seq if rotulos[i]==grupo],dias,inicio):
                for dia in {inicio[i].date()for i in periodo}:resultado[usuario,dia].add(grupo)
    return resultado


def correlacionar(res,p,grupos,T,prior,densidade,temperatura=.75,posterior=True):
    usuarios,inicio,fim,telas,z,q,nomes,diag=res
    episodios=episodios_observados(res)
    registros=[]
    for usuario,seq in usuarios.items():
        dias=defaultdict(list)
        for i in seq:dias[inicio[i].date()].append(i)
        for dia,indices in dias.items():
            registros.append(probabilistico.rotear_marginal(indices,inicio,fim,z,nomes,p,T,prior,grupos,episodios.get((usuario,dia)),densidade,coef=temperatura,ancora_posterior=posterior))
    return registros

def estimar_entradas(res,p,groups,prior,records,strength=.5,group_weight=False):
 users,ini,fim,s,z,q,names,d=res;roots=episodios_observados(res);owner={i:u for u,seq in users.items()for i in seq};counts=np.zeros(len(prior))
 for paths,_,_,_ in records:
  for path in paths:
   if roots.get((owner[path[0]],ini[path[0]].date())):continue
   last=-1;first=True
   for i in path:
    if names.get(int(z[i]))==m.TRANSVERSAL:continue
    st=int(p[i].argmax())if p[i].max()>=.8 else -1
    if st>=0 and(first or(last>=0 and groups[last]!=groups[st])):counts[st]+=float(p[i,st])
    last=st;first=False
 new=prior.copy();stats=[];ordinary=[]
 for group in set(groups):
  ids=np.array([j for j,g in enumerate(groups)if g==group]);total=counts[ids].sum()
  if total<5:continue
  original=prior[ids]/prior[ids].sum();entry=(counts[ids]+5*original)/(total+5)
  new[ids]=entry*prior[ids].sum();ordinary.append(group)
  stats.append((group,round(float(total),1),int(ids[entry.argmax()]),round(float(entry.max()),3)))
 if group_weight and ordinary:
  mask=np.array([g in ordinary for g in groups]);totalmass=prior[mask].sum();total=counts[mask].sum()
  for group in ordinary:
   ids=np.array([j for j,g in enumerate(groups)if g==group]);new[ids]*=totalmass*(counts[ids].sum()/total)/new[ids].sum()
 return (1-strength)*prior+strength*new,stats

def blocos_temporais(res,p,groups,T,records,initial,blend=.9,penalty=1.):
 users,ini,fim,s,z,q,names,d=res;roots=episodios_observados(res);owner={i:user for user,ss in users.items()for i in ss};gaps=[]
 for paths,_,_,_ in records:
  for path in paths:
   root=roots.get((owner[path[0]],ini[path[0]].date()),set())
   for i,j in zip(path,path[1:]):
    if p[i].max()<.8 or p[j].max()<.8:continue
    aa=int(p[i].argmax());bb=int(p[j].argmax())
    if groups[aa]in root or groups[bb]in root or names[groups[aa]]==m.TRANSVERSAL or names[groups[bb]]==m.TRANSVERSAL:continue
    if groups[aa]!=groups[bb]or T[aa,bb]<.5:continue
    gap=(ini[j]-fim[i]).total_seconds()
    if 0<=gap<=1800:gaps.append(gap)
 if len(gaps)<20:return initial,{'metodo':'fallback_poucas_arestas','amostras':len(gaps)}
 hist=np.bincount(np.array(gaps,dtype=int)//5,minlength=361);cum=np.r_[0,np.cumsum(hist)];dp=np.full(362,-np.inf);dp[0]=0;back=np.zeros(362,dtype=int);lam=penalty*math.log(len(gaps))
 for end in range(1,362):
  starts=np.arange(end);n=cum[end]-cum[:end];length=end-starts;ll=np.where(n>0,n*np.log(np.maximum(n,1)/length),0.);score=dp[:end]+ll-lam;best=int(score.argmax());dp[end]=score[best];back[end]=best
 end=361;segments=[];density=np.zeros(361)
 while end:
  start=int(back[end]);count=int(cum[end]-cum[start]);rate=count/(max(1,len(gaps))*5*(end-start));density[start:end]=rate;segments.append((start*5,end*5,count,rate));end=start
 @lru_cache(None)
 def kernel(gap):
  value=float(density[int(gap//5)])if gap<1805 else 0.
  return max(1e-100,blend*value+(1-blend)*initial(gap))
 return kernel,{'metodo':'histograma_segmentado','amostras':len(gaps),'blocos':list(reversed(segments)),'peso_empirico':blend,'penalidade_log_amostras':penalty}


def preservar_tarefas(casos,res,grupos,prior,decodificados,entradas,limiar=.98):
    episodios=episodios_observados(res)
    familias_episodio={res[6][g]for gs in episodios.values()for g in gs}
    pais={}
    for caso in casos:
        if any(e.episodio_longo for e in caso):
            pais[next(e.episodio_longo for e in caso if e.episodio_longo)]=caso
    if not pais:return casos,{'locais_protegidos':0,'eventos_restituidos':0}
    fases={i:st for _,ph,_,_ in decodificados for i,st in ph.items()}
    grupos=np.asarray(grupos)
    elegiveis={int(g):int(st)for g,n,st,confianca in entradas if n>=5 and confianca>=.5}
    eventos={e.linha:e for caso in casos for e in caso}
    locais=defaultdict(list)
    for e in eventos.values():locais[e.caso_local].append(e)
    restituidos=set();protegidos=0
    for local in locais.values():
        local.sort(key=lambda e:(e.inicio,e.linha))
        trabalho=[e for e in local if e.familia not in familias_episodio and e.familia!=m.TRANSVERSAL]
        candidatos=[e for e in trabalho if e.episodio_longo]
        if not candidatos:continue
        primeiro=trabalho[0];fase=fases.get(primeiro.linha-2,-1)
        if fase<0 or elegiveis.get(int(grupos[fase]))!=fase or primeiro.evidencia<limiar:continue
        restituidos.update(e.linha for e in candidatos);protegidos+=1
    mantidos=[[e for e in caso if e.linha not in restituidos]for caso in pais.values()]
    mantidos=[c for c in mantidos if c]
    selecionados={e.linha for caso in mantidos for e in caso}
    filhos=defaultdict(list)
    for e in eventos.values():
        if e.linha not in selecionados:
            filhos[e.caso_local].append(replace(e,episodio_longo=0,criterio='tarefa_local_preservada'if e.linha in restituidos else e.criterio))
    resultado=mantidos+[sorted(c,key=lambda e:(e.inicio,e.linha))for c in filhos.values()]
    assert sorted(e.linha for c in resultado for e in c)==sorted(eventos)
    return resultado,{'locais_protegidos':protegidos,'eventos_restituidos':len(restituidos)}


def descobrir(observacoes,diagnostico):
    observacoes=[{k:r[k]for k in m.ATRIBUTOS_MODELO}for r in observacoes]
    print('Passagem 1/3: aprendendo fluxos e etapas iniciais...',flush=True)
    res0,p0,train0,grupos0,T0,pi0=etapas.construir(observacoes,prefixo_maximo=4)
    densidade0,_=probabilistico.aprender_tempos(res0,p0,T0)
    preliminares=correlacionar(res0,p0,grupos0,T0,pi0,densidade0,temperatura=.5,posterior=False)
    print('Passagem 2/3: estimando entradas de tarefa...',flush=True)
    res,p,train,grupos,T,pi=etapas.construir(observacoes,prefixo_maximo=8)
    assert train==train0 and grupos==grupos0
    entrada1,stats1=estimar_entradas(res,p,grupos,pi,preliminares,1.)
    densidade_inicial,diag_tempo=probabilistico.aprender_tempos(res,p,T)
    intermedios=correlacionar(res,p,grupos,T,entrada1,densidade_inicial,posterior=False)
    entrada2,stats2=estimar_entradas(res,p,grupos,pi,intermedios,1.)
    densidade,diag_blocos=blocos_temporais(res,p,grupos,T,intermedios,densidade_inicial,.9)
    print('Passagem 3/3: refinando fronteiras e episodios...',flush=True)
    registros=correlacionar(res,p,grupos,T,entrada2,densidade)
    decodificados=probabilistico.suavizar_fases(res,p,grupos,T,entrada2,registros)
    casos=probabilistico.reconstruir_casos(observacoes,res,train,grupos,T,entrada2,decodificados)
    resultado,diag_hierarquia=preservar_tarefas(casos,res,grupos,entrada2,decodificados,stats2)
    resultado.sort(key=lambda c:(c[0].inicio,c[0].linha))
    diagnostico=dict(diagnostico)
    diagnostico.update(metodo='entradas_e_hierarquia_adaptativas',
        criterios=dict(Counter(e.criterio for c in resultado for e in c)),
        casos_locais=len({e.caso_local for c in resultado for e in c}),
        episodios_longos=len({e.episodio_longo for c in resultado for e in c if e.episodio_longo}),
        sequencial={'passagens':3,'largura_feixe':128,'temperatura_final':.75,'peso_viterbi':.5,
                    'ancora_posterior':.98,'prefixo_maximo_inicial':4,'prefixo_maximo_final':8,
                    'prototipos':len(train),'entradas_primeira_estimativa':stats1,'entradas_refinadas':stats2,
                    'tempos_iniciais':diag_tempo,'tempos_refinados':diag_blocos,'hierarquia':diag_hierarquia,
                    'evidencia':'apoio relativo condicionado ao modelo; sem calibracao externa'})
    return resultado,diagnostico

```

### testar_algoritmo.py

```python
"""Validação em domínio sintético novo e controles de ausência de estrutura."""
from pathlib import Path
import sys,csv,random,json
from datetime import datetime,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parent))
import analisar_amostra as m

def gerar(seed=83017):
    rng=random.Random(seed)
    simbolos={g:[f'{rng.getrandbits(48):012x}' for _ in range(4)] for g in range(3)}
    for g in simbolos:
        simbolos[g][2]='a94e02f77d1b'  # Tela compartilhada, com o mesmo aplicativo.
    rows=[]
    case=0
    for dia in range(20):
        for usuario in ('operador-x','operador-y'):
            for trilha in range(2):
                agora=datetime(2024,2,1,8)+timedelta(days=dia,seconds=trilha*180)
                for rodada in range(10):
                    grupo=rng.randrange(3)
                    case+=1
                    for etapa in range(4):
                        duracao=rng.randint(30,90)
                        fim=agora+timedelta(seconds=duracao)
                        rows.append(dict(
                            codigo_racf=usuario,nome_programa=f'app-{etapa%2}',
                            nome_tela_foco=simbolos[grupo][etapa],
                            data_hora_inicio_exec=str(agora),data_hora_fim_exec=str(fim),
                            quantidade_teclas_digitadas='7',quantidade_clicks='4',
                            quantidade_copias='0',quantidade_colagens='0',
                            referencia_processo_id=f'{case}',referencia_processo=f'tipo-{grupo}'))
                        agora=fim+timedelta(seconds=rng.randint(5,30))
                    agora+=timedelta(seconds=rng.randint(120,600))
    rows.sort(key=lambda r:(r['data_hora_inicio_exec'],r['codigo_racf']))
    return rows

def main():
    pasta=Path('work/validacao_v3');pasta.mkdir(exist_ok=True)
    rows=gerar()
    with (pasta/'dominio_novo.csv').open('w',encoding='utf8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    casos,diag=m.descobrir(rows,True)
    medidas=m.metricas(casos,rows)
    cegos=[{k:v for k,v in r.items() if not k.startswith('referencia_')} for r in rows]
    repeticao=m.descobrir(cegos)
    assinatura=lambda cs: sorted((tuple(e.linha for e in c),tuple(e.familia for e in c)) for c in cs)
    assert assinatura(casos)==assinatura(repeticao)
    assert sum(map(len,casos))==len({e.linha for c in casos for e in c})==len(rows)
    assert medidas['score']>medidas['baseline_isolados_score']
    compartilhadas={e.familia for c in casos for e in c if rows[e.linha-2]['nome_tela_foco']=='a94e02f77d1b'}
    assert len(compartilhadas-{m.INCERTO})==3
    rng=random.Random(113)
    embaralhada=[dict(r) for r in rows]
    indices=list(range(len(rows)));rng.shuffle(indices)
    for i,j in enumerate(indices):
        for campo in ('nome_tela_foco','nome_programa'):
            embaralhada[i][campo]=rows[j][campo]
    nulos=m.descobrir(embaralhada)
    mn=m.metricas(nulos,embaralhada)
    assert mn['cobertura_rotinas']==0
    (pasta/'resultados.json').write_text(json.dumps({
        'dominio_novo':medidas,'controle_embaralhado':mn,'diagnostico':diag,
        'grupos_da_tela_compartilhada':sorted(compartilhadas)},ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'dominio_novo':medidas,'controle':mn},ensure_ascii=False,indent=2),flush=True)
    print('OK: conservação, inferência sem rótulos, tela compartilhada e controle negativo.',flush=True)

if __name__=='__main__':
    main()

```

### work/auditar_v7.py

```python
from pathlib import Path
import sys,pickle,json,hashlib,ast,time,csv
from collections.abc import Mapping
sys.path.insert(0,str(Path.cwd()))
import motor_descoberta as m
import analisar_amostra as a
class Observacoes(Mapping):
 def __init__(self,row):self.data={k:row[k]for k in m.ATRIBUTOS_MODELO}
 def __getitem__(self,k):
  assert k in m.ATRIBUTOS_MODELO,f'Acesso proibido: {k}'
  return self.data[k]
 def __iter__(self):return iter(self.data)
 def __len__(self):return len(self.data)
origem=Path('amostra_validacao_fechamento_100k.csv').resolve();rows=a.ler_amostra(origem)
start=time.perf_counter();cs,diag=m.descobrir([Observacoes(r)for r in rows],True)
signature=lambda cases:sorted(tuple(sorted((e.linha,e.familia,e.etapa)for e in c))for c in cases)
experiment=Path('work/pesquisa7_final_full.pkl')
comparison=None
if experiment.exists():
 with experiment.open('rb')as f:expected=pickle.load(f)[9]
 assert signature(cs)==signature(expected),'Divergência entre experimento completo e implementação final'
 comparison='100 mil eventos: casos, famílias e etapas idênticos ao experimento'
assert sorted(e.linha for c in cs for e in c)==list(range(2,len(rows)+2))
for c in cs:
 for e in c:assert 0<=e.evidencia<=1
metric=next(n for n in ast.parse(Path('analisar_amostra.py').read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef)and n.name=='metricas')
assert hashlib.sha256(ast.dump(metric).encode()).hexdigest()==Path('work/hash_avaliador80.txt').read_text()
_,met=a.salvar_resultados(origem,rows,cs,diag)
out=list(csv.DictReader((origem.parent/(origem.stem+'_resultados')/'eventos_classificados.csv').open(encoding='utf-8-sig',newline='')))
assert len(out)==len(rows)and all(all(row[k]==rows[i][k]for k in rows[i])for i,row in enumerate(out))
report={'inferência_somente_cinco_atributos':True,'campos_proibidos_bloqueados':True,'comparacao_com_experimento':comparison,'tarefas_locais_restauradas':sum(e.criterio=='tarefa_local_preservada'for c in cs for e in c),'linhas_preservadas':len(rows),'avaliador_intacto':True,'apoio_das_fases_entre_0_e_1':True,'segundos':time.perf_counter()-start,'metricas':met}
Path('work/auditoria_v7.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False),flush=True)

```

### work/conferir_entrega_v7.py

```python
from pathlib import Path
import json,hashlib,zipfile
from html.parser import HTMLParser
class Pagina(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.processos=[];self.opcoes=[];self.current=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if tag=='article'and 'data-familia'in a:self.processos.append(a['data-familia'])
  if tag=='option':self.current=[a.get('value'),[]]
 def handle_data(self,data):
  if self.current is not None:self.current[1].append(data)
 def handle_endtag(self,tag):
  if tag=='option'and self.current is not None:
   value,data=self.current;self.opcoes.append(value if value is not None else ''.join(data));self.current=None
for stem in ['amostra_validacao_fechamento_100k','logs_fechamento_contabil_6m']:
 folder=Path(stem+'_resultados');report=json.loads((folder/'metricas.json').read_text(encoding='utf8'))
 assert report['sha256_amostra']==hashlib.sha256(Path(stem+'.csv').read_bytes()).hexdigest(),'source hash'
 assert report['sha256_codigo']==hashlib.sha256(Path('analisar_amostra.py').read_bytes()).hexdigest(),'driver hash'
 for file,digest in report['sha256_modulos'].items():assert digest==hashlib.sha256(Path(file).read_bytes()).hexdigest(),file
 m=report['metricas'];assert abs(m['score']-(.1*m['f1_familias']+.4*m['f1_pares']+.5*m['f1_casos']))<1e-10,'formula'
 html=(folder/'estudo.html').read_text(encoding='utf8');p=Pagina();p.feed(html)
 assert len(p.ids)==len(set(p.ids)),'duplicate IDs'
 assert set(p.processos)<=set(p.opcoes),'navigation'
 assert 'Modelo 7.0'in html and f"{m['score']:.2f}"in html,'version/score'
 print(stem,round(m['score'],4),'OK hashes, fórmula, HTML e navegação',flush=True)
files=['analisar_amostra.py','motor_descoberta.py','motor_sequencial.py','motor_probabilistico.py','motor_adaptativo.py','requirements.txt','testar_algoritmo.py','LEIA-ME.md','ESTUDO_METODOLOGICO.md','RESULTADOS_V7.md','work/auditoria_v7.json','work/auditar_v7.py','work/registro_pesquisa_v7.json','work/erros_v7.json','work/erros_v7.py','work/hash_avaliador80.txt','work/registrar_pesquisa_v7.py','amostra_validacao_fechamento_100k_resultados/estudo.html','amostra_validacao_fechamento_100k_resultados/metricas.json','logs_fechamento_contabil_6m_resultados/metricas.json']
files.append('work/conferir_entrega_v7.py')
with zipfile.ZipFile('algoritmo_descoberta_v7.zip','w',zipfile.ZIP_DEFLATED)as z:
 for f in files:z.write(f,f)
print('ZIP v7 criado com código, dependências, estudo, relatório e auditoria.')

with zipfile.ZipFile('algoritmo_descoberta_v7.zip') as z:
 assert z.testzip() is None
 assert 'motor_adaptativo.py' in z.namelist()
print('Integridade do ZIP verificada.')

```

## Anexo D. Inventário de evidências locais
Nome, tamanho e SHA-256 dos fontes e registros textuais disponíveis. Caches binários e CSVs classificados não são transcritos no artigo. O inventário não afirma que cada arquivo tenha sido incorporado ao algoritmo.

- `amostra_validacao_fechamento_100k_resultados/metricas.json` — 7634 bytes — SHA-256 `db36b7fd998f582cd8d46e2aad29608299aa377bf98410dc7acdd3c8e9863764`

- `analisar_amostra.py` — 28274 bytes — SHA-256 `47b8ea79000566724c64694ac0df6157ccca5393c27ff66e4716a535efc55374`

- `ESTUDO_METODOLOGICO.md` — 33003 bytes — SHA-256 `296693fa14e4507d8e198b497dc8694f4d91c6d179bb03cf5ff2a8203f088a94`

- `LEIA-ME.md` — 7119 bytes — SHA-256 `05d285824fc687fcfe578c186e4a022a8fb8117b694df9ca996ea296177f0404`

- `logs_fechamento_contabil_6m_resultados/metricas.json` — 3676 bytes — SHA-256 `70c99576173a931261f647671a2391ed774b142fd19f6f965a7706d26872c185`

- `motor_adaptativo.py` — 9110 bytes — SHA-256 `a08e3855a65c7389af90ca432971ca561d21f3dd884a7a95ee614ba9f9d90750`

- `motor_descoberta.py` — 24399 bytes — SHA-256 `6a0f517d253ba72fd15af5462666f1cb29cd1adb1facb99eeb5113211140da56`

- `motor_probabilistico.py` — 11833 bytes — SHA-256 `d767a5a51e717b0cedc7361fa2eea9a02fcb068d490bbf4c93ebefd6cc1c3b07`

- `motor_sequencial.py` — 10633 bytes — SHA-256 `7c870b33211dc076c26914502e2aa6d19bd49dd7666e2e5d26cba6eea9a4ac67`

- `requirements.txt` — 59 bytes — SHA-256 `5cd2d61d2e7a23c69e8b7fb0f8a45e6b56b403e1d03fcf02eb61325c3b8699e3`

- `RESULTADOS_V5.md` — 2073 bytes — SHA-256 `3f4d886a0e8e2eb1609ea390ce15e5973d1baf2bc9c5ed0a736d8022151755db`

- `RESULTADOS_V6.md` — 3226 bytes — SHA-256 `eefc55ea148820661d4a8fe66e7062521ef33e0627273283a9895571d64e73a0`

- `RESULTADOS_V7.md` — 4279 bytes — SHA-256 `e1008919c6659307098eeb82b4892400d263a4fe3628b55bc0ad59b9ae564cb2`

- `testar_algoritmo.py` — 3596 bytes — SHA-256 `e3c8e8df3313e4fb18307cd327618d05f05c6ee8fed647ddffbce5b0b1709b34`

- `work/adaptar.py` — 3549 bytes — SHA-256 `46a9c3eaafb7b3b25976c05284ec6e08fb0434eb91651d2e573b9f96327d5c11`

- `work/analisar_amostra_v5_antes_v6.py` — 27340 bytes — SHA-256 `c495c1e2ec67b38a63e3276fa92f6ef293fc25c3b9acf5f96cc924ec185582a6`

- `work/analisar_contadores80.py` — 968 bytes — SHA-256 `5b08a5d410d116a59af6157c3b0e33d8470a2185170104cc8f4f2d26a6deff54`

- `work/auditar_v5.py` — 1918 bytes — SHA-256 `a5054218a23887d276ea7cb32e34986c2989990ed369032659d5b308642bec97`

- `work/auditar_v5_final.py` — 1804 bytes — SHA-256 `b92bd04093e2429a7887ebabfbbbe53ab0f9e6633fe8cdd021828e81b5758f08`

- `work/auditar_v6.py` — 2363 bytes — SHA-256 `6a16ae1aa061bc054c409f1f849bac278b6c3a34b0040ef41cefbbd0911ea6dc`

- `work/auditar_v7.py` — 2322 bytes — SHA-256 `8eb82dcf582760da2ed6375601d2e715336098e106ac2b3ccb47764166691ac3`

- `work/auditoria_strict80.py` — 1318 bytes — SHA-256 `4df1b7952239e1292931f8650887c6d713fac431c08bda7ee31d5d0b2573d99f`

- `work/auditoria_v5.json` — 1101 bytes — SHA-256 `7ada5045eb4c10abe83c45ab2dde9fe3cbc6301a27577d685e6cde71598335a5`

- `work/auditoria_v5_62p53.json` — 986 bytes — SHA-256 `5c4624204d111fc85ab7d2ee75b462580a467007678b66ebe68a58d1bb47af4e`

- `work/auditoria_v6.json` — 1106 bytes — SHA-256 `4bc4b15505a738cbf76c6b24fe8ec99fd6ca4e25458341c7fdcec06f9d45e5ea`

- `work/auditoria_v6_68p30.json` — 1050 bytes — SHA-256 `c9aafe6959c1924737906da00b87d3d5aa901db05ca00c9358e1c778d27c5e9a`

- `work/auditoria_v7.json` — 1144 bytes — SHA-256 `094d5a9d5619eee2559c278dc14d9ef14cd986f348b2981ab71cee0e157eaaf6`

- `work/avaliacao_v2.py` — 3131 bytes — SHA-256 `f53c968b30d7df968f81d8bee0b48712acecff37087e89a91c322eb83bf392a9`

- `work/avaliar_prefixo80.py` — 1225 bytes — SHA-256 `671ae96e08915941f6b22c2b244fa9530471fab9b89e507ed7784d99023c0431`

- `work/beam80.py` — 6984 bytes — SHA-256 `939481961816109af204875eb0b29891297cfce9052c2d94b1aa5dcfa415e613`

- `work/belief80.py` — 3167 bytes — SHA-256 `2681b9907adc9702d29bd56e2d1e03d97756ca048bd84042789a2e0a3936492a`

- `work/conferir_entrega_v5.py` — 2223 bytes — SHA-256 `0489db50cde0a20c615ba4d1a95532b8a32bf5edbcf65b4d4017268f338d065d`

- `work/conferir_entrega_v6.py` — 2522 bytes — SHA-256 `485797a56427591edfac69092e089802404275bf45a51ceecc93e197f8edc37a`

- `work/conferir_entrega_v7.py` — 2738 bytes — SHA-256 `f12b794d03503c4f41941affa9309a145b41f6fcace9954a839201040b4cd228`

- `work/contadores_cv80.json` — 1611 bytes — SHA-256 `5f15b37fb79d57894067573b25ca249d6e513cf39d6a4069dda0d7f7c98a9eb8`

- `work/context_decode80.py` — 1127 bytes — SHA-256 `65d289c84523efbaac8c9221b3245025c275099135ecebce1d33d128582b5e6e`

- `work/contexto_condicional_v3.py` — 35743 bytes — SHA-256 `78f865b610a5433a7a94f44c085b1d23103377db40eb4fd486fb84dbd91b1c72`

- `work/contexto_mascarado80.json` — 182 bytes — SHA-256 `2a2ab8f6e1b043b11f4d7ee7bfbed456c8f8c6042c11db68d2c8e38c3faa836a`

- `work/contexto_mascarado80.py` — 2467 bytes — SHA-256 `2f89c70f30c1d5771d1edbd4c1fef10df00f37084ef66ea75947126b107ad188`

- `work/contexto_v3_experimento.py` — 35263 bytes — SHA-256 `9d0032f93c53ab86e326b5785340138624430e66c67d3c2ed39b4270c3c59626`

- `work/core80model.py` — 18683 bytes — SHA-256 `757c8dd9e0f3992257579f387679d8dbc4232dbac2d9dc3d065f08d4bb5d3568`

- `work/densidade_condicional80_0.0.json` — 46171 bytes — SHA-256 `c5eb56091f18880bcf22a09ae52b9ddc21290c944ee4b5aed71705c855f7c9c9`

- `work/densidade_condicional80_2.0.json` — 47001 bytes — SHA-256 `f115b68368c8f9700dde06a56f24a4bf22acba67aa8f5f1cc9a9ee143004bff1`

- `work/densidade_condicional80_4.0.json` — 47166 bytes — SHA-256 `adaa8ed02d7df7c37061d709ea98e67a7bf0a1a08aac2df54adbc441b6419288`

- `work/densidade_excesso80.json` — 23029 bytes — SHA-256 `2a7ed43cfa10e390b398711154bfce4d29a15f4690349b7fcb513c96011bcc74`

- `work/densidade_excesso_longo80_0.0.json` — 46026 bytes — SHA-256 `70c5f172deb9e2386efc295988f9c0491f82e1da81f0a658d4cbd81f8671dec5`

- `work/densidade_excesso_longo80_2.0.json` — 46079 bytes — SHA-256 `47f71cc5c17988c00c327c55a3a605eb0e542d26ced98186057a781ea39647a2`

- `work/densidade_excesso_longo80_4.0.json` — 46724 bytes — SHA-256 `cc4c5a5aadfd44e393db176e7b8fb3528cc21aebea540708995e68d15e29ddb5`

- `work/descoberta.txt` — 4783 bytes — SHA-256 `d93ec9dbbaa3ab0901bba77f26a85b50cfad750ab23cef29aa71627d8b8cad97`

- `work/diagnostico_80.py` — 1325 bytes — SHA-256 `cc0bb6d3bbf859bb871fafa54940dbadffe346b3b7f17d892f110d1aa8bdac74`

- `work/dom-v2.txt` — 2284824 bytes — SHA-256 `6cbdb33e1fd931ebca847691f45339560c4d4705d0e775558ae620cd83fa0a92`

- `work/dom-v3.txt` — 1939559 bytes — SHA-256 `582902d73d8e64d4d9a5883f9bc99e077a82ca99aec8cc0097fbed251a2c5062`

- `work/edge-v3/Default/arbitration_service_config.json` — 20395 bytes — SHA-256 `5153ba36524b344071bd538d9c92b431b5479dfdee382c8ceab82af85b7b8a64`

- `work/edge-v3/Default/DualEngine/SiteList-Consumer.json` — 2 bytes — SHA-256 `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`

- `work/edge-v3/Default/DualEngine/SiteList-Enterprise.json` — 2 bytes — SHA-256 `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`

- `work/edge-verificacao/Default/arbitration_service_config.json` — 20395 bytes — SHA-256 `5153ba36524b344071bd538d9c92b431b5479dfdee382c8ceab82af85b7b8a64`

- `work/edge-verificacao/Default/DualEngine/SiteList-Consumer.json` — 2 bytes — SHA-256 `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`

- `work/edge-verificacao/Default/DualEngine/SiteList-Enterprise.json` — 2 bytes — SHA-256 `44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a`

- `work/em80.py` — 1312 bytes — SHA-256 `598732d4373fe30e5eb2d21c50b9358431c325cbd1a12deeea6a4fdd88c1a7b2`

- `work/erros_v5.json` — 1008 bytes — SHA-256 `3577aa2ca2c6afb68f829c42ffabe8eb95a2d4a95d8bfb15df9ab83f95133e2a`

- `work/erros_v5.py` — 996 bytes — SHA-256 `958641316cc3da4ce3de78002868a7cfd647b82d411d4f1c12e58511b8300af2`

- `work/erros_v6.json` — 1008 bytes — SHA-256 `28a6f0d6dea9abd624b38069892d318c5b80498dcc5bc81d11247825e0356d6c`

- `work/erros_v6.py` — 1013 bytes — SHA-256 `5072cfd96d5bdde1ab23b40639c9d78e5dc9079b1f6aa0390a7d0b81cba3db4a`

- `work/erros_v7.json` — 1008 bytes — SHA-256 `149e62f4d4e220a438b6c02c3718e89c7466b2cfe6b92277685d30350125a6fe`

- `work/erros_v7.py` — 1013 bytes — SHA-256 `4109321bdaf5250031453ea7c1313ad01dce93d7f0b1bab478d1f4824e7e98a9`

- `work/escrever_artigo_completo.py` — 14496 bytes — SHA-256 `cfec79da8be6cd3f78755bd8949c224a4b435c0e57a956a70ba6ee4eb3ab789b`

- `work/estender80.py` — 2004 bytes — SHA-256 `3cea923cb070d4a2184afebd98c1e1b0cf306e23162b4616bd7a2400a923f350`

- `work/estudo_template.md` — 10909 bytes — SHA-256 `5a8aae03d7f2604dd8305990ef0939603cbcb9578382cfaafeac76bf1624c4fb`

- `work/excesso_full.py` — 1079 bytes — SHA-256 `18bb3146a254fe6781e0adbe377d061107f931bd3e5671df963890aa48104d81`

- `work/excesso_full_metricas.json` — 712 bytes — SHA-256 `5862d6467193801d9c913300bb7b934364bfa55167237f8eba22bd9b832f6c7c`

- `work/experimentos.py` — 3871 bytes — SHA-256 `fa402de7c6d01816c0055193f2f259365d31fb566f3f66a94b67780889793888`

- `work/experimentos80.py` — 5489 bytes — SHA-256 `92b7f1e506a7592063186b07f232472ddcc2f1b54f08a85cdbc0a0f51958cebe`

- `work/experimentos80_etapas.py` — 5942 bytes — SHA-256 `76869a585c4440b00cb000450352f43b64d49fba4107779e07e2a15462d8dc0e`

- `work/experimentos80_fdr.py` — 5484 bytes — SHA-256 `29f842d43e5e2f3ede80f710c6e69ab883bcb3b87b6dcb1237ff4b86693e9ddc`

- `work/experimentos80_fdr_etapas.py` — 5945 bytes — SHA-256 `992fe9b86d7714c574dfa1eac2c9b5cdd4119fa5f9252de53b58292035cd579b`

- `work/fronteiras80.py` — 1053 bytes — SHA-256 `b11d28d8fb8581e02a43dd46b3735da6ab7c3b447c1e5aa064aac6983ab9b550`

- `work/futuro80.py` — 2230 bytes — SHA-256 `7e2fd906f914eb0a76ed5160c5e054c26537a7bed26d46023b2b929d5afbc314`

- `work/grade80.py` — 2647 bytes — SHA-256 `0bc0d7d5d0fedde885398fa223c16537053ecf98056baf5a7fbc1e78c7d34bbb`

- `work/grade80_janeiro.json` — 31057 bytes — SHA-256 `972a518b59dcd9abecf52fb1822001b54730b0fab17498738869c39a965917b5`

- `work/gramatica80.py` — 4936 bytes — SHA-256 `36d6ac97eef849ab599548304c268b977d228d3f5d1a9926023cad7228915f34`

- `work/gramatica_flexivel80.json` — 5944 bytes — SHA-256 `143e93eb54fe0d5b872ae1ee55ea673ebffae6907a5e8ef40b0bcdcc111597e4`

- `work/gramatica_flexivel80.py` — 1187 bytes — SHA-256 `b00e487b761c1471f8ba9721b8dd168cb8805ab19522df215a73000d487b0239`

- `work/hash_avaliador80.txt` — 64 bytes — SHA-256 `5425f05cce7e82a05523447e624c471ca80f595d579c74e089359333f0ce4cf5`

- `work/hmm80.py` — 5801 bytes — SHA-256 `1160b0b5e90a131aca47d6373c0b928b386c940c0a0997b74d2bc6adb7bf8299`

- `work/hmm80_estados.py` — 6004 bytes — SHA-256 `3daf1c0697956feebaa7f68687d311b7b7634bbae1cd87ddab4e33b23d894ba4`

- `work/hmm80_likelihood.py` — 5998 bytes — SHA-256 `5c084b2907d0043be34542e61ca98758a2ed2c6377f1369b05d09ba15967a4b9`

- `work/hmm_kernel80.py` — 8295 bytes — SHA-256 `a28f59f5cf598412c5dc4612bc2917efca7a4003a37967ad95a9dda2351023af`

- `work/hmm_parent80.py` — 6972 bytes — SHA-256 `a62b442fc8e7b3855e58548fe09e9737e343a45e875eafb501d0185ebf42fd9b`

- `work/hmm_wildcard80.py` — 7464 bytes — SHA-256 `334f27b3a40fb86a2378ce28a8b0bfb08eaf2b88a8452168a60715e62f3e088a`

- `work/html_final.txt` — 11764 bytes — SHA-256 `5574d7ecc319756e9c02a2b1ac2d682c2fc69c1a786f83116905255d1f958275`

- `work/insercao80.py` — 3981 bytes — SHA-256 `11a3ec664b552cd323318c441b8e6eef40a7a4e2c8fd2c0c69c05466236725a8`

- `work/instalar_v3.py` — 6038 bytes — SHA-256 `0fe4c87755b58df591e073ab2213d8e0e8992162b8e724932cbe595f4f0491af`

- `work/instalar_v4.py` — 3807 bytes — SHA-256 `21729d50a2fee536cc7526db109e42a1cd11896f63ae61e6063f1835978cccb0`

- `work/joint80.py` — 5840 bytes — SHA-256 `cf3e0a29f5d3ee8e2628e147ffca2601f7e3ade3ce101e8132b7b8cdc4c923c2`

- `work/joint_consistent80.py` — 5984 bytes — SHA-256 `a52e184d805635b1092b3f4b8965fe6ff0c1d58a7c785aae552c7e0dd1381c8d`

- `work/metricas_prefixo80_100000.json` — 728 bytes — SHA-256 `6087c5dd8525fd08afa212f1e14c2fb86296639a069e47fdc1c17eeeea6f58bc`

- `work/metricas_prefixo80_60000.json` — 720 bytes — SHA-256 `1210ab4a3873693fd5e2b38805492206ee3230ca78539f2a3d30be6b4af21f7b`

- `work/modelo_anterior.py` — 21947 bytes — SHA-256 `092e7dd78dafe13838e2f2d9134f3e4294bfab47ef6ac5dcc99a6f1ba367478c`

- `work/motor_descoberta_v5_antes_v6.py` — 24332 bytes — SHA-256 `89a1af92dfe7fa2f855f8e06d127be67b36ef0d43b6d9d48d80f050c4e6be6b9`

- `work/motor_excesso80.py` — 10552 bytes — SHA-256 `b6c656fcf2be13bbd7b7fa093d06f8c2daba31ddcfae67bc2984965e4ec62142`

- `work/motor_final.txt` — 11346 bytes — SHA-256 `8e2a475df71c75c704e73795e06593a476d7a9ccc2ac113a1a03c560693c5d71`

- `work/motor_futuro80.py` — 10655 bytes — SHA-256 `611a870092ef755ba37e6665441c15a0ca5d23adbbc002d188b92a9dbdb06b70`

- `work/motor_sequencial_v5_antes_v6.py` — 10603 bytes — SHA-256 `75e6f00def9f992e7bf2f8cc6e4bce38ebd35e668165ea790e40890180606382`

- `work/motor_suporte10.py` — 23534 bytes — SHA-256 `0961bd7cbb271ffd506acc70cb673838eee291fadcfe1876fe395e9385eec8c3`

- `work/motor_suporte20.py` — 23534 bytes — SHA-256 `652583d8aeaa3ee9b2ff9b5670de0cb77cf669a272aae0911df1bee244eed4ed`

- `work/motor_suporte6.py` — 23532 bytes — SHA-256 `ccfe7b173f43ef4ea9a401f7cf6cf6fc8cddec73789c9d3b3349c9bd2383de7f`

- `work/motor_v3_estavel.py` — 17943 bytes — SHA-256 `df06786ad5a9f9931bfc38326617604579d853496738bf08702a3b67a22bc094`

- `work/motor_v3_experimento.py` — 34289 bytes — SHA-256 `89ba562ff1db0d3c57ff980607529a59075ac68621318265c2abbe9f9a1a1df2`

- `work/motor_v4_lexical_estavel.py` — 23455 bytes — SHA-256 `c9814edfbfe116cf7938b77062d3d5fe596bf7ec09168e18969c461df4f43a18`

- `work/nonparam80.py` — 3235 bytes — SHA-256 `cc102aa4f8e0aaaa28f7fda937efa77d4c9435a33f7d81d2eb15c95569d93640`

- `work/nonparam_longo80.py` — 3117 bytes — SHA-256 `a364271708ad6d7e915dd0f3fbf40fbb720ccce743822a539d0cc571e58204a0`

- `work/novas_fases80.py` — 1512 bytes — SHA-256 `8b37041d8b87ac2c960d5f4d12496367a52446b9f03b7694e4a6772e29643934`

- `work/otimizar_fluxos80.py` — 4430 bytes — SHA-256 `55c4645f540092dff40aa0f10a9dad9e69c548e736268dc4d50931694fa76a3a`

- `work/pesquisa7_aliases.py` — 3675 bytes — SHA-256 `1e5b80cc0dd09db231da6a5187e6d2d6108706a9317fc6bdde201d2af4d39737`

- `work/pesquisa7_ancoras.py` — 2823 bytes — SHA-256 `53fb4b1730fc2c367874e6e4d6a50466b16b889394be8afa16473fed7bc859d2`

- `work/pesquisa7_blocos.py` — 3490 bytes — SHA-256 `8be8f0ba4562b2d7f1e0805ec547198f2690ad2ba1587328fe09239b3ea112da`

- `work/pesquisa7_consenso.py` — 2380 bytes — SHA-256 `8f22d5dbf5e1dec811dfba5c927e0512f1c0484bc25fd2ea9e3eb87207017819`

- `work/pesquisa7_contexto.py` — 7048 bytes — SHA-256 `1a46bd1947c1bda64c9d0a9db3930c7c817db515593df3e2e3897d1cdde406c3`

- `work/pesquisa7_cortes.py` — 1743 bytes — SHA-256 `a438d563272a6a3225fdafda80395c8f70813000dddaae7e3142d2f8e99771ef`

- `work/pesquisa7_entrada_unica.py` — 1689 bytes — SHA-256 `9b455a9ded9dddca62f90be19bb5c7200ed5e60d18a6ab47ea12b7f006e1802e`

- `work/pesquisa7_entradas.py` — 2643 bytes — SHA-256 `144d51ee573e4c55b7498bab64b3f76b05096ba3fe65314cf6943109eb74acbe`

- `work/pesquisa7_entradas_suaves.py` — 3035 bytes — SHA-256 `8a6af60022be92f7adf01255afae07563014cbd13bc1d4c229a486246562a792`

- `work/pesquisa7_evidencia.py` — 3058 bytes — SHA-256 `0faa0971c544f47fcec34e297cd05f32c72c6a46bbae2def416066d295eaa88d`

- `work/pesquisa7_feixe.py` — 1717 bytes — SHA-256 `73d7873dcbd4e5023fbd334e9d3d6847f7082d8159edb4678df5ff8ad0ab4739`

- `work/pesquisa7_final_full.py` — 2034 bytes — SHA-256 `459bcca7dfdad3b8e44494843b8e178949d48ee45034d6fd9e05b88d8c2b5462`

- `work/pesquisa7_final_full_metricas.json` — 1634 bytes — SHA-256 `06da533a6ca5b4b182816025b1d26eab1e70948f6ba58930e76d192a0e867d95`

- `work/pesquisa7_fronteiras.py` — 3140 bytes — SHA-256 `e772d1f3b7bf1cdcd274664560a58b4c0d82e89d119caa0823dbfb665483c036`

- `work/pesquisa7_full.py` — 1476 bytes — SHA-256 `89754d835eff23b1bc509cfdf662cbe2ee09cf520ceee814864c53f7801b5255`

- `work/pesquisa7_full_metricas.json` — 713 bytes — SHA-256 `4e2ba1ddc21c2011950ec583f1e69a7155f964bd91cdd66a035feda8fd1be44e`

- `work/pesquisa7_hierarquia.py` — 7286 bytes — SHA-256 `c276fffdc0a21ef46084824029380267fad3bb953e3d4107e872a263922e93b6`

- `work/pesquisa7_lexico.py` — 1605 bytes — SHA-256 `8e2b85416350e7da55632af8d70beddd204cb9e2bb4d957aa2b9c338a0fdc1c2`

- `work/pesquisa7_locais.py` — 2861 bytes — SHA-256 `de7af2456242e228819bf3da71b0e89a371263b02917266a7c28e2a99ce9acf8`

- `work/pesquisa7_novo_fluxo.py` — 1551 bytes — SHA-256 `832dac68e3876a36461570e15ad9c2d37ebfdd7b42756f0aa7b3ae765bcdc438`

- `work/pesquisa7_nucleos.py` — 1865 bytes — SHA-256 `eb2b5d269fefb2f496f46d1b2898e4f3dea82e277f002da52ce38dea21e1d77b`

- `work/pesquisa7_papeis.py` — 3871 bytes — SHA-256 `5f4cff9fc90a94f599ba50c0cbb378e14007f4d487429da238ac9018e6396438`

- `work/pesquisa7_particao.py` — 3338 bytes — SHA-256 `c5c670032ca129aca880b8f1f50725f5a6b470e13b4f127ae8546c64be407a9b`

- `work/pesquisa7_prefixo8.py` — 1402 bytes — SHA-256 `04b84a3de78977eb4177f49ae78bbcae71261af558fc59b626f1f547e0a18a21`

- `work/pesquisa7_presenca.py` — 2428 bytes — SHA-256 `44291d694594011e98abac32fc0feeb31d9ad4513078cb5d31b6e191e97d2a46`

- `work/pesquisa7_recuperar_fluxos.py` — 1772 bytes — SHA-256 `11c02a74c43ad9c0b5f0208a0907fc62f175bf04424fe89573b8ded1961b43f8`

- `work/pesquisa7_refinamento.py` — 2157 bytes — SHA-256 `735ddf8ca99b2c95115a80d2d0a8f09e8cda2a2962872d59d0f35d96158020ea`

- `work/pesquisa7_restauracao.py` — 3220 bytes — SHA-256 `fcd700cda386aab67d3fab8b2705ad501201b1fedd8a7efa987e86b094360a67`

- `work/pesquisa7_reversa.py` — 4246 bytes — SHA-256 `67a41d1b827a615a0c482d2f94fe9a947dc6f12f80fcd5e00dc854de1c6f53a2`

- `work/pesquisa7_reversa_atual.py` — 4491 bytes — SHA-256 `ae546caa571e4a50692407d1c09b38520bf525b05cbe3093ae0aa0e6c0afa776`

- `work/pesquisa7_reversa_final.py` — 1873 bytes — SHA-256 `25d026b65a18537724cba39c54fa5b5a458e7329213286280a0836da0f63be44`

- `work/pesquisa7_tempos_adj.py` — 2740 bytes — SHA-256 `42d7d9f1409bc23c189a867145ae7b4835e2a27960a9fae462a448469c603e5c`

- `work/pesquisa_likelihood80.py` — 4964 bytes — SHA-256 `46ac0be3fd2554d3f8a3c68111a9e5f2238aa9b80d2050bd2dd35ce251dc3fbe`

- `work/pesquisa_suporte80.json` — 6047 bytes — SHA-256 `0bef75a01e0b33c19a8c38133325ee80027e8eb2c4f57b45fb895d9858bf2e17`

- `work/pesquisa_suporte80.py` — 1911 bytes — SHA-256 `4c28957d783a11e41363611c6c2faf60c2e0e7f31f673d479de27cd603c35c61`

- `work/preparar_casos80.py` — 1979 bytes — SHA-256 `ebc5e2181a2d258615df49a18842dfb9197f8bf845e34d667030737fb71cc2fe`

- `work/preparar_grade80.py` — 502 bytes — SHA-256 `e156b787179e7c286721c9bc33b0ef3f9df8af8825ff687f2bf95f2ed4b81e6e`

- `work/promocoes80.py` — 477 bytes — SHA-256 `ddbbf5c8f2d24ab53a1cebe3f0d699c1297055bac4c8c2cbe559991845b1f2ab`

- `work/rao80.py` — 4152 bytes — SHA-256 `b2c95ad29cf1aff8af6ff838f69ac4e752cfb3035caf5d757b256fd34817bab3`

- `work/rao80_full_metricas.json` — 714 bytes — SHA-256 `92c5d7f8a59f9468099c1419dd70c289e554c3c9d464c33c5ac84bae6a1724ba`

- `work/rao_full80.py` — 1077 bytes — SHA-256 `7b41ee684a8631193a70b27159f9274b1095d03aa24edfce3a73bdd7ba4e00dc`

- `work/rao_suporte6_80.py` — 1807 bytes — SHA-256 `f2939301b0fcd68cb0a1bfa6d6458cb1ecf74eb3ee9bf94e5e6f8faab93b5bda`

- `work/rao_temperature80.py` — 1379 bytes — SHA-256 `5bcf6b9ad787f9d26600584c787dc457cfd3fb3bb1feba27d30904249275cf51`

- `work/refinar_episodio80.py` — 3615 bytes — SHA-256 `42bc30fca176bc778ccd02670d119bef732875e71b59a7ed09edb543c83b4980`

- `work/registrar_pesquisa_v6.py` — 1330 bytes — SHA-256 `6cdc4bb38c9a282929d74d92e140b766c77765eb40799687918625606225032d`

- `work/registrar_pesquisa_v7.py` — 1942 bytes — SHA-256 `36b823ea183ed5d27fc35bfb56a240ef0bd6ce107ee59bc019e608db99efc155`

- `work/registro_pesquisa_v6.json` — 54944 bytes — SHA-256 `2f681bdf400e77ed83a4f40f1deba3ef22243343311e635b6afe455c1e3d340b`

- `work/registro_pesquisa_v7.json` — 138980 bytes — SHA-256 `be50927425b1ba73761acfbe51e021c1133db5ca6dc67fe6baff12027341eda4`

- `work/reset_family_full_metricas.json` — 713 bytes — SHA-256 `9a09e95c1eb8f98f78ab3719cf5b867eeb07a6310e8f377292e3281c7484e3ec`

- `work/roteamento80.py` — 4721 bytes — SHA-256 `05733b16adf138a6bcaaf48b90fbf4deecf4c3fbd3dd712e0377e0e3e6dfb98c`

- `work/roteamento_beam80.py` — 5050 bytes — SHA-256 `564b0ca27d86098793b8af556fdf1664f87dfddca215a5308eea369cf7408c02`

- `work/roteamento_etapas80.py` — 6099 bytes — SHA-256 `e8ca30d63105642911490e8453411d8627fa28dfd6609669590de694c8b2aa87`

- `work/sequencial80_60000_metrics.json` — 719 bytes — SHA-256 `b466e7128b78549371046f6a73465bb013d6df79a0da58445b1bb87820240f7f`

- `work/sequencial80_sintetico_metrics.json` — 658 bytes — SHA-256 `dc702cdbc027b4ffbd0e003320f59f42ea1edaf5f249ea8eae55de45b06c766d`

- `work/sinal_contadores80.py` — 1751 bytes — SHA-256 `df4082f0e4d7add694c1f6cd2f690c56f0c11a318ab169c62bc8689f5c73cdb2`

- `work/smoother80.py` — 2654 bytes — SHA-256 `b9fa096d851aeddc5c1b94501d07d4f8728bb209fc175a41f6d0abbe9c0fd484`

- `work/smoother_full80.py` — 752 bytes — SHA-256 `372cd0ec7cbc7bdcbbede6d5130979e6703134958dd212f3798e6dabaabf831b`

- `work/smoother_full_metricas.json` — 713 bytes — SHA-256 `605333da3af1fb54322a8991bf901a5f053379913632b7b2becdc355da7e408e`

- `work/strict80.py` — 6055 bytes — SHA-256 `1cf0630561b00887856a199e8940eccdb5770c4641001d8f435b8566bc82309f`

- `work/strict80_full_metrics.json` — 713 bytes — SHA-256 `3ab5c060c167eb1aefe69ced289fa62416521987df7c9ff274ef93e07eb83237`

- `work/strict_boundary80.py` — 846 bytes — SHA-256 `88ef97e8d1f8e6bc226fea3ecc61522505971a052f1815701da7f9ec91c2ab58`

- `work/strict_coef80.py` — 776 bytes — SHA-256 `5287657317473c7bbeedf87c875026895a6a824d8d818bc350123cb019902bad`

- `work/strict_full80.py` — 639 bytes — SHA-256 `da0b697ff15f06d5ba73e7cd4ca072f06c750abb716b04ba3c12c7a8f04665f7`

- `work/strict_kernel80.py` — 881 bytes — SHA-256 `7ee1155a9edf972dee2e4949beb0dee39309ee4a58498a11f4c8120e82be1255`

- `work/strict_persistent80.py` — 757 bytes — SHA-256 `db7f71c66f970604332769dbdc13a0410d300f88c7a325aa74409f7440c15cb5`

- `work/tempo_condicional80.py` — 3190 bytes — SHA-256 `abed84c9bb1b5907f50e984bcd6fdfbf38c9d21e4bdce7b09c964a38032b6225`

- `work/tempos_v3.txt` — 1939 bytes — SHA-256 `4b95e6b84fdec52866a4f50fcd49b351c767635544769613b09931a804ac65be`

- `work/testar_contexto.py` — 800 bytes — SHA-256 `0fa33db9be22e7ddaa6360e1a86a40b091c7fcf4d4a14083cf38fa58641e7855`

- `work/testar_contexto_condicional.py` — 811 bytes — SHA-256 `cf8307da72eee859231e17f57bb45bd0de0231457bea5e1f71a5b5d4ac9d6a85`

- `work/testar_tempos.py` — 401 bytes — SHA-256 `0e64a3428defcc03d1fc9e7845c7e6e0d5820f10473908750c8fe01befd56447`

- `work/testar_v3_completo.py` — 468 bytes — SHA-256 `a767710545ad0dbbbc315a41564456951a9939ad14643b487b3d7b2ed066649e`

- `work/teste_lote/a_resultados/metricas.json` — 762 bytes — SHA-256 `cb3b181c942e807c6c828d47ef2b5aceb7a4ac4ae2149ec663103367dcd04a08`

- `work/teste_lote/b_resultados/metricas.json` — 762 bytes — SHA-256 `907bdfb3384c596d43fb1c985ce843a6b2c9665c642fc8e8816923047523c1f2`

- `work/teste_lote/executar_lote.py` — 32336 bytes — SHA-256 `8c0231bd9b075b0fd00572d6b5cdf05c6844bb5b3fa620996556944c2b817497`

- `work/teste_lote_v3/a_resultados/metricas.json` — 1968 bytes — SHA-256 `8b2da2939628aa2c79e5043e31ba1f9667bf2986ef9d6c2987610a876db45770`

- `work/teste_lote_v3/analisar_amostra.py` — 24615 bytes — SHA-256 `a876c5f352bd55d2872b85b8353ac6900ad0bff2af298a1aee8cf9f04fe318dd`

- `work/teste_lote_v3/b_resultados/metricas.json` — 1968 bytes — SHA-256 `fc118dd7b1ee08b79a589911ade35de4ff18b9fbb9c16e0205b7288a25b6a07e`

- `work/teste_lote_v3/motor_descoberta.py` — 17943 bytes — SHA-256 `df06786ad5a9f9931bfc38326617604579d853496738bf08702a3b67a22bc094`

- `work/testes_v3.py` — 3548 bytes — SHA-256 `66317a3b733b6b9091ada74b15499fd0a3b4316333141555706e0a5a111fe3be`

- `work/validacao_v3/resultados.json` — 2698 bytes — SHA-256 `59fade3269d2f6e4b77d711370ca8633c40dc6ecf67291f804fde6d2743fb19b`

- `work/validar_sequencial80.py` — 767 bytes — SHA-256 `d85d45e3e6d4a310a78cd9b3355dc051d4ca8e55b8e83eed36f20d0a159e2016`

- `work/variacoes_v4.txt` — 5524 bytes — SHA-256 `4e35cb9b2d63ab24aa884ae38c40c2ffb18c9e7563e317f6a4ecb8d19c53f99c`

- `work/verificar_entrega.py` — 1790 bytes — SHA-256 `688713970828c8e5d2a08d69b150174666949decebeb7ab5faeb3aff77b856a2`

- `work/verificar_entrega_v3.py` — 1985 bytes — SHA-256 `39927f6758697781f1ec8bd359042d26761cc0cc47d6f8d6fa830e7ec30850e6`

- `work/verificar_v2.py` — 2771 bytes — SHA-256 `acbff299343c9984ff2176ce4d9dd992a01f3fe8bace278cfb3fc87b7b5e63d1`

- `work/versao6_snapshot/analisar_amostra.py` — 27938 bytes — SHA-256 `8cf4d5824427c08301fa2cfc73f48f18ef8897a31ff0b3975dfe835627ffb51b`

- `work/versao6_snapshot/ESTUDO_METODOLOGICO.md` — 26675 bytes — SHA-256 `f6eed28f11dec49835532d73c2449dc1b64228eb3792fb9b81f5c9aa9d469b51`

- `work/versao6_snapshot/LEIA-ME.md` — 5920 bytes — SHA-256 `71b2359f441e361f5cc17a16d23ca73e53e9f6b6e9198caa55da4698013604f2`

- `work/versao6_snapshot/motor_descoberta.py` — 24403 bytes — SHA-256 `d984f1323a6802514f7118911fa13dcd7e9ea092ee5cea969ea1b8fde19b697d`

- `work/versao6_snapshot/motor_probabilistico.py` — 11769 bytes — SHA-256 `8121bcae31e2e34c56df2985f2a48fcd33cf3fcf8a761dede88cd783cacb09db`

- `work/versao6_snapshot/motor_sequencial.py` — 10603 bytes — SHA-256 `75e6f00def9f992e7bf2f8cc6e4bce38ebd35e668165ea790e40890180606382`

- `work/versao_2_estavel.py` — 33191 bytes — SHA-256 `efdfc1c7716d041b03599b59d701697c0f6b5f30b3afc77976094d9d44b773d5`

- `work/versao_comunidades.py` — 19217 bytes — SHA-256 `c49ff3e1a8aa6d9737d3c6daec5e59cc4098bb2a9eff5a013ff4199afcccce2e`

