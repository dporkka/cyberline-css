"""Optional real-browser smoke test for the runnable Go SaaS reference.

Start the standard-library example with `go run .`, then run this script
using an isolated Playwright Python environment. No JavaScript is shipped
to example users; the browser automation runs only during development.
"""
import argparse
from urllib.parse import parse_qs, urlparse
from playwright.sync_api import sync_playwright


def inspect(browser, base_url: str, name: str) -> None:
    context = browser.new_context(viewport={"width": 320, "height": 850})
    page = context.new_page()
    try:
        response = page.goto(base_url, wait_until="load")
        assert response is not None and response.status == 200
        assert page.title().startswith("Overview")
        assert page.locator("script").count() == 0, "Example must not require browser JS"
        assert page.locator("body").get_attribute("data-syn-theme") == "studio"

        page.get_by_role("navigation", name="Workspace").get_by_role("link", name="Customers").click()
        assert page.get_by_role("heading", name="Filter customers").is_visible()
        page.get_by_label("Search by name, ID or plan").fill("Alpha")
        page.get_by_label("Subscription status").select_option("active")
        page.get_by_role("button", name="Apply filters").click()
        assert page.locator("tbody tr").count() == 1, "Filters must run on the server"
        assert "Example Alpha Agency" in page.locator("tbody").inner_text()
        assert parse_qs(urlparse(page.url).query)["q"] == ["Alpha"]

        page.get_by_role("navigation", name="Choose interface theme").get_by_role("link", name="Grid").click()
        assert page.locator("body").get_attribute("data-syn-theme") == "grid"
        params = parse_qs(urlparse(page.url).query)
        assert params["q"] == ["Alpha"] and params["status"] == ["active"]
        assert page.locator("tbody tr").count() == 1

        # Tables may scroll internally, but ordinary page content must not
        # introduce a horizontal page scrollbar at a 320 CSS-pixel viewport.
        for font_scale in (1, 2):
            page.evaluate("(scale) => { document.documentElement.style.fontSize = (16 * scale) + 'px'; }", font_scale)
            widths = page.evaluate("""() => ({
                root: document.documentElement.scrollWidth,
                viewport: document.documentElement.clientWidth,
            })""")
            assert widths["root"] <= widths["viewport"] + 1, (
                f"{name}: {font_scale}x text at 320px overflow: {widths}"
            )

        page.locator("tbody a").first.click()
        assert page.locator("body").get_attribute("data-syn-theme") == "grid"
        assert page.get_by_role("heading", name="Example Alpha Agency").is_visible()

        response = page.request.get(base_url + "/customers.csv?q=Alpha&status=active&theme=grid")
        assert response.status == 200
        assert "text/csv" in response.headers["content-type"]
        assert "cust-alpha" in response.text() and "cust-beacon" not in response.text()
        print(f"PASS {name}: native filters, theme, details, CSV, 320px reflow")
    finally:
        context.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--browsers", nargs="+", choices=("chromium", "firefox", "webkit"), default=["chromium", "firefox"])
    args = parser.parse_args()
    with sync_playwright() as playwright:
        for name in args.browsers:
            browser = getattr(playwright, name).launch(headless=True)
            try:
                inspect(browser, args.base_url, name)
            finally:
                browser.close()


if __name__ == "__main__":
    main()
