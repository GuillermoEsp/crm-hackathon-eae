#!/usr/bin/env python3
"""Genera el dataset ficticio del CRM Verdelia en dos capas:

  datos/raw/        -> fuentes tal como salen de cada sistema (formatos distintos, emails sucios)
  datos/warehouse/  -> tablas limpias y relacionadas por contact_id
  app/data.json     -> mismo contenido para la app web

Todos los datos son inventados. No corresponden a personas reales.
"""
import csv
import json
import os
from datetime import date, datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "datos", "raw")
WH = os.path.join(BASE, "datos", "warehouse")
APP = os.path.join(BASE, "app")
for d in (RAW, WH, APP):
    os.makedirs(d, exist_ok=True)

FECHA_REF = date(2026, 11, 4)  # "hoy" para la regla

# ----------------------------------------------------------------------------
# 1. CLIENTES (dim_clientes). El email es la clave natural en las fuentes;
#    contact_id es la clave del CRM.
# ----------------------------------------------------------------------------
clientes = [
    # contact_id, nombre ficticio, email normalizado, origen, fecha alta, consentimiento
    ("C001", "Lucía Ferrer",  "lucia.ferrer@ejemplo.es",  "instagram",  "2025-03-12", "si"),
    ("C002", "Marcos Vidal",  "marcos.vidal@ejemplo.es",  "google",     "2025-06-02", "si"),
    ("C003", "Elena Soto",    "elena.soto@ejemplo.es",    "referido",   "2025-09-20", "no"),
    ("C004", "Jorge Pardo",   "jorge.pardo@ejemplo.es",   "google",     "2024-11-15", "si"),
    ("C005", "Aina Roca",     "aina.roca@ejemplo.es",     "instagram",  "2026-01-10", "si"),
    ("C006", "Pablo Núñez",   "pablo.nunez@ejemplo.es",   "newsletter", "2025-02-05", "si"),
    ("C007", "Carla Ibáñez",  "carla.ibanez@ejemplo.es",  "instagram",  "2025-05-30", "si"),
    ("C008", "Tomás Gil",     "tomas.gil@ejemplo.es",     "referido",   "2025-08-08", "si"),
    ("C009", "Nerea Alonso",  "nerea.alonso@ejemplo.es",  "google",     "2025-04-22", "si"),
    ("C010", "Diego Mora",    "diego.mora@ejemplo.es",    "instagram",  "2026-02-14", "si"),
]
email_to_id = {c[2]: c[0] for c in clientes}

# Variantes "sucias" con las que cada sistema escribe el email (para demostrar
# la resolución de identidad: minúsculas + sin espacios -> contact_id).
raw_email = {
    "C001": {"tienda": "Lucia.Ferrer@ejemplo.es", "email": "lucia.ferrer@ejemplo.es", "soporte": " lucia.ferrer@ejemplo.es"},
    "C002": {"tienda": "marcos.vidal@ejemplo.es", "email": "Marcos.Vidal@ejemplo.es", "soporte": "marcos.vidal@ejemplo.es "},
    "C003": {"tienda": "elena.soto@ejemplo.es", "email": "elena.soto@ejemplo.es", "soporte": "elena.soto@ejemplo.es"},
    "C004": {"tienda": "JORGE.PARDO@ejemplo.es", "email": "jorge.pardo@ejemplo.es", "soporte": "jorge.pardo@ejemplo.es"},
    "C005": {"tienda": "aina.roca@ejemplo.es", "email": "aina.roca@ejemplo.es", "soporte": "aina.roca@ejemplo.es"},
    "C006": {"tienda": "pablo.nunez@ejemplo.es", "email": "Pablo.Nunez@Ejemplo.es", "soporte": "pablo.nunez@ejemplo.es"},
    "C007": {"tienda": "carla.ibanez@ejemplo.es", "email": "carla.ibanez@ejemplo.es", "soporte": "carla.ibanez@ejemplo.es"},
    "C008": {"tienda": "Tomas.Gil@ejemplo.es", "email": "tomas.gil@ejemplo.es", "soporte": "tomas.gil@ejemplo.es"},
    "C009": {"tienda": "nerea.alonso@ejemplo.es", "email": "nerea.alonso@ejemplo.es", "soporte": "nerea.alonso@ejemplo.es"},
    "C010": {"tienda": "diego.mora@ejemplo.es", "email": "diego.mora@ejemplo.es", "soporte": "Diego.Mora@ejemplo.es"},
}

# ----------------------------------------------------------------------------
# 2. TRANSACCIONES (pedidos de la tienda online)
# ----------------------------------------------------------------------------
transacciones = [
    # transaccion_id, contact_id, fecha, producto, importe, estado
    ("P-1001", "C004", "2025-01-20", "Champú sólido de romero", 24.00, "entregado"),
    ("P-1003", "C001", "2025-11-20", "Pack aceites esenciales", 62.00, "entregado"),
    ("P-1004", "C006", "2025-11-28", "Pack aceites esenciales", 71.00, "entregado"),
    ("P-1005", "C004", "2025-12-01", "Bálsamo labial de karité", 12.00, "entregado"),
    ("P-1008", "C002", "2026-01-15", "Champú sólido de romero", 24.00, "entregado"),
    ("P-1011", "C001", "2026-03-02", "Crema facial de caléndula", 58.00, "entregado"),
    ("P-1012", "C007", "2026-03-15", "Champú sólido de romero", 24.00, "entregado"),
    ("P-1014", "C009", "2026-03-28", "Bálsamo labial de karité", 12.00, "entregado"),
    ("P-1016", "C006", "2026-04-10", "Sérum de rosa mosqueta", 42.00, "entregado"),
    ("P-1019", "C005", "2026-05-05", "Sérum de rosa mosqueta", 42.00, "entregado"),
    ("P-1020", "C010", "2026-06-07", "Champú sólido de romero", 24.00, "entregado"),
    ("P-1022", "C003", "2026-06-10", "Crema corporal de almendra", 36.00, "entregado"),
    ("P-1021", "C007", "2026-06-27", "Pack regalo cosmética", 89.00, "entregado"),
    ("P-1024", "C001", "2026-07-17", "Pack regalo cosmética", 71.00, "entregado"),
    ("P-1025", "C003", "2026-07-20", "Jabones artesanales (x3)", 25.00, "entregado"),
    ("P-1023", "C009", "2026-07-27", "Jabones artesanales (x3)", 25.00, "entregado"),
    ("P-1026", "C008", "2026-07-30", "Crema facial de caléndula", 58.00, "entregado"),
    ("P-1027", "C002", "2026-08-01", "Pack regalo cosmética", 89.00, "en incidencia"),
    ("P-1029", "C006", "2026-08-26", "Crema facial de caléndula", 58.00, "entregado"),
    ("P-1033", "C008", "2026-09-20", "Jabones artesanales (x3)", 25.00, "entregado"),
    ("P-1034", "C005", "2026-10-15", "Crema facial de caléndula", 58.00, "entregado"),
]

# ----------------------------------------------------------------------------
# 3. INTERACCIONES (email marketing, web, whatsapp, llamada)
#    fuente = sistema del que procede el dato
# ----------------------------------------------------------------------------
interacciones = [
    # interaccion_id, contact_id, fecha, canal, evento, detalle, resultado, fuente
    ("I-001", "C006", "2026-04-12", "web",   "resena_producto", "Sérum de rosa mosqueta", "4 estrellas", "web"),
    ("I-002", "C006", "2026-07-05", "email", "email_clic",      "Campaña Verano 2026", "clic en producto", "email_marketing"),
    ("I-003", "C001", "2026-07-06", "email", "email_abierto",   "Campaña Verano 2026", "abierto", "email_marketing"),
    ("I-004", "C009", "2026-07-08", "email", "email_abierto",   "Campaña Verano 2026", "abierto", "email_marketing"),
    ("I-005", "C008", "2026-07-31", "email", "email_abierto",   "Campaña Verano 2026", "abierto", "email_marketing"),
    ("I-006", "C004", "2026-08-20", "email", "email_enviado",   "Campaña genérica Q3", "no abierto", "email_marketing"),
    ("I-007", "C006", "2026-08-20", "email", "email_enviado",   "Recordatorio reposición", "abierto", "email_marketing"),
    ("I-008", "C008", "2026-09-18", "web",   "resena_producto", "Crema facial de caléndula", "5 estrellas", "web"),
    ("I-009", "C003", "2026-09-21", "web",   "baja_comunicaciones", "Formulario de preferencias", "consentimiento retirado", "web"),
    ("I-010", "C001", "2026-10-18", "email", "email_enviado",   "Campaña Otoño 2026", "pendiente", "email_marketing"),
    ("I-011", "C002", "2026-10-18", "email", "email_enviado",   "Campaña Otoño 2026", "no abierto", "email_marketing"),
    ("I-012", "C007", "2026-10-18", "email", "email_enviado",   "Campaña Otoño 2026", "no abierto", "email_marketing"),
    ("I-013", "C005", "2026-10-19", "email", "email_clic",      "Campaña Otoño 2026", "clic en producto", "email_marketing"),
    ("I-014", "C006", "2026-10-20", "email", "email_abierto",   "Campaña Otoño 2026", "abierto", "email_marketing"),
    ("I-015", "C009", "2026-10-28", "email", "email_abierto",   "Campaña Otoño 2026", "abierto", "email_marketing"),
]
# Dato NUEVO que entra durante la demostración (no está en la base inicial):
interaccion_nueva = ("I-016", "C001", "2026-11-02", "email", "email_abierto", "Campaña Otoño 2026", "abierto", "email_marketing")

# ----------------------------------------------------------------------------
# 4. INCIDENCIAS (tickets de soporte)
# ----------------------------------------------------------------------------
incidencias = [
    # ticket_id, contact_id, fecha_apertura, motivo, estado, fecha_cierre, valoracion, pedido
    ("T-301", "C004", "2025-12-03", "Pregunta sobre devolución", "resuelto", "2025-12-04", 3, "P-1005"),
    ("T-302", "C010", "2026-06-09", "Consulta estado del envío", "resuelto", "2026-06-10", 5, "P-1020"),
    ("T-303", "C002", "2026-08-03", "Pedido recibido con el envase roto", "abierto", "", "", "P-1027"),
]

# ----------------------------------------------------------------------------
# 5. ACCIONES (decisiones ya tomadas y su resultado). Cierra el ciclo.
# ----------------------------------------------------------------------------
acciones = [
    # accion_id, contact_id, fecha, segmento, prioridad, recomendacion, responsable, estado, resultado, fecha_resultado
    ("A-001", "C006", "2026-08-20", "En riesgo / Alto", 5, "Email recordatorio reposición (sin descuento)", "Marketing", "cerrada", "Compra P-1029 (58 €)", "2026-08-26"),
    ("A-002", "C004", "2026-08-20", "Perdido / Bajo", 2, "Incluir en campaña genérica trimestral", "Marketing", "cerrada", "Sin respuesta", "2026-09-20"),
]

# ----------------------------------------------------------------------------
# REGLA DE REACTIVACIÓN (misma lógica que las fórmulas de la hoja y que la app)
# ----------------------------------------------------------------------------
UMBRALES = {
    "activo_max": 60, "riesgo_max": 90, "inactivo_max": 180,
    "valor_alto": 150, "valor_medio": 60,
    "ventana_valor_dias": 365, "ventana_engagement_dias": 30,
}

def d(s):
    return datetime.strptime(s, "%Y-%m-%d").date()

def evaluar(contact_id, trans, inter, inc, cli, fecha_ref=FECHA_REF):
    c = next(x for x in cli if x[0] == contact_id)
    compras = [t for t in trans if t[1] == contact_id and t[5] != "devuelto"]
    ultima = max((d(t[2]) for t in compras), default=None)
    dias = (fecha_ref - ultima).days if ultima else 9999
    valor = round(sum(t[4] for t in compras if (fecha_ref - d(t[2])).days <= UMBRALES["ventana_valor_dias"]), 2)
    eng = any(i[1] == contact_id and i[4] in ("email_abierto", "email_clic")
              and (fecha_ref - d(i[2])).days <= UMBRALES["ventana_engagement_dias"] for i in inter)
    inc_abierta = any(i[1] == contact_id and i[4] == "abierto" for i in inc)
    consent = c[5] == "si"
    if dias <= UMBRALES["activo_max"]: rec = "Activo"
    elif dias <= UMBRALES["riesgo_max"]: rec = "En riesgo"
    elif dias <= UMBRALES["inactivo_max"]: rec = "Inactivo"
    else: rec = "Perdido"
    if valor >= UMBRALES["valor_alto"]: val = "Alto"
    elif valor >= UMBRALES["valor_medio"]: val = "Medio"
    else: val = "Bajo"
    score = {"Activo": 0, "En riesgo": 2, "Inactivo": 3, "Perdido": 1}[rec] + {"Alto": 3, "Medio": 2, "Bajo": 1}[val] + (1 if eng else 0)
    if not consent:
        reco, resp, score = "No contactar (sin consentimiento)", "Nadie", 0
    elif inc_abierta:
        reco, resp = "Resolver incidencia antes de ofertar", "Soporte"
    elif rec == "Activo":
        reco, resp = "Ninguna acción", "Nadie"
    elif rec == "Inactivo" and val == "Alto":
        reco, resp = "WhatsApp personal + cupón 15 %", "Atención al cliente"
    elif rec == "Inactivo" and val == "Medio":
        reco, resp = "Email cupón 10 % + producto recomendado", "Marketing"
    elif rec == "Inactivo":
        reco, resp = "Email producto recomendado (sin cupón)", "Marketing"
    elif rec == "En riesgo":
        reco, resp = "Email recordatorio reposición (sin descuento)", "Marketing"
    else:
        reco, resp = "Incluir en campaña genérica trimestral", "Marketing"
    return dict(contact_id=contact_id, nombre=c[1], ultima_compra=str(ultima) if ultima else "", dias_sin_compra=dias,
                valor_12m=valor, engagement_30d=eng, incidencia_abierta=inc_abierta, consentimiento=consent,
                recencia=rec, valor=val, score=score, recomendacion=reco, responsable=resp)

# ----------------------------------------------------------------------------
# Escritura de ficheros
# ----------------------------------------------------------------------------
def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)

def ddmmyyyy(s):
    y, m, dd = s.split("-")
    return f"{dd}/{m}/{y}"

# --- RAW: cada fuente con SU formato -----------------------------------------
# Tienda online: fecha dd/mm/aaaa, importe con coma decimal, email con mayúsculas
write_csv(os.path.join(RAW, "tienda_pedidos.csv"),
          ["order_id", "customer_email", "order_date", "product", "total_eur", "fulfillment_status"],
          [(t[0], raw_email[t[1]]["tienda"], ddmmyyyy(t[2]), t[3], f"{t[4]:.2f}".replace(".", ","), t[5]) for t in transacciones])

# Registros web (alta de cuenta + consentimiento). Fuente de dim_clientes.
write_csv(os.path.join(RAW, "web_registros.csv"),
          ["signup_ts", "email", "first_name", "last_name", "utm_source", "marketing_optin"],
          [(c[4] + "T10:00:00Z", raw_email[c[0]]["tienda"], c[1].split()[0], c[1].split()[1], c[3], "true" if c[5] == "si" else "false") for c in clientes])

# Plataforma de email marketing: timestamp ISO, un evento por fila
write_csv(os.path.join(RAW, "email_eventos.csv"),
          ["event_ts", "recipient", "campaign", "event_type"],
          [(i[2] + "T09:30:00Z", raw_email[i[1]]["email"], i[5], i[4].replace("email_", "")) for i in interacciones if i[7] == "email_marketing"])

# Web: reseñas y formularios
write_csv(os.path.join(RAW, "web_eventos.csv"),
          ["ts", "user_email", "event", "item", "value"],
          [(i[2] + "T18:05:00Z", raw_email[i[1]]["tienda"], i[4], i[5], i[6]) for i in interacciones if i[7] == "web"])

# Soporte: fecha ISO, email con espacios
write_csv(os.path.join(RAW, "soporte_tickets.csv"),
          ["ticket_id", "requester_email", "created_at", "subject", "status", "closed_at", "csat", "order_ref"],
          [(i[0], raw_email[i[1]]["soporte"], i[2], i[3], i[4], i[5], i[6], i[7]) for i in incidencias])

# --- WAREHOUSE: tablas limpias relacionadas por contact_id ---------------------
write_csv(os.path.join(WH, "dim_clientes.csv"),
          ["contact_id", "nombre", "email", "origen", "fecha_alta", "consentimiento_marketing"], clientes)
write_csv(os.path.join(WH, "fact_transacciones.csv"),
          ["transaccion_id", "contact_id", "fecha", "producto", "importe", "estado"], transacciones)
write_csv(os.path.join(WH, "fact_interacciones.csv"),
          ["interaccion_id", "contact_id", "fecha", "canal", "evento", "detalle", "resultado", "fuente"], interacciones)
write_csv(os.path.join(WH, "fact_incidencias.csv"),
          ["ticket_id", "contact_id", "fecha_apertura", "motivo", "estado", "fecha_cierre", "valoracion", "pedido"], incidencias)
write_csv(os.path.join(WH, "fact_acciones.csv"),
          ["accion_id", "contact_id", "fecha", "segmento", "prioridad", "recomendacion", "responsable", "estado", "resultado", "fecha_resultado"], acciones)

# Vista calculada (resultado de la regla hoy) para contrastar con la hoja
regla = [evaluar(c[0], transacciones, interacciones, incidencias, clientes) for c in clientes]
write_csv(os.path.join(WH, "vista_regla_reactivacion.csv"), list(regla[0].keys()), [list(r.values()) for r in regla])

# --- JSON para la app ---------------------------------------------------------
data = {
    "fecha_referencia": str(FECHA_REF),
    "umbrales": UMBRALES,
    "clientes": [dict(zip(["contact_id", "nombre", "email", "origen", "fecha_alta", "consentimiento"], c)) for c in clientes],
    "raw_email": raw_email,
    "transacciones": [dict(zip(["transaccion_id", "contact_id", "fecha", "producto", "importe", "estado"], t)) for t in transacciones],
    "interacciones": [dict(zip(["interaccion_id", "contact_id", "fecha", "canal", "evento", "detalle", "resultado", "fuente"], i)) for i in interacciones],
    "interaccion_nueva": dict(zip(["interaccion_id", "contact_id", "fecha", "canal", "evento", "detalle", "resultado", "fuente"], interaccion_nueva)),
    "incidencias": [dict(zip(["ticket_id", "contact_id", "fecha_apertura", "motivo", "estado", "fecha_cierre", "valoracion", "pedido"], i)) for i in incidencias],
    "acciones": [dict(zip(["accion_id", "contact_id", "fecha", "segmento", "prioridad", "recomendacion", "responsable", "estado", "resultado", "fecha_resultado"], a)) for a in acciones],
}
with open(os.path.join(APP, "data.json"), "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print(f"Fecha de referencia: {FECHA_REF}")
    print(f"{'id':5} {'nombre':14} {'últ.compra':11} {'días':>5} {'valor12m':>9} {'eng':>4} {'inc':>4} {'cons':>5} {'recencia':10} {'valor':6} {'sc':>3}  recomendación")
    for r in sorted(regla, key=lambda r: -r["score"]):
        print(f"{r['contact_id']:5} {r['nombre']:14} {r['ultima_compra']:11} {r['dias_sin_compra']:>5} {r['valor_12m']:>9.2f} {str(r['engagement_30d'])[0]:>4} {str(r['incidencia_abierta'])[0]:>4} {str(r['consentimiento'])[0]:>5} {r['recencia']:10} {r['valor']:6} {r['score']:>3}  {r['recomendacion']}")
    # Con el dato nuevo de la demo
    r2 = evaluar("C001", transacciones, interacciones + [interaccion_nueva], incidencias, clientes)
    print("\nTras el dato nuevo (Lucía abre el email):", r2["score"], r2["recomendacion"])
    inc2 = [(i[0], i[1], i[2], i[3], "resuelto", "2026-11-05", 4, i[7]) if i[0] == "T-303" else i for i in incidencias]
    r3 = evaluar("C002", transacciones, interacciones, inc2, clientes)
    print("Tras cerrar el ticket de Marcos:", r3["score"], r3["recomendacion"])
