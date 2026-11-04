#!/usr/bin/env python3
"""Construye crm_verdelia.xlsx: capa RAW, capa WAREHOUSE, REGLA con fórmulas y FICHA 360.

Pensado para importarse en Google Sheets (Archivo > Importar). Usa IFS, MAXIFS, FILTER y SORT,
que Google Sheets interpreta directamente. En Excel 365 estas funciones existen pero el archivo
generado con openpyxl puede mostrar #NAME? hasta volver a introducir la fórmula.
"""
import csv
import os
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "datos", "raw")
WH = os.path.join(BASE, "datos", "warehouse")
OUT = os.path.join(BASE, "crm_verdelia.xlsx")

MAXR = 200  # filas reservadas en cada tabla para añadir datos en la demo

HEAD_RAW = PatternFill("solid", fgColor="D9CFC1")
HEAD_WH = PatternFill("solid", fgColor="BFD4C8")
HEAD_RULE = PatternFill("solid", fgColor="A7C4B5")
HEAD_FICHA = PatternFill("solid", fgColor="E7DDA8")
NEW_ROW = PatternFill("solid", fgColor="FFF4CC")
BOLD = Font(bold=True)
TITLE = Font(bold=True, size=14)
WRAP = Alignment(wrap_text=True, vertical="top")
THIN = Side(style="thin", color="CCCCCC")


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def to_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return s


def write_table(ws, header, rows, fill, date_cols=(), num_cols=(), widths=None, note=None):
    r0 = 1
    if note:
        ws.cell(row=1, column=1, value=note).font = Font(italic=True, color="555555")
        r0 = 3
    for j, h in enumerate(header, 1):
        c = ws.cell(row=r0, column=j, value=h)
        c.font = BOLD
        c.fill = fill
        c.border = Border(bottom=THIN)
    for i, row in enumerate(rows, r0 + 1):
        for j, v in enumerate(row, 1):
            if j - 1 in date_cols:
                v = to_date(v)
            elif j - 1 in num_cols and v not in ("", None):
                try:
                    v = float(v)
                    if v.is_integer() and "importe" not in header[j - 1]:
                        v = int(v)
                except ValueError:
                    pass
            c = ws.cell(row=i, column=j, value=v)
            if j - 1 in date_cols and hasattr(v, "year"):
                c.number_format = "yyyy-mm-dd"
            if j - 1 in num_cols and header[j - 1] == "importe":
                c.number_format = "#,##0.00 €"
    for j in range(1, len(header) + 1):
        w = (widths or {}).get(j, max(12, min(42, max(len(str(header[j - 1])), *(len(str(r[j - 1])) for r in rows)) + 2)))
        ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(row=r0 + 1, column=1)
    return r0


wb = Workbook()

# ---------------------------------------------------------------- LEEME
ws = wb.active
ws.title = "LEEME"
leeme = [
    ("CRM Verdelia · Hackathon CRM Data Driven (EAE)", TITLE),
    ("Empresa ficticia: Verdelia, tienda online de cosmética natural. Problema: recuperar clientes inactivos.", None),
    ("Decisión que apoya el CRM: a qué clientes inactivos contactamos esta semana, con qué oferta y por qué canal.", None),
    ("", None),
    ("CÓMO ESTÁ ORGANIZADO EL LIBRO", BOLD),
    ("Pestañas RAW_*  = Data Lake. Los datos tal como salen de cada sistema (tienda, web, email, soporte). Formatos distintos, emails sucios. No se tocan.", None),
    ("Pestañas DIM_* y FACT_* = Data Warehouse. Tablas limpias y relacionadas por contact_id. Es el modelo del CRM.", None),
    ("Pestaña REGLA = Interpretación. Una fila por cliente con fórmulas que calculan recencia, valor, engagement, incidencias, score y recomendación.", None),
    ("Pestaña FICHA_360 = Vista integrada. Elige un contact_id en la celda B2 y verás perfil, situación, historial y acción recomendada.", None),
    ("Pestaña PARAMETROS = Fecha de referencia ('hoy') y umbrales de la regla. Cámbialos y todo se recalcula.", None),
    ("Pestaña HISTORIAS = Las dos historias de cliente que se demuestran en el vídeo.", None),
    ("", None),
    ("RECORRIDO DEL DATO (lo que se debe demostrar)", BOLD),
    ("1 Captura: un evento nuevo llega a una fuente (ej. RAW_email_eventos: lucia.ferrer abre la campaña Otoño 2026).", None),
    ("2 Identificación: el email se normaliza (minúsculas, sin espacios) y se busca en DIM_clientes → contact_id C001. La fila se añade a FACT_interacciones.", None),
    ("3 Interpretación: REGLA recalcula a Lucía: Inactivo + valor Alto + engagement → score 7, recomendación 'WhatsApp personal + cupón 15 %'.", None),
    ("4 Activación: la responsable decide y registra la acción en FACT_acciones (estado 'pendiente').", None),
    ("5 Resultado: cuando Lucía compra, el pedido entra en FACT_transacciones y la acción se cierra con su resultado. La regla la pasa a 'Activo'.", None),
    ("", None),
    ("PARA LA DEMO EN VIVO", BOLD),
    ("Las filas sombreadas en amarillo al final de FACT_interacciones, FACT_transacciones y FACT_acciones están vacías para que escribáis los datos nuevos durante la grabación.", None),
    ("Este libro está pensado para Google Sheets (Archivo > Importar > Subir). Usa IFS, MAXIFS, FILTER y SORT.", None),
    ("Todos los datos son ficticios. Ningún nombre, email ni pedido corresponde a personas reales.", None),
]
for i, (t, f) in enumerate(leeme, 1):
    c = ws.cell(row=i, column=1, value=t)
    c.alignment = WRAP
    if f:
        c.font = f
ws.column_dimensions["A"].width = 120

# ---------------------------------------------------------------- PARAMETROS
ws = wb.create_sheet("PARAMETROS")
params = [
    ("Parámetro", "Valor", "Significado"),
    ("fecha_referencia", datetime(2026, 11, 4).date(), "'Hoy' para la regla. Cambiadla para ver cómo evoluciona la cartera."),
    ("activo_max_dias", 60, "Hasta estos días sin comprar el cliente es Activo"),
    ("riesgo_max_dias", 90, "Hasta estos días: En riesgo"),
    ("inactivo_max_dias", 180, "Hasta estos días: Inactivo. Más: Perdido"),
    ("valor_alto_eur", 150, "Gasto en 12 meses a partir del cual el valor es Alto"),
    ("valor_medio_eur", 60, "Gasto en 12 meses a partir del cual el valor es Medio (menos: Bajo)"),
    ("ventana_valor_dias", 365, "Días hacia atrás para sumar el valor"),
    ("ventana_engagement_dias", 30, "Días hacia atrás para considerar que abrió o hizo clic en un email"),
]
for i, row in enumerate(params, 1):
    for j, v in enumerate(row, 1):
        c = ws.cell(row=i, column=j, value=v)
        if i == 1:
            c.font = BOLD
            c.fill = HEAD_RULE
ws["B2"].number_format = "yyyy-mm-dd"
ws.column_dimensions["A"].width = 26
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 70

# ---------------------------------------------------------------- RAW
raw_specs = [
    ("RAW_tienda_pedidos", "tienda_pedidos.csv", "Fuente: tienda online. Fecha dd/mm/aaaa, importe con coma, emails con mayúsculas. Clave natural: customer_email."),
    ("RAW_web_registros", "web_registros.csv", "Fuente: formulario de alta en la web. Origen (utm_source) y consentimiento de marketing (marketing_optin)."),
    ("RAW_email_eventos", "email_eventos.csv", "Fuente: plataforma de email marketing. Un evento por fila (sent / abierto / clic). Timestamp ISO."),
    ("RAW_web_eventos", "web_eventos.csv", "Fuente: web. Reseñas y formularios de preferencias."),
    ("RAW_soporte_tickets", "soporte_tickets.csv", "Fuente: herramienta de soporte. Emails con espacios al principio o al final."),
]
for name, fn, note in raw_specs:
    ws = wb.create_sheet(name)
    header, rows = read_csv(os.path.join(RAW, fn))
    write_table(ws, header, rows, HEAD_RAW, note=note)

# ---------------------------------------------------------------- WAREHOUSE
ws = wb.create_sheet("DIM_clientes")
header, rows = read_csv(os.path.join(WH, "dim_clientes.csv"))
write_table(ws, header, rows, HEAD_WH, date_cols=(4,),
            note="Un cliente = una fila. contact_id es la clave que conecta todas las tablas. email normalizado = minúsculas y sin espacios.")

ws = wb.create_sheet("FACT_transacciones")
header, rows = read_csv(os.path.join(WH, "fact_transacciones.csv"))
r0 = write_table(ws, header, rows, HEAD_WH, date_cols=(2,), num_cols=(4,),
                 note="Pedidos. Vienen de RAW_tienda_pedidos: fecha a ISO, importe a número, email → contact_id. Filas amarillas: para la demo.")
for r in range(r0 + 1 + len(rows), r0 + 1 + len(rows) + 3):
    for j in range(1, len(header) + 1):
        ws.cell(row=r, column=j).fill = NEW_ROW
    ws.cell(row=r, column=3).number_format = "yyyy-mm-dd"
    ws.cell(row=r, column=5).number_format = "#,##0.00 €"

ws = wb.create_sheet("FACT_interacciones")
header, rows = read_csv(os.path.join(WH, "fact_interacciones.csv"))
r0 = write_table(ws, header, rows, HEAD_WH, date_cols=(2,),
                 note="Eventos de email y web unificados. evento ∈ {email_enviado, email_abierto, email_clic, resena_producto, baja_comunicaciones, whatsapp, llamada}. Filas amarillas: para la demo.")
for r in range(r0 + 1 + len(rows), r0 + 1 + len(rows) + 3):
    for j in range(1, len(header) + 1):
        ws.cell(row=r, column=j).fill = NEW_ROW
    ws.cell(row=r, column=3).number_format = "yyyy-mm-dd"

ws = wb.create_sheet("FACT_incidencias")
header, rows = read_csv(os.path.join(WH, "fact_incidencias.csv"))
r0 = write_table(ws, header, rows, HEAD_WH, date_cols=(2, 5), num_cols=(6,),
                 note="Tickets de soporte. estado ∈ {abierto, resuelto}. Un ticket abierto bloquea cualquier oferta comercial.")
for r in range(r0 + 1 + len(rows), r0 + 1 + len(rows) + 2):
    for j in range(1, len(header) + 1):
        ws.cell(row=r, column=j).fill = NEW_ROW

ws = wb.create_sheet("FACT_acciones")
header, rows = read_csv(os.path.join(WH, "fact_acciones.csv"))
r0 = write_table(ws, header, rows, HEAD_WH, date_cols=(2, 9), num_cols=(4,),
                 note="Decisiones tomadas y su resultado. Aquí se cierra el ciclo: estado ∈ {pendiente, ejecutada, cerrada}. Filas amarillas: para la demo.")
for r in range(r0 + 1 + len(rows), r0 + 1 + len(rows) + 4):
    for j in range(1, len(header) + 1):
        ws.cell(row=r, column=j).fill = NEW_ROW
    ws.cell(row=r, column=3).number_format = "yyyy-mm-dd"
    ws.cell(row=r, column=10).number_format = "yyyy-mm-dd"

# ---------------------------------------------------------------- REGLA
ws = wb.create_sheet("REGLA")
rule_header = ["contact_id", "nombre", "consentimiento", "ultima_compra", "dias_sin_compra", "valor_12m",
               "engagement_30d", "incidencia_abierta", "recencia", "valor", "score", "recomendacion", "responsable", "orden"]
ws.cell(row=1, column=1, value="Regla de reactivación. Se recalcula sola con PARAMETROS y las tablas FACT. Ordenad por 'score' para obtener la cola de trabajo de la semana.").font = Font(italic=True, color="555555")
for j, h in enumerate(rule_header, 1):
    c = ws.cell(row=3, column=j, value=h)
    c.font = BOLD
    c.fill = HEAD_RULE
P = "PARAMETROS!$B$"
T = f"FACT_transacciones!$%s$4:$%s${MAXR}"
I = f"FACT_interacciones!$%s$4:$%s${MAXR}"
K = f"FACT_incidencias!$%s$4:$%s${MAXR}"
n_cli = 10
for i in range(n_cli):
    r = 4 + i
    ws.cell(row=r, column=1, value=f"=DIM_clientes!A{4 + i}")
    ws.cell(row=r, column=2, value=f"=INDEX(DIM_clientes!$B$4:$B${MAXR},MATCH($A{r},DIM_clientes!$A$4:$A${MAXR},0))")
    ws.cell(row=r, column=3, value=f"=INDEX(DIM_clientes!$F$4:$F${MAXR},MATCH($A{r},DIM_clientes!$A$4:$A${MAXR},0))")
    ws.cell(row=r, column=4, value=f"=MAXIFS({T % ('C','C')},{T % ('B','B')},$A{r},{T % ('F','F')},\"<>devuelto\")").number_format = "yyyy-mm-dd"
    ws.cell(row=r, column=5, value=f"=IF(D{r}=0,9999,{P}2-D{r})")
    ws.cell(row=r, column=6, value=f"=SUMIFS({T % ('E','E')},{T % ('B','B')},$A{r},{T % ('C','C')},\">=\"&({P}2-{P}8),{T % ('F','F')},\"<>devuelto\")").number_format = "#,##0.00 €"
    ws.cell(row=r, column=7, value=(f"=(COUNTIFS({I % ('B','B')},$A{r},{I % ('E','E')},\"email_abierto\",{I % ('C','C')},\">=\"&({P}2-{P}9))"
                                     f"+COUNTIFS({I % ('B','B')},$A{r},{I % ('E','E')},\"email_clic\",{I % ('C','C')},\">=\"&({P}2-{P}9)))>0"))
    ws.cell(row=r, column=8, value=f"=COUNTIFS({K % ('B','B')},$A{r},{K % ('E','E')},\"abierto\")>0")
    ws.cell(row=r, column=9, value=f"=IFS(E{r}<={P}3,\"Activo\",E{r}<={P}4,\"En riesgo\",E{r}<={P}5,\"Inactivo\",TRUE,\"Perdido\")")
    ws.cell(row=r, column=10, value=f"=IFS(F{r}>={P}6,\"Alto\",F{r}>={P}7,\"Medio\",TRUE,\"Bajo\")")
    ws.cell(row=r, column=11, value=(f"=IF(C{r}=\"no\",0,IFS(I{r}=\"Activo\",0,I{r}=\"En riesgo\",2,I{r}=\"Inactivo\",3,TRUE,1)"
                                      f"+IFS(J{r}=\"Alto\",3,J{r}=\"Medio\",2,TRUE,1)+IF(G{r},1,0))"))
    ws.cell(row=r, column=12, value=(f"=IFS(C{r}=\"no\",\"No contactar (sin consentimiento)\",H{r},\"Resolver incidencia antes de ofertar\","
                                      f"I{r}=\"Activo\",\"Ninguna acción\",AND(I{r}=\"Inactivo\",J{r}=\"Alto\"),\"WhatsApp personal + cupón 15 %\","
                                      f"AND(I{r}=\"Inactivo\",J{r}=\"Medio\"),\"Email cupón 10 % + producto recomendado\","
                                      f"I{r}=\"Inactivo\",\"Email producto recomendado (sin cupón)\",I{r}=\"En riesgo\",\"Email recordatorio reposición (sin descuento)\","
                                      f"TRUE,\"Incluir en campaña genérica trimestral\")"))
    ws.cell(row=r, column=13, value=(f"=IFS(C{r}=\"no\",\"Nadie\",H{r},\"Soporte\",I{r}=\"Activo\",\"Nadie\","
                                      f"AND(I{r}=\"Inactivo\",J{r}=\"Alto\"),\"Atención al cliente\",TRUE,\"Marketing\")"))
    ws.cell(row=r, column=14, value=f"=RANK(K{r},$K$4:$K${3 + n_cli},0)")
widths = [11, 16, 14, 13, 15, 12, 15, 17, 11, 8, 7, 44, 20, 7]
for j, w in enumerate(widths, 1):
    ws.column_dimensions[get_column_letter(j)].width = w
ws.freeze_panes = "C4"
# Explicación de la regla debajo
expl = [
    "CÓMO FUNCIONA LA REGLA",
    "recencia: días desde la última compra → Activo (≤60) · En riesgo (≤90) · Inactivo (≤180) · Perdido (>180).",
    "valor: suma de pedidos no devueltos en los últimos 365 días → Alto (≥150 €) · Medio (≥60 €) · Bajo.",
    "engagement_30d: abrió o hizo clic en algún email en los últimos 30 días (señal de que sigue receptivo).",
    "incidencia_abierta: tiene un ticket de soporte sin resolver (no se le vende nada hasta resolverlo).",
    "score = puntos recencia (Inactivo 3 · En riesgo 2 · Perdido 1 · Activo 0) + puntos valor (Alto 3 · Medio 2 · Bajo 1) + 1 si engagement. Sin consentimiento → 0.",
    "recomendacion: 1) sin consentimiento → no contactar · 2) incidencia abierta → resolverla antes · 3) Activo → nada · 4) Inactivo+Alto → WhatsApp + 15 % · 5) Inactivo+Medio → email + 10 % · 6) Inactivo+Bajo → email sin cupón · 7) En riesgo → recordatorio · 8) Perdido → campaña genérica.",
    "La regla RECOMIENDA. La persona responsable DECIDE y lo registra en FACT_acciones.",
]
for i, t in enumerate(expl, 4 + n_cli + 2):
    c = ws.cell(row=i, column=1, value=t)
    if i == 4 + n_cli + 2:
        c.font = BOLD

# ---------------------------------------------------------------- FICHA_360
ws = wb.create_sheet("FICHA_360")
ws["A1"] = "FICHA 360 DEL CLIENTE"
ws["A1"].font = TITLE
ws["A2"] = "contact_id"
ws["A2"].font = BOLD
ws["B2"] = "C001"
ws["B2"].fill = NEW_ROW
ws["B2"].font = BOLD
ws["C2"] = "← elige un cliente (desplegable)"
dv = DataValidation(type="list", formula1=f"=DIM_clientes!$A$4:$A$13", allow_blank=False)
ws.add_data_validation(dv)
dv.add("B2")
R = f"REGLA!$A$4:$N${3 + n_cli}"
def rule(col):
    return f"=INDEX(REGLA!${col}$4:${col}${3 + n_cli},MATCH($B$2,REGLA!$A$4:$A${3 + n_cli},0))"
def dim(col):
    return f"=INDEX(DIM_clientes!${col}$4:${col}${MAXR},MATCH($B$2,DIM_clientes!$A$4:$A${MAXR},0))"
ficha = [
    ("PERFIL", None, HEAD_FICHA),
    ("Nombre", dim("B"), None), ("Email", dim("C"), None), ("Origen", dim("D"), None),
    ("Fecha de alta", dim("E"), "yyyy-mm-dd"), ("Consentimiento marketing", dim("F"), None),
    ("SITUACIÓN (calculada por REGLA)", None, HEAD_FICHA),
    ("Última compra", rule("D"), "yyyy-mm-dd"), ("Días sin comprar", rule("E"), None),
    ("Valor 12 meses", rule("F"), "#,##0.00 €"), ("Abrió/clic email últimos 30 días", rule("G"), None),
    ("Incidencia abierta", rule("H"), None), ("Segmento recencia", rule("I"), None), ("Segmento valor", rule("J"), None),
    ("Score de prioridad", rule("K"), None),
    ("RECOMENDACIÓN", None, HEAD_FICHA),
    ("Acción recomendada", rule("L"), None), ("Responsable", rule("M"), None),
    ("Nº pedidos", f"=COUNTIF(FACT_transacciones!$B$4:$B${MAXR},$B$2)", None),
    ("Nº interacciones", f"=COUNTIF(FACT_interacciones!$B$4:$B${MAXR},$B$2)", None),
    ("Nº acciones registradas", f"=COUNTIF(FACT_acciones!$B$4:$B${MAXR},$B$2)", None),
]
r = 4
for label, formula, fmt in ficha:
    c = ws.cell(row=r, column=1, value=label)
    if formula is None:
        c.font = BOLD
        c.fill = fmt
        ws.cell(row=r, column=2).fill = fmt
    else:
        c2 = ws.cell(row=r, column=2, value=formula)
        if fmt:
            c2.number_format = fmt
    r += 1
ws.column_dimensions["A"].width = 34
ws.column_dimensions["B"].width = 40
# Historial con FILTER (Google Sheets)
r += 1
blocks = [
    ("HISTORIAL DE PEDIDOS", ["fecha", "transaccion_id", "producto", "importe", "estado"],
     f"=IFERROR(SORT(FILTER({{FACT_transacciones!$C$4:$C${MAXR},FACT_transacciones!$A$4:$A${MAXR},FACT_transacciones!$D$4:$D${MAXR},FACT_transacciones!$E$4:$E${MAXR},FACT_transacciones!$F$4:$F${MAXR}}},FACT_transacciones!$B$4:$B${MAXR}=$B$2),1,FALSE),\"sin pedidos\")"),
    ("HISTORIAL DE INTERACCIONES", ["fecha", "canal", "evento", "detalle", "resultado", "fuente"],
     f"=IFERROR(SORT(FILTER({{FACT_interacciones!$C$4:$C${MAXR},FACT_interacciones!$D$4:$D${MAXR},FACT_interacciones!$E$4:$E${MAXR},FACT_interacciones!$F$4:$F${MAXR},FACT_interacciones!$G$4:$G${MAXR},FACT_interacciones!$H$4:$H${MAXR}}},FACT_interacciones!$B$4:$B${MAXR}=$B$2),1,FALSE),\"sin interacciones\")"),
    ("INCIDENCIAS", ["fecha_apertura", "ticket_id", "motivo", "estado", "fecha_cierre", "valoracion"],
     f"=IFERROR(SORT(FILTER({{FACT_incidencias!$C$4:$C${MAXR},FACT_incidencias!$A$4:$A${MAXR},FACT_incidencias!$D$4:$D${MAXR},FACT_incidencias!$E$4:$E${MAXR},FACT_incidencias!$F$4:$F${MAXR},FACT_incidencias!$G$4:$G${MAXR}}},FACT_incidencias!$B$4:$B${MAXR}=$B$2),1,FALSE),\"sin incidencias\")"),
    ("ACCIONES Y RESULTADOS", ["fecha", "accion_id", "recomendacion", "responsable", "estado", "resultado", "fecha_resultado"],
     f"=IFERROR(SORT(FILTER({{FACT_acciones!$C$4:$C${MAXR},FACT_acciones!$A$4:$A${MAXR},FACT_acciones!$F$4:$F${MAXR},FACT_acciones!$G$4:$G${MAXR},FACT_acciones!$H$4:$H${MAXR},FACT_acciones!$I$4:$I${MAXR},FACT_acciones!$J$4:$J${MAXR}}},FACT_acciones!$B$4:$B${MAXR}=$B$2),1,FALSE),\"sin acciones\")"),
]
for title, cols, formula in blocks:
    c = ws.cell(row=r, column=1, value=title)
    c.font = BOLD
    for j in range(1, len(cols) + 1):
        ws.cell(row=r, column=j).fill = HEAD_FICHA
    r += 1
    for j, h in enumerate(cols, 1):
        ws.cell(row=r, column=j).value = h
        ws.cell(row=r, column=j).font = Font(italic=True)
    r += 1
    ws.cell(row=r, column=1, value=formula)
    for k in range(r, r + 8):
        ws.cell(row=k, column=1).number_format = "yyyy-mm-dd"
    r += 9
for col in "CDEFG":
    ws.column_dimensions[col].width = 24

# ---------------------------------------------------------------- HISTORIAS
ws = wb.create_sheet("HISTORIAS")
historias = [
    ("DOS HISTORIAS DE CLIENTE (mismo CRM, respuestas distintas)", TITLE),
    ("", None),
    ("HISTORIA A · Lucía Ferrer (C001) · 'La clienta valiosa que se ha enfriado'", BOLD),
    ("Situación: 3 pedidos en 12 meses (191 €), última compra hace 110 días. Inactiva, valor Alto. Score 6.", None),
    ("Dato nuevo (2 nov): la plataforma de email registra que lucia.ferrer abre la campaña Otoño 2026. Se normaliza el email y se vincula a C001.", None),
    ("Interpretación: engagement_30d pasa a VERDADERO → score 7. Pasa a ser la primera de la cola. Recomendación: WhatsApp personal + cupón 15 %.", None),
    ("Decisión: Atención al cliente decide llamarla y le ofrece el cupón. Se registra A-003 (pendiente).", None),
    ("Resultado: Lucía compra (P-1035, 68 €). El pedido entra en FACT_transacciones, la acción se cierra con 'Compra 68 €'. La regla la pasa a Activo.", None),
    ("", None),
    ("HISTORIA B · Marcos Vidal (C002) · 'El inactivo al que NO hay que venderle nada todavía'", BOLD),
    ("Situación: 2 pedidos (113 €), última compra hace 95 días. Inactivo, valor Medio. Pero tiene el ticket T-303 abierto: el pack regalo llegó roto.", None),
    ("Interpretación: aunque es inactivo, la regla bloquea la oferta: 'Resolver incidencia antes de ofertar'. Responsable: Soporte.", None),
    ("Decisión: Soporte reenvía el producto y pide disculpas. Se registra A-004.", None),
    ("Resultado: el ticket se cierra con valoración 4. FACT_incidencias cambia a 'resuelto'. La regla recalcula: ahora sí, 'Email cupón 10 % + producto recomendado'.", None),
    ("Moraleja: el mismo dato (95 días sin comprar) produce una acción distinta porque el CRM relaciona pedidos, soporte y consentimiento bajo un mismo contact_id.", None),
    ("", None),
    ("HISTORIA EXTRA · Elena Soto (C003) · 'La inactiva que no podemos contactar'", BOLD),
    ("Inactiva y con valor Medio, pero retiró el consentimiento el 21 de septiembre. Score 0, 'No contactar'. Demuestra que la privacidad forma parte de la regla.", None),
]
for i, (t, f) in enumerate(historias, 1):
    c = ws.cell(row=i, column=1, value=t)
    c.alignment = WRAP
    if f:
        c.font = f
ws.column_dimensions["A"].width = 130

wb.save(OUT)
print("escrito", OUT)
