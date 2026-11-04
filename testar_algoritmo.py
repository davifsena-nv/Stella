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
