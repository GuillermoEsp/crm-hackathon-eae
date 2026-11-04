# Guion del vídeo · 4 minutos · Verdelia CRM

Formato recomendado: grabación de pantalla de la app (y un vistazo a la hoja) con voz en off. Una persona narra cada bloque. Tiempo total objetivo: 3:45, margen de 15 s.

Antes de grabar: abrir `app/index.html`, pulsar **Reiniciar datos de ejemplo**, y tener la hoja de Google Sheets abierta en la pestaña `FACT_interacciones` en otra ventana. Ensayar dos veces con cronómetro.

| Tiempo | Pantalla | Quién | Texto (orientativo) |
|---|---|---|---|
| 0:00–0:25 | Cabecera de la app, recorrido de 5 pasos | Negocio | "Somos Verdelia, una tienda online de cosmética natural. Nuestro problema: clientes que compraron y llevan más de 90 días sin volver. La decisión que queremos tomar cada semana es a quién contactamos, con qué oferta y por qué canal. Y a quién no. Para eso hemos construido un CRM mínimo que sigue el dato en cinco pasos." |
| 0:25–0:55 | Sección 1 (Captura), cambiar entre pestañas Tienda / Email / Soporte | Datos | "Los datos nacen en cuatro sistemas que no se ponen de acuerdo: la tienda escribe fechas con barras e importes con coma, el email marketing timestamps, soporte deja espacios en los correos. Esto es nuestro Data Lake: lo guardamos tal cual, sin tocar." |
| 0:55–1:25 | Sección 2 (Identificación): escribir `Lucia.Ferrer@ejemplo.es` y luego ` lucia.ferrer@ejemplo.es` en el campo; pestaña DIM_clientes | Datos | "Para que todo eso hable de la misma persona, el warehouse normaliza el email y asigna un contact_id. Lucía aparece de tres formas distintas en las fuentes; en el CRM es siempre C001. Cinco tablas: clientes, transacciones, interacciones, incidencias y acciones, todas unidas por esa clave." |
| 1:25–1:55 | Sección 3 (Interpretación): cola de prioridad | CRM | "Con las tablas limpias, una regla calcula por cliente cuatro señales: días sin comprar, valor en doce meses, si abrió un email hace poco y si tiene una incidencia abierta. Más el consentimiento. De ahí sale un score de 0 a 7 y una recomendación. Hoy Lucía y Pablo empatan a 6." |
| 1:55–2:20 | Pulsar **Entra un dato nuevo**; se ve el "antes / después"; (opcional) pegar la fila en la hoja y ver REGLA recalcular | Datos | "Entra un dato nuevo: Lucía abre la campaña de otoño. Se normaliza, se vincula a C001, y el score sube a 7. Ahora es la primera de la cola. Si pegamos la misma fila en la hoja, la fórmula de la pestaña REGLA hace exactamente lo mismo." |
| 2:20–2:50 | Sección 4 (Ficha 360 de Lucía): KPIs, "por qué", historial; registrar la acción | CRM | "Esta es su ficha: perfil, situación, historial completo y la recomendación con su porqué: inactiva, valor alto, receptiva. La regla recomienda; Marta, de atención al cliente, decide llamarla y lo registra como acción pendiente." |
| 2:50–3:10 | Sección 5 (Resultado): registrar Compra 68 €; ver el "antes / después" y la fila en el registro | Prueba | "Dos días después Lucía compra. El pedido entra como transacción, la acción se cierra con su resultado y la regla la pasa a Activo. El ciclo se ha cerrado: la próxima decisión ya sabe que esta acción funcionó." |
| 3:10–3:35 | Historia B: seleccionar C002 Marcos; mostrar ticket abierto y recomendación "Resolver incidencia"; registrar resultado "Incidencia resuelta" y ver cómo cambia la recomendación | Prueba | "Segunda historia. Marcos también lleva 95 días sin comprar, pero su último pedido llegó roto y el ticket sigue abierto. Mismo dato, respuesta distinta: el CRM no le manda un cupón, manda a soporte. Cuando el ticket se cierra, la regla recalcula y ahora sí propone el email. Y Elena, que retiró el consentimiento, no recibe nada." |
| 3:35–3:55 | Sección "Limitaciones" | Negocio | "Principal limitación: identificamos solo por email y los umbrales están puestos a mano. Siguiente mejora: que un pedido nuevo cierre solo la acción pendiente y guardar la tasa de respuesta por segmento para ajustar la regla cada trimestre. Todos los datos son inventados." |

## Reglas para que salga bien

- Una sola historia completa antes que muchas pantallas. Si hay que recortar, se recorta Historia B a 15 segundos (solo el bloqueo por incidencia), nunca el ciclo de Lucía.
- Decir siempre **de dónde viene el dato, a quién pertenece, qué significa y qué decisión cambia**. Son las cuatro cosas que pide el enunciado.
- Nombrar las tablas por su nombre (`FACT_interacciones`, `contact_id`): demuestra que entendéis el modelo.
- No vender la herramienta: la app y la hoja hacen lo mismo; lo que se evalúa es el flujo.
- Comprobar que el enlace de la grabación se abre sin permisos antes de entregar.
