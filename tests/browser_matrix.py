"""Opt-in browser matrix: no runtime JS or CSS dependency introduced.

Requires developer-only Playwright + browsers:
  python3 tests/browser_matrix.py --browsers chromium firefox webkit
  PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium-browser python3 ...
Run on a machine with the native browser dependencies installed. A missing
browser is reported as BLOCKED and never counted as PASS.
"""
import argparse
from pathlib import Path
import os
import shutil
import sys
from playwright.sync_api import sync_playwright
from browser_launch import launch_options

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("index.html", "docs/index.html", "examples/console.html",
         "examples/resources.html", "examples/pricing.html",
         "docs/console-kit.html", "examples/saas.html",
         "examples/business.html", "examples/terminal.html", "examples/geometry-terminal.html",
         "examples/operations-console.html", "examples/themes.html",
         "examples/vertigo-admin.html", "examples/saas-workflows.html", "examples/minimalist-patterns.html", "examples/design-states.html", "examples/symbols.html", "examples/motion.html")


def assert_page(browser, name: str, viewport: int) -> None:
    context = browser.new_context(viewport={"width": viewport, "height": 820},
                                  reduced_motion="reduce")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda err: errors.append(str(err)))
    url = (ROOT / name).as_uri()
    response = page.goto(url, wait_until="load")
    assert page.url == url, (url, page.url)
    assert response is None or response.ok, (url, response.status)
    assert page.locator("script").count() == 0, name
    assert page.get_by_role("main").count() == 1, name
    assert page.locator('link[rel="stylesheet"]').count() >= 1
    css = page.locator("body").evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()")
    if name == "examples/minimalist-patterns.html":
        assert "light-dark(" in css, (name, css)
    else:
        assert css in ("#76e7f7", "#f1b574", "#2458c6", "#ffb36b", "#65e8a0", "#155ac8", "#313a45"), (name, css)
    overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
    assert overflow <= 1, (name, viewport, overflow)
    assert not errors, (name, errors)
    if name == "docs/index.html" and viewport == 1280:
        button = page.get_by_role("button", name="OPEN COMMAND")
        button.focus()
        outline = button.evaluate("e => getComputedStyle(e).outlineStyle")
        assert outline != "none", outline
        page.keyboard.press("Enter")
        popover = page.locator("#command-popover")
        assert popover.evaluate('e => e.matches(":popover-open")'), "popover cannot open"
        page.keyboard.press("Escape")
        assert not popover.evaluate('e => e.matches(":popover-open")'), "popover cannot dismiss"
        details = page.locator("#components details").first
        details.locator("summary").click()
        assert details.evaluate("e => e.open"), "disclosure cannot open"
        # New HTML-first navigation and static loading states must render in-browser.
        breadcrumb = page.get_by_role("navigation", name="Breadcrumb")
        assert breadcrumb.get_by_text("Component gallery").get_attribute("aria-current") == "page"
        pages = page.get_by_role("navigation", name="Gallery sections")
        assert pages.get_by_role("link").count() == 3
        first_page_link = pages.get_by_role("link").first
        assert first_page_link.evaluate("e => e.getBoundingClientRect().height") >= 44
        # Match keyboard modality before programmatic focus: focus-visible is
        # intentionally not required after a pointer-originated interaction.
        page.keyboard.press("Tab")
        first_page_link.focus()
        assert first_page_link.evaluate("e => getComputedStyle(e).outlineStyle") != "none"
        skeleton = page.locator(".syn-skeleton").first
        assert skeleton.get_attribute("aria-hidden") == "true"
        assert skeleton.evaluate("e => getComputedStyle(e).animationName") == "none"
        assert skeleton.evaluate("e => getComputedStyle(e).backgroundColor") != "rgba(0, 0, 0, 0)"
    if name == "examples/resources.html":
        assert page.get_by_role("search").count() == 1
        assert page.get_by_role("table").count() == 1
        assert page.get_by_role("searchbox", name="SEARCH BY NAME").count() == 1
    if name == "examples/themes.html":
        expected = {
            "grid": ("#76e7f7", "dark"),
            "noir": ("#f1b574", "dark"),
            "studio": ("#2458c6", "light"),
            "industrial": ("#ffb36b", "dark"),
            "terminal": ("#65e8a0", "dark"),
            "corporate": ("#155ac8", "light"),
            "minimal": ("#313a45", "light"),
        }
        assert page.locator(".theme-tile").count() == len(expected)
        for theme, (accent, scheme) in expected.items():
            tile = page.locator(f'.theme-tile[data-syn-theme="{theme}"]')
            assert tile.count() == 1, theme
            values = tile.evaluate("""e => ({
                accent: getComputedStyle(e).getPropertyValue('--syn-accent').trim(),
                colorScheme: getComputedStyle(e).colorScheme
            })""")
            assert values["accent"] == accent, (theme, values)
            assert values["colorScheme"] == scheme, (theme, values)
            button = tile.locator(".syn-button--primary")
            assert button.is_visible(), (theme, "primary button hidden")
        if viewport == 1280:
            nested = page.evaluate("""() => {
                function create(parent, name, classes) {
                    const node = document.createElement('section');
                    node.className = classes;
                    node.dataset.synTheme = name;
                    node.innerHTML = '<h3>Nested theme heading</h3>';
                    parent.append(node);
                    const style = getComputedStyle(node);
                    return {
                        text: getComputedStyle(node.querySelector('h3')).color,
                        colorScheme: style.colorScheme,
                        radius: style.getPropertyValue('--syn-radius').trim(),
                        cut: style.getPropertyValue('--syn-cut').trim()
                    };
                }
                const grid = document.querySelector('.theme-tile[data-syn-theme="grid"]');
                const corporate = document.querySelector('.theme-tile[data-syn-theme="corporate"]');
                const terminal = document.querySelector('.theme-tile[data-syn-theme="terminal"]');
                const minimal = document.querySelector('.theme-tile[data-syn-theme="minimal"]');
                const plain = document.createElement('section');
                plain.dataset.synTheme = 'grid';
                plain.innerHTML = '<h3>Plain nested theme</h3>';
                minimal.append(plain);
                const plainStyles = getComputedStyle(plain);
                const plainBoundary = {
                    background: plainStyles.backgroundColor,
                    text: getComputedStyle(plain.querySelector('h3')).color
                };
                const lightInDark = create(grid, 'corporate', 'syn-price-card');
                const darkInLight = create(corporate, 'grid', 'syn-price-card');
                const gridInTerminal = create(terminal, 'grid', 'syn-panel syn-panel--cut');
                const flex = document.createElement('div');
                flex.className = 'syn-u-flex syn-u-between syn-u-center';
                corporate.append(flex);
                return {lightInDark, darkInLight, gridInTerminal, plainBoundary,
                        justify: getComputedStyle(flex).justifyContent,
                        align: getComputedStyle(flex).alignItems};
            }""")
            assert nested["lightInDark"]["text"] == "rgb(24, 39, 60)", nested
            assert nested["lightInDark"]["colorScheme"] == "light", nested
            assert nested["darkInLight"]["text"] == "rgb(237, 249, 255)", nested
            assert nested["darkInLight"]["colorScheme"] == "dark", nested
            assert nested["plainBoundary"]["background"] == "rgb(8, 15, 25)", nested
            assert nested["plainBoundary"]["text"] == "rgb(237, 249, 255)", nested
            assert nested["gridInTerminal"]["radius"] == ".25rem", nested
            assert nested["gridInTerminal"]["cut"] == ".9rem", nested
            assert nested["justify"] == "space-between", nested
            assert nested["align"] == "center", nested
    if name == "examples/operations-console.html":
        assert page.get_by_role("heading", name="An operations console built on HTML.").count() == 1
        assert page.locator(".syn-kpi-grid article").count() == 4
        assert page.get_by_role("table").count() == 1
        assert page.locator("progress").count() == 4
        assert page.locator(".syn-terminal").count() == 1
        noir = page.locator(".ops-metric[data-syn-theme='noir']")
        assert noir.evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()") == "#f1b574"
        if viewport == 1280:
            page.get_by_role("link", name="Skip to content").focus()
            assert page.locator(":focus").evaluate("e => getComputedStyle(e).outlineStyle") != "none"
            details = page.locator("#integration details").first
            details.locator("summary").click()
            assert details.evaluate("e => e.open"), "native disclosure should work without JS"
    if name == "examples/geometry-terminal.html":
        frames = page.locator(".syn-frame")
        assert frames.count() == 5, "all five frame profiles must render"
        bevel = frames.first
        clip = bevel.evaluate("e => getComputedStyle(e, '::before').clipPath")
        assert clip.startswith("polygon("), (name, viewport, clip)
        fill = bevel.evaluate("e => getComputedStyle(e, '::after').backgroundColor")
        assert fill not in ("rgba(0, 0, 0, 0)", "transparent"), fill
        assert page.locator(".syn-terminal-error").count() == 1
        assert page.locator(".syn-terminal-warning").count() == 1
        numeric = page.locator(".syn-cell--numeric").first
        assert numeric.evaluate("e => getComputedStyle(e).textAlign") == "right"
        if viewport == 1280:
            panel_group = page.locator("#geometry .syn-grid")
            panel_group.evaluate("e => e.style.setProperty('--syn-frame-fill', '#225533')")
            inherited_fill = bevel.evaluate("e => getComputedStyle(e, '::after').backgroundColor")
            assert inherited_fill == "rgb(34, 85, 51)", inherited_fill

            page.evaluate("""() => {
                const controls = document.createElement('div');
                controls.innerHTML = '<button class="syn-button syn-button--primary" aria-disabled="true" id="syn-aria-disabled">ARIA disabled</button>'
                    + '<button class="syn-button syn-button--primary" disabled id="syn-native-disabled">Native disabled</button>';
                document.querySelector('main').append(controls);
            }""")
            aria_button = page.locator("#syn-aria-disabled")
            original_background = aria_button.evaluate("e => getComputedStyle(e).backgroundColor")
            aria_button.hover()
            assert aria_button.evaluate("e => getComputedStyle(e).backgroundColor") == original_background
            assert aria_button.evaluate("e => getComputedStyle(e).cursor") == "not-allowed"
            assert aria_button.evaluate("e => getComputedStyle(e).pointerEvents") != "none"
            native_button = page.locator("#syn-native-disabled")
            assert native_button.evaluate("e => getComputedStyle(e).cursor") == "not-allowed"

            page.emulate_media(forced_colors="active")
            assert bevel.evaluate("e => getComputedStyle(e).borderTopStyle") == "solid"
            assert bevel.evaluate("e => getComputedStyle(e, '::before').display") == "none"
    if name == "examples/design-states.html":
        assert page.get_by_role("heading", name="Clarity in every state.").count() == 1
        assert page.get_by_role("button", name="Disabled native button").is_disabled()
        if viewport == 1280:
            field_bottom = page.locator("#classless-name").evaluate("e => e.getBoundingClientRect().bottom")
            button_top = page.get_by_role("button", name="Native button", exact=True).evaluate("e => e.getBoundingClientRect().top")
            assert button_top - field_bottom >= 8, "semantic example controls need vertical rhythm"
            grid = page.locator('[data-syn-theme="grid"]')
            studio = page.locator("body")
            token = "e => getComputedStyle(e).getPropertyValue('--syn-focus-ring').trim()"
            assert grid.evaluate(token) != studio.evaluate(token), "nested focus color failed"
            regular = page.get_by_role("button", name="Execute")
            compact = page.get_by_role("button", name="Review")
            measure = "e => e.getBoundingClientRect().height"
            assert compact.evaluate(measure) < regular.evaluate(measure), "compact control height failed"
            selected = page.get_by_role("button", name="Selected")
            background = "e => getComputedStyle(e).backgroundColor"
            selected_color = selected.evaluate(background)
            selected.hover()
            assert selected.evaluate(background) == selected_color, "pressed state lost on hover"
            invalid = page.locator("#email")
            border = "e => getComputedStyle(e).borderTopColor"
            invalid.hover()
            invalid_color = invalid.evaluate(border)
            invalid.focus()
            assert invalid.evaluate(border) == invalid_color, "invalid state lost on focus"
            page.keyboard.press("Tab")
            selected.focus()
            assert selected.evaluate("e => getComputedStyle(e).outlineStyle") != "none"
            page.emulate_media(forced_colors="active")
            assert selected.evaluate("e => getComputedStyle(e).outlineStyle") != "none"
    if name == "examples/symbols.html":
        icons = page.locator(".syn-icon")
        assert icons.count() == 2
        for icon in icons.all():
            values = icon.evaluate("""e => ({
                width: e.getBoundingClientRect().width,
                height: e.getBoundingClientRect().height,
                color: getComputedStyle(e).color,
            })""")
            assert values["width"] >= 12 and abs(values["width"] - values["height"]) <= 1, values
        ascii = page.locator(".syn-ascii").first
        styles = ascii.evaluate("""e => ({
            whiteSpace: getComputedStyle(e).whiteSpace,
            overflowX: getComputedStyle(e).overflowX,
            fontVariantLigatures: getComputedStyle(e).fontVariantLigatures,
        })""")
        assert styles == {"whiteSpace": "pre", "overflowX": "auto",
                          "fontVariantLigatures": "none"}, styles
        # The long line must scroll *inside* the pre, not expand the document.
        ascii.evaluate("e => e.style.inlineSize = '10ch'")
        assert ascii.evaluate("e => e.scrollWidth > e.clientWidth")
        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
        assert page.locator(".syn-symbol[aria-hidden='true']").count() >= 5
        if viewport == 1280:
            accessible = page.locator('main').aria_snapshot()
            # Decorative glyphs and text-art disappear from the accessibility
            # tree; visible equivalents remain.
            for phrase in ('API online and jobs online',
                           'Gateway healthy and queue connected',
                           'Search example (disabled)', 'Network healthy'):
                assert phrase in accessible, (phrase, accessible)
            for hidden in ('JOBS [OK]', 'Queue: connected', 'SYNTYR / CONTROLLER'):
                assert hidden not in accessible, (hidden, accessible)
            # Check actual cascade scoping, not only the CSS source strings:
            # unrelated pages using the same class names must remain untouched.
            result = page.evaluate("""() => {
                document.body.classList.remove('syn-root');
                document.body.innerHTML = [
                  '<div id="outside"><span class="syn-icon"></span>',
                  '<pre class="syn-ascii">xy</pre>',
                  '<span class="syn-symbol">◇</span></div>',
                  '<div id="inside" class="syn-root">',
                  '<span class="syn-icon"></span><pre class="syn-ascii">xy</pre>',
                  '<span class="syn-symbol">◇</span></div>',
                  '<pre id="self" class="syn-root syn-ascii">xy</pre>'
                ].join('');
                function measure(selector) {
                  const el = document.querySelector(selector);
                  const cs = getComputedStyle(el);
                  return {display: cs.display, whitespace: cs.whiteSpace,
                    ligatures: cs.fontVariantLigatures, lineHeight: cs.lineHeight};
                }
                return {
                  outsideIcon: measure('#outside .syn-icon'),
                  insideIcon: measure('#inside .syn-icon'),
                  outsideText: measure('#outside .syn-ascii'),
                  insideText: measure('#inside .syn-ascii'),
                  rootSelf: measure('#self'),
                  outsideSymbol: measure('#outside .syn-symbol'),
                  insideSymbol: measure('#inside .syn-symbol')
                };
            }""")
            assert result['outsideIcon']['display'] == 'inline', result
            assert result['insideIcon']['display'] == 'inline-block', result
            assert result['outsideText']['ligatures'] != 'none', result
            assert result['insideText']['ligatures'] == 'none', result
            assert result['rootSelf']['ligatures'] == 'none', result
            assert result['outsideSymbol']['display'] == 'inline', result
            assert result['insideSymbol']['display'] == 'inline-block', result
    if name == "examples/saas-workflows.html":
        assert page.get_by_role("search").count() == 1, name
        assert page.get_by_role("table").count() == 1, name
        assert page.get_by_role("navigation", name="Breadcrumb").count() == 1, name
        assert page.get_by_role("navigation", name="Pagination example").get_by_role("link").count() == 3
        assert page.locator("#results tbody tr").count() == 3, name
        assert page.get_by_role("searchbox", name="SEARCH RECORDS").count() == 1
        assert page.locator(".syn-skeleton[aria-hidden='true']").count() == 2
        assert page.get_by_role("navigation", name="Pagination example").get_by_role("link").first.evaluate(
            "e => e.getBoundingClientRect().height") >= 44
        if viewport == 1280:
            page.get_by_text("Display preferences").click()
            assert page.locator("#preferences details").first.evaluate("e => !e.open")
            page.get_by_text("Display preferences").click()
            assert page.locator("#preferences details").first.evaluate("e => e.open")
            compact = page.get_by_role("checkbox", name="Compact record density (local preview)")
            cell = page.locator("#results tbody td").first
            compact_height = cell.evaluate("e => getComputedStyle(e).paddingTop")
            assert compact.is_checked()
            compact.uncheck()
            expanded_height = cell.evaluate("e => getComputedStyle(e).paddingTop")
            assert float(expanded_height.removesuffix("px")) > float(compact_height.removesuffix("px"))
            notifications = page.get_by_role("checkbox", name="Email notifications (requires server)")
            assert notifications.is_disabled()
            searchbox = page.get_by_role("searchbox", name="SEARCH RECORDS")
            searchbox.fill("Atlas")
            assert searchbox.input_value() == "Atlas"
    if name == "examples/vertigo-admin.html" and viewport == 1280:
        def styles():
            return page.evaluate("""() => {
                const card = document.querySelector('.syn-vertigo-admin .card');
                const button = document.querySelector('.syn-vertigo-admin button');
                function themeColor(token) {
                    const probe = document.createElement('span');
                    probe.style.backgroundColor = 'var(' + token + ')';
                    document.body.appendChild(probe);
                    const value = getComputedStyle(probe).backgroundColor;
                    probe.remove();
                    return value;
                }
                return {
                    cardBackground: getComputedStyle(card).backgroundColor,
                    surface: themeColor('--syn-surface'),
                    buttonBackground: getComputedStyle(button).backgroundColor,
                    accent: themeColor('--syn-accent')
                };
            }""")
        studio = styles()
        assert studio["cardBackground"] == studio["surface"], studio
        assert studio["buttonBackground"] == studio["accent"], studio
        page.locator("body").evaluate("e => e.setAttribute('data-syn-theme', 'noir')")
        noir = styles()
        assert noir["cardBackground"] == noir["surface"], noir
        assert noir["buttonBackground"] == noir["accent"], noir
        assert noir["accent"] != studio["accent"], "theme override was ignored"
        # Negative control: removing the optional adapter must remove its paint.
        page.locator('link[href="../integrations/vertigo/admin.css"]').evaluate("e => e.remove()")
        without_adapter = styles()
        assert without_adapter["cardBackground"] != without_adapter["surface"], (
            "adapter has no observable opt-in behavior"
        )
    context.close()


def assert_visual_refinement(browser) -> None:
    """Verify interactive state and compact controls in each real rendering engine."""
    context = browser.new_context(viewport={"width": 900, "height": 700})
    try:
        page = context.new_page()
        css = (ROOT / "dist/syntyr.core.css").read_text()
        page.set_content(f"""<style>{css}</style>
        <main class="syn-root" data-syn-theme="studio">
          <label for="ordinary">Ordinary</label><input class="syn-input" id="ordinary">
          <label for="ordinary-choice">Choice</label>
          <select class="syn-select" id="ordinary-choice"><option>One</option></select>
          <div data-syn-density="compact">
            <label for="compact">Compact</label><input class="syn-input" id="compact">
            <label for="compact-choice">Choice</label>
            <select class="syn-select" id="compact-choice"><option>One</option></select>
          </div>
          <table role="grid" class="syn-table"><tbody>
            <tr id="chosen" aria-selected="true"><td>Chosen</td></tr>
            <tr id="available"><td>Available</td></tr>
          </tbody></table>
        </main>""")
        for ordinary, compact in (("ordinary", "compact"),
                                  ("ordinary-choice", "compact-choice")):
            large_height = page.locator(f"#{ordinary}").evaluate(
                "e => e.getBoundingClientRect().height")
            small_height = page.locator(f"#{compact}").evaluate(
                "e => e.getBoundingClientRect().height")
            assert small_height < large_height - 4, (
                "compact height unchanged", ordinary, large_height, small_height)
            assert small_height >= 36, ("compact target too small", compact, small_height)
        row = page.locator("#chosen")
        selected_background = row.evaluate("e => getComputedStyle(e).backgroundColor")
        row.hover()
        assert row.evaluate("e => getComputedStyle(e).backgroundColor") == selected_background, (
            "hover must preserve selected-row emphasis")
        other = page.locator("#available")
        other.hover()
        assert other.evaluate("e => getComputedStyle(e).backgroundColor") != selected_background, (
            "nonselected hover must not look selected")
    finally:
        context.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browsers", nargs="+",
                        choices=("chromium", "firefox", "webkit"),
                        default=("chromium", "firefox", "webkit"))
    args = parser.parse_args()
    with sync_playwright() as p:
        failed = 0
        for name in args.browsers:
            kwargs = launch_options(name)
            try:
                browser = getattr(p, name).launch(**kwargs)
            except Exception as exc:
                failed += 1
                print(f"BLOCKED {name}: {str(exc).splitlines()[0]}", flush=True)
                continue
            try:
                for path in PAGES:
                    for width in (320, 390, 1280):
                        try:
                            assert_page(browser, path, width)
                        except Exception as exc:
                            raise AssertionError(f"{path} viewport {width}: {exc}") from exc
                assert_visual_refinement(browser)
                print(f"PASS {name}: {len(PAGES)} pages × 3 viewports + keyboard/popover and design-refinement checks",
                      flush=True)
            except Exception as exc:
                failed += 1
                print(f"FAIL {name}: {type(exc).__name__} {exc}", flush=True)
            finally:
                browser.close()
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
