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
