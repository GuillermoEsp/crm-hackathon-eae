# CRM Verdelia · Hackathon CRM Data Driven (EAE)

Prototipo de CRM mínimo para el reto del profesor Javier Lorente. Empresa ficticia: Verdelia, tienda online de cosmética natural. Problema: recuperar clientes inactivos. Todos los datos son inventados.

## Qué hay aquí

| Ruta | Qué es |
|---|---|
| `docs/GUIA_RETO.md` | Caso de negocio, arquitectura (Data Lake → Data Warehouse → regla → acción → resultado), diccionario de datos, regla, dos historias, limitaciones, checklist y rúbrica. **Empezad por aquí.** |
| `docs/GUION_VIDEO.md` | Guion de la grabación de 4 minutos con tiempos, pantalla y quién habla. |
| `crm_verdelia.xlsx` | Hoja de cálculo con capa RAW, capa WAREHOUSE, `REGLA` con fórmulas, `FICHA_360` e `HISTORIAS`. Importarla en Google Sheets. |
| `app/index.html` | App de demostración (un solo archivo, se abre con doble clic). Misma regla que la hoja. Permite pegar las pestañas de Sheets. |
| `datos/raw/` | Las cinco fuentes tal como salen de cada sistema (formatos distintos, emails sucios). |
| `datos/warehouse/` | Tablas limpias relacionadas por `contact_id` + `vista_regla_reactivacion.csv` con el resultado de la regla. |
| `scripts/` | Generan datos, hoja y app. `python3 scripts/generate_data.py && python3 scripts/build_xlsx.py && python3 scripts/build_app.py` |

## El flujo en una frase

Un dato nuevo entra en una fuente → se normaliza el email y se vincula a un `contact_id` → la regla recalcula segmento, score y recomendación → una persona decide y registra la acción → el resultado vuelve al CRM como transacción, ticket o baja y la regla se recalcula.

## Google Sheet del equipo

Copia en Google Sheets (configuración regional Estados Unidos, fórmulas verificadas): https://docs.google.com/spreadsheets/d/1DMdDl5t8pUfQlY7Ou_Jd_iYmEJxk70jabTpBzjhWMkg/edit

## Web pública (GitHub Pages)

- Inicio: https://guillermoesp.github.io/crm-hackathon-eae/
- App: https://guillermoesp.github.io/crm-hackathon-eae/app/
- Guía y guion: https://guillermoesp.github.io/crm-hackathon-eae/docs/guia.html

Cada `git push` a `main` vuelve a publicar la web en uno o dos minutos.
