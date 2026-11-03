#!/usr/bin/env python3
"""Renders the share images of the project pages (og-<slug>.png, og-<slug>-es.png) with headless Chrome.

Usage: python3 blog/build_og.py
"""
import html
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CARDS = {
    "odoo-rag": ("Odoo RAG", "A docs assistant I can measure", [("0.822", "recall@5 on 45 questions"), ("0.50 → 0.90", "Spanish recall@5"), ("0 of 20", "in-scope questions wrongly refused")]),
    "odoo-rag-es": ("Odoo RAG", "Un asistente de documentación que puedo medir", [("0,822", "recall@5 en 45 preguntas"), ("0,50 → 0,90", "recall@5 en español"), ("0 de 20", "preguntas válidas rechazadas")]),
    "modomax": ("ModoMax", "An online store with AI assistants", [("End to end", "designed and built by me"), ("WhatsApp", "support, stale replies dropped"), ("TypeScript", "store, checkout and admin")]),
    "modomax-es": ("ModoMax", "Una tienda online con asistentes de IA", [("De punta a punta", "diseñada y construida por mí"), ("WhatsApp", "soporte, sin respuestas obsoletas"), ("TypeScript", "tienda, pagos y administración")]),
    "apps": ("iPhone apps", "Norte, Citofonía and Maratón Marvel", [("SwiftUI", "native finance and health app"), ("React Native", "digital intercom for buildings"), ("140+", "titles in the Marvel guide")]),
    "apps-es": ("Apps de iPhone", "Norte, Citofonía y Maratón Marvel", [("SwiftUI", "app nativa de finanzas y salud"), ("React Native", "citófono digital para edificios"), ("140+", "títulos en la guía de Marvel")]),
    "citofonia": ("Citofonía", "The building intercom on your phone", [("Calls", "a server-side state machine per apartment"), ("Privacy", "built into the data and tested")]),
    "citofonia-es": ("Citofonía", "El citófono del edificio en el celular", [("Llamadas", "una máquina de estados por depto, en el servidor"), ("Privacidad", "incorporada en los datos y probada")]),
    "flagforge": ("FlagForge", "Feature flags in Rust, one engine everywhere", [("Under a microsecond", "per evaluation, worst case measured"), ("245 tests", "in four layers, open source")]),
    "flagforge-es": ("FlagForge", "Feature flags en Rust, un solo motor en todas partes", [("Menos de 1 microsegundo", "por evaluación, en el peor caso medido"), ("245 pruebas", "en cuatro capas, código abierto")]),
    "construye-hoy": ("Construye Hoy", "Site control for construction firms, with AI that proposes", [("Five roles", "one app, offline first"), ("101 test files", "and no network in any of them")]),
    "construye-hoy-es": ("Construye Hoy", "Control de obras, con IA que propone", [("Cinco roles", "una app, primero sin conexión"), ("101 archivos de prueba", "y ninguno usa la red")]),
    "sac-next": ("SAC Next", "Community alarms: remotes, sirens and a live console", [("Signed commands", "that expire, and silence that is reported"), ("One stack per client", "with encrypted data and backups")]),
    "sac-next-es": ("SAC Next", "Alarma comunitaria: controles, sirenas y una consola en vivo", [("Órdenes firmadas", "que vencen, y el silencio se informa"), ("Un stack por cliente", "con datos y respaldos cifrados")]),
    "how-i-build": ("How I organize development", "process and architecture", [("5 systems", "their architecture and the reasons behind it"), ("8 steps", "from plan to production, with real examples")]),
    "how-i-build-es": ("Cómo organizo el desarrollo", "proceso y arquitectura", [("5 sistemas", "su arquitectura y las razones detrás"), ("8 pasos", "del plan a producción, con ejemplos reales")]),
}

PAGE = """<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0;width:1200px;height:630px;overflow:hidden;font-family:-apple-system,Helvetica,Arial,sans-serif;color:#eef0f6;
background:radial-gradient(circle at 85% 8%,#1b2a55 0,transparent 42%),radial-gradient(#23262e 1px,transparent 1px),#0c0e13;background-size:auto,22px 22px,auto}}
.in{{position:absolute;left:80px;right:80px;top:150px}}
h1{{font-size:62px;line-height:1.1;margin:0;letter-spacing:-.5px}}p{{font-size:32px;color:#a4abbb;margin:18px 0 58px}}
.s{{display:flex;gap:56px}}b{{display:block;font-size:40px;color:#86a4ff}}span{{display:block;font-size:21px;color:#a4abbb;margin-top:6px;max-width:330px}}
</style><div class="in"><h1>{title}</h1><p>{sub}</p><div class="s">{stats}</div></div>"""


def main():
    with tempfile.TemporaryDirectory() as tmp:
        for name, (title, sub, stats) in CARDS.items():
            cells = "".join(f"<div><b>{html.escape(n)}</b><span>{html.escape(t)}</span></div>" for n, t in stats)
            page = pathlib.Path(tmp) / f"{name}.html"
            page.write_text(PAGE.format(title=html.escape(title), sub=html.escape(sub), stats=cells), encoding="utf-8")
            out = ROOT / f"og-{name}.png"
            out.unlink(missing_ok=True)
            # Chrome can exit non-zero while shutting down after writing the file, so the file is what counts.
            result = subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox", f"--user-data-dir={tmp}/chrome", "--hide-scrollbars",
                                     "--window-size=1200,630", f"--screenshot={out}", page.as_uri()], stderr=subprocess.PIPE, stdout=subprocess.DEVNULL, text=True)
            if not out.exists():
                raise SystemExit(f"Chrome did not write {out.name}: {result.stderr[-500:]}")
            print(f"og-{name}.png")


if __name__ == "__main__":
    main()
