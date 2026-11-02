#!/usr/bin/env python3
"""Builds the project pages (projects/ and es/projects/) from the content in this file.

Usage: python3 blog/build_pages.py

Figures on these pages must match their source: odoo-rag's evals/results.json for the RAG numbers.
"""
import html
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from build import FAVICON, NOFLASH, SCRIPTS, SITE, T, TOGGLE

ROOT = pathlib.Path(__file__).resolve().parent.parent

MODOMAX_REPO_NOTE = {
    "en": "The source is private. Happy to walk through it in an interview.",
    "es": "El código es privado. Con gusto lo recorro en una entrevista.",
}


def shot(name, alt, caption="", width=1400, height=875):
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (f'<figure class="shot"><img src="%ROOT%img/{name}.webp" alt="{html.escape(alt)}" '
            f'width="{width}" height="{height}" loading="lazy" decoding="async">{cap}</figure>')


def phones(label, items, height=1175):
    cells = "".join(
        f'<div><img src="%ROOT%img/{name}.webp" alt="{html.escape(alt)}" width="540" height="{height}" loading="lazy" decoding="async">'
        f"<span>{html.escape(cap)}</span></div>"
        for name, alt, cap in items
    )
    return f'<div class="phones" role="group" aria-label="{html.escape(label)}">{cells}</div>'


def term(title, lines, caption):
    body = "".join(f'<span class="{k}">{html.escape(t)}</span>' if k else f"<span>{html.escape(t)}</span>" for k, t in lines)
    return (f'<figure class="term" data-replay><div class="term-bar"><i></i><i></i><i></i><b>{html.escape(title)}</b></div>'
            f'<code class="term-body">{body}</code></figure><p class="cap">{caption}</p>')


def bars(caption, rows):
    trs = ""
    for label, value, top in rows:
        cls = ' class="top"' if top else ""
        trs += (f'<tr{cls}><th scope="row">{html.escape(label)}</th>'
                f'<td data-tip="{html.escape(label)}: {value}%"><i style="width:{value * 0.8:.0f}%"></i><b>{value}%</b></td></tr>')
    return f"<table><caption>{html.escape(caption)}</caption><tbody>{trs}</tbody></table>"


RAG_RUN = [
    ("cmd", '$ uv run python -m odoo_rag.ask "¿Cómo ejecuto solo algunos tests desde la línea de comandos?"'),
    ("", "Para ejecutar solo algunos tests desde la línea de comandos, puedes utilizar"),
    ("", "el comando `odoo-bin --test-tags` con los tags correspondientes."),
    ("", "$ odoo-bin --test-tags '/sale,-slow'"),
    ("", ""),
    ("dim", "[2] developer_reference_backend_testing.rst | Testing Python code > Test selection > Invocation"),
    ("dim", "[3] developer_reference_backend_testing.rst | Testing Python code > Test selection > Examples"),
    ("", ""),
    ("cmd", '$ uv run python -m odoo_rag.ask "What is the capital of France?"'),
    ("ok", "NOT_IN_DOCS"),
]

TEST_RUN = [
    ("cmd", "$ uv run pytest -q"),
    ("ok", "10 passed in 0.16s"),
    ("cmd", "$ gh run list -R Ssebv/odoo-rag -L 1 --json conclusion,status -q '.[0]'"),
    ("ok", '{"conclusion":"success","status":"completed"}'),
]


def rag_charts(lang):
    es = lang == "es"
    a = bars("Recall@5, todas las preguntas" if es else "Recall@5, all questions", [
        ("Palabras clave" if es else "Keyword", 73, False),
        ("Vectorial" if es else "Vector", 67, False),
        ("Híbrida" if es else "Hybrid", 73, False),
        ("Híbrida + traducción" if es else "Hybrid + translation", 82, True),
    ])
    b = bars("Recall@5, preguntas en español" if es else "Recall@5, Spanish questions", [
        ("Palabras clave" if es else "Keyword", 40, False),
        ("Vectorial" if es else "Vector", 20, False),
        ("Híbrida" if es else "Hybrid", 50, False),
        ("Híbrida + traducción" if es else "Hybrid + translation", 90, True),
    ])
    return f'<div class="bars">{a}{b}</div>'


PAGES = {
    "odoo-rag": {
        "en": dict(
            title="Odoo RAG: a docs assistant I can measure",
            summary="A RAG assistant over the Odoo 19 developer docs, with an evaluation suite that shows which changes actually helped, and what it still gets wrong.",
            body=f"""
<p class="lead">An assistant that answers only from the Odoo 19 developer docs and my migration notes, cites its sources, and says so when it does not know. The part I care about most is the evaluation: every retrieval change is measured instead of assumed.</p>
<div class="actions"><a href="https://github.com/Ssebv/odoo-rag" target="_blank" rel="noopener">Source code on GitHub →</a></div>

<h2 id="how">How it works</h2>
<ol class="flow"><li>Question</li><li class="arrow">→</li><li>Translate if Spanish</li><li class="arrow">→</li><li>Vector + keyword search</li><li class="arrow">→</li><li>Rank fusion</li><li class="arrow">→</li><li>llama3.2</li><li class="arrow">→</li><li class="end">Cited answer or NOT_IN_DOCS</li></ol>
<p>It runs on PostgreSQL with pgvector and local Ollama models, over 341 chunks from 14 documents. There are no API keys and no per-call cost. The trade-off is speed: a median of about 20 seconds per answer on a laptop.</p>
{term("odoo-rag", RAG_RUN, "Replay of a real run, shortened. The first question is in Spanish; the docs are in English. The second is out of scope, so the assistant refuses.")}

<h2 id="numbers">The numbers</h2>
<p>I compared four retrieval modes on 45 hand-written questions, 35 in English and 10 in Spanish. Recall@5 is how often the right passage appears in the top five results.</p>
{rag_charts("en")}
<p>The surprise was where the gain came from. Hybrid search alone did not beat keyword search on Recall@5. Translating the question did: Spanish went from 50% to 90%, and English stayed at 80%.</p>
<p>On 20 in-scope and 8 out-of-scope questions, 90% of answers contained the expected terms, 80% had valid citations, none was wrongly refused, and 7 of 8 out-of-scope questions were refused.</p>

<h2 id="wrong">What it still gets wrong</h2>
<ul>
<li><strong>A wrong answer on a key question.</strong> Asked how to stop a data file from overwriting records users edited, it answers <code>forcecreate</code>. The right answer is <code>noupdate</code>.</li>
<li><strong>One refusal it should have made.</strong> It answered a question about the 2022 World Cup.</li>
<li><strong>The evaluation has limits too.</strong> I wrote the questions against this same corpus, so the numbers compare modes and do not predict performance elsewhere. The citation metric checks that a cited excerpt exists, not that it supports the claim.</li>
</ul>
<p>Both failures are recorded in the <a href="https://github.com/Ssebv/odoo-rag/blob/main/evals/results.json" target="_blank" rel="noopener">results file</a>, so any future change has to prove it fixes them.</p>
""",
        ),
        "es": dict(
            title="Odoo RAG: un asistente de documentación que puedo medir",
            summary="Un asistente RAG sobre la documentación de Odoo 19, con una evaluación que muestra qué cambios ayudaron de verdad y en qué sigue fallando.",
            body=f"""
<p class="lead">Un asistente que responde solo desde la documentación de Odoo 19 y mis notas de migración, cita sus fuentes y lo dice cuando no sabe. Lo que más me importa es la evaluación: cada cambio en la búsqueda se mide en vez de suponerse.</p>
<div class="actions"><a href="https://github.com/Ssebv/odoo-rag" target="_blank" rel="noopener">Código en GitHub →</a></div>

<h2 id="como">Cómo funciona</h2>
<ol class="flow"><li>Pregunta</li><li class="arrow">→</li><li>Traducción si está en español</li><li class="arrow">→</li><li>Búsqueda vectorial + palabras clave</li><li class="arrow">→</li><li>Fusión de rankings</li><li class="arrow">→</li><li>llama3.2</li><li class="arrow">→</li><li class="end">Respuesta citada o NOT_IN_DOCS</li></ol>
<p>Corre sobre PostgreSQL con pgvector y modelos locales de Ollama, con 341 fragmentos de 14 documentos. No usa claves de API ni tiene costo por consulta. A cambio es más lento: una mediana de unos 20 segundos por respuesta en un notebook.</p>
{term("odoo-rag", RAG_RUN, "Repetición de una ejecución real, acortada. La primera pregunta está en español y la documentación en inglés. La segunda está fuera de alcance, así que el asistente se niega a responder.")}

<h2 id="cifras">Las cifras</h2>
<p>Comparé cuatro modos de búsqueda con 45 preguntas escritas a mano, 35 en inglés y 10 en español. Recall@5 indica con qué frecuencia el pasaje correcto aparece entre los cinco primeros resultados.</p>
{rag_charts("es")}
<p>Lo sorprendente fue de dónde salió la mejora. La búsqueda híbrida por sí sola no le ganó a la de palabras clave en Recall@5. Traducir la pregunta sí: el español subió de 50 % a 90 %, y el inglés se mantuvo en 80 %.</p>
<p>Con 20 preguntas dentro de alcance y 8 fuera, el 90 % de las respuestas incluyó los términos esperados, el 80 % trajo citas válidas, ninguna se rechazó por error y se rechazaron 7 de las 8 fuera de alcance.</p>

<h2 id="fallas">En qué sigue fallando</h2>
<ul>
<li><strong>Una respuesta incorrecta en una pregunta clave.</strong> Si se le pregunta cómo evitar que un archivo de datos sobrescriba registros editados por usuarios, responde <code>forcecreate</code>. Lo correcto es <code>noupdate</code>.</li>
<li><strong>Un rechazo que debió hacer.</strong> Respondió una pregunta sobre el Mundial de 2022.</li>
<li><strong>La evaluación también tiene límites.</strong> Escribí las preguntas sobre este mismo corpus, así que las cifras comparan modos y no predicen el resultado en otros casos. La métrica de citas revisa que el fragmento citado exista, no que respalde lo que se afirma.</li>
</ul>
<p>Ambas fallas quedan registradas en el <a href="https://github.com/Ssebv/odoo-rag/blob/main/evals/results.json" target="_blank" rel="noopener">archivo de resultados</a>, así que cualquier cambio futuro tiene que demostrar que las corrige.</p>
""",
        ),
    },
    "modomax": {
        "en": dict(
            title="ModoMax: an online store with AI assistants",
            summary="A full online store platform in TypeScript with a shopping assistant, WhatsApp support and an admin panel with AI tools.",
            body=f"""
<p class="lead">A full online store I designed and built end to end: catalog, checkout flows, tax documents, a shopping assistant, WhatsApp support and an admin panel with AI tools.</p>
<div class="actions"><a href="https://modomax.ressc.vip" target="_blank" rel="noopener">Visit the store →</a></div>
{shot("modomax-home", "ModoMax store home page with the headline Protege lo que coleccionas", "The deployed store. It runs on test data, so prices, ratings and sales figures are not real.")}
<div class="gallery">
{shot("modomax-catalog", "ModoMax catalog with product cards and filters", "Catalog.")}
{shot("modomax-product", "ModoMax product page for a wireless charger", "Product page.")}
</div>

<h2 id="decisions">Decisions worth explaining</h2>
<ul>
<li><strong>Tool calling instead of RAG.</strong> The catalog is small and structured, so the assistant searches it through a tool that always returns current data. A vector index would have added moving parts it did not need.</li>
<li><strong>Stale replies are discarded.</strong> On WhatsApp, people send several short messages in a row. If a new one arrives while the model is working, the old reply is dropped rather than answering a question that has already changed.</li>
<li><strong>The public endpoint is limited.</strong> The assistant needs no login, so it is limited to 10 requests per minute per IP address.</li>
<li><strong>AI output is validated.</strong> Business insights in the admin panel must pass Zod schemas before they are shown.</li>
</ul>

<h2 id="stack">Stack and tests</h2>
<p>TypeScript, Next.js, React, Prisma, PostgreSQL, Vercel AI SDK and the Anthropic API, with 48 test files across Vitest and Playwright.</p>
<p>{MODOMAX_REPO_NOTE["en"]}</p>
""",
        ),
        "es": dict(
            title="ModoMax: una tienda online con asistentes de IA",
            summary="Una plataforma completa de tienda online en TypeScript, con asistente de compras, atención por WhatsApp y panel de administración con herramientas de IA.",
            body=f"""
<p class="lead">Una tienda online completa que diseñé y construí de punta a punta: catálogo, flujos de compra, documentos tributarios, asistente de compras, atención por WhatsApp y un panel de administración con herramientas de IA.</p>
<div class="actions"><a href="https://modomax.ressc.vip" target="_blank" rel="noopener">Ver la tienda →</a></div>
{shot("modomax-home", "Portada de la tienda ModoMax con el titular Protege lo que coleccionas", "La tienda desplegada. Funciona con datos de prueba, así que precios, valoraciones y cifras de venta no son reales.")}
<div class="gallery">
{shot("modomax-catalog", "Catálogo de ModoMax con tarjetas de producto y filtros", "Catálogo.")}
{shot("modomax-product", "Página de producto de ModoMax de un cargador inalámbrico", "Página de producto.")}
</div>

<h2 id="decisiones">Decisiones que vale la pena explicar</h2>
<ul>
<li><strong>Tool calling en lugar de RAG.</strong> El catálogo es pequeño y estructurado, así que el asistente lo consulta con una herramienta que siempre devuelve datos actuales. Un índice vectorial habría sumado piezas que no necesitaba.</li>
<li><strong>Las respuestas obsoletas se descartan.</strong> Por WhatsApp la gente envía varios mensajes cortos seguidos. Si llega uno nuevo mientras el modelo trabaja, se descarta la respuesta anterior en vez de contestar una pregunta que ya cambió.</li>
<li><strong>El acceso público tiene límite.</strong> El asistente no pide iniciar sesión, así que está limitado a 10 consultas por minuto por dirección IP.</li>
<li><strong>Lo que genera la IA se valida.</strong> Los insights de negocio del panel deben pasar esquemas Zod antes de mostrarse.</li>
</ul>

<h2 id="stack">Tecnologías y pruebas</h2>
<p>TypeScript, Next.js, React, Prisma, PostgreSQL, Vercel AI SDK y la API de Anthropic, con 48 archivos de prueba entre Vitest y Playwright.</p>
<p>{MODOMAX_REPO_NOTE["es"]}</p>
""",
        ),
    },
    "apps": {
        "en": dict(
            title="iPhone apps: Norte, Citofonía and Maratón Marvel",
            summary="Three mobile products I designed and built: a native finance and health app, a digital intercom for apartment buildings and a guide to watching Marvel in story order.",
            body=f"""
<p class="lead">Three mobile products I designed and built with <a href="./how-i-build.html">coding agents</a>, each on a different stack. These are real screens, not design mockups.</p>

<h2 id="norte">Norte</h2>
<p>A personal app that brings finances, training, nutrition and habits together. It is native SwiftUI with no third-party dependencies, with Apple Watch and widget targets, a Next.js API over SQLite, and Claude for analysis.</p>
{phones("Norte screens", [("app-norte-finanzas", "Norte finances with net worth and a savings goal", "Finances"), ("app-norte-salud", "Norte health summary with recovery, calories and protein", "Health"), ("app-norte-entreno", "Norte training session with the muscles worked today", "Training")])}
<p class="cap">Captured in the iPhone simulator against a local test server with seeded demo data. None of these figures are real.</p>
<p>More than 280 Swift files, over 80 of them tests. The screen tests refuse to run against production. The source is private.</p>

<h2 id="citofonia">Citofonía</h2>
<p>The building intercom on your phone: concierge calls, door opening, QR visits, parcels, reservations and votes, with a tablet for the concierge and a panel for administrators. It is in development, built with React Native and Expo, Hono, Supabase and LiveKit for calls.</p>
{phones("Citofonía screens", [("app-citofonia-llamada", "Incoming concierge call on the resident's phone", "Concierge call"), ("app-citofonia-reservas", "Common-area reservations with their rules", "Reservations"), ("app-citofonia-qr", "Visits list with a QR pass that expires", "Visits")], 1169)}
<p class="cap">Real captures of the app with a fictional building and fictional residents.</p>
<figure class="shot"><video controls preload="none" playsinline muted width="1280" height="720" poster="%ROOT%img/citofonia-video.webp" aria-label="Tour of Citofonía"><source src="%ROOT%video/citofonia.mp4" type="video/mp4"></video><figcaption>A 65-second silent tour, with on-screen text in Spanish. All data is fictional.</figcaption></figure>
<p>23 resident screens, 9 for the concierge and 17 admin pages over 105 database migrations. CI runs type checks, pgTAP, Vitest and end-to-end tests. The source is private.</p>

<h2 id="marvel">Maratón Marvel</h2>
<p>Every Marvel and X-Men title in story order, with progress tracking: more than 140 titles, counting comics and animation, and 1,600 episodes. The web app is live and free. A native SwiftUI version is in development, and that is the one shown here.</p>
{phones("Maratón Marvel screens", [("app-marvel-inicio", "Maratón Marvel home with progress and the next title", "Home"), ("app-marvel-cronologia", "Timeline of X-Men films in story order", "Timeline"), ("app-marvel-ficha", "Detail page for a film", "Title page")])}
<p class="cap">Captured in the iPhone simulator. Film images belong to their studios.</p>
<div class="actions"><a href="https://ssebv.github.io/maraton-marvel/?lang=en" target="_blank" rel="noopener">Open the web app →</a><a href="https://github.com/Ssebv/maraton-marvel" target="_blank" rel="noopener">Source code</a></div>
""",
        ),
        "es": dict(
            title="Apps de iPhone: Norte, Citofonía y Maratón Marvel",
            summary="Tres productos móviles que diseñé y construí: una app nativa de finanzas y salud, un citófono digital para edificios y una guía para ver Marvel.",
            body=f"""
<p class="lead">Tres productos móviles que diseñé y construí con <a href="./how-i-build.html">agentes de programación</a>, cada uno con un stack distinto. Son pantallas reales, no maquetas de diseño.</p>

<h2 id="norte">Norte</h2>
<p>Una app personal que reúne finanzas, entrenamiento, alimentación y hábitos. Es nativa en SwiftUI y sin dependencias de terceros, con objetivos para Apple Watch y widgets, una API en Next.js sobre SQLite, y Claude para los análisis.</p>
{phones("Pantallas de Norte", [("app-norte-finanzas", "Finanzas de Norte con patrimonio y una meta de ahorro", "Finanzas"), ("app-norte-salud", "Resumen de salud de Norte con recuperación, calorías y proteína", "Salud"), ("app-norte-entreno", "Sesión de entrenamiento de Norte con los músculos del día", "Entreno")])}
<p class="cap">Capturadas en el simulador de iPhone contra un servidor local de prueba con datos de demostración. Ninguna de estas cifras es real.</p>
<p>Más de 280 archivos Swift, más de 80 de ellos de pruebas. Las pruebas de pantalla se niegan a correr contra producción. El código es privado.</p>

<h2 id="citofonia">Citofonía</h2>
<p>El citófono del edificio en el celular: llamadas de portería, apertura de puertas, visitas con QR, encomiendas, reservas y votaciones, con una tablet para conserjería y un panel para la administración. Está en desarrollo, con React Native y Expo, Hono, Supabase y LiveKit para las llamadas.</p>
{phones("Pantallas de Citofonía", [("app-citofonia-llamada", "Llamada entrante de portería en el celular del residente", "Llamada de portería"), ("app-citofonia-reservas", "Reservas de espacios comunes con sus reglas", "Reservas"), ("app-citofonia-qr", "Lista de visitas con un pase QR que vence", "Visitas")], 1169)}
<p class="cap">Capturas reales de la app con un edificio y residentes ficticios.</p>
<figure class="shot"><video controls preload="none" playsinline muted width="1280" height="720" poster="%ROOT%img/citofonia-video.webp" aria-label="Recorrido por Citofonía"><source src="%ROOT%video/citofonia.mp4" type="video/mp4"></video><figcaption>Un recorrido de 65 segundos sin sonido. Todos los datos son ficticios.</figcaption></figure>
<p>23 pantallas del residente, 9 de conserjería y 17 páginas de administración, sobre 105 migraciones de base de datos. La integración continua corre tipos, pgTAP, Vitest y pruebas de punta a punta. El código es privado.</p>

<h2 id="marvel">Maratón Marvel</h2>
<p>Todo Marvel y X-Men en el orden de la historia, con seguimiento de avance: más de 140 títulos, contando cómics y animación, y 1.600 episodios. La app web está publicada y es gratis. Hay una versión nativa en SwiftUI en desarrollo, y es la que se ve aquí.</p>
{phones("Pantallas de Maratón Marvel", [("app-marvel-inicio", "Inicio de Maratón Marvel con el avance y el siguiente título", "Inicio"), ("app-marvel-cronologia", "Cronología de las películas de X-Men en el orden de la historia", "Cronología"), ("app-marvel-ficha", "Ficha de una película", "Ficha")])}
<p class="cap">Capturadas en el simulador de iPhone. Las imágenes de las películas pertenecen a sus estudios.</p>
<div class="actions"><a href="https://ssebv.github.io/maraton-marvel/" target="_blank" rel="noopener">Abrir la app web →</a><a href="https://github.com/Ssebv/maraton-marvel" target="_blank" rel="noopener">Código fuente</a></div>
""",
        ),
    },
    "how-i-build": {
        "en": dict(
            title="How I build software with coding agents",
            summary="Coding agents are my main workflow. This is the process that keeps that safe in production, with real examples.",
            body=f"""
<p class="lead">Coding agents are my main workflow: over 2,600 AI-assisted commits on a production ERP alone. The agent writes a lot of the code. I own the decisions, and this process is what makes that safe.</p>

<h2 id="process">The process</h2>
<ol class="steps">
<li><h3>Start from the project's rules</h3><p>Every repo has a short file that says how to install it, how to test it and what not to touch. The agent reads it first, then checks the branch and any uncommitted work. <a href="https://github.com/Ssebv/odoo-rag/blob/main/CLAUDE.md" target="_blank" rel="noopener">Here is a real one.</a></p></li>
<li><h3>Plan before risky work</h3><p>Anything large, or anything touching payments, production, tax documents or personal data, gets a written plan that I approve before a single file changes.</p></li>
<li><h3>Build in small, verifiable steps</h3><p>Each block of work is small enough to check, and the tests run after each one. On some projects a hook runs type checks and unit tests automatically whenever the agent finishes.</p></li>
<li><h3>Test without touching anything real</h3><p>Tests use no real network, credentials or data. The ERP's critical flows are backed by about 180 test files, plus PostgreSQL invariants that block inconsistent data.</p>
{term("odoo-rag", TEST_RUN, "Replay of real commands.")}
{shot("ci-green", "GitHub Actions showing a successful CI run for odoo-rag", "Continuous integration on the public repo.", 1400, 218)}</li>
<li><h3>Measure what tests can't</h3><p>A passing test does not tell you whether an AI answer is good. For that I build evaluations and compare options on the same questions. In <a href="./odoo-rag.html">Odoo RAG</a>, that is how I learned translation mattered more than hybrid search.</p>
{rag_charts("en")}</li>
<li><h3>Review, and check claims against the code</h3><p>Changes get a code review before they are committed, and a security review if they touch authentication, payments or personal data. It applies to what I write about my work too: a review found that my own article said a monitor ran every six hours, while the code said daily. I corrected the article.</p></li>
<li><h3>Ship in stages</h3><p>Changes go through staging before production, and production deploys avoid business hours. For the ERP migration, I compared the result against a pre-upgrade baseline: invoices, orders and deliveries were identical.</p></li>
<li><h3>Watch it in production</h3><p>A daily health check runs over 40 detectors, with urgent alerts every 30 minutes. <a href="../writing/health-check.html">I wrote about what it found</a>, including the detector of mine that was confidently wrong.</p></li>
</ol>

<h2 id="limits">What the agent can't do alone</h2>
<div class="guards"><ul>
<li>Push to the ERP's production or staging branches.</li>
<li>Send email: it only writes drafts.</li>
<li>Read secret files or force-push: those commands are blocked by rule.</li>
<li>Make the calls that are hard to undo: those stay with me.</li>
</ul></div>
""",
        ),
        "es": dict(
            title="Cómo desarrollo software con agentes de programación",
            summary="Los agentes de programación son mi flujo principal. Este es el proceso que lo hace seguro en producción, con ejemplos reales.",
            body=f"""
<p class="lead">Los agentes de programación son mi flujo principal: más de 2.600 commits asistidos por IA solo en un ERP en producción. El agente escribe mucho código. Las decisiones son mías, y este proceso es lo que lo hace seguro.</p>

<h2 id="proceso">El proceso</h2>
<ol class="steps">
<li><h3>Partir de las reglas del proyecto</h3><p>Cada repo tiene un archivo corto que dice cómo instalarlo, cómo probarlo y qué no tocar. El agente lo lee primero y luego revisa la rama y si hay trabajo sin commit. <a href="https://github.com/Ssebv/odoo-rag/blob/main/CLAUDE.md" target="_blank" rel="noopener">Aquí hay uno real.</a></p></li>
<li><h3>Planificar antes del trabajo riesgoso</h3><p>Todo lo grande, o lo que toque pagos, producción, documentos tributarios o datos personales, parte con un plan escrito que apruebo antes de cambiar un solo archivo.</p></li>
<li><h3>Construir en pasos chicos y verificables</h3><p>Cada bloque de trabajo es lo bastante chico para revisarlo, y las pruebas corren después de cada uno. En algunos proyectos, un hook corre tipos y pruebas unitarias automáticamente cuando el agente termina.</p></li>
<li><h3>Probar sin tocar nada real</h3><p>Las pruebas no usan red, credenciales ni datos reales. Los flujos críticos del ERP tienen unos 180 archivos de prueba, más invariantes en PostgreSQL que bloquean datos inconsistentes.</p>
{term("odoo-rag", TEST_RUN, "Repetición de comandos reales.")}
{shot("ci-green", "GitHub Actions con una ejecución exitosa de integración continua de odoo-rag", "Integración continua en el repo público.", 1400, 218)}</li>
<li><h3>Medir lo que las pruebas no ven</h3><p>Que una prueba pase no dice si una respuesta de IA es buena. Para eso construyo evaluaciones y comparo opciones con las mismas preguntas. En <a href="./odoo-rag.html">Odoo RAG</a>, así descubrí que traducir importaba más que la búsqueda híbrida.</p>
{rag_charts("es")}</li>
<li><h3>Revisar, y contrastar lo que se afirma con el código</h3><p>Los cambios pasan por revisión de código antes del commit, y por revisión de seguridad si tocan autenticación, pagos o datos personales. También vale para lo que escribo sobre mi trabajo: una revisión detectó que un artículo mío decía que un monitoreo corría cada seis horas, y el código decía que una vez al día. Corregí el artículo.</p></li>
<li><h3>Desplegar por etapas</h3><p>Los cambios pasan por staging antes de producción, y los despliegues a producción evitan el horario laboral. En la migración del ERP comparé el resultado contra una línea base previa: facturas, pedidos y despachos quedaron idénticos.</p></li>
<li><h3>Vigilar en producción</h3><p>Un health check diario corre más de 40 detectores, con alertas urgentes cada 30 minutos. <a href="../writing/health-check.html">Escribí sobre lo que encontró</a>, incluido el detector mío que estaba seguro y equivocado.</p></li>
</ol>

<h2 id="limites">Lo que el agente no puede hacer solo</h2>
<div class="guards"><ul>
<li>Subir a las ramas de producción o staging del ERP.</li>
<li>Enviar correos: solo escribe borradores.</li>
<li>Leer archivos con secretos o forzar un push: esos comandos están bloqueados por regla.</li>
<li>Tomar las decisiones difíciles de revertir: esas quedan en mis manos.</li>
</ul></div>
""",
        ),
    },
}


def render(slug, lang):
    page = PAGES[slug][lang]
    t = T[lang]
    root = "../../" if lang == "es" else "../"
    en_url = f"{SITE}/projects/{slug}.html"
    es_url = f"{SITE}/es/projects/{slug}.html"
    url = es_url if lang == "es" else en_url
    en_href = f"../../projects/{slug}.html" if lang == "es" else f"./{slug}.html"
    es_href = f"./{slug}.html" if lang == "es" else f"../es/projects/{slug}.html"
    title = html.escape(page["title"])
    summary = html.escape(page["summary"])
    card = f"og-{slug}{'-es' if lang == 'es' else ''}.png"
    image = f"{SITE}/{card if (ROOT / card).exists() else 'og.png'}"
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": page["title"],
        "description": page["summary"],
        "image": image,
        "url": url,
        "author": {"@type": "Person", "name": "Sebastián Allende Cuello", "url": f"{SITE}/"},
        "inLanguage": lang,
    }, ensure_ascii=False, indent=2).replace("</", "<\\/")
    current = {"en": ' aria-current="true"' if lang == "en" else "", "es": ' aria-current="true"' if lang == "es" else ""}
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
{NOFLASH}

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{title} — Sebastián Allende</title>
<meta name="description" content="{summary}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="en" href="{en_url}">
<link rel="alternate" hreflang="es" href="{es_url}">
<meta property="og:type" content="article">
<meta property="og:locale" content="{'es_CL' if lang == 'es' else 'en_US'}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{summary}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{summary}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{schema}
</script>

<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{root}style.css">
<script src="{root}term.js" defer></script>
</head>
<body>

<nav class="lang-switch" aria-label="{t['langlabel']}">
  <a href="{en_href}" hreflang="en"{current['en']}>EN</a>
  <a href="{es_href}" hreflang="es"{current['es']}>ES</a>
</nav>

{TOGGLE.format(lbl=t['themelabel'])}

<a class="skip" href="#main">{t['skip']}</a>

<div class="wrap">
  <a class="back" href="../">{t['back']}</a>

  <main id="main">
  <article class="page">

    <h1>{title}</h1>
{page['body'].replace('%ROOT%', root)}
  </article>
  </main>

  <footer>
    <span><a href="../">{t['backfoot']}</a></span>
    <span>sallendec@outlook.com</span>
  </footer>
</div>
{SCRIPTS.replace('%SECTIONS%', t['sections'])}
</body>
</html>
"""


def main():
    for slug in PAGES:
        for lang, prefix in (("en", "projects"), ("es", "es/projects")):
            dest = ROOT / prefix / f"{slug}.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(render(slug, lang), encoding="utf-8")
            print(dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
