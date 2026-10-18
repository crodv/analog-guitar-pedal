"""Anotación didáctica del esquema ITS8 de JD Sleep, sin alterar conexiones."""
from pathlib import Path
import math
import pymupdf as fitz

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output' / 'pdf'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'docs' / 'ggg_its8_sc.pdf'
doc = fitz.open()
W, H = 1190.55, 841.89  # A3 horizontal
INK = (0.10, 0.15, 0.22)
MUTED = (0.34, 0.39, 0.46)
FONT_DIR = Path('C:/Windows/Fonts')
REG = str(FONT_DIR / 'arial.ttf')
BOLD = str(FONT_DIR / 'arialbd.ttf')

def page():
    p = doc.new_page(width=W, height=H)
    p.insert_font(fontname='Body', fontfile=REG)
    p.insert_font(fontname='Strong', fontfile=BOLD)
    return p

def text(p, x, y, s, size=11, bold=False, color=INK):
    p.insert_text((x, y), s, fontname='Strong' if bold else 'Body', fontsize=size, color=color)

def para(p, box, s, size=11, color=INK, bold=False):
    spare = p.insert_textbox(fitz.Rect(box), s, fontname='Strong' if bold else 'Body', fontsize=size, color=color, lineheight=1.32)
    if spare < 0:
        raise ValueError(f'Texto desbordado: {s[:60]} ({spare})')

COLORS = ['#B77708', '#246BC3', '#C83F51', '#7752BA', '#087F93', '#328248', '#66717D']
def rgb(h):
    return tuple(int(h[i:i+2], 16)/255 for i in (1,3,5))

STAGES = [
    ('Alimentación y referencia', 'D5, C12, R9, R10, C7',
     'Filtrado de 9 V y generación de Vr ≈ 4,5 V.',
     [(242,318),(489,318),(489,436),(242,436)], (472,326)),
    ('Buffer de entrada', 'R22, C1, R1, R2, Q1, R3, C2, R5',
     'Acopla la guitarra; adapta impedancias y fija la polarización.',
     [(292,483),(400,483),(400,441),(490,441),(490,515),(526,515),(526,561),(618,561),(618,636),(646,636),(646,688),(407,688),(407,658),(292,658)], (310,496)),
    ('Ganancia y recorte', 'IC1a, R6, C3, R7, R19, D1, D2, C4',
     'Drive aumenta la ganancia; los diodos producen el overdrive.',
     [(522,361),(735,361),(735,636),(620,636),(620,552),(522,552)], (713,378)),
    ('Filtro y tono activo', 'R8, C5, R16, R20, C9, R11, R17, IC1b, C8, R18',
     'Filtra agudos y permite variar el brillo con Tone.',
     [(790,347),(1073,347),(1073,546),(873,546),(873,684),(790,684),(790,614),(737,614),(737,554),(790,554)], (1038,364)),
    ('Volumen', 'R21: 100 kΩ log, según este esquema',
     'Atenúa la señal que sale de la sección de tono.',
     [(1079,412),(1147,412),(1147,550),(1079,550)], (1127,530)),
    ('Buffer de salida', 'C10, R12, Q2, R14, R15, C11, R13',
     'Reduce la impedancia y bloquea la continua hacia el amplificador.',
     [(1153,395),(1309,395),(1309,640),(1161,640),(1161,726),(1003,726),(1003,615),(1137,615),(1137,470),(1153,470)], (1292,412)),
    ('Bypass e indicador', '3PDT, R23, D4, J1, J2, J3 y batería',
     'El pulsador conmuta efecto/directo y controla el LED.',
     [(113,487),(286,487),(286,665),(374,665),(374,798),(113,798)], (132,765)),
]

p = page()
text(p, 30, 37, 'ITS8 / Tube Screamer: el circuito por etapas', 23, True)
text(p, 30, 61, 'Lectura de izquierda a derecha · Esquema original conservado, con zonas funcionales superpuestas', 11, color=MUTED)

# Banda con recorrido de audio. La alimentación y el bypass se leen aparte.
route = [(1,'Entrada'), (2,'Drive / clipping'), (3,'Tono'), (4,'Volumen'), (5,'Salida')]
x = 30
for idx, label in route:
    color = rgb(COLORS[idx])
    width = 202
    p.draw_rect(fitz.Rect(x,77,x+width,104), color=color, fill=color, fill_opacity=.08, width=1)
    text(p,x+10,95,f'{idx+1}  {label}',11,True,color)
    if idx < 5:
        text(p,x+width+7,95,'>',12,True,MUTED)
    x += 229

src = fitz.open(SOURCE)
clip = fitz.Rect(55,162,735,470)
dest = fitz.Rect(26,116,1164,116+1138*clip.height/clip.width)
p.show_pdf_page(dest,src,0,clip=clip)
scale = dest.width/clip.width
def point(x,y):
    # Coordenadas de la vista de referencia renderizada a escala 1,8.
    return fitz.Point(dest.x0+(x/1.8-clip.x0)*scale, dest.y0+(y/1.8-clip.y0)*scale)

def zone(points, color):
    sh=p.new_shape()
    ps=[point(*q) for q in points]
    sh.draw_polyline(ps+[ps[0]])
    sh.finish(color=color,fill=color,fill_opacity=.055,width=1.8,closePath=True)
    sh.commit()

def badge(n, xy, color):
    pt=point(*xy)
    p.draw_circle(pt,8.5,color=(1,1,1),fill=color,width=1)
    text(p,pt.x-3.0,pt.y+3.5,str(n),10,True,(1,1,1))

for i, st in enumerate(STAGES):
    c=rgb(COLORS[i])
    zone(st[3],c)
    badge(i+1,st[4],c)
zone([(1168,644),(1290,644),(1290,725),(1168,725)],rgb(COLORS[6]))
badge(7,(1273,710),rgb(COLORS[6]))

# Leyenda compacta bajo el esquema, sin tapar componentes.
legend_y=650
for i, st in enumerate(STAGES):
    col=i%4; row=i//4
    xx=30+col*288; yy=legend_y+row*69
    c=rgb(COLORS[i])
    p.draw_rect(fitz.Rect(xx,yy-11,xx+4,yy+42),color=None,fill=c)
    text(p,xx+12,yy,f'{i+1}. {st[0]}',11,True,c)
    para(p,(xx+12,yy+7,xx+273,yy+48),st[2],10)
text(p,30,805,'Los recuadros agrupan funciones; los cables de +9 V, Vr y masa atraviesan varios bloques. Detalles de repaso: página 2.',10,color=MUTED)
text(p,30,825,'Fuente: ITS8, JD Sleep / General Guitar Gadgets, versión 2009-09-18. Anotación didáctica; conexiones y valores originales.',8.5,color=MUTED)
p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(30,812,1000,834),'uri':'https://generalguitargadgets.com/pdf/ggg_its8_sc.pdf'})

p=page()
text(p,30,38,'Qué recordar al leer cada etapa',23,True)
text(p,30,62,'Componentes y cálculos tomados del esquema ITS8 marcado en la página anterior.',11,color=MUTED)

cards=[
('1. Alimentación y referencia',
 'R9 = R10 = 10 kΩ forman un divisor: Vr ≈ 9 V / 2 = 4,5 V. C7 = 47 µF estabiliza esa referencia y C12 = 100 µF filtra la alimentación. D5 es un diodo en derivación para la protección frente a polaridad inversa.\n\nVr es una referencia de continua para polarizar la señal. No es la masa física (GND), que sigue estando a 0 V.'),
('2. Buffer de entrada',
 'C1 = 22 nF bloquea la continua; R22 = 1,5 MΩ mantiene la entrada referida a masa. R2 polariza la base de Q1 desde Vr. Q1 es un seguidor de emisor: su ganancia de tensión es cercana a 1 y adapta impedancias.\n\nVemisor ≈ Vbase - 0,6 a 0,7 V. La corriente de base produce una caída en R2 = 510 kΩ: Vbase depende de la ganancia del transistor y es menor que Vr. C2 = 1 µF bloquea esa continua; R5 refiere la entrada de IC1a a Vr.'),
('3. Ganancia y recorte suave',
 'IC1a es un amplificador no inversor. R19 (Drive, 500 kΩ log) varía la realimentación junto con R7 = 51 kΩ. D1 y D2 (1N914), conectados en sentidos opuestos, reducen la ganancia en los picos y producen el recorte.\n\nSin conducción de los diodos y donde C3 actúa casi como cortocircuito: Av ≈ 1 + (51 kΩ + R19) / 4,7 kΩ ≈ 12 a 118. Es ganancia de pequeña señal, no la ganancia durante el recorte.'),
('4. Filtros y Tone',
 'En la etapa 3, R6 = 4,7 kΩ con C3 = 47 nF hace crecer la ganancia de IC1a con la frecuencia: fc ≈ 1 / (2πRC) ≈ 720 Hz. Por debajo, la ganancia tiende a 1; los graves reciben menos saturación. C4 = 51 pF limita la ganancia a frecuencias altas.\n\nDespués, R8 = 1 kΩ y C5 = 220 nF atenúan agudos (aprox. 720 Hz sin considerar cargas). IC1b, R20, C9, R11 y R17 forman el tono activo. C8 bloquea la continua antes de Volume.'),
('5. Volumen',
 'R21 es un potenciómetro de 100 kΩ log en este esquema. Funciona como divisor de tensión: el cursor toma una fracción de la señal y la envía al buffer de salida.\n\nBajar Level reduce el nivel final, pero la saturación ya se produjo en IC1a. Por eso se puede aumentar Drive y compensar con Level.'),
('6. Buffer de salida',
 'C10 = 100 nF acopla el cursor de Volume a Q2; R12 polariza su base desde Vr. Q2 es otro seguidor de emisor, con R14 = 10 kΩ como carga. R15 = 100 Ω queda en serie con la salida.\n\nC11 = 10 µF bloquea la continua del emisor y R13 = 10 kΩ deja la salida referida a masa. El objetivo es entregar audio al siguiente pedal o amplificador con baja impedancia.'),
]

for i,(title,body) in enumerate(cards):
    col=i%2; row=i//2
    xx=30+col*575; yy=88+row*204
    c=rgb(COLORS[i])
    p.draw_rect(fitz.Rect(xx,yy,xx+555,yy+190),color=c,fill=c,fill_opacity=.025,width=.9)
    p.draw_rect(fitz.Rect(xx,yy,xx+5,yy+190),color=None,fill=c)
    text(p,xx+16,yy+24,title,13,True,c)
    para(p,(xx+16,yy+38,xx+538,yy+181),body,11)

yy=710
p.draw_rect(fitz.Rect(30,yy,1160,779),color=rgb(COLORS[6]),fill=rgb(COLORS[6]),fill_opacity=.04)
text(p,44,yy+22,'7. Bypass, LED y una comprobación de continua',12,True)
para(p,(44,yy+30,1145,yy+66),
     'El 3PDT selecciona efecto o conexión directa y conmuta D4 con R23 = 1 kΩ. Sin señal y con alimentación de 9 V: Vr y las salidas de IC1a/IC1b quedan cerca de 4,5 V; cada emisor, unos 0,6 a 0,7 V por debajo de su base; los jacks de audio, cerca de 0 V DC. Las bases quedan por debajo de Vr por la corriente en R2/R12. Medir respecto de GND.',10.5)
text(p,30,804,'Referencia de construcción: confirmar pinout de transistores y potenciómetros en los componentes elegidos.',10,color=MUTED)
text(p,30,825,'Esquema de referencia: https://generalguitargadgets.com/pdf/ggg_its8_sc.pdf  |  Guía de lectura, sin cambios eléctricos.',9,color=MUTED)
p.insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(30,812,1000,834),'uri':'https://generalguitargadgets.com/pdf/ggg_its8_sc.pdf'})

doc.set_metadata({'title':'ITS8 / Tube Screamer - esquema por etapas', 'author':'Anotación didáctica sobre el esquema de JD Sleep / General Guitar Gadgets', 'subject':'Etapas analógicas, polarización, ganancia, clipping y tono'})
target=OUT/'its8_etapas_anotado.pdf'
doc.save(target,garbage=4,deflate=True)
doc.close()
check=fitz.open(target)
for i,pg in enumerate(check):
    pg.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(OUT/f'its8_etapas_pagina_{i+1}.png')
assert len(check)==2
assert 'Ganancia' in check[1].get_text()
print(target)
print('PDF verificado: 2 páginas; texto extraíble; sin desbordes en cuadros de texto.')
