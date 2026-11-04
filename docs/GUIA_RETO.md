# CRM Verdelia · Guía del reto (Hackathon CRM Data Driven, EAE)

Todo lo que el equipo necesita para construir, entender y demostrar el CRM. Los datos son ficticios.

## 1. Caso de negocio (lo que hay que decir en los primeros 30 segundos)

| Elemento | Decisión del equipo |
|---|---|
| Empresa | **Verdelia**, tienda online de cosmética natural (ficticia). Vende por web, hace email marketing y atiende soporte por tickets. |
| Cliente | Compradores particulares (B2C) con cuenta en la web. |
| Problema | **Recuperar clientes inactivos**: personas que compraron y llevan más de 90 días sin volver. |
| Decisión que apoya el CRM | *¿A qué clientes inactivos contactamos esta semana, con qué oferta y por qué canal? ¿Y a cuáles no?* |
| Acción posterior | WhatsApp personal con cupón, email con cupón, email sin cupón, recordatorio, campaña genérica, resolver incidencia primero, o no contactar. |
| Valor esperado | Concentrar el esfuerzo (y el descuento) en quien más vale y está receptivo; no molestar a quien tiene una queja abierta o ha retirado el consentimiento. |

## 2. Arquitectura: el recorrido del dato en cinco pasos

```
 FUENTES (raw)            WAREHOUSE                 INTERPRETACIÓN        ACTIVACIÓN           RESULTADO
 tienda_pedidos.csv  ─┐                            
 web_registros.csv   ─┤  normalizar email ─▶ DIM_clientes (contact_id)
 email_eventos.csv   ─┼▶ fecha a ISO       ─▶ FACT_transacciones  ─▶ REGLA (score,   ─▶ Ficha 360 ─▶  FACT_acciones
 web_eventos.csv     ─┤  importe a número  ─▶ FACT_interacciones      segmento,        decisión +     (resultado) ──┐
 soporte_tickets.csv ─┘  asignar contact_id─▶ FACT_incidencias        recomendación)   acción                        │
                                              ▲                                                                       │
                                              └───────────── el resultado vuelve como transacción / ticket / baja ────┘
```

| Paso | Qué ocurre | Dónde se ve |
|---|---|---|
| 1 Captura | Cada sistema escribe con su formato: la tienda usa `dd/mm/aaaa` e importes con coma, el email marketing timestamps ISO, soporte deja espacios en los correos. No se toca nada: es el **Data Lake** (zona raw). | Pestañas `RAW_*` de la hoja · sección 1 de la app · carpeta `datos/raw/` |
| 2 Identificación | Se normaliza el email (`trim` + minúsculas), se busca en `DIM_clientes` y se asigna el `contact_id`. Fechas e importes se estandarizan. Es el **Data Warehouse**: tablas limpias relacionadas por una clave. | Pestañas `DIM_clientes`, `FACT_*` · sección 2 de la app · `datos/warehouse/` |
| 3 Interpretación | Una regla calcula por cliente cuatro señales + consentimiento y produce segmento, score (0-7) y recomendación. | Pestaña `REGLA` · sección 3 de la app |
| 4 Activación | La ficha 360 reúne perfil, situación e historial. Una persona decide y registra la acción en `FACT_acciones` (estado `pendiente`). | Pestaña `FICHA_360` · sección 4 de la app |
| 5 Resultado | Lo que pasó vuelve al CRM: una compra entra como transacción, un ticket se cierra, una baja retira el consentimiento. La acción se cierra con su resultado y la regla se recalcula. | `FACT_acciones`, `FACT_transacciones`, `FACT_incidencias` · sección 5 de la app |

**Por qué dos capas.** Si la regla leyera directamente las fuentes, tendría que entender cinco formatos distintos y cuatro maneras de escribir un email. Separar raw de warehouse hace que cada dato tenga un único lugar de verdad, una clave común y un formato conocido. El Data Lake conserva la evidencia original; el Data Warehouse responde preguntas.

## 3. Modelo de datos (diccionario)

Clave de todo: `contact_id` (C001…). En las fuentes la clave natural es el email, que no es fiable (mayúsculas, espacios). El warehouse lo normaliza una vez y a partir de ahí todo se relaciona por `contact_id`.

### DIM_clientes · ¿Quién es y cuál es su situación?
| Campo | Para qué se recoge |
|---|---|
| contact_id | Clave que conecta todas las tablas. |
| nombre | Ficticio. Para que la responsable sepa a quién llama. |
| email | Normalizado. Es la clave natural con la que llegan los datos de las fuentes. |
| origen | Canal de captación (instagram, google, referido, newsletter). Sirve para la mejora futura: ¿qué origen retiene mejor? |
| fecha_alta | Antigüedad del cliente. |
| consentimiento_marketing | `si`/`no`. Sin consentimiento la regla no recomienda contacto. |

### FACT_transacciones · ¿Qué relación mantiene con la empresa?
`transaccion_id, contact_id, fecha, producto, importe, estado (entregado / devuelto / en incidencia)`. Alimenta recencia (última compra) y valor (suma 12 meses).

### FACT_interacciones · ¿Qué ha ocurrido y cuándo?
`interaccion_id, contact_id, fecha, canal (email/web/whatsapp/llamada), evento, detalle, resultado, fuente`. Eventos usados: `email_enviado`, `email_abierto`, `email_clic`, `resena_producto`, `baja_comunicaciones`. Alimenta el engagement de 30 días.

### FACT_incidencias · ¿Tiene un problema abierto?
`ticket_id, contact_id, fecha_apertura, motivo, estado (abierto / resuelto), fecha_cierre, valoracion, pedido`. Un ticket abierto bloquea cualquier oferta.

### FACT_acciones · ¿Qué hacemos a continuación y qué pasó?
`accion_id, contact_id, fecha, segmento, prioridad, recomendacion, responsable, estado (pendiente / ejecutada / cerrada), resultado, fecha_resultado`. Es donde el CRM aprende: sin esta tabla no se puede saber si la acción funcionó.

## 4. La regla de reactivación

Fecha de referencia ("hoy"): **4 de noviembre de 2026**. Está en `PARAMETROS!B2`; cambiarla recalcula todo.

| Señal | Cálculo | Clases |
|---|---|---|
| Recencia | Días desde la última compra no devuelta | Activo ≤ 60 · En riesgo ≤ 90 · Inactivo ≤ 180 · Perdido > 180 |
| Valor | Suma de pedidos no devueltos en los últimos 365 días | Alto ≥ 150 € · Medio ≥ 60 € · Bajo < 60 € |
| Engagement | Abrió o hizo clic en algún email en los últimos 30 días | sí / no |
| Incidencia abierta | Algún ticket en estado `abierto` | sí / no |
| Consentimiento | De `DIM_clientes` | sí / no |

**Score (0-7)** = puntos de recencia (Inactivo 3 · En riesgo 2 · Perdido 1 · Activo 0) + puntos de valor (Alto 3 · Medio 2 · Bajo 1) + 1 si hay engagement. Sin consentimiento, 0.

**Recomendación**, evaluada en este orden (la primera que se cumple gana):

1. Sin consentimiento → **No contactar**. Responsable: nadie.
2. Incidencia abierta → **Resolver incidencia antes de ofertar**. Responsable: Soporte.
3. Activo → **Ninguna acción**.
4. Inactivo + valor Alto → **WhatsApp personal + cupón 15 %**. Atención al cliente.
5. Inactivo + valor Medio → **Email cupón 10 % + producto recomendado**. Marketing.
6. Inactivo + valor Bajo → **Email producto recomendado (sin cupón)**. Marketing.
7. En riesgo → **Email recordatorio de reposición (sin descuento)**. Marketing.
8. Perdido → **Incluir en campaña genérica trimestral**. Marketing.

Justificación corta para el vídeo: el descuento se reserva para quien más vale (margen), el canal personal para quien justifica el tiempo de una persona, y nadie recibe una oferta con una queja sin resolver ni sin consentimiento.

### Cola de prioridad con los datos iniciales

| # | Cliente | Días | Valor 12 m | Email 30 d | Incidencia | Consent. | Segmento | Score | Recomendación |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C001 Lucía Ferrer | 110 | 191 € | no | — | sí | Inactivo / Alto | 6 | WhatsApp personal + cupón 15 % |
| 2 | C006 Pablo Núñez | 70 | 171 € | sí | — | sí | En riesgo / Alto | 6 | Email recordatorio reposición |
| 3 | C002 Marcos Vidal | 95 | 113 € | no | abierta | sí | Inactivo / Medio | 5 | Resolver incidencia antes de ofertar |
| 4 | C007 Carla Ibáñez | 130 | 113 € | no | — | sí | Inactivo / Medio | 5 | Email cupón 10 % + producto |
| 5 | C009 Nerea Alonso | 100 | 37 € | sí | — | sí | Inactivo / Bajo | 5 | Email producto (sin cupón) |
| 6 | C010 Diego Mora | 150 | 24 € | no | — | sí | Inactivo / Bajo | 4 | Email producto (sin cupón) |
| 7 | C005 Aina Roca | 20 | 100 € | sí | — | sí | Activo / Medio | 3 | Ninguna acción |
| 8 | C004 Jorge Pardo | 338 | 12 € | no | — | sí | Perdido / Bajo | 2 | Campaña genérica trimestral |
| 9 | C008 Tomás Gil | 45 | 83 € | no | — | sí | Activo / Medio | 2 | Ninguna acción |
| 10 | C003 Elena Soto | 107 | 61 € | no | — | **no** | Inactivo / Medio | 0 | No contactar |

## 5. Las dos historias (mismo CRM, respuestas distintas)

### Historia A · Lucía Ferrer (C001): la clienta valiosa que se ha enfriado
1. **Situación**: 3 pedidos en 12 meses (191 €), última compra hace 110 días. Inactiva, valor Alto, score 6.
2. **Captura**: el 2 de noviembre la plataforma de email registra que `lucia.ferrer@ejemplo.es` abre la campaña Otoño 2026. En la tienda su email aparece como `Lucia.Ferrer@ejemplo.es` y en soporte con un espacio delante: es la misma persona.
3. **Identificación**: `trim` + minúsculas → se encuentra en `DIM_clientes` → `C001`. La fila entra en `FACT_interacciones` como `I-016`.
4. **Interpretación**: engagement pasa a sí → score 7. Primera de la cola. Recomendación: WhatsApp personal + cupón 15 %.
5. **Activación**: Atención al cliente decide llamarla el jueves. Se registra `A-003`, pendiente.
6. **Resultado**: compra un pack regalo (68 €). Entra `P-1035` en `FACT_transacciones`, `A-003` se cierra con "Compra 68 €". La regla la pasa a Activo: ninguna acción más.

### Historia B · Marcos Vidal (C002): el inactivo al que no hay que venderle nada todavía
1. **Situación**: 95 días sin comprar, valor Medio. Solo por recencia sería candidato a cupón.
2. **Relación**: su último pedido `P-1027` está "en incidencia" y el ticket `T-303` (envase roto) sigue abierto desde agosto.
3. **Interpretación**: la regla bloquea la oferta: "Resolver incidencia antes de ofertar". Responsable: Soporte, no Marketing.
4. **Activación**: Soporte reenvía el pack y pide disculpas. Se registra `A-004`.
5. **Resultado**: el ticket se cierra con valoración 4. `FACT_incidencias` pasa a `resuelto`, la regla recalcula y ahora sí recomienda "Email cupón 10 % + producto recomendado". Marketing puede actuar en el siguiente ciclo.

**Moraleja**: el mismo dato (unos 100 días sin comprar) produce acciones distintas porque el CRM relaciona pedidos, soporte y consentimiento bajo un mismo `contact_id`. Un envío "a todos los inactivos" habría mandado un cupón a Marcos con la queja sin resolver y otro a Elena (C003), que retiró el consentimiento.

## 6. Cómo usar la hoja y la app juntas

1. **Google Sheets es la fuente de verdad.** Importad `crm_verdelia.xlsx` (Archivo → Importar → Subir). Las fórmulas de `REGLA` y `FICHA_360` usan `IFS`, `MAXIFS`, `FILTER` y `SORT`; están pensadas para Google Sheets.
2. **La app (`app/index.html`) es la vista de demostración.** Arranca con los mismos datos. Para que use los de vuestra hoja: en la sección "Datos", copiad una pestaña entera de Sheets (Ctrl+A, Ctrl+C), pegadla y pulsad "Cargar en la app". Repetid por tabla.
3. **Cada cambio que hagáis en la app aparece en "Registro de esta sesión"** con un botón "Copiar fila". Pegad esa fila en la pestaña correspondiente de la hoja (filas amarillas) y veréis cómo `REGLA` y `FICHA_360` se recalculan solas.
4. Para el vídeo basta con la app, pero enseñar la fila entrando en la hoja y la fórmula recalculándose es la prueba más clara de que el dato recorre todo el camino.

Regenerar todo desde cero (si cambiáis datos en `scripts/generate_data.py`):

```bash
python3 scripts/generate_data.py && python3 scripts/build_xlsx.py && python3 scripts/build_app.py
```

## 7. Reparto de responsabilidades (6.1 del enunciado)

| Rol | Quién | Qué debe poder explicar |
|---|---|---|
| Negocio | | Por qué recuperar inactivos, la decisión semanal y el valor esperado. |
| Datos | | Las cinco fuentes, por qué se normaliza el email, qué campo alimenta qué señal. |
| CRM | | La ficha 360 y la regla, con la cola de prioridad delante. |
| Prueba | | Las dos historias y el caso de Elena. Que cambiar `PARAMETROS` cambia la cola. |
| Demostración | | El guion de 4 minutos y la grabación. |

Todos deben poder seguir el dato de Lucía de principio a fin sin mirar notas.

## 8. Limitaciones reconocidas y siguiente mejora

**Limitaciones**
- La identidad se resuelve solo por email. Dos personas con el mismo correo (o una con dos) se confunden. Un teléfono o un identificador de cliente en la tienda lo mejoraría.
- Los umbrales (60/90/180 días, 150/60 €) están fijados a mano, no aprendidos de los datos.
- Acciones y resultados se registran a mano. No hay integración real con WhatsApp ni con la plataforma de email.
- No se mide causalidad: no sabemos si Lucía habría comprado igual sin la llamada (no hay grupo de control).
- Solo 10 clientes: suficiente para explicar el flujo, no para validar la regla.

**Siguiente mejora** (elegir una para el vídeo)
- Cerrar el ciclo de forma automática: que un pedido nuevo en la tienda cierre solo la acción pendiente de ese cliente.
- Guardar la tasa de respuesta por segmento y acción en `FACT_acciones` para revisar los umbrales cada trimestre.
- Regla de "no insistir": tras dos acciones sin respuesta, pausar al cliente seis meses (Jorge ya lleva una).

## 9. Checklist del enunciado, cubierto

| Checklist | Dónde está |
|---|---|
| Caso, cliente y decisión definidos | Sección 1 de esta guía, cabecera de la app |
| Datos ficticios con finalidad clara | Diccionario (sección 3), todos los nombres inventados |
| Identificador común | `contact_id` en todas las tablas; demostración de normalización en la app (sección 2) |
| Vista integrada | `FICHA_360` en la hoja, sección 4 de la app |
| Regla de segmentación / prioridad | `REGLA` en la hoja, sección 3 de la app |
| Decisión y acción concreta | `FACT_acciones` + formulario en la ficha |
| Resultado vuelve al CRM | Sección 5 de la app, filas amarillas de la hoja |
| Dos historias con resultados distintos | Lucía (compra) y Marcos (incidencia primero) |
| Grabación autoexplicativa ≤ 4 min | `docs/GUION_VIDEO.md` |
| Limitación y mejora | Sección 8 |

## 10. Rúbrica: dónde se gana cada punto

| Criterio | Peso | Qué enseñar |
|---|---|---|
| Comprensión del flujo de datos | 35 % | El dato de Lucía entrando en raw, normalizándose, vinculándose, cambiando el score, generando acción y volviendo como pedido. Enseñar las dos capas. |
| Coherencia del modelo CRM | 25 % | Cinco tablas, una clave, cada campo con una finalidad. La ficha 360. |
| Decisión y acción | 20 % | La cola de prioridad y la recomendación con su "por qué". Que una persona decide. |
| Claridad de la demostración | 15 % | Seguir el guion; una historia completa antes que muchas pantallas. |
| Privacidad y reflexión crítica | 5 % | Datos ficticios, Elena sin consentimiento, limitaciones y mejora. |
