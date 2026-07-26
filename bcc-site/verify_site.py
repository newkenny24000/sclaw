"""Headless render check for the Buffalo Claw Co site (Ken's verify-before-done rule).

Serves bcc-site/ locally, loads it in headless Chromium, and asserts:
console has no errors, key sections render, the claw scene animates on scroll,
form pills toggle, and submit shows the success card.

Run: python verify_site.py
"""
import http.server
import socketserver
import threading
import os
import sys

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = 8791


def serve():
    os.chdir(ROOT)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", PORT), handler) as httpd:
        httpd.serve_forever()


def main():
    threading.Thread(target=serve, daemon=True).start()
    failures = []
    console_errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on(
            "console",
            lambda m: console_errors.append(m.text) if m.type == "error" else None,
        )
        page.on("pageerror", lambda e: console_errors.append(str(e)))
        page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle")

        for sel, label in [
            ("h1", "hero headline"),
            ("#how h2", "how-it-works heading"),
            ("#hosting h2", "hosting heading"),
            ("#rentals h2", "rentals heading"),
            ("#about h2", "about heading"),
            ("#interest-form", "contact form"),
            ("footer", "footer"),
        ]:
            if not page.locator(sel).first.is_visible():
                failures.append(f"{label} ({sel}) not visible")

        if "steady revenue" not in page.locator("h1").inner_text():
            failures.append("hero headline text wrong")

        # claw scene reacts to scroll
        before = page.locator("#claw-rig").get_attribute("style") or ""
        page.evaluate("window.scrollTo(0, 1400)")
        page.wait_for_timeout(400)
        after = page.locator("#claw-rig").get_attribute("style") or ""
        if "translateY" not in after or before == after:
            failures.append("claw scene did not animate on scroll")

        # reveals fired
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(600)
        revealed = page.evaluate(
            "document.querySelectorAll('[data-reveal].rv').length"
        )
        total = page.evaluate("document.querySelectorAll('[data-reveal]').length")
        if revealed < total * 0.5:
            failures.append(f"reveals not firing (only {revealed}/{total})")

        # pill toggle
        page.locator('.pill-btn[data-value="Call"]').click()
        if "on" not in (
            page.locator('.pill-btn[data-value="Call"]').get_attribute("class") or ""
        ):
            failures.append("contact-method pill did not toggle")

        # form submit -> success card (mailto fallback path)
        page.locator("#f-name").fill("Test Person")
        page.locator("#f-email").fill("test@example.com")
        page.locator('#interest-form button[type="submit"]').click()
        page.wait_for_timeout(400)
        if not page.locator("#form-success").is_visible():
            failures.append("success card did not show after submit")

        # images loaded (placeholders or real)
        broken = page.evaluate(
            "Array.from(document.images).filter(i => !i.complete || i.naturalWidth === 0).length"
        )
        if broken:
            failures.append(f"{broken} broken image(s)")

        page.screenshot(path=os.path.join(ROOT, "verify_screenshot.png"), full_page=True)
        browser.close()

    real_errors = [e for e in console_errors if "favicon" not in e.lower()]
    if real_errors:
        failures.append(f"console errors: {real_errors}")

    if failures:
        print("FAIL")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    print("PASS — all render checks green; screenshot at verify_screenshot.png")


if __name__ == "__main__":
    main()
