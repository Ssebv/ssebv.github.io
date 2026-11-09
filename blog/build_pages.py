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


def video(name, poster, label, caption, link):
    return (f'<figure class="shot"><video controls preload="none" playsinline width="1280" height="720" '
            f'poster="%ROOT%img/{poster}.webp" aria-label="{html.escape(label)}"><source src="%ROOT%video/{name}.mp4" type="video/mp4">'
            f'<a href="%ROOT%video/{name}.mp4">{html.escape(link)}</a></video>'
            f'<figcaption>{html.escape(caption)} <a href="%ROOT%video/{name}.mp4">{html.escape(link)}</a></figcaption></figure>')


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


def flow(items):
    cells = "".join(f"<li>{html.escape(i)}</li>" for i in items[:-1])
    return f'<ol class="flow">{cells}<li class="end">{html.escape(items[-1])}</li></ol>'


def arch(label, layers):
    rows = ""
    for name, items in layers:
        chips = "".join(
            f'<li class="key">{html.escape(i[1:])}</li>' if i.startswith("*") else f"<li>{html.escape(i)}</li>"
            for i in items
        )
        rows += f"<li><b>{html.escape(name)}</b><ul>{chips}</ul></li>"
    return f'<ol class="arch" aria-label="{html.escape(label)}">{rows}</ol>'


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
{flow(["Question", "Translate if Spanish", "Vector + keyword search", "Rank fusion", "llama3.2", "Cited answer or NOT_IN_DOCS"])}
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
{flow(["Pregunta", "Traducción si está en español", "Búsqueda vectorial + palabras clave", "Fusión de rankings", "llama3.2", "Respuesta citada o NOT_IN_DOCS"])}
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
<p class="lead">Three mobile products I designed and built, each on a different stack. These are real screens, not design mockups. <a href="./how-i-build.html#arch-norte">Read how Norte</a> and <a href="./how-i-build.html#arch-citofonia">Citofonía</a> are organized.</p>

<h2 id="norte">Norte</h2>
<p>A personal app that brings finances, training, nutrition and habits together. It is native SwiftUI with no third-party dependencies, with Apple Watch and widget targets, a Next.js API over SQLite, and Claude for analysis.</p>
{phones("Norte screens", [("app-norte-finanzas", "Norte finances with net worth and a savings goal", "Finances"), ("app-norte-salud", "Norte health summary with recovery, calories and protein", "Health"), ("app-norte-entreno", "Norte training session with the muscles worked today", "Training")])}
<p class="cap">Captured in the iPhone simulator against a local test server with seeded demo data. None of these figures are real.</p>
<p>More than 280 Swift files, over 80 of them tests. The screen tests refuse to run against production. The source is private.</p>

<h2 id="citofonia">Citofonía</h2>
<p>The building intercom on your phone: concierge calls, door opening, QR visits, parcels, reservations and votes, with a tablet for the concierge and a panel for administrators. It is in development, built with React Native and Expo, Hono, Supabase and LiveKit for calls.</p>
{phones("Citofonía screens", [("app-citofonia-llamada", "Incoming concierge call on the resident's phone", "Concierge call"), ("app-citofonia-reservas", "Common-area reservations with their rules", "Reservations"), ("app-citofonia-qr", "Visits list with a QR pass that expires", "Visits")], 1169)}
<p class="cap">Real captures of the app with a fictional building and fictional residents.</p>
{video("citofonia", "citofonia-video", "Tour of Citofonía", "A 65-second silent tour with on-screen text in Spanish: concierge calls, parcels with a PIN, shared keys, building services and the modules each building chooses. All data is fictional.", "Download the video")}
<p>23 resident screens, 9 for the concierge and 17 admin pages over 105 database migrations. CI runs type checks, pgTAP, Vitest and end-to-end tests. The source is private. <a href="./citofonia.html">Read the full case →</a></p>

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
<p class="lead">Tres productos móviles que diseñé y construí, cada uno con un stack distinto. Son pantallas reales, no maquetas de diseño. <a href="./how-i-build.html#arq-norte">Lee cómo se organizan Norte</a> y <a href="./how-i-build.html#arq-citofonia">Citofonía</a>.</p>

<h2 id="norte">Norte</h2>
<p>Una app personal que reúne finanzas, entrenamiento, alimentación y hábitos. Es nativa en SwiftUI y sin dependencias de terceros, con objetivos para Apple Watch y widgets, una API en Next.js sobre SQLite, y Claude para los análisis.</p>
{phones("Pantallas de Norte", [("app-norte-finanzas", "Finanzas de Norte con patrimonio y una meta de ahorro", "Finanzas"), ("app-norte-salud", "Resumen de salud de Norte con recuperación, calorías y proteína", "Salud"), ("app-norte-entreno", "Sesión de entrenamiento de Norte con los músculos del día", "Entreno")])}
<p class="cap">Capturadas en el simulador de iPhone contra un servidor local de prueba con datos de demostración. Ninguna de estas cifras es real.</p>
<p>Más de 280 archivos Swift, más de 80 de ellos de pruebas. Las pruebas de pantalla se niegan a correr contra producción. El código es privado.</p>

<h2 id="citofonia">Citofonía</h2>
<p>El citófono del edificio en el celular: llamadas de portería, apertura de puertas, visitas con QR, encomiendas, reservas y votaciones, con una tablet para conserjería y un panel para la administración. Está en desarrollo, con React Native y Expo, Hono, Supabase y LiveKit para las llamadas.</p>
{phones("Pantallas de Citofonía", [("app-citofonia-llamada", "Llamada entrante de portería en el celular del residente", "Llamada de portería"), ("app-citofonia-reservas", "Reservas de espacios comunes con sus reglas", "Reservas"), ("app-citofonia-qr", "Lista de visitas con un pase QR que vence", "Visitas")], 1169)}
<p class="cap">Capturas reales de la app con un edificio y residentes ficticios.</p>
{video("citofonia", "citofonia-video", "Recorrido por Citofonía", "Un recorrido de 65 segundos sin sonido: llamadas de portería, encomiendas con PIN, llaves compartidas, servicios del edificio y los módulos que elige cada edificio. Todos los datos son ficticios.", "Descargar el video")}
<p>23 pantallas del residente, 9 de conserjería y 17 páginas de administración, sobre 105 migraciones de base de datos. La integración continua corre tipos, pgTAP, Vitest y pruebas de punta a punta. El código es privado. <a href="./citofonia.html">Leer el caso completo →</a></p>

<h2 id="marvel">Maratón Marvel</h2>
<p>Todo Marvel y X-Men en el orden de la historia, con seguimiento de avance: más de 140 títulos, contando cómics y animación, y 1.600 episodios. La app web está publicada y es gratis. Hay una versión nativa en SwiftUI en desarrollo, y es la que se ve aquí.</p>
{phones("Pantallas de Maratón Marvel", [("app-marvel-inicio", "Inicio de Maratón Marvel con el avance y el siguiente título", "Inicio"), ("app-marvel-cronologia", "Cronología de las películas de X-Men en el orden de la historia", "Cronología"), ("app-marvel-ficha", "Ficha de una película", "Ficha")])}
<p class="cap">Capturadas en el simulador de iPhone. Las imágenes de las películas pertenecen a sus estudios.</p>
<div class="actions"><a href="https://ssebv.github.io/maraton-marvel/" target="_blank" rel="noopener">Abrir la app web →</a><a href="https://github.com/Ssebv/maraton-marvel" target="_blank" rel="noopener">Código fuente</a></div>
""",
        ),
    },
    "citofonia": {
        "en": dict(
            title="Citofonía: the building intercom on your phone",
            summary="A digital intercom for apartment buildings: concierge calls, door opening, parcels and visits, with the call handled on the server and privacy built into the data.",
            body=f"""
<p class="lead">Concierge calls, door opening, QR visits, parcels, reservations and votes. One app serves residents and the concierge's tablet, and a web panel serves the administration. It is in development, shown here with a fictional building.</p>
<div class="actions"><a href="./how-i-build.html#arch-citofonia">Architecture</a><a href="./apps.html">Other iPhone apps</a></div>
{video("citofonia", "citofonia-video", "Tour of Citofonía", "A 65-second silent tour with on-screen text in Spanish. All data is fictional.", "Download the video")}

<h2 id="roles">One product, three seats</h2>
<p>A resident, a concierge and an administrator need very different screens, but they work on the same data. The resident and concierge modes share one React Native app, and each building turns on only the modules it wants.</p>
{phones("Resident screens", [("app-citofonia-llamada", "Incoming concierge call on the resident's phone", "Concierge call"), ("app-citofonia-reservas", "Common-area reservations with their rules", "Reservations"), ("app-citofonia-qr", "Visits list with a QR pass that expires", "Visits")], 1169)}
{shot("citofonia-tablet", "Concierge tablet screen for calling an apartment", "The concierge's tablet. A call rings on the apartment's phones for 30 seconds, and the first person to answer takes it.", 1400, 973)}
<div class="gallery">
{shot("citofonia-panel", "Administration panel with the day's parcels, visits, missed calls and pending tasks", "The administration panel.")}
{shot("citofonia-modulos", "Building modules that can be turned on or off", "Modules per building.", 1400, 428)}
</div>

<h2 id="call">How a call works</h2>
{flow(["Concierge calls", "Rings for 30 s", "First answer takes it", "Door can open for a short time"])}
<p>The call is the hard part of this product. It has to behave correctly when several phones ring at once, when someone answers on two devices, and when a database write fails halfway.</p>
<ul>
<li><strong>A pure state machine.</strong> The call logic has no network or storage, and it takes the clock as an argument. A Durable Object runs it on the server, and an in-memory version runs the same logic in tests.</li>
<li><strong>Limits that respect emergencies.</strong> A concierge station has one active call, and each apartment has a limit on attempts per minute. An emergency call has its own higher limit, so it is not lost to that cap.</li>
<li><strong>One owner for the audio.</strong> A call to the concierge rings on every concierge device, but the audio and the hang-up button belong to the one that answered.</li>
<li><strong>Failures that clean up.</strong> If a database write fails, a job that runs every minute closes the stuck call, so it does not keep blocking new calls to that apartment.</li>
</ul>

<h2 id="privacy">Privacy in the data, not only in the text</h2>
<ul>
<li><strong>Notifications carry no names.</strong> A parcel or visit alert says how many arrived, without a name, apartment or detail.</li>
<li><strong>The audit log removes personal data.</strong> Personal data such as names, ID numbers, license plates and QR codes is removed from visit and parcel changes before they reach the audit log.</li>
<li><strong>Data has an expiry date.</strong> A daily job applies the retention period set for each type of data.</li>
<li><strong>Reports are tested for leaks.</strong> The monthly report has aggregate figures only, and a database test checks that no names or apartment numbers come out.</li>
</ul>
<p>The privacy and terms text follows Chile's Law 21.719, but it is still a draft that a lawyer needs to review.</p>

<h2 id="tests">Tests</h2>
<p>105 database migrations, 88 pgTAP test files for access rules and data, and more than 30 Vitest files for the API and panel. CI also runs end-to-end tests against a local database. The source is private, and I am happy to walk through it in an interview.</p>
""",
        ),
        "es": dict(
            title="Citofonía: el citófono del edificio en el celular",
            summary="Un citófono digital para edificios: llamadas de portería, apertura de puertas, encomiendas y visitas, con la llamada manejada en el servidor y la privacidad incorporada en los datos.",
            body=f"""
<p class="lead">Llamadas de portería, apertura de puertas, visitas con QR, encomiendas, reservas y votaciones. Una app sirve a residentes y a la tablet de conserjería, y un panel web a la administración. Está en desarrollo, y aquí se muestra con un edificio ficticio.</p>
<div class="actions"><a href="./how-i-build.html#arq-citofonia">Arquitectura</a><a href="./apps.html">Otras apps de iPhone</a></div>
{video("citofonia", "citofonia-video", "Recorrido por Citofonía", "Un recorrido de 65 segundos sin sonido. Todos los datos son ficticios.", "Descargar el video")}

<h2 id="roles">Un producto, tres puestos</h2>
<p>Residente, conserje y administración necesitan pantallas muy distintas, pero trabajan sobre los mismos datos. Los modos de residente y conserjería comparten una app en React Native, y cada edificio enciende solo los módulos que quiere.</p>
{phones("Pantallas del residente", [("app-citofonia-llamada", "Llamada entrante de portería en el celular del residente", "Llamada de portería"), ("app-citofonia-reservas", "Reservas de espacios comunes con sus reglas", "Reservas"), ("app-citofonia-qr", "Lista de visitas con un pase QR que vence", "Visitas")], 1169)}
{shot("citofonia-tablet", "Pantalla de la tablet de conserjería para llamar a un departamento", "La tablet de conserjería. La llamada suena 30 segundos en los teléfonos del depto, y la toma el primero que contesta.", 1400, 973)}
<div class="gallery">
{shot("citofonia-panel", "Panel de administración con las encomiendas, visitas, llamadas perdidas y tareas pendientes del día", "El panel de administración.")}
{shot("citofonia-modulos", "Módulos del edificio que se pueden encender o apagar", "Módulos por edificio.", 1400, 428)}
</div>

<h2 id="llamada">Cómo funciona una llamada</h2>
{flow(["Conserjería llama", "Suena 30 s", "Contesta el primero", "Se puede abrir por poco tiempo"])}
<p>La llamada es la parte difícil de este producto. Tiene que comportarse bien cuando suenan varios teléfonos a la vez, cuando alguien contesta en dos dispositivos y cuando una escritura en la base falla a medias.</p>
<ul>
<li><strong>Una máquina de estados pura.</strong> La lógica de la llamada no tiene red ni almacenamiento, y recibe el reloj como argumento. En el servidor la corre un Durable Object, y en las pruebas una versión en memoria corre la misma lógica.</li>
<li><strong>Límites que respetan las emergencias.</strong> Cada puesto de conserjería tiene una llamada activa, y cada depto tiene un límite de intentos por minuto. Una llamada de emergencia tiene su propio límite, más alto, para que ese tope no la deje fuera.</li>
<li><strong>Un solo dueño del audio.</strong> Una llamada a portería suena en todos los equipos de conserjería, pero el audio y el botón de colgar son del que contestó.</li>
<li><strong>Las fallas se limpian solas.</strong> Si falla una escritura en la base, una tarea que corre cada minuto cierra la llamada colgada, para que no siga bloqueando llamadas nuevas a ese depto.</li>
</ul>

<h2 id="privacidad">Privacidad en los datos, no solo en el texto</h2>
<ul>
<li><strong>Los avisos no llevan nombres.</strong> Un aviso de encomienda o visita dice cuántas llegaron, sin nombre, depto ni detalle.</li>
<li><strong>La auditoría quita los datos personales.</strong> Los datos personales, como nombre, RUT, patente y QR, se quitan de los cambios en visitas y encomiendas antes de que lleguen a la auditoría.</li>
<li><strong>Los datos tienen fecha de vencimiento.</strong> Una tarea diaria aplica el plazo de retención de cada tipo de dato.</li>
<li><strong>Se prueba que los reportes no filtren datos.</strong> El reporte del mes solo trae cifras agregadas, y una prueba de base de datos revisa que no salgan nombres ni números de depto.</li>
</ul>
<p>El texto de privacidad y términos sigue la Ley 21.719, pero todavía es un borrador que debe revisar un abogado.</p>

<h2 id="pruebas">Pruebas</h2>
<p>105 migraciones de base de datos, 88 archivos de pruebas pgTAP para reglas de acceso y datos, y más de 30 archivos de Vitest para la API y el panel. La integración continua también corre pruebas de punta a punta contra una base local. El código es privado, y con gusto lo recorro en una entrevista.</p>
""",
        ),
    },
    "flagforge": {
        "en": dict(
            title="FlagForge: feature flags in Rust, with one engine everywhere",
            summary="A multi-tenant feature-flag service built from scratch in Rust, with the same evaluation engine on the server, in the SDK and in the dashboard.",
            body=f"""
<p class="lead">A multi-tenant feature-flag service I built from scratch in Rust: targeted rollouts, A/B experiments, an audit trail and a dashboard compiled to WebAssembly. It answers one question, whether this user should get this feature, and it has to answer the same way on every server.</p>
<div class="actions"><a href="https://github.com/Ssebv/flagforge" target="_blank" rel="noopener">Source code on GitHub →</a><a href="./how-i-build.html#arch-flagforge">Architecture</a></div>
{shot("flagforge-editor", "FlagForge flag editor with a targeting rule, a rollout slider and a live preview", "The flag editor. Its validation and preview call the same engine the server runs, compiled to WebAssembly.")}

<h2 id="what">What it does</h2>
<ul>
<li><strong>Targeting rules</strong> with seventeen operators, including regex, semver and set membership.</li>
<li><strong>Reusable segments,</strong> so widening an audience is one edit instead of twelve.</li>
<li><strong>Percentage rollouts</strong> that are deterministic and sticky, with no shared state between servers.</li>
<li><strong>A/B experiments</strong> that end in a verdict: rates, 95% confidence intervals and a significance test against the control.</li>
<li><strong>An audit trail</strong> with a before and after for every change.</li>
</ul>
<div class="gallery">
{shot("flagforge-experiments", "Experiment results with a conversion rate and confidence interval per arm", "Experiment results.")}
{shot("flagforge-audit", "Audit log with a before and after diff", "Audit log.")}
</div>

<h2 id="decisions">Decisions worth explaining</h2>
<ul>
<li><strong>Evaluation never touches the database.</strong> A service may check flags on every request, so each node keeps an immutable snapshot in memory, with lock-free reads.</li>
<li><strong>PostgreSQL tells the nodes when to reload.</strong> Triggers send a notification on every write, with no message broker. Because this lives in the database, a change made by anything, even a migration, refreshes every node.</li>
<li><strong>An invalid flag can never reach the database.</strong> The API and the dashboard run the same validation, so an error appears as you type, with the same message the API would return.</li>
<li><strong>Two operators cannot silently overwrite each other.</strong> A write carries the version it expects, PostgreSQL resolves the race in one statement, and the loser gets a 409 that says what happened.</li>
</ul>

<h2 id="reversed">A decision I had to reverse</h2>
<p>The snapshot originally withheld the bucketing salt, and a test asserted it never appeared. That felt prudent and was wrong. Without the salt, an SDK matches rules correctly but assigns rollouts differently from the server, so every answer looks plausible and roughly a quarter of them are wrong, with nothing to indicate it.</p>
<p>The salt now goes to server-scoped keys, and only to them. Client-scoped keys still get decisions only, and tests pin that boundary.</p>

<h2 id="numbers">Speed and tests</h2>
<table><caption>Time per evaluation, from the repo's benchmark on an M-series laptop</caption>
<thead><tr><th scope="col">Flag shape</th><th scope="col">Time</th></tr></thead>
<tbody><tr><td>On, no rules</td><td>40 ns</td></tr><tr><td>Percentage rollout</td><td>114 ns</td></tr><tr><td>5 rules, the last one matches</td><td>298 ns</td></tr><tr><td>20 rules, none match (worst case)</td><td>985 ns</td></tr></tbody></table>
<p>It is a plain benchmark, enough to back the claim and notice a regression, not a statistical study.</p>
<p>There are 245 tests in four layers: 86 for the domain, including property tests with proptest, 79 for HTTP, 65 for integration, each with its own migrated database, and 15 for the SDK. One of them starts a real server and compares 300 users evaluated locally and remotely.</p>
""",
        ),
        "es": dict(
            title="FlagForge: feature flags en Rust, con un solo motor en todas partes",
            summary="Un servicio multi-tenant de feature flags construido desde cero en Rust, con el mismo motor de evaluación en el servidor, el SDK y el panel.",
            body=f"""
<p class="lead">Un servicio multi-tenant de feature flags que construí desde cero en Rust: despliegues segmentados, experimentos A/B, registro de auditoría y un panel compilado a WebAssembly. Responde una pregunta, si este usuario debe recibir esta función, y tiene que responder igual en todos los servidores.</p>
<div class="actions"><a href="https://github.com/Ssebv/flagforge" target="_blank" rel="noopener">Código en GitHub →</a><a href="./how-i-build.html#arq-flagforge">Arquitectura</a></div>
{shot("flagforge-editor", "Editor de flags de FlagForge con una regla de segmentación, un control de despliegue y una vista previa", "El editor de flags. Su validación y su vista previa llaman al mismo motor que corre el servidor, compilado a WebAssembly.")}

<h2 id="que-hace">Qué hace</h2>
<ul>
<li><strong>Reglas de segmentación</strong> con diecisiete operadores, incluidos regex, semver y pertenencia a conjuntos.</li>
<li><strong>Segmentos reutilizables,</strong> para que ampliar una audiencia sea un cambio y no doce.</li>
<li><strong>Despliegues por porcentaje</strong> deterministas y estables, sin estado compartido entre servidores.</li>
<li><strong>Experimentos A/B</strong> que terminan en un veredicto: tasas, intervalos de confianza del 95 % y una prueba de significancia contra el control.</li>
<li><strong>Registro de auditoría</strong> con el antes y el después de cada cambio.</li>
</ul>
<div class="gallery">
{shot("flagforge-experiments", "Resultados de un experimento con la tasa de conversión e intervalo de confianza por variante", "Resultados de un experimento.")}
{shot("flagforge-audit", "Registro de auditoría con el antes y el después de un cambio", "Registro de auditoría.")}
</div>

<h2 id="decisiones">Decisiones que vale la pena explicar</h2>
<ul>
<li><strong>La evaluación nunca toca la base de datos.</strong> Un servicio puede consultar flags en cada solicitud, así que cada nodo mantiene una copia inmutable en memoria, con lecturas sin bloqueos.</li>
<li><strong>PostgreSQL avisa a los nodos cuándo recargar.</strong> Los triggers envían una notificación en cada escritura, sin un broker de mensajes. Como esto vive en la base, un cambio hecho por cualquier vía, incluso una migración, actualiza todos los nodos.</li>
<li><strong>Un flag inválido nunca llega a la base de datos.</strong> La API y el panel corren la misma validación, así que el error aparece mientras se escribe, con el mismo mensaje que devolvería la API.</li>
<li><strong>Dos operadores no pueden sobrescribirse sin saberlo.</strong> Cada escritura lleva la versión que espera, PostgreSQL resuelve la carrera en una sola sentencia, y quien pierde recibe un 409 que explica lo ocurrido.</li>
</ul>

<h2 id="revertida">Una decisión que tuve que revertir</h2>
<p>Al principio, la copia que recibe el SDK ocultaba el salt de asignación, y una prueba exigía que nunca apareciera. Parecía prudente y estaba mal. Sin el salt, el SDK evalúa bien las reglas, pero asigna los despliegues distinto que el servidor: todas las respuestas parecen razonables y cerca de una cuarta parte son incorrectas, sin nada que lo indique.</p>
<p>Ahora el salt llega a las claves de servidor, y solo a ellas. Las claves de cliente siguen recibiendo solo decisiones, y hay pruebas que fijan ese límite.</p>

<h2 id="cifras">Velocidad y pruebas</h2>
<table><caption>Tiempo por evaluación, según el benchmark del repo en un notebook con chip serie M</caption>
<thead><tr><th scope="col">Tipo de flag</th><th scope="col">Tiempo</th></tr></thead>
<tbody><tr><td>Activo, sin reglas</td><td>40 ns</td></tr><tr><td>Despliegue por porcentaje</td><td>114 ns</td></tr><tr><td>5 reglas, coincide la última</td><td>298 ns</td></tr><tr><td>20 reglas, ninguna coincide (peor caso)</td><td>985 ns</td></tr></tbody></table>
<p>Es un benchmark simple, suficiente para respaldar la cifra y notar una regresión, no un estudio estadístico.</p>
<p>Hay 245 pruebas en cuatro capas: 86 del dominio, incluidas pruebas de propiedades con proptest, 79 de HTTP, 65 de integración, cada una con su propia base migrada, y 15 del SDK. Una de ellas levanta un servidor real y compara 300 usuarios evaluados en local y en remoto.</p>
""",
        ),
    },
    "construye-hoy": {
        "en": dict(
            title="Construye Hoy: daily site control for construction firms",
            summary="A field app, a web panel and AI that reads invoices and quantity take-offs for construction firms with several sites: the model proposes, a person confirms, and the database decides who sees what.",
            body=f"""
<p class="lead">Daily reports, GPS attendance, warehouse, schedule, cost control and a client portal, for small and mid-sized construction firms running several sites at once. One app serves the site manager, the warehouse, workers, subcontractors and the client, and a web panel serves owners and accounting. I build it as an independent contractor for a construction firm, where it is in a pilot. Everything shown here uses fictional data.</p>
{phones("Client portal screens", [("app-construye-avance", "Client portal home with progress, the delivery date and a decision the client still owes", "Progress"), ("app-construye-adicional", "A change order with its price, VAT and an approve button", "Change order"), ("app-construye-mensajes", "Messages between the client and the site manager, linked to the change order", "Messages")], 1169)}
<p class="cap">The client portal, with a fictional firm and house.</p>

<h2 id="stack">How it is put together</h2>
{arch("Construye Hoy architecture", [("Apps", ["*Expo app with five roles, offline first", "Web panel for owners and accounting"]), ("Server", ["Hono API on Cloudflare Workers", "AI reading, invitations, 2FA, QR access", "Scheduled jobs"]), ("Data", ["*PostgreSQL with row-level security", "Files and encrypted fields"])])}
<p>The apps read and write the database directly with the user's own session, so row-level security decides what each person sees. The API only does what a user cannot do alone, and it uses elevated access only for those cases. Domain logic that every app needs lives in one shared package.</p>

<h2 id="ai">AI that proposes and waits for a person</h2>
{flow(["Photo or PDF", "Model fills a schema", "Totals are checked", "A person confirms"])}
<ul>
<li><strong>Structured output, then arithmetic.</strong> Invoices and quantity take-offs come back as schema-validated data with a readability flag and a confidence per item. The invoice totals are then checked arithmetically, before anyone is asked to confirm.</li>
<li><strong>Documents are data, not instructions.</strong> The document goes to the model separately from the instruction, so text inside a PDF cannot act as an order.</li>
<li><strong>The cheaper model first.</strong> A fast model reads first, and a stronger one retries only when the result is unreadable. A truncated answer is not retried.</li>
<li><strong>Cost on every call, content on none.</strong> Every call, failed ones included, is logged with its model, tokens and computed cost, but not the document. Each company has a monthly quota, and an unknown model is charged at the highest rate.</li>
<li><strong>The provider is swappable.</strong> The model sits behind an interface, and without a key the app keeps working by hand.</li>
</ul>
<p>The AI reading is built and tested, but it has not yet run against the live API, so there are no real cost figures yet.</p>

<h2 id="security">The database is the security boundary</h2>
<ul>
<li><strong>Row-level security on every table.</strong> Owner and accounting roles only work after two-factor authentication.</li>
<li><strong>Money where few can see it.</strong> Amounts are stored as integers, and only in tables that site staff and clients cannot read. Supplier tax IDs are encrypted.</li>
</ul>

<h2 id="tests">Tests</h2>
<p>59 Vitest files with about 580 cases for the API, panel, app and shared logic, 42 pgTAP files for the database rules, and two end-to-end scripts that drive the app and the panel in Chrome, one of them with the network cut on purpose. Model answers are recorded, so no test calls the API: one feeds the real SDK a recorded response and checks the request and the computed cost. The CI workflow type-checks, starts a local database and runs all of them. The source is private, and I am happy to walk through it in an interview.</p>
""",
        ),
        "es": dict(
            title="Construye Hoy: control diario de obras para constructoras",
            summary="Una app de terreno, un panel web e IA que lee facturas y cubicaciones para constructoras con varias obras: el modelo propone, una persona confirma y la base de datos decide quién ve qué.",
            body=f"""
<p class="lead">Partes diarios, asistencia con GPS, bodega, programa, control de costos y un portal para el cliente, para constructoras pequeñas y medianas con varias obras a la vez. Una app sirve al jefe de obra, a bodega, a trabajadores, a subcontratos y al cliente, y un panel web a los dueños y a contabilidad. La desarrollo como independiente para una constructora, donde está en piloto. Todo lo que se ve aquí usa datos ficticios.</p>
{phones("Pantallas del portal del cliente", [("app-construye-avance", "Inicio del portal del cliente con el avance, la fecha de entrega y una decisión pendiente", "Avance"), ("app-construye-adicional", "Un adicional con su precio, IVA y un botón para aprobarlo", "Adicional"), ("app-construye-mensajes", "Mensajes entre el cliente y el jefe de obra, ligados al adicional", "Mensajes")], 1169)}
<p class="cap">El portal del cliente, con una constructora y una casa ficticias.</p>

<h2 id="stack">Cómo está armada</h2>
{arch("Arquitectura de Construye Hoy", [("Apps", ["*App Expo con cinco roles, primero sin conexión", "Panel web para dueños y contabilidad"]), ("Servidor", ["API Hono en Cloudflare Workers", "Lectura con IA, invitaciones, 2FA, acceso con QR", "Tareas programadas"]), ("Datos", ["*PostgreSQL con seguridad por fila", "Archivos y campos cifrados"])])}
<p>Las apps leen y escriben en la base directamente con la sesión de cada usuario, así que la seguridad por fila decide qué ve cada persona. La API solo hace lo que un usuario no puede hacer solo, y usa acceso elevado únicamente en esos casos. La lógica del negocio que necesitan todas las apps vive en un paquete compartido.</p>

<h2 id="ia">IA que propone y espera a una persona</h2>
{flow(["Foto o PDF", "El modelo llena un esquema", "Se revisan los totales", "Una persona confirma"])}
<ul>
<li><strong>Salida estructurada, y después aritmética.</strong> Las facturas y cubicaciones vuelven como datos validados con un esquema, con una marca de legibilidad y una confianza por ítem. Después se revisan los totales de la factura con aritmética, antes de pedirle a alguien que confirme.</li>
<li><strong>Los documentos son datos, no instrucciones.</strong> El documento va al modelo separado de la instrucción, así que el texto dentro de un PDF no puede actuar como una orden.</li>
<li><strong>Primero el modelo barato.</strong> Lee primero un modelo rápido, y uno más fuerte reintenta solo si el resultado no es legible. Una respuesta cortada no se reintenta.</li>
<li><strong>Costo en cada llamada, contenido en ninguna.</strong> Cada llamada, incluidas las fallidas, queda registrada con su modelo, tokens y costo calculado, pero sin el documento. Cada empresa tiene una cuota mensual, y un modelo desconocido se cobra a la tarifa más alta.</li>
<li><strong>El proveedor es intercambiable.</strong> El modelo está detrás de una interfaz, y sin clave la app sigue funcionando a mano.</li>
</ul>
<p>La lectura con IA está construida y probada, pero todavía no ha corrido contra la API real, así que aún no hay cifras de costo reales.</p>

<h2 id="seguridad">La base de datos es la frontera de seguridad</h2>
<ul>
<li><strong>Seguridad por fila en cada tabla.</strong> Los roles de dueño y contabilidad solo funcionan después de la autenticación en dos pasos.</li>
<li><strong>La plata donde pocos la ven.</strong> Los montos se guardan como enteros y solo en tablas que el personal de obra y los clientes no pueden leer. El RUT de los proveedores va cifrado.</li>
</ul>

<h2 id="pruebas">Pruebas</h2>
<p>59 archivos de Vitest con unos 580 casos para la API, el panel, la app y la lógica compartida, 42 archivos de pgTAP para las reglas de la base, y dos scripts de punta a punta que manejan la app y el panel en Chrome, uno de ellos con la red cortada a propósito. Las respuestas del modelo están grabadas, así que ninguna prueba llama a la API: una le entrega al SDK real una respuesta grabada y revisa la solicitud y el costo calculado. El flujo de integración continua revisa tipos, levanta una base local y corre todas. El código es privado, y con gusto lo recorro en una entrevista.</p>
""",
        ),
    },
    "sac-next": {
        "en": dict(
            title="SAC Next: a community alarm platform",
            summary="A neighbourhood alarm system for a municipal security programme: remotes, an app, calls and texts raise an alert, nearby street sirens sound, and an operations room follows it live. Consulting work, in development.",
            body=f"""
<p class="lead">Residents raise an alert for security, fire or a medical emergency from a mobile app, a radio remote, a phone call or a text message. The alert sounds the sirens on nearby street panels and appears live in the console of the operations room. I built it as consulting work for a municipal programme. It is in development: it has run against simulated panels only, and it is not deployed.</p>
{arch("SAC Next architecture", [("Devices", ["Street panels with sirens", "Radio remotes", "Phone calls and text messages"]), ("Server", ["*MQTT broker", "*Fastify API", "PostgreSQL with PostGIS"]), ("People", ["Live console for the operations room", "Mobile app", "Push and text alerts"])])}

<h2 id="alarm">From a button to a siren</h2>
{flow(["Remote, app, call or text", "Checked and recorded", "Nearby sirens sound", "Seen live"])}
<ul>
<li><strong>Every message is checked.</strong> Panels talk to the server over MQTT, and every message is validated against a schema before it reaches the database. Repeated presses of the same remote become one incident.</li>
<li><strong>The nearest panels, by distance.</strong> A PostGIS query picks the panels near the alert, and they receive the siren command.</li>
<li><strong>Commands are signed and expire.</strong> Each command carries a signature, a one-time value and an expiry, so a replayed or forged command is refused. Remotes use a rolling code.</li>
<li><strong>Silence is reported, not hidden.</strong> A command that no panel confirms is marked expired, logged on the incident and opened as a maintenance ticket, so the operator knows which siren did not sound.</li>
</ul>

<h2 id="assistant">An assistant that knows its limits</h2>
<ul>
<li><strong>Emergencies come first.</strong> Emergency detection runs before anything else, and an emergency gets a fixed answer with call buttons. It never reaches the language model.</li>
<li><strong>Known questions, known answers.</strong> Common questions are answered from a fixed list of topics. Only the rest go to the model, which is told to answer from the programme's knowledge base only.</li>
<li><strong>Personal data stays home.</strong> Emails, national ID numbers and phone numbers are removed before any text leaves the server, and if the model fails the assistant falls back to its own answers.</li>
</ul>

<h2 id="data">One deployment per client, personal data protected</h2>
<ul>
<li><strong>Each client gets its own stack.</strong> Database, broker, API and console run as one Docker Compose project on an internal network, and only the proxy is exposed. The broker refuses anonymous connections, and each panel can read only its own commands.</li>
<li><strong>Personal fields are encrypted.</strong> A keyed index still allows exact lookups without keeping the value in clear.</li>
<li><strong>The audit log is chained.</strong> Each entry is hashed with the one before it, so an edited or deleted entry can be detected.</li>
<li><strong>Backups are encrypted as they are written,</strong> so a plain dump never touches the disk, and a script tests restoring one.</li>
<li><strong>The code does not know its client.</strong> A test fails if any source file names the client or contains its coordinates, so the same code can serve another municipality.</li>
</ul>

<h2 id="tests">Tests</h2>
<p>14 Vitest files with 136 unit tests, and three scripted suites: one end to end through the API, MQTT and simulated panels, and two that drive the mobile web app and the console in Chrome. The end-to-end suite imports 1,100 households and 1,100 remotes and checks that importing twice creates no duplicates. Shell scripts test restoring a backup and upgrading with a rollback. There is no CI or load test yet, and nothing has run on real hardware or with users. The source belongs to the engagement and is private, and I am happy to walk through it in an interview.</p>
""",
        ),
        "es": dict(
            title="SAC Next: una plataforma de alarma comunitaria",
            summary="Un sistema de alarma vecinal para un programa municipal de seguridad: controles, una app, llamadas y SMS levantan una alerta, suenan las sirenas cercanas y una central la sigue en vivo. Trabajo de consultoría, en desarrollo.",
            body=f"""
<p class="lead">Los vecinos levantan una alerta de seguridad, incendio o emergencia médica desde una app, un control remoto por radio, una llamada o un SMS. La alerta hace sonar las sirenas de las centrales cercanas y aparece en vivo en la consola de la central de operaciones. La construí como consultoría para un programa municipal. Está en desarrollo: solo ha corrido contra centrales simuladas y no está desplegada.</p>
{arch("Arquitectura de SAC Next", [("Equipos", ["Centrales con sirena en la calle", "Controles remotos por radio", "Llamadas y SMS"]), ("Servidor", ["*Broker MQTT", "*API en Fastify", "PostgreSQL con PostGIS"]), ("Personas", ["Consola en vivo de la central", "App móvil", "Avisos push y por SMS"])])}

<h2 id="alarma">De un botón a una sirena</h2>
{flow(["Control, app, llamada o SMS", "Se revisa y se registra", "Suenan las sirenas cercanas", "Se ve en vivo"])}
<ul>
<li><strong>Cada mensaje se revisa.</strong> Las centrales hablan con el servidor por MQTT, y cada mensaje se valida contra un esquema antes de llegar a la base. Varias pulsaciones del mismo control quedan como un solo incidente.</li>
<li><strong>Las centrales más cercanas, por distancia.</strong> Una consulta en PostGIS elige las centrales cerca de la alerta, y ellas reciben la orden de sirena.</li>
<li><strong>Las órdenes van firmadas y vencen.</strong> Cada orden lleva una firma, un valor de un solo uso y un vencimiento, así que una orden repetida o falsificada se rechaza. Los controles usan código rotativo.</li>
<li><strong>El silencio se informa, no se esconde.</strong> Una orden que ninguna central confirma queda vencida, se anota en el incidente y abre un ticket de mantención, para que el operador sepa qué sirena no sonó.</li>
</ul>

<h2 id="asistente">Un asistente que conoce sus límites</h2>
<ul>
<li><strong>Las emergencias van primero.</strong> La detección de emergencias corre antes que todo, y una emergencia recibe una respuesta fija con botones para llamar. Nunca llega al modelo de lenguaje.</li>
<li><strong>Preguntas conocidas, respuestas conocidas.</strong> Las preguntas comunes se responden desde una lista fija de temas. Solo el resto va al modelo, que tiene la instrucción de responder únicamente con la base de conocimiento del programa.</li>
<li><strong>Los datos personales no salen.</strong> Correos, RUN y teléfonos se quitan antes de que el texto salga del servidor, y si el modelo falla el asistente vuelve a sus propias respuestas.</li>
</ul>

<h2 id="datos">Un despliegue por cliente y datos personales protegidos</h2>
<ul>
<li><strong>Cada cliente tiene su propio stack.</strong> Base, broker, API y consola corren como un proyecto de Docker Compose en una red interna, y solo el proxy queda expuesto. El broker rechaza conexiones anónimas, y cada central solo puede leer sus propias órdenes.</li>
<li><strong>Los campos personales van cifrados.</strong> Un índice con clave permite buscar por valor exacto sin guardarlo en claro.</li>
<li><strong>La auditoría va encadenada.</strong> Cada registro lleva el hash del anterior, así que se puede detectar uno editado o borrado.</li>
<li><strong>Los respaldos se cifran mientras se escriben,</strong> así que un volcado en claro nunca toca el disco, y un script prueba restaurar uno.</li>
<li><strong>El código no conoce a su cliente.</strong> Una prueba falla si algún archivo nombra al cliente o trae sus coordenadas, así que el mismo código puede servir a otra municipalidad.</li>
</ul>

<h2 id="pruebas">Pruebas</h2>
<p>14 archivos de Vitest con 136 pruebas unitarias, y tres suites con script: una de punta a punta por la API, MQTT y centrales simuladas, y dos que manejan la app web y la consola en Chrome. La suite de punta a punta importa 1.100 hogares y 1.100 controles y revisa que importar dos veces no cree duplicados. Unos scripts de shell prueban restaurar un respaldo y actualizar con vuelta atrás. Todavía no hay integración continua ni prueba de carga, y nada ha corrido en hardware real ni con usuarios. El código es del proyecto de consultoría y es privado, y con gusto lo recorro en una entrevista.</p>
""",
        ),
    },
    "how-i-build": {
        "en": dict(
            title="How I organize development: process and architecture",
            summary="How I take a change from plan to production, and the architecture of five real systems, with the reasons behind each decision.",
            body=f"""
<p class="lead">I organize software around three ideas: clear boundaries between parts, releases that can be checked, and production that reports its own health. This page shows the process, then the architecture of five real systems and why each one is built that way.</p>
<div class="actions"><a href="#process">The process</a><a href="#architecture">The architecture</a><a href="#rules">The rules</a></div>

<h2 id="process">From plan to production</h2>
{flow(["Plan", "Short branch", "Tests in layers", "Review", "Staging", "Production", "Monitoring"])}
<ol class="steps">
<li><h3>Write down how the project works</h3><p>Projects have a short document: how to install it, how to test it and what not to touch. Larger systems also keep one document per module, updated in the same commit as the code, and a record of architecture decisions with their trade-offs. <a href="https://github.com/Ssebv/odoo-rag#run-it" target="_blank" rel="noopener">Install and test steps from a public repo.</a></p></li>
<li><h3>Plan before risky work</h3><p>Anything large, or anything touching payments, production, tax documents or personal data, starts with a written plan before a single file changes.</p></li>
<li><h3>Work in short branches</h3><p>Each change is small enough to check on its own, with tests run after each block. Norte's iPhone app grew this way, in numbered rounds: tests, review, merge, deploy.</p></li>
<li><h3>Test in layers</h3><p>Types catch the cheap mistakes, unit tests the logic, database tests the access rules and end-to-end tests the full flow. Citofonía's CI runs all of them against a local database, and fails if the generated database types are out of date. Automated tests use test data and no real credentials. The ERP's critical flows are backed by about 180 test files, and I rehearsed its migration on a copy of production before the cutover.</p>
{term("odoo-rag", TEST_RUN, "Replay of real commands.")}
{shot("ci-green", "GitHub Actions showing a successful CI run for odoo-rag", "Continuous integration on the public repo.", 1400, 218)}</li>
<li><h3>Measure what tests can't</h3><p>A passing test does not tell you whether an AI answer is good. For that I build evaluations and compare options on the same questions. In <a href="./odoo-rag.html">Odoo RAG</a>, that is how I learned translation mattered more than hybrid search.</p>
{rag_charts("en")}</li>
<li><h3>Review, and check claims against the code</h3><p>Changes get a code review before they are committed, and a security review if they touch authentication, payments or personal data. It applies to what I write about my work too: a review found that my own article said a monitor ran every six hours, while the code said daily. I corrected the article.</p></li>
<li><h3>Ship in stages</h3><p>On the ERP, work moves from a development branch to staging and then to production. Production deploys happen only outside business hours in all three countries, because a build restarts the server. For the migration, I compared the result against a pre-upgrade baseline: invoices, orders and deliveries were identical.</p></li>
<li><h3>Watch it in production</h3><p>A daily health check runs over 40 detectors, with urgent alerts every 30 minutes. <a href="../writing/health-check.html">I wrote about what it found</a>, including the detector of mine that was confidently wrong.</p></li>
</ol>

<h2 id="architecture">Architecture of five systems</h2>
<p>Each system has different constraints, so each one has a different shape. The diagrams read from top to bottom, from the people using the system down to where the data lives. The highlighted part is the one that defines the design.</p>

<h3 id="arch-erp">ERP on Odoo 19</h3>
<p>A production ERP for 4 companies in 3 countries, hosted on Odoo.sh. The source is private.</p>
{arch("ERP layers", [
    ("Channels", ["Back office", "Retail consignment", "Mercado Libre", "Yuju"]),
    ("18 custom modules", ["*Shared core: sales, stock, invoices", "Consignment", "Invoicing by delivery", "Reports"]),
    ("Tax localization", ["Chile · SII", "Colombia · DIAN", "Peru · SUNAT"]),
    ("Platform", ["Odoo 19", "PostgreSQL with invariants", "Health check and alerts"]),
])}
<ul>
<li><strong>Fewer modules, clearer ownership.</strong> I consolidated 41 custom modules into 18, so there is less to upgrade and shared logic has one home.</li>
<li><strong>Critical rules live in the database.</strong> A PostgreSQL trigger enforces the consignment stock invariant, so no code path or script can skip it.</li>
<li><strong>Explicit fields, not naming conventions.</strong> A warehouse reorganization had to update 45 places in 7 modules that relied on location names. The rule now is to identify consignment by a field.</li>
</ul>

<h3 id="arch-citofonia">Citofonía</h3>
<p>A digital building intercom, in development, <a href="./citofonia.html">with its own page</a>. It is a monorepo with pnpm and Turborepo: a mobile app, an admin panel, an API and shared packages for database types and UI. The source is private.</p>
{arch("Citofonía layers", [
    ("Clients", ["Resident app · React Native, Expo", "Concierge tablet", "Admin panel · React, Vite"]),
    ("API on the edge", ["Hono on Cloudflare Workers", "Calls", "Doors", "Push", "Invitations", "Votes"]),
    ("Call state", ["*One Durable Object per unit: the call", "One per station: the call limit"]),
    ("Data and media", ["Supabase PostgreSQL with row-level security", "LiveKit for calls"]),
])}
<ul>
<li><strong>The database enforces access.</strong> For everyday data, the apps talk to PostgreSQL directly, under row-level security tested with pgTAP. The API handles what the database cannot, such as calls, doors, push and invitations.</li>
<li><strong>The call lives on the server, not on a device.</strong> Each apartment has a state machine in a Durable Object, with its own alarms. Tests run the same logic through an in-memory version.</li>
<li><strong>Door hardware sits behind one interface.</strong> A driver has one method, <code>openDoor</code>. Today there are two, for the tablet and for an HTTP relay, and a new door system means a new driver.</li>
<li><strong>Migrations are never edited.</strong> There is one per topic and 105 so far. Types are generated from the schema, and CI checks they are current.</li>
</ul>

<h3 id="arch-norte">Norte</h3>
<p>A personal finance and health app with native and web clients. The source is private.</p>
{arch("Norte layers", [
    ("Clients", ["iPhone, Apple Watch and widgets · SwiftUI", "Web · Next.js, React"]),
    ("API", ["*One REST JSON API for every client", "Session check on each request"]),
    ("Domain", ["Finance", "Training", "Nutrition", "Habits"]),
    ("Data and services", ["SQLite", "Bank email reader · IMAP", "Anthropic API, validated output"]),
    ("Hosting", ["VPS", "Caddy", "systemd"]),
])}
<ul>
<li><strong>One API for every client.</strong> The iPhone and the web use the same endpoints, so a business rule is written once.</li>
<li><strong>No third-party dependencies on iOS.</strong> The app uses only what the platform provides, so there is nothing to update or audit from outside.</li>
<li><strong>A single-file database.</strong> A single-user app does not need a database server. SQLite keeps hosting and backups simple.</li>
<li><strong>Screen tests are isolated.</strong> They run against a local server with a temporary database and demo data, and refuse to run against production.</li>
</ul>

<h3 id="arch-flagforge">FlagForge</h3>
<p>Multi-tenant feature flags in Rust. <a href="./flagforge.html">It has its own page</a>, and <a href="https://github.com/Ssebv/flagforge" target="_blank" rel="noopener">the source is public</a>.</p>
{arch("FlagForge layers", [
    ("Clients", ["Service SDK", "Dashboard · Leptos, WebAssembly", "Operators and CI"]),
    ("API · axum", ["Evaluation, from memory", "Management API", "Snapshot cache"]),
    ("Engine", ["*flagforge-core: pure functions, no I/O"]),
    ("Data", ["flagforge-storage: SQL checked at compile time", "PostgreSQL, LISTEN/NOTIFY"]),
])}
<ul>
<li><strong>The part that must be correct has no I/O.</strong> Evaluation is a pure function of the flag, the context and the environment (salt and segments), so it can be tested thoroughly.</li>
<li><strong>One engine, three consumers.</strong> The server, the SDK and the dashboard's rule editor reuse the same crate, so they cannot disagree.</li>
<li><strong>A schema change breaks the build, not production.</strong> <code>sqlx</code> verifies every query against the real schema at compile time.</li>
</ul>

<h3 id="arch-modomax">ModoMax</h3>
<p>An online store. <a href="./modomax.html">Its assistant decisions have their own page.</a> The source is private.</p>
{arch("ModoMax layers", [
    ("Clients", ["Storefront", "Admin panel", "WhatsApp"]),
    ("Application", ["*One Next.js app: pages, server actions, API routes, scheduled jobs"]),
    ("Domain and validation", ["Prisma", "Zod", "Audit log"]),
    ("Data and services", ["PostgreSQL, local access only", "Payments", "Tax documents", "Email", "Anthropic API"]),
    ("Hosting", ["VPS", "Caddy", "systemd"]),
])}
<ul>
<li><strong>One deployable app.</strong> For a store this size, a single application on a VPS is easier to run and debug than separate services.</li>
<li><strong>The database is not exposed.</strong> PostgreSQL accepts local connections only.</li>
<li><strong>Schema changes go through migrations.</strong> Production uses <code>prisma migrate deploy</code>, never <code>db push</code>.</li>
</ul>

<h2 id="rules">Rules I keep</h2>
<div class="guards"><ul>
<li>No deploys to the ERP's production during business hours in any of its three countries.</li>
<li>Secrets stay out of repositories.</li>
<li>A committed migration is never edited.</li>
<li>Automated tests never touch production, and sample data is always fictional.</li>
<li>Changes that are hard to undo get an explicit decision first.</li>
</ul></div>
""",
        ),
        "es": dict(
            title="Cómo organizo el desarrollo: proceso y arquitectura",
            summary="Cómo llevo un cambio del plan a producción, y la arquitectura de cinco sistemas reales, con las razones detrás de cada decisión.",
            body=f"""
<p class="lead">Organizo el software en torno a tres ideas: límites claros entre las partes, entregas que se pueden verificar y una producción que informa su propio estado. Esta página muestra el proceso y luego la arquitectura de cinco sistemas reales, con el porqué de cada uno.</p>
<div class="actions"><a href="#proceso">El proceso</a><a href="#arquitectura">La arquitectura</a><a href="#reglas">Las reglas</a></div>

<h2 id="proceso">Del plan a producción</h2>
{flow(["Plan", "Rama corta", "Pruebas por capas", "Revisión", "Staging", "Producción", "Monitoreo"])}
<ol class="steps">
<li><h3>Dejar escrito cómo funciona el proyecto</h3><p>Los proyectos tienen un documento corto: cómo instalarlo, cómo probarlo y qué no tocar. Los sistemas más grandes también tienen un documento por módulo, que se actualiza en el mismo commit que el código, y un registro de decisiones de arquitectura con sus compromisos. <a href="https://github.com/Ssebv/odoo-rag#run-it" target="_blank" rel="noopener">Pasos para instalar y probar de un repo público.</a></p></li>
<li><h3>Planificar antes del trabajo riesgoso</h3><p>Todo lo grande, o lo que toque pagos, producción, documentos tributarios o datos personales, parte con un plan escrito antes de cambiar un solo archivo.</p></li>
<li><h3>Trabajar en ramas cortas</h3><p>Cada cambio es lo bastante chico para revisarlo por separado, y las pruebas corren después de cada bloque. La app de iPhone de Norte creció así, por rondas numeradas: pruebas, revisión, merge y despliegue.</p></li>
<li><h3>Probar por capas</h3><p>Los tipos atajan los errores simples, las pruebas unitarias la lógica, las de base de datos las reglas de acceso y las de punta a punta el flujo completo. La integración continua de Citofonía corre todas contra una base local, y falla si los tipos generados desde la base están desactualizados. Las pruebas automáticas usan datos de prueba y ninguna credencial real. Los flujos críticos del ERP tienen unos 180 archivos de prueba, y ensayé su migración en una copia de producción antes del corte.</p>
{term("odoo-rag", TEST_RUN, "Repetición de comandos reales.")}
{shot("ci-green", "GitHub Actions con una ejecución exitosa de integración continua de odoo-rag", "Integración continua en el repo público.", 1400, 218)}</li>
<li><h3>Medir lo que las pruebas no ven</h3><p>Que una prueba pase no dice si una respuesta de IA es buena. Para eso construyo evaluaciones y comparo opciones con las mismas preguntas. En <a href="./odoo-rag.html">Odoo RAG</a>, así descubrí que traducir importaba más que la búsqueda híbrida.</p>
{rag_charts("es")}</li>
<li><h3>Revisar, y contrastar lo que se afirma con el código</h3><p>Los cambios pasan por revisión de código antes del commit, y por revisión de seguridad si tocan autenticación, pagos o datos personales. También vale para lo que escribo sobre mi trabajo: una revisión detectó que un artículo mío decía que un monitoreo corría cada seis horas, y el código decía que una vez al día. Corregí el artículo.</p></li>
<li><h3>Desplegar por etapas</h3><p>En el ERP, el trabajo pasa de una rama de desarrollo a staging y luego a producción. Los despliegues a producción se hacen solo fuera del horario laboral de los tres países, porque cada build reinicia el servidor. En la migración comparé el resultado contra una línea base previa: facturas, pedidos y despachos quedaron idénticos.</p></li>
<li><h3>Vigilar en producción</h3><p>Un health check diario corre más de 40 detectores, con alertas urgentes cada 30 minutos. <a href="../writing/health-check.html">Escribí sobre lo que encontró</a>, incluido el detector mío que estaba seguro y equivocado.</p></li>
</ol>

<h2 id="arquitectura">Arquitectura de cinco sistemas</h2>
<p>Cada sistema tiene restricciones distintas, así que cada uno tiene una forma distinta. Los diagramas se leen de arriba hacia abajo, desde quienes usan el sistema hasta donde viven los datos. La parte destacada es la que define el diseño.</p>

<h3 id="arq-erp">ERP en Odoo 19</h3>
<p>Un ERP en producción para 4 empresas en 3 países, alojado en Odoo.sh. El código es privado.</p>
{arch("Capas del ERP", [
    ("Canales", ["Administración", "Consignación con retail", "Mercado Libre", "Yuju"]),
    ("18 módulos propios", ["*Núcleo común: ventas, stock, facturas", "Consignación", "Facturación por despacho", "Informes"]),
    ("Localización tributaria", ["Chile · SII", "Colombia · DIAN", "Perú · SUNAT"]),
    ("Plataforma", ["Odoo 19", "PostgreSQL con invariantes", "Health check y alertas"]),
])}
<ul>
<li><strong>Menos módulos, responsabilidades más claras.</strong> Consolidé 41 módulos propios en 18, así hay menos que actualizar y la lógica común tiene un solo lugar.</li>
<li><strong>Las reglas críticas viven en la base de datos.</strong> Un trigger de PostgreSQL impone la invariante del stock en consignación, y ningún flujo ni script puede saltársela.</li>
<li><strong>Campos explícitos, no convenciones de nombres.</strong> Una reorganización de bodegas obligó a cambiar 45 puntos en 7 módulos que dependían del nombre de la ubicación. La regla ahora es identificar la consignación por un campo.</li>
</ul>

<h3 id="arq-citofonia">Citofonía</h3>
<p>Un citófono digital para edificios, en desarrollo, <a href="./citofonia.html">con su propia página</a>. Es un monorepo con pnpm y Turborepo: una app móvil, un panel de administración, una API y paquetes compartidos para los tipos de la base y la interfaz. El código es privado.</p>
{arch("Capas de Citofonía", [
    ("Clientes", ["App del residente · React Native, Expo", "Tablet de conserjería", "Panel de administración · React, Vite"]),
    ("API en el borde", ["Hono en Cloudflare Workers", "Llamadas", "Puertas", "Avisos push", "Invitaciones", "Votaciones"]),
    ("Estado de la llamada", ["*Un Durable Object por unidad: la llamada", "Uno por estación: el límite de llamadas"]),
    ("Datos y medios", ["Supabase PostgreSQL con seguridad por fila", "LiveKit para las llamadas"]),
])}
<ul>
<li><strong>La base de datos impone el acceso.</strong> Para los datos del día a día, las apps hablan directo con PostgreSQL, bajo seguridad por fila probada con pgTAP. La API se encarga de lo que la base no puede hacer, como llamadas, puertas, avisos e invitaciones.</li>
<li><strong>La llamada vive en el servidor, no en un dispositivo.</strong> Cada depto tiene una máquina de estados en un Durable Object, con sus propias alarmas. Las pruebas corren la misma lógica con una versión en memoria.</li>
<li><strong>El hardware de las puertas está detrás de una sola interfaz.</strong> Un driver tiene un método, <code>openDoor</code>. Hoy hay dos, para la tablet y para un relé HTTP, y un sistema de puertas nuevo significa un driver nuevo.</li>
<li><strong>Las migraciones no se editan.</strong> Hay una por tema y van 105. Los tipos se generan desde el esquema, y la integración continua revisa que estén al día.</li>
</ul>

<h3 id="arq-norte">Norte</h3>
<p>Una app personal de finanzas y salud con clientes nativos y web. El código es privado.</p>
{arch("Capas de Norte", [
    ("Clientes", ["iPhone, Apple Watch y widgets · SwiftUI", "Web · Next.js, React"]),
    ("API", ["*Una sola API REST JSON para todos los clientes", "Revisión de sesión en cada consulta"]),
    ("Dominio", ["Finanzas", "Entrenamiento", "Alimentación", "Hábitos"]),
    ("Datos y servicios", ["SQLite", "Lector de correos del banco · IMAP", "API de Anthropic, con salida validada"]),
    ("Alojamiento", ["VPS", "Caddy", "systemd"]),
])}
<ul>
<li><strong>Una sola API para todos los clientes.</strong> El iPhone y la web usan los mismos endpoints, así que cada regla de negocio se escribe una vez.</li>
<li><strong>Sin dependencias de terceros en iOS.</strong> La app usa solo lo que trae la plataforma, así que no hay nada externo que actualizar o auditar.</li>
<li><strong>Una base de datos en un solo archivo.</strong> Una app de un usuario no necesita un servidor de base de datos. SQLite simplifica el alojamiento y los respaldos.</li>
<li><strong>Las pruebas de pantalla están aisladas.</strong> Corren contra un servidor local con una base temporal y datos de demostración, y se niegan a correr contra producción.</li>
</ul>

<h3 id="arq-flagforge">FlagForge</h3>
<p>Feature flags multi-tenant en Rust. <a href="./flagforge.html">Tiene su propia página</a>, y <a href="https://github.com/Ssebv/flagforge" target="_blank" rel="noopener">el código es público</a>.</p>
{arch("Capas de FlagForge", [
    ("Clientes", ["SDK para servicios", "Panel · Leptos, WebAssembly", "Operadores e integración continua"]),
    ("API · axum", ["Evaluación, desde memoria", "API de administración", "Caché de snapshots"]),
    ("Motor", ["*flagforge-core: funciones puras, sin I/O"]),
    ("Datos", ["flagforge-storage: SQL revisado al compilar", "PostgreSQL, LISTEN/NOTIFY"]),
])}
<ul>
<li><strong>La parte que debe ser correcta no tiene I/O.</strong> La evaluación es una función pura del flag, el contexto y el entorno (salt y segmentos), así que se puede probar a fondo.</li>
<li><strong>Un motor, tres consumidores.</strong> El servidor, el SDK y el editor de reglas del panel reutilizan el mismo crate, así que no pueden contradecirse.</li>
<li><strong>Un cambio de esquema rompe el build, no producción.</strong> <code>sqlx</code> verifica cada consulta contra el esquema real al compilar.</li>
</ul>

<h3 id="arq-modomax">ModoMax</h3>
<p>Una tienda online. <a href="./modomax.html">Las decisiones de su asistente tienen su propia página.</a> El código es privado.</p>
{arch("Capas de ModoMax", [
    ("Clientes", ["Tienda", "Panel de administración", "WhatsApp"]),
    ("Aplicación", ["*Una sola app Next.js: páginas, server actions, rutas de API, tareas programadas"]),
    ("Dominio y validación", ["Prisma", "Zod", "Registro de auditoría"]),
    ("Datos y servicios", ["PostgreSQL, solo acceso local", "Pagos", "Documentos tributarios", "Correo", "API de Anthropic"]),
    ("Alojamiento", ["VPS", "Caddy", "systemd"]),
])}
<ul>
<li><strong>Una sola aplicación desplegable.</strong> Para una tienda de este tamaño, una app en un VPS es más fácil de operar y depurar que varios servicios separados.</li>
<li><strong>La base de datos no está expuesta.</strong> PostgreSQL acepta solo conexiones locales.</li>
<li><strong>Los cambios de esquema van por migraciones.</strong> Producción usa <code>prisma migrate deploy</code>, nunca <code>db push</code>.</li>
</ul>

<h2 id="reglas">Reglas que mantengo</h2>
<div class="guards"><ul>
<li>Sin despliegues a producción del ERP en horario laboral de ninguno de sus tres países.</li>
<li>Los secretos no entran a los repositorios.</li>
<li>Una migración ya commiteada no se edita.</li>
<li>Las pruebas automáticas no tocan producción, y los datos de ejemplo siempre son ficticios.</li>
<li>Los cambios difíciles de revertir requieren una decisión explícita antes.</li>
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
    if not (ROOT / card).exists():
        print(f"warning: {card} is missing, run build_og.py and rebuild", file=sys.stderr)
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
<link rel="preload" href="{root}fonts/space-grotesk-latin.woff2" as="font" type="font/woff2" crossorigin>
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
