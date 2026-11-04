#!/usr/bin/env python3
"""Inyecta app/data.json en app/template.html y escribe app/index.html (archivo único, funciona sin servidor)."""
import json, os
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(BASE, "app", "data.json"), encoding="utf-8") as f:
    data = json.load(f)
with open(os.path.join(BASE, "app", "template.html"), encoding="utf-8") as f:
    tpl = f.read()
payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
out = tpl.replace("/*__DATA__*/", payload, 1)
with open(os.path.join(BASE, "app", "index.html"), "w", encoding="utf-8") as f:
    f.write(out)
print("escrito app/index.html", len(out), "bytes")
