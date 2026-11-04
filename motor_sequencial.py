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
