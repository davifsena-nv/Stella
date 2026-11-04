"""Modelo 8: trilhas físicas, ciclos de etapas, interrupções e episódios.

Nenhuma função recebe referências ou IDs de execução. A estrutura é aprendida no arquivo:
1. grupos e protótipos de telas (motor_sequencial, v7);
2. estados limpos: protótipos cujo nome aparece em um só aplicativo, mais nomes frequentes
   e não derivados que faltavam ao grafo;
3. ciclo de cada grupo por atribuição húngara e entrada pelo maior salto de frequência;
4. emissão lexical inicial (sufixos, prefixos curtos, inicial+dígitos, aplicativo) refinada por EM;
5. feixe sobre trilhas sem sobreposição, com crença de fase por trilha e custos aprendidos.
"""
import math, re
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
from scipy.optimize import linear_sum_assignment
import motor_descoberta as m
import motor_sequencial as etapas

OPT_CONT, OPT_NOVA, OPT_RETOMA, OPT_EMB, OPT_EMBC, OPT_NAV, OPT_F = range(7)
DEPURACAO = {}
CRITERIOS = {OPT_CONT: 'trilha_continuacao', OPT_NOVA: 'trilha_nova_tarefa', OPT_RETOMA: 'trilha_retomada',
             OPT_EMB: 'episodio_subtarefa', OPT_EMBC: 'episodio_subtarefa', OPT_NAV: 'interrupcao',
             OPT_F: 'episodio_etapa'}
# Hiperparâmetros de episódio escolhidos em jan-mar e conferidos em abr-jun (ver RESULTADOS_V8.md).
PARAMETROS_V8 = dict(feixe=128, iteracoes=4, lambda_emissao=5.0, horizonte_trilha=1300,
                     c_emb=2.2, c_embc=1.1, c_toF=0.5, suporte_candidato=30,
                     espera='fixa', retorno='aprendido', feixe_final=256,
                     etapas_subtarefa='frequencia', contexto_emissao=0.5, contexto_familia=0.5)


# ---------------------------------------------------------------- estrutura
def _ciclo(ids, c):
    sub = c[np.ix_(ids, ids)].copy()
    esperada = np.outer(sub.sum(1), sub.sum(0)) / max(1e-9, sub.sum())
    sc = np.log((sub + 1) / (esperada + 1)); np.fill_diagonal(sc, -1e6)
    a, b = linear_sum_assignment(sc, maximize=True)
    suc = {int(x): int(y) for x, y in zip(a, b)}
    ciclos, vis = [], set()
    for i in range(len(ids)):
        if i in vis: continue
        cc, j = [], i
        while j not in vis: vis.add(j); cc.append(j); j = suc[j]
        ciclos.append(cc)
    while len(ciclos) > 1:
        best = None; c0 = ciclos[0]
        for pos, cc in enumerate(ciclos[1:], 1):
            for i in c0:
                for j in cc:
                    g = sc[i, suc[j]] + sc[j, suc[i]] - sc[i, suc[i]] - sc[j, suc[j]]
                    if best is None or g > best[0]: best = (g, pos, i, j)
        _, pos, i, j = best; suc[i], suc[j] = suc[j], suc[i]
        ciclos[0] += ciclos.pop(pos)
    ordem = [0]
    while suc[ordem[-1]] != 0: ordem.append(suc[ordem[-1]])
    return [ids[k] for k in ordem]


def aprender_estrutura(app, nome, t0, t1, dia, train, grupos, z, nomes, suporte=30):
    TRANS = next(g for g, v in nomes.items() if v == m.TRANSVERSAL)
    apps_do_nome = defaultdict(set)
    for a, s in zip(app, nome): apps_do_nome[s].add(a)
    opacos = {s for s, aa in apps_do_nome.items() if len(aa) >= 3}
    keep = [i for i, (a, s) in enumerate(train) if s not in opacos]
    cnt = Counter(zip(app, nome)); treino = set(train)
    canon = {train[i][1] for i in keep}
    def derivado(s):
        if any(s != c and s.startswith(c) for c in canon): return True
        if any(p in opacos for p in re.split(r'[_.?]', s) if p): return True
        return any(o in s for o in opacos if len(o) >= 3)
    cand = sorted((a, s) for (a, s), k in cnt.items() if k >= suporte and (a, s) not in treino
                  and len(apps_do_nome[s]) == 1 and not derivado(s))
    states = [train[i] for i in keep] + cand
    sgroup = [grupos[i] for i in keep]
    anc_state = {train[i]: grupos[i] for i in keep}
    ai = np.flatnonzero(np.array([(a, s) in anc_state for a, s in zip(app, nome)]))
    tot_anc = Counter((app[j], nome[j]) for j in ai)
    for a, s in cand:
        votos = Counter()
        for i in np.flatnonzero((app == a) & (nome == s)):
            mm = ai[(dia[ai] == dia[i]) & (t1[ai] <= t0[i]) & (t0[i] - t1[ai] <= 90)]
            for j in mm:
                if anc_state[app[j], nome[j]] != TRANS: votos[app[j], nome[j]] += 1 / len(mm)
        if votos:
            sgroup.append(int(anc_state[max(votos, key=lambda k: votos[k] / tot_anc[k])]))
        else:
            sgroup.append(TRANS)
    sgroup = np.array(sgroup); S = len(states); sid = {s: i for i, s in enumerate(states)}
    por_app = defaultdict(list)
    for i, (a, s) in enumerate(states): por_app[a].append(i)
    def lex(a, s):
        v = np.zeros(S)
        if (a, s) in sid: v[sid[a, s]] = 1; return v
        cc = [i for i in por_app[a] if s.startswith(states[i][1])]
        if cc: v[max(cc, key=lambda i: len(states[i][1]))] = 1; return v
        mt = re.match(r'^([a-z0-9\-]{2})_', s)
        if mt:
            cc = [i for i in por_app[a] if states[i][1][:2] == mt.group(1)]
            if cc: v[cc] = 1; return v
        mt = re.match(r'^([a-z])\d+$', s)
        if mt:
            cc = [i for i in por_app[a] if states[i][1][0] == mt.group(1)]
            if cc: v[cc] = 1; return v
        if por_app[a]: v[por_app[a]] = 1
        else: v[:] = 1
        return v
    chaves = sorted(cnt); kid = {k: i for i, k in enumerate(chaves)}
    P0 = np.array([lex(a, s) for a, s in chaves]); P0 /= P0.sum(1, keepdims=True)
    ekey = np.array([kid[a, s] for a, s in zip(app, nome)])
    est0 = P0[ekey].argmax(1); exato = P0[ekey].max(1) > .99
    # grupo episódico: maior concentração em poucos dias
    dias = np.unique(dia); di = np.searchsorted(dias, dia); share = {}
    for g in set(sgroup.tolist()):
        if g == TRANS or g not in nomes: continue
        v = np.sort(np.bincount(di[(sgroup[est0] == g) & exato], minlength=len(dias)))[::-1]
        share[g] = v[:max(1, len(dias) // 15)].sum() / max(1, v.sum())
    EP = max(share, key=share.get)
    # ciclos a partir de âncoras exatas próximas
    anc = np.flatnonzero(exato); ordem = anc[np.lexsort((t0[anc], dia[anc]))]
    c = np.zeros((S, S))
    for a_i, i in enumerate(ordem):
        js = []
        for j in ordem[a_i + 1:a_i + 12]:
            if dia[j] != dia[i] or t0[j] - t1[i] > 90: break
            if t0[j] >= t1[i] and sgroup[est0[j]] == sgroup[est0[i]] and est0[j] != est0[i]: js.append(j)
        for j in js: c[est0[i], est0[j]] += 1 / len(js)
    cyc = {}
    soft = P0[ekey].sum(0)
    for g in sorted(set(sgroup.tolist())):
        ids = [i for i in range(S) if sgroup[i] == g]
        if g in (TRANS, EP) or len(ids) < 2: continue
        o = _ciclo(ids, c)
        # ciclos truncados: a entrada é o maior salto de frequência sobre o estado anterior
        rate = {o[k]: soft[o[k]] / max(1e-9, soft[o[k - 1]]) for k in range(len(o))}
        k = o.index(max(rate, key=rate.get)); cyc[g] = o[k:] + o[:k]
    return dict(states=states, sgroup=sgroup, TRANS=TRANS, EP=EP, cyc=cyc, P0=P0, ekey=ekey,
                chaves=chaves, opacos=opacos, candidatos=cand, exato=exato)


def periodos(sel, dia, dias_obs):
    """Dias de concentração elevada do grupo episódico (mesma regra robusta da v5-v7)."""
    cnt = Counter(dia[sel]); tot = Counter(dia)
    dias = sorted(dias_obs)
    if len(dias) < 15: return {}
    rates = np.array([cnt[d] / tot[d] for d in dias]); med = np.median(rates); mad = np.median(abs(rates - med))
    lim = max(.1, med * 4, med + 6 * mad)
    escolhidos = [d for d, r in zip(dias, rates) if r >= lim and cnt[d] >= 10]
    epis, cur, last = {}, -1, None; pos = {d: i for i, d in enumerate(dias)}
    for d in escolhidos:
        if last is None or pos[d] - last > 2: cur += 1
        epis[d] = cur; last = pos[d]
    tam = Counter(epis.values())
    return {d: e for d, e in epis.items() if tam[e] >= 3}


# ---------------------------------------------------------------- decodificação
def _fb(Qc, suc, init, leak=1e-3):
    n, S = Qc.shape; A = suc * (1 - leak) + leak / S
    al = np.zeros((n, S)); be = np.ones((n, S))
    a = init * Qc[0]; al[0] = a / (a.sum() + 1e-300)
    for t in range(1, n):
        a = (al[t - 1] @ A) * Qc[t]; al[t] = a / (a.sum() + 1e-300)
    for t in range(n - 2, -1, -1):
        b = A @ (Qc[t + 1] * be[t + 1]); be[t] = b / (b.sum() + 1e-300)
    g = al * be
    return g / (g.sum(1, keepdims=True) + 1e-300)


def _concorrencia(t0, t1):
    ev = sorted([(a, 1) for a in t0] + [(b, -1) for b in t1], key=lambda x: (x[0], x[1]))
    c = mx = 0
    for _, s in ev: c += s; mx = max(mx, c)
    return mx


def decodificar_dia(kind, R, t0, t1, suc, ent, non, episodio, CT, gap_tab, gap_bin, longo, navmax, B, embd=None):
    """Feixe sobre trilhas. CT[modo, pendente, tipo]: custos -log P(tipo | estado da trilha)."""
    n, S = R.shape; L = max(1, _concorrencia(t0, t1))
    score = np.zeros(1); end = np.full((1, L), -1e12); mode = np.zeros((1, L), np.int8)
    pend = np.zeros((1, L), bool); bel = np.zeros((1, L, S))
    bpp, bpl, bpo = [], [], []
    nb_tab = len(gap_tab)
    for e in range(n):
        free = end <= t0[e]; g = t0[e] - end; long_gap = g > longo
        gidx = np.clip((np.maximum(g, 0) // gap_bin).astype(int), 0, nb_tab - 1)
        gc = np.where((mode == 0) | long_gap, 0.0, gap_tab[gidx])
        mm = np.where(long_gap, 0, mode); pp = (pend & ~long_gap).astype(int)
        tc = CT[mm, pp]; base = np.where(free, gc, np.inf); k = kind[e]
        if k == 1:
            cand = (base + tc[..., OPT_NAV])[:, :, None]; opts = np.array([OPT_NAV])
        elif k == 2:
            cand = (base + tc[..., OPT_F])[:, :, None]; opts = np.array([OPT_F])
        else:
            r = R[e]; pc = bel @ suc; cl = np.maximum(pc @ r, 1e-300)
            le = max(float(ent @ r), 1e-300); ln = max(float(non @ r), 1e-300)
            expirou = pend & (g > navmax)
            k1 = np.where(expirou, CT[np.minimum(mode, 3), 0, OPT_NOVA], tc[..., OPT_NOVA])
            o0 = np.where((mode == 1) & ~long_gap & ~expirou, base + tc[..., OPT_CONT] - np.log(cl), np.inf)
            o1 = base + k1 - np.log(le)
            o2 = np.where(pend & ~long_gap & ~expirou, base + tc[..., OPT_RETOMA] - np.log(ln), np.inf)
            ep = episodio & ((mode == 2) | (mode == 3)) & ~long_gap
            lb = 0.0 if embd is None else -math.log(max(float(embd @ r), 1e-300))
            o3 = np.where(ep, base + tc[..., OPT_EMB] + lb, np.inf)
            o4 = np.where(ep & (mode == 3), base + tc[..., OPT_EMBC] - np.log(cl), np.inf)
            cand = np.stack([o0, o1, o2, o3, o4], -1); opts = np.arange(5)
        tot = (score[:, None, None] + cand).ravel()
        fin = np.isfinite(tot); nb = min(B, int(fin.sum()))
        if nb == 0: raise RuntimeError('feixe vazio')
        sel = np.argpartition(tot, nb - 1)[:nb] if nb < len(tot) else np.arange(len(tot))
        sel = sel[np.isfinite(tot[sel])]
        h, l, o = np.unravel_index(sel, cand.shape)
        oo = opts[o]; score = tot[sel]
        end = end[h].copy(); mode = mode[h].copy(); pend = pend[h].copy(); bel = bel[h].copy()
        ar = np.arange(len(sel)); end[ar, l] = t1[e]
        if k == 1:
            pend[ar, l] = True
        elif k == 2:
            mode[ar, l] = 2; pend[ar, l] = False
        else:
            r = R[e]; pcl = bel[ar, l] @ suc
            nbel = np.where(((oo == OPT_CONT) | (oo == OPT_EMBC))[:, None], pcl * r,
                   np.where((oo == OPT_NOVA)[:, None], ent * r,
                   np.where((oo == OPT_RETOMA)[:, None], non * r, r * (1 if embd is None else embd))))
            bel[ar, l] = nbel / np.maximum(nbel.sum(1, keepdims=True), 1e-300)
            mode[ar, l] = np.where(oo <= OPT_RETOMA, 1, 3); pend[ar, l] = False
        bpp.append(h); bpl.append(l); bpo.append(oo)
    best = int(np.argmin(score)); lanes = np.zeros(n, int); optv = np.zeros(n, int)
    for e in range(n - 1, -1, -1):
        lanes[e] = bpl[e][best]; optv[e] = bpo[e][best]; best = bpp[e][best]
    return lanes, optv


def _simular(kind, lanes, optv, t0, t1, longo):
    """Casos, segmentos de fase e estatísticas de transição a partir das decisões."""
    n = len(kind); caso = np.full(n, -1); ep = np.zeros(n, bool)
    lc = defaultdict(lambda: -1); lp = defaultdict(lambda: -1); mode = defaultdict(int)
    pend = defaultdict(bool); lend = defaultdict(lambda: -1e12); seg = {}
    segs, NCT, gaps, navgaps = [], np.zeros((4, 2, 7)), [], []
    nxt = 0
    for e in range(n):
        l, o = lanes[e], optv[e]
        g = t0[e] - lend[l]; lg = g > longo
        mm = 0 if lg else mode[l]; pp = int(pend[l] and not lg)
        NCT[mm, pp, o] += 1
        if mode[l] and not lg: gaps.append(g)
        if pp and o in (OPT_CONT, OPT_RETOMA): navgaps.append(g)
        lend[l] = t1[e]
        if o == OPT_NAV:
            caso[e] = nxt; lp[l] = nxt; nxt += 1; pend[l] = True; continue
        pend[l] = False
        if o == OPT_F:
            ep[e] = True; lp[l] = -1; mode[l] = 2; seg.pop(l, None); continue
        if o in (OPT_EMB, OPT_EMBC):
            ep[e] = True; lp[l] = -1
        elif o == OPT_CONT:
            if lp[l] >= 0: lc[l] = lp[l]
            caso[e] = lc[l]; lp[l] = -1
        elif o == OPT_NOVA:
            lc[l] = nxt; caso[e] = nxt; nxt += 1; lp[l] = -1
        else:
            lc[l] = lp[l]; caso[e] = lc[l]; lp[l] = -1
        if o in (OPT_CONT, OPT_EMBC) and l in seg:
            seg[l][1].append(e)
        else:
            seg[l] = (o, [e]); segs.append(seg[l])
        mode[l] = 1 if o <= OPT_RETOMA else 3
    return caso, ep, segs, NCT, gaps, navgaps


def contexto_por_vizinhos(grupos_dia, LN, OP, kind, app, Qg, limpo, t0, t1, episodio_evento, semente=0):
    """Autotreinamento: eventos de tela limpa (rótulo lexical) ensinam a prever o grupo só pelo contexto.
    Atributos: aplicativo do próprio evento, emissão por grupo dos vizinhos na trilha (2 de cada lado)
    e no tempo (3 de cada lado), esperas e a decisão do feixe. A tela do próprio evento não entra."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    n, NG = Qg.shape
    V = np.zeros((n, NG + 3)); V[:, :NG] = Qg; V[kind != 0, :NG] = 0
    V[:, NG] = kind == 1; V[:, NG + 1] = kind == 2; V[:, NG + 2] = limpo
    viz = {k: np.full(n, -1) for k in ('lp1', 'lp2', 'ln1', 'ln2', 'tp1', 'tp2', 'tp3', 'tn1', 'tn2', 'tn3')}
    for ix in grupos_dia.values():
        for a, e in enumerate(ix):
            for k in range(3):
                if a - 1 - k >= 0: viz['tp%d' % (k + 1)][e] = ix[a - 1 - k]
                if a + 1 + k < len(ix): viz['tn%d' % (k + 1)][e] = ix[a + 1 + k]
        seq = defaultdict(list)
        for e in ix: seq[LN[e]].append(e)
        for s_ in seq.values():
            for a, e in enumerate(s_):
                if a > 0: viz['lp1'][e] = s_[a - 1]
                if a > 1: viz['lp2'][e] = s_[a - 2]
                if a + 1 < len(s_): viz['ln1'][e] = s_[a + 1]
                if a + 2 < len(s_): viz['ln2'][e] = s_[a + 2]
    ar = np.arange(n)
    apps = sorted(set(app)); A = (app[:, None] == np.array(apps)[None, :]).astype(float)
    cols = [A]
    for nb in viz.values():
        ok = nb >= 0; j = np.maximum(nb, 0)
        gap = np.where(t0[j] >= t0, t0[j] - t1, t0 - t1[j])
        cols += [np.where(ok[:, None], V[j], 0), np.where(ok, np.abs(gap), 9999)[:, None]]
    cols.append(np.c_[OP == OPT_NOVA, OP == OPT_CONT, OP == OPT_RETOMA, np.isin(OP, [OPT_EMB, OPT_EMBC]), episodio_evento])
    X = np.hstack(cols).astype(np.float32)
    tr = (kind == 0) & limpo
    clf = HistGradientBoostingClassifier(max_iter=300, learning_rate=.1, max_leaf_nodes=63, random_state=semente)
    clf.fit(X[tr], Qg[tr].argmax(1))
    Pc = np.full((n, NG), 1e-6); Pc[:, clf.classes_] = clf.predict_proba(X)
    return Pc / Pc.sum(1, keepdims=True)


def retorno_imediato(g, largura=10.0, fracao=.1):
    """Joelho da densidade de esperas interrupção->continuação: primeiro intervalo após o platô
    cuja contagem cai abaixo de uma fração da mediana do platô."""
    h = np.bincount((g // largura).astype(int))
    topo = np.median(np.sort(h)[-max(3, len(h) // 4):])
    for i in range(int(np.argmax(h)), len(h)):
        if h[i] < fracao * topo:
            return float(i * largura)
    return float(len(h) * largura)


def descobrir(observacoes, diagnostico):
    observacoes = [{k: r[k] for k in m.ATRIBUTOS_MODELO} for r in observacoes]
    P = PARAMETROS_V8
    print('Passagem 1/3: aprendendo grupos e etapas...', flush=True)
    res, p, train, grupos, T, pi0 = etapas.construir(observacoes, prefixo_maximo=8)
    u, ini, fim, telas, z, q, nomes, diag = res
    n = len(observacoes)
    app = np.array([a for a, s in telas]); nome = np.array([s for a, s in telas])
    t0 = np.array([x.timestamp() for x in ini]); t1 = np.array([x.timestamp() for x in fim])
    usuario = np.array([r['codigo_racf'] for r in observacoes])
    dia = np.array([x.date().isoformat() for x in ini])
    chave_dia = np.array([a + '|' + b for a, b in zip(usuario, dia)])
    E = aprender_estrutura(app, nome, t0, t1, chave_dia, train, grupos, z, nomes, P['suporte_candidato'])
    states, sgroup, cyc = E['states'], E['sgroup'], E['cyc']
    S = len(states); work = np.array([sgroup[s] in cyc for s in range(S)])
    Wst = np.flatnonzero(work); Sw = len(Wst)
    suc = np.zeros((S, S)); entry = np.zeros(S)
    for g, o in cyc.items():
        for k_, s in enumerate(o): suc[s, o[(k_ + 1) % len(o)]] = 1
        entry[o[0]] = 1
    suc = suc[np.ix_(Wst, Wst)]; entry = entry[Wst]
    P0w = E['P0'][:, Wst]; sm = P0w.sum(1, keepdims=True)
    P0w = np.where(sm > 0, P0w / np.maximum(sm, 1e-12), 1.0 / Sw)
    Q = P0w[E['ekey']]
    est_full = E['P0'][E['ekey']].argmax(1)
    kind = np.zeros(n, int); kind[sgroup[est_full] == E['TRANS']] = 1
    epis = {}
    for usr in np.unique(usuario):
        sel = usuario == usr
        ep_sel = sel & (sgroup[est_full] == E['EP']) & E['exato']
        per = periodos(ep_sel[sel], dia[sel], set(dia[sel]))
        for d_, e_ in per.items(): epis[usr + '|' + d_] = f'{usr}#{e_}'
    em_ep = np.array([k in epis for k in chave_dia])
    kind[em_ep & (sgroup[est_full] == E['EP']) & E['exato']] = 2
    grupos_dia = {k: (lambda ix: ix[np.lexsort((ix, t0[ix]))])(np.flatnonzero(chave_dia == k)) for k in np.unique(chave_dia)}
    # custos iniciais: preferência genérica por continuar; espera sem limiares (log(1+g/60))
    CT = np.full((4, 2, 7), 5.0)
    CT[:, :, OPT_NAV] = 0.0; CT[:, :, OPT_F] = P['c_toF']; CT[2:, :, OPT_F] = 0.0
    CT[:, :, OPT_NOVA] = 1.1; CT[1, :, OPT_CONT] = 0.4; CT[:, 1, OPT_RETOMA] = 1.5
    CT[2:, :, OPT_EMB] = P['c_emb']; CT[3, :, OPT_EMBC] = P['c_embc']
    gap_bin = 15.0; longo = float(P['horizonte_trilha'])
    gap_tab = np.log1p(np.arange(int(longo // gap_bin) + 1) * gap_bin / 60.0)
    if P['espera'] == 'fixa':
        xs = np.arange(len(gap_tab)) * gap_bin
        gap_tab = np.where(xs < 90, 0.0, 5.2)
    navmax = math.inf; embd = None
    for it in range(P['iteracoes']):
        print(f'Passagem {min(it + 2, 3)}/3: decodificando trilhas (iteração {it + 1})...', flush=True)
        pi = Q[kind == 0].sum(0) + 1e-3; pi /= pi.sum(); R = Q / pi[None, :]
        ent = entry * pi; ent /= ent.sum(); non = (1 - entry) * pi; non /= non.sum()
        caso = np.empty(n, object); ep = np.zeros(n, bool); LN = np.zeros(n, int); OP = np.zeros(n, int)
        segs, NCT, gaps, navgaps = [], np.zeros((4, 2, 7)), [], []
        for k, ix in grupos_dia.items():
            lanes, optv = decodificar_dia(kind[ix], R[ix], t0[ix], t1[ix], suc, ent, non, k in epis,
                                          CT, gap_tab, gap_bin, longo, navmax,
                                          P['feixe_final'] if it == P['iteracoes'] - 1 else P['feixe'], embd)
            c, e_, sg, nc, gs, ngs = _simular(kind[ix], lanes, optv, t0[ix], t1[ix], longo)
            caso[ix] = [f'{k}|{x}' for x in c]; ep[ix] = e_; LN[ix] = lanes; OP[ix] = optv
            segs += [(o, [ix[j] for j in ch]) for o, ch in sg]; NCT += nc; gaps += gs; navgaps += ngs
        # E: fases por segmento; M: emissão por chave, custos de tarefa, esperas e retorno de interrupção
        G = Q.copy()
        for o, ch in segs:
            init = ent if o == OPT_NOVA else (non if o == OPT_RETOMA else pi)
            G[ch] = _fb(Q[ch] / pi[None, :], suc, init)
        if P.get('etapas_subtarefa') == 'aprendidas':
            inicios = [ch[0] for o, ch in segs if o == OPT_EMB]
            if len(inicios) > 50:
                embd = G[inicios].sum(0) + 1.0; embd /= embd.sum()
        W = np.flatnonzero(kind == 0); K = len(E['chaves'])
        num = np.zeros((K, Sw)); np.add.at(num, E['ekey'][W], G[W])
        Ek = (num + P['lambda_emissao'] * P0w) / (num.sum(1, keepdims=True) + P['lambda_emissao'])
        Q = Ek[E['ekey']]
        if P['contexto_emissao'] > 0 or (P['contexto_familia'] > 0 and it == P['iteracoes'] - 1):
            gid = np.array(sorted(set(sgroup[Wst].tolist())))
            Mg = (sgroup[Wst][:, None] == gid[None, :]).astype(float)       # estado -> grupo
            Qg = Q @ Mg; prior_g = Qg[kind == 0].mean(0)
            Pc = contexto_por_vizinhos(grupos_dia, LN, OP, kind, app, Qg, E['exato'], t0, t1, ep)
            opaco = (kind == 0) & ~E['exato']
            if P['contexto_emissao'] > 0:
                fator = ((Pc / np.maximum(prior_g, 1e-9)) ** P['contexto_emissao']) @ Mg.T
                Qn = Q * fator; Qn /= Qn.sum(1, keepdims=True)
                Q = np.where(opaco[:, None], Qn, Q)
        # custos de tarefa por frequência das decisões (EM rígido); episódio fica fixo
        c_ = NCT + .5
        tc, tn = c_[1, 0, OPT_CONT], c_[1, 0, OPT_NOVA]
        c_cont, c_nova = -math.log(tc / (tc + tn)), -math.log(tn / (tc + tn))
        pc_, pn_, pr_ = c_[:, 1, OPT_CONT].sum(), c_[:, 1, OPT_NOVA].sum(), c_[:, 1, OPT_RETOMA].sum()
        c_ret = -math.log(pr_ / (pc_ + pn_ + pr_)); c_novanav = -math.log(pn_ / (pc_ + pn_ + pr_)) - c_nova
        CT[:, :, OPT_NAV] = 0.0; CT[:, :, OPT_NOVA] = c_nova; CT[:, 1, OPT_NOVA] += c_novanav
        CT[1, :, OPT_CONT] = c_cont; CT[:, 1, OPT_RETOMA] = c_ret
        CT[2:, :, OPT_EMB] = P['c_emb']; CT[3, :, OPT_EMBC] = P['c_embc']; CT[:2, :, OPT_F] = P['c_toF']
        if len(gaps) > 50 and P['espera'] == 'aprendida':
            h = np.bincount(np.clip((np.array(gaps) // gap_bin).astype(int), 0, len(gap_tab) - 1),
                            minlength=len(gap_tab)) + .5
            gap_tab = -np.log(h / h.max())
        if len(navgaps) > 50 and P['retorno'] == 'aprendido':
            navmax = retorno_imediato(np.array(navgaps))
        elif isinstance(P['retorno'], (int, float)):
            navmax = float(P['retorno'])
        DEPURACAO.update(navgaps=np.array(navgaps), gaps=np.array(gaps))
    G = Q.copy()
    for o, ch in segs:
        init = ent if o == OPT_NOVA else (non if o == OPT_RETOMA else pi)
        G[ch] = _fb(Q[ch] / pi[None, :], suc, init)
    est = Wst[G.argmax(1)]; conf = G.max(1)
    grupo_evento = sgroup[est].copy()
    if P['contexto_familia'] > 0:
        # família das telas opacas: posterior do feixe x contexto aprendido x emissão / prior
        Gg = G @ Mg
        lg = P['contexto_familia'] * np.log(Gg + 1e-9) + np.log(Pc + 1e-9) + np.log(Qg + 1e-12) - np.log(prior_g + 1e-9)
        grupo_evento = np.where(opaco, gid[lg.argmax(1)], grupo_evento)
    DEPURACAO.update(G=G, Q=Q, Wst=Wst, sgroup=sgroup, kind=kind, est_full=est_full, LN=LN, OP=OP, segs=segs,
                     pi=pi, ent=ent, non=non, suc=suc, ep=ep, nomes=nomes, EP=E['EP'], TRANS=E['TRANS'], ekey=E['ekey'], P0=E['P0'])
    # Montagem dos casos
    casos = defaultdict(list); locais = {}
    for i in range(n):
        chave = ('EP', epis[chave_dia[i]]) if ep[i] else ('L', caso[i])
        casos[chave].append(i)
    numero_ep = {v: j + 1 for j, v in enumerate(sorted(set(epis.values())))}
    for j, (chave, ids) in enumerate(casos.items(), 1):
        for i in ids: locais[i] = j
    resultado = []
    for chave, ids in casos.items():
        evs = []
        for i in sorted(ids, key=lambda j: (t0[j], j)):
            if kind[i] == 1:
                fam = m.TRANSVERSAL; etapa = ' / '.join(telas[i]); ev = 1.0
            elif kind[i] == 2:
                fam = nomes[E['EP']]; etapa = ' / '.join(states[est_full[i]]); ev = 1.0
            else:
                fam = nomes.get(int(grupo_evento[i]), m.INCERTO); etapa = ' / '.join(states[est[i]]); ev = float(conf[i])
            evs.append(m.Evento(i + 2, observacoes[i]['codigo_racf'], ini[i], fim[i], etapa, fam, ev,
                                CRITERIOS[int(OP[i])], locais[i],
                                numero_ep[epis[chave_dia[i]]] if ep[i] else 0))
        resultado.append(evs)
    resultado.sort(key=lambda c: (c[0].inicio, c[0].linha))
    diagnostico = dict(diagnostico)
    diagnostico.update(
        metodo='trilhas_ciclos_interrupcoes_episodios',
        criterios=dict(Counter(e.criterio for c in resultado for e in c)),
        casos_locais=len({e.caso_local for c in resultado for e in c}),
        episodios_longos=len(numero_ep),
        trilhas={'parametros': P, 'estados': S, 'estados_de_trabalho': int(Sw),
                 'removidos_opacos': [list(train[i]) for i in range(len(train)) if train[i][1] in E['opacos']],
                 'candidatos_adicionados': [list(c) for c in E['candidatos']],
                 'ciclos': {nomes.get(int(g), str(g)): [states[s][1] for s in o] for g, o in cyc.items()},
                 'grupo_episodico': nomes.get(int(E['EP'])), 'dias_episodio': len(epis),
                 'retorno_interrupcao_s': None if math.isinf(navmax) else round(navmax, 1),
                 'custos_tarefa': np.round(CT[:2], 3).tolist(),
                 'evidencia': 'apoio posterior condicionado ao modelo; sem calibração externa'})
    return resultado, diagnostico
