#!/usr/bin/env python3
"""Convierte docs/GUIA_RETO.md + docs/GUION_VIDEO.md en docs/guia.html (página única para compartir)."""
import os, markdown
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def md(p):
    with open(os.path.join(BASE, "docs", p), encoding="utf-8") as f:
        return markdown.markdown(f.read(), extensions=["tables", "fenced_code"])
guia = md("GUIA_RETO.md"); guion = md("GUION_VIDEO.md")
html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guía CRM Verdelia</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
<style>
:root{{--bg:#F3F6F2;--surface:#FFFFFF;--surface-2:#E9EFE9;--ink:#1C2822;--muted:#5C6963;--line:#D3DBD3;--accent:#1F5F5B;--accent-soft:#DAEBE6;--raw:#8A6A3F;
--font-display:"Fraunces",Georgia,serif;--font-body:"Source Sans 3","Helvetica Neue",Arial,sans-serif;color-scheme:light}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#121917;--surface:#1A2320;--surface-2:#222E29;--ink:#E4ECE6;--muted:#98A79F;--line:#2C3A33;--accent:#72C4B6;--accent-soft:#1E3A36;--raw:#D1B07C;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#121917;--surface:#1A2320;--surface-2:#222E29;--ink:#E4ECE6;--muted:#98A79F;--line:#2C3A33;--accent:#72C4B6;--accent-soft:#1E3A36;--raw:#D1B07C;color-scheme:dark}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--font-body);font-size:17px;line-height:1.55}}
.wrap{{max-width:980px;margin:0 auto;padding:28px 16px 60px}}
h1,h2,h3{{font-family:var(--font-display);font-weight:700;text-wrap:balance;line-height:1.15}} h1{{font-size:2.1rem;margin:0 0 6px}} h2{{font-size:1.5rem;margin:40px 0 10px;padding-top:14px;border-top:1px solid var(--line)}} h3{{font-size:1.15rem;margin:22px 0 6px}}
p,li{{max-width:72ch}} a{{color:var(--accent)}} code{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.88em;background:var(--surface-2);padding:1px 5px;border-radius:4px}}
pre{{background:var(--surface-2);padding:14px;border-radius:10px;overflow-x:auto;font-size:.82rem;line-height:1.35}} pre code{{background:none;padding:0}}
.tbl{{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--surface);margin:12px 0}} table{{border-collapse:collapse;width:100%;font-size:.92rem;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}} th{{background:var(--surface-2);font-weight:600}} tr:last-child td{{border-bottom:0}}
.lead{{color:var(--muted);margin:0 0 20px}} .tag{{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.8rem;font-weight:600;background:var(--accent-soft);color:var(--accent)}}
nav{{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px}} nav a{{text-decoration:none;font-size:.9rem;padding:5px 12px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--ink)}}
blockquote{{margin:0;padding:8px 14px;border-left:4px solid var(--accent);background:var(--surface-2);border-radius:0 8px 8px 0}}
</style></head><body><div class="wrap">
<span class="tag">Hackathon CRM Data Driven · EAE</span>
<nav><a href="#guia">Guía del reto</a><a href="#guion">Guion del vídeo</a></nav>
<section id="guia">{guia}</section>
<section id="guion" style="margin-top:50px">{guion}</section>
<p class="lead" style="margin-top:40px">Todos los datos son ficticios. Material complementario: <code>crm_verdelia.xlsx</code> y la app "Verdelia CRM".</p>
</div></body></html>"""
html = html.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
with open(os.path.join(BASE, "docs", "guia.html"), "w", encoding="utf-8") as f:
    f.write(html)
print("escrito docs/guia.html", len(html))
