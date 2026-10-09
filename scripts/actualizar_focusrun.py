"""Actualiza la sección "Remediación de Vulnerabilidades en Focus Run" del tablero
con el resumen del SAP Notes Control Center (RPC public.focusrun_resumen).

Uso: python3 scripts/actualizar_focusrun.py index.html resumen.json

Cada campo se localiza por su etiqueta (no por su valor anterior) y debe aparecer
exactamente una vez; si algo no coincide, aborta sin escribir.
"""
import json
import re
import sys

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
         'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
PALABRAS = ['cero', 'una', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho',
            'nueve', 'diez', 'once', 'doce', 'trece', 'catorce', 'quince', 'dieciséis',
            'diecisiete', 'dieciocho', 'diecinueve', 'veinte']


def palabra(n: int) -> str:
    return PALABRAS[n] if 0 <= n < len(PALABRAS) else str(n)


def main(html_path: str, json_path: str) -> None:
    s = open(html_path, encoding='utf-8').read()
    d = json.load(open(json_path, encoding='utf-8'))
    for k in ('pct', 'imp', 'req', 'notas', 'sistemas', 'concluidas', 'mas90', 'buckets', 'generado'):
        if k not in d:
            sys.exit(f'Resumen incompleto: falta "{k}"')
    if not d['req'] or not d['buckets']:
        sys.exit('Resumen vacío: no se publica')

    pct, imp, req = int(d['pct']), int(d['imp']), int(d['req'])
    notas, sis, concl, m90 = int(d['notas']), int(d['sistemas']), int(d['concluidas']), int(d['mas90'])
    y, mo, da = (int(x) for x in d['generado'][:10].split('-'))
    corte = f'{da} de {MESES[mo - 1]} de {y}'

    # Corte anterior (para el delta), solo si ya venía del mismo sistema.
    prev = re.search(r'donut:\{impl:(\d+),pend:\d+\}', s)
    misma_fuente = 'Fuente: SAP Notes Control Center' in s
    prev_imp = int(prev.group(1)) if prev and misma_fuente else None

    if concl == 0:
        frase = f'Aún no hay notas concluidas al 100% entre las {notas} en alcance'
        if m90:
            frase += f'; {palabra(m90)} {"supera" if m90 == 1 else "superan"} el 90%'
    else:
        frase = (f'Una de las {notas} notas en alcance está concluida al 100%' if concl == 1 else
                 f'{palabra(concl).capitalize()} de las {notas} notas en alcance están concluidas al 100%')
        if m90 == 1:
            frase += ' y una más supera el 90%'
        elif m90 > 1:
            frase += f' y {palabra(m90)} más superan el 90%'
    insight = (f'El programa alcanza {pct}% de avance: {imp} de {req} remediaciones implementadas '
               f'sobre {sis} sistemas SAP. {frase}.')

    valor = f'El programa de remediación registra <em>{imp} implementaciones concluidas sobre {req} requeridas</em>'
    if prev_imp is not None and imp > prev_imp:
        valor += f' y suma {imp - prev_imp} más respecto del corte anterior'
    valor += ('. La medición se toma directamente del SAP Notes Control Center, donde cada administrador '
              'documenta su avance por nota y por sistema: una trazabilidad verificable del nivel de '
              'protección alcanzado en la plataforma.')

    filas = ','.join("['{}',{},{},{},{}]".format(str(b[0]).replace("'", "\\'"), *[int(v) for v in b[1:]])
                     for b in d['buckets'])

    reglas = [
        (r'<span class="tag ok">\d+ concluidas</span><div class="big num c-rust" data-count="\d+" data-suffix="%">0</div>'
         r'<div class="lab">Focus Run — avance</div><div class="sub">[^<]*</div>',
         f'<span class="tag ok">{concl} concluidas</span><div class="big num c-rust" data-count="{pct}" data-suffix="%">0</div>'
         f'<div class="lab">Focus Run — avance</div><div class="sub">{notas} notas · {sis} sistemas · {req} remediaciones</div>'),
        (r'El programa alcanza [^<]*', insight),
        (r'data-count="\d+" data-suffix="%">0</div><div class="l">Avance global</div>',
         f'data-count="{pct}" data-suffix="%">0</div><div class="l">Avance global</div>'),
        (r'data-count="\d+">0</div><div class="l">Notas SAP en alcance</div>',
         f'data-count="{notas}">0</div><div class="l">Notas SAP en alcance</div>'),
        (r'data-count="\d+">0</div><div class="l">Sistemas SAP</div>',
         f'data-count="{sis}">0</div><div class="l">Sistemas SAP</div>'),
        (r'data-count="\d+">0</div><div class="l">Remediaciones requeridas</div>',
         f'data-count="{req}">0</div><div class="l">Remediaciones requeridas</div>'),
        (r'data-count="\d+">0</div><div class="l">Implementadas</div>',
         f'data-count="{imp}">0</div><div class="l">Implementadas</div>'),
        (r'data-count="\d+">0</div><div class="l">Notas concluidas</div>',
         f'data-count="{concl}">0</div><div class="l">Notas concluidas</div>'),
        (r'Fuente: SAP Notes Control Center · [^<]*',
         f'Fuente: SAP Notes Control Center · {notas} notas SAP sobre {sis} sistemas · corte {corte}.'),
        (r'El programa de remediación registra <em>[^<]*</em>[^<]*', valor),
        (r'avarows:\[\[.*?\]\]', f'avarows:[{filas}]'),
        (r'donut:\{impl:\d+,pend:\d+\}', f'donut:{{impl:{imp},pend:{req - imp}}}'),
    ]
    for patron, nuevo in reglas:
        encontrados = len(re.findall(patron, s, flags=re.S))
        if encontrados != 1:
            sys.exit(f'Patrón encontrado {encontrados} veces (se esperaba 1): {patron[:70]}')
        s = re.sub(patron, lambda _m: nuevo, s, count=1, flags=re.S)

    open(html_path, 'w', encoding='utf-8').write(s)
    print(f'Focus Run actualizado: {pct}% · {imp}/{req} · {notas} notas · {sis} sistemas · corte {corte}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
