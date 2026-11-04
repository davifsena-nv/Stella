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
</style><header><div class="over">Exploração de logs · Modelo 8.0</div><h1>Rotinas descobertas</h1><p>""" + html.escape(origem.name)+' · '+periodo+"""</p></header><main>
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
<p>Quando há atividades transversais detectadas, o modelo 8 usa trilhas físicas. Telas cujo nome aparece em
vários aplicativos são tratadas como opacas e não definem etapas; nomes frequentes de um só aplicativo que
faltavam ao grafo são acrescentados. Cada rotina recebe um ciclo de etapas por atribuição húngara, e a etapa de
entrada é o maior salto de frequência ao longo do ciclo, porque tarefas truncadas tornam as etapas finais mais raras.</p>
<p>Um feixe de até 256 hipóteses distribui os eventos de cada pessoa e dia entre trilhas sem sobreposição. Cada
trilha mantém uma distribuição sobre a etapa da tarefa em andamento. Um evento pode continuar a tarefa, iniciar
outra, retomar a tarefa após uma interrupção ou, em dias de episódio concentrado, compor o episódio. Uma
interrupção inicia um caso; o trabalho imediatamente seguinte na mesma trilha passa a esse caso. O limite de
retorno imediato é estimado pelo joelho da distribuição das esperas decodificadas.</p>
<p>A emissão de cada combinação de aplicativo e tela começa por regras de variação de nome (sufixos, prefixos
curtos, inicial seguida de dígitos) e é reestimada por EM com as fases decodificadas. Os custos das decisões de
tarefa são frequências das decisões anteriores. Três custos de episódio foram escolhidos com janeiro a março e
conferidos em abril a junho. A agregação em episódios continua sendo uma hipótese de correlação.</p>
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
                     sha256_modulos={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__).with_name('motor_descoberta.py'),Path(__file__).with_name('motor_sequencial.py'),Path(__file__).with_name('motor_probabilistico.py'),Path(__file__).with_name('motor_adaptativo.py'),Path(__file__).with_name('motor_trilhas.py')]},
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
