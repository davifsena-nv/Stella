# Descoberta de rotinas — versão 8.0

Mantenha juntos analisar_amostra.py, motor_descoberta.py, motor_sequencial.py, motor_probabilistico.py, motor_adaptativo.py e motor_trilhas.py. O primeiro configura a amostra e gera os relatórios. Os demais implementam a descoberta de grupos, o aprendizado das etapas e a correlação das execuções.

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

Sem atividades transversais detectadas, usa a cobertura de caminhos por rotina. Quando esse detector encontra interrupções frequentes, usa o modelo 8 (motor_trilhas.py). Telas cujo nome aparece em três ou mais aplicativos são tratadas como opacas; nomes frequentes de um só aplicativo, não derivados, são acrescentados como etapas. Cada rotina recebe um ciclo de etapas por atribuição húngara; a entrada é o maior salto de frequência ao longo do ciclo.

Um feixe (128 hipóteses; 256 na última iteração) distribui os eventos de cada pessoa e dia entre trilhas sem sobreposição. Cada trilha mantém uma distribuição sobre a etapa da tarefa em andamento. Um evento continua a tarefa, inicia outra, retoma a tarefa logo após uma interrupção ou, em dias de episódio concentrado, compõe o episódio. A interrupção inicia um caso, e o trabalho imediatamente seguinte na mesma trilha passa a esse caso; o limite de retorno imediato é o joelho da distribuição decodificada (80 s na base estudada).

A emissão de cada par aplicativo/tela começa por regras de variação de nome e é reestimada por EM em quatro iterações. Os custos de decisão de tarefa são frequências das decisões anteriores. A cada iteração, um classificador de contexto treinado só com telas de nome inequívoco reestima o processo provável das telas opacas a partir dos vizinhos. Três custos de episódio (c_emb=2,2, c_embc=1,1, c_toF=0,5) foram escolhidos em janeiro–março e conferidos em abril–junho. A espera usa uma janela fixa de 90 s com penalização de pausa; a versão aprendida por EM rígido piorou o resultado e foi descartada.

É um método offline. A quantidade de trilhas é o mínimo exigido pela concorrência dos intervalos, não o número real comprovado de fluxos. A escolha entre correlacionadores depende dos dados, sem condição por nome do arquivo ou número de linhas. O CSV marca o critério de cada evento: trilha_continuacao, trilha_nova_tarefa, trilha_retomada, interrupcao, episodio_etapa e episodio_subtarefa.

caso_local preserva a hipótese local e episodio_longo identifica os episódios mantidos na atribuição final. As transições exibidas são adjacências cronológicas, não prova de causalidade entre todas as etapas. As trilhas locais são reconstruídas por pessoa e data; tarefas que atravessam a meia-noite podem ser fragmentadas fora dos episódios longos.

Os nomes de rotina são exemplos de telas, sem confirmação do significado de negócio. O apoio posterior da fase é condicionado às trilhas escolhidas e não é uma probabilidade calibrada de acerto. Manualidade significa teclas, cliques, cópias e colagens por ocorrência. Dias úteis no painel são segunda a sexta, sem lista de feriados.

## Avaliação

O score original foi mantido: 10% F1 das famílias alinhadas + 40% F1 dos pares + 50% F1 dos casos inteiros. Nenhuma linha é excluída da pontuação.

| Amostra | Versão 7 | Versão 8 |
| --- | ---: | ---: |
| 100 mil eventos | 76,10 | 78,17 |
| 60 mil eventos | 72,96 | 72,96 |

Na base de 100 mil eventos, 91,78% dos eventos recebem o processo correto e 29.056 de 37.689 casos são recuperados exatamente. F1 das famílias: 89,45%; dos pares: 79,28%; dos casos inteiros: 75,02%. A meta de 90/100 não foi atingida; os experimentos de teto em RESULTADOS_V8.md indicam que ela exige informação ausente dos cinco campos. Cobertura de 100% não significa acerto de 100%.

Para calcular o score completo, todas as linhas precisam de processo_id/processo_sintetico ou referencia_processo_id/referencia_processo. Sem essas referências, a análise e o HTML são gerados, mas a pontuação correspondente fica indisponível. Não se estima acurácia real apenas pela confiança interna.

As duas bases foram consultadas no desenvolvimento e na seleção de parâmetros. Isso não constitui validação externa, embora os rótulos não sejam atributos de inferência. Consulte ESTUDO_METODOLOGICO.md, RESULTADOS_V7.md e RESULTADOS_V8.md para equações, fontes, experimentos e limitações.

## Verificações

    py testar_algoritmo.py

Esse teste controlado de 3.200 eventos preservou score 73,51 e F1 das famílias 95,20; após embaralhar telas e aplicativos, não encontrou rotinas. Sua pasta de saída mantém o nome legado work/validacao_v3.

    py work/auditar_v8.py

A auditoria completa usa a amostra de 100 mil linhas, expõe ao motor somente os cinco atributos permitidos e reconcilia todas as linhas originais. Também confere o hash sintático do avaliador. O resultado fica em work/auditoria_v8.json (score 78,1659).

Os ensaios da versão 8, incluindo os experimentos de teto com oráculos, estão em work/registro_pesquisa_v8.json; os scripts correspondentes estão em work/pesquisa_v8/. A versão 7 continua disponível em motor_adaptativo.py, e seus arquivos anteriores estão em work/backup_v7/.

Verificado com Python 3.14, NumPy 2.4.6, SciPy 1.17.1, NetworkX 3.6.1 e scikit-learn 1.9.1. Outras versões podem resolver empates numéricos de modo diferente.

Na máquina usada na auditoria, a execução completa levou cerca de quatro minutos. O programa mostra as passagens antes de gerar os artefatos.
