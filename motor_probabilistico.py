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
