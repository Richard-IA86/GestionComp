import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(Path(__file__).resolve().parent / ".env")

APP_USUARIO = os.getenv("APP_USUARIO", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")


def test_login():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
        )
        context = browser.new_context(
            accept_downloads=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",  # noqa: E501
            viewport={"width": 1366, "height": 768},
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"  # noqa: E501
        )
        page = context.new_page()

        # ── Monitoreo completo de red (todo, desde el inicio) ────────────────
        def on_request(req):
            if req.resource_type in ("xhr", "fetch"):
                print(f"  --> AJAX [{req.method}] {req.url}")
                if any(
                    x in req.url
                    for x in ["SetBase", "GetBase", "TablaGenerica"]
                ):
                    try:
                        body = req.post_data
                        if body:
                            print(f"      >>> POST DATA: {body[:400]}")
                    except Exception:
                        pass

        def on_response(res):
            if res.request.resource_type in ("xhr", "fetch"):
                # Capturamos los endpoints clave: bases disponibles,
                # selección de base y tabla
                if any(
                    x in res.url
                    for x in ["TablaGenerica", "GetBase", "SetBase"]
                ):
                    try:
                        body = res.text()
                        print(f"  <-- AJAX [{res.status}] {res.url}")
                        print(
                            f"      >>> BODY ({len(body)} chars): {body[:800]}"
                        )
                    except Exception as e:
                        print(f"      >>> No se pudo leer el body: {e}")

        def on_request_failed(req):
            print(f"❌ [FALLA RED] {req.url} — {req.failure}")

        page.on("request", on_request)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)

        print(">>> Navegando al login...")
        page.goto("http://10.2.1.81/")

        print(">>> Ingresando credenciales...")
        page.fill("#userName", APP_USUARIO)
        page.fill("#Password", APP_PASSWORD)
        page.click("#botonLogin")
        # Esperamos que se ejecuten todos los AJAX post-login
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        # ── Buscar el dropdown de empresa en la UI ───────────────────────────
        print()
        print(
            ">>> Buscando select/inputs con 'base'"
            " o 'empresa' en la página..."
        )
        selects = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('select, input[list]').forEach(el => {
                results.push({
                    tag: el.tagName,
                    id: el.id,
                    name: el.name,
                    className: el.className,
                    outerHTML: el.outerHTML.substring(0, 400)
                });
            });
            return results;
        }""")
        for s in selects:
            print(
                f"  [{s['tag']}]"
                f" id={s['id']!r} name={s['name']!r}"
                f" class={s['className']!r}"
            )
            print(f"    HTML: {s['outerHTML'][:300]}")

        print()
        print(">>> Listo. Revisando resultados arriba...")
        browser.close()
        print("Prueba finalizada.")


if __name__ == "__main__":
    test_login()
