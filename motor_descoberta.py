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
    "versao": "8.0",
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
        from motor_trilhas import descobrir as descobrir_sequencias
        resultado,diagnostico=descobrir_sequencias(observacoes,diagnostico)
    return (resultado,diagnostico)if devolver_diagnostico else resultado
