"""Opt-in real-browser motion smoke test; developer-only Playwright dependency.

Run with `python3 tests/motion_browser.py --browsers chromium firefox webkit`.
Set PLAYWRIGHT_<BROWSER>_EXECUTABLE if local browser builds differ from the
Playwright package's default. Never interpret a missing browser as a pass.
"""
import argparse
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def check(browser, name):
    base = (ROOT / 'dist/syntyr.core.css').read_text()
    motion = (ROOT / 'dist/syntyr.motion.css').read_text()
    markup = '''
      <div data-syn-animate="enter" id="outside">Unstyled outside</div>
      <main class="syn-root" data-syn-theme="grid">
        <h1 id="enter" data-syn-animate="enter" data-syn-from="left">Enter</h1>
        <p id="fade" data-syn-animate="fade">Fade</p>
        <div id="scale" data-syn-animate="scale">Scale</div>
        <div id="reveal" data-syn-animate="reveal">Reveal</div>
        <ul data-syn-stagger>
          <li id="stagger" data-syn-animate="enter" style="--syn-motion-index: 2">Third</li>
        </ul>
        <span id="loader" class="syn-loader" aria-hidden="true"></span>
        <button class="syn-button" id="reveal-control" data-syn-animate="reveal">Review focus</button>
        <button class="syn-button" id="disabled-control" data-syn-animate="fade" disabled>Disabled</button>
        <button popovertarget="menu">Menu</button>
        <div id="menu" popover class="syn-motion-popover">Menu content</div>
      </main>'''
    for preference in ('no-preference', 'reduce'):
        context = browser.new_context(reduced_motion=preference)
        page = context.new_page()
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.set_content(f'<style>{base}</style><style>{motion}</style>{markup}')
        def style(selector, prop):
            return page.locator(selector).evaluate(
                '(e, prop) => getComputedStyle(e).getPropertyValue(prop).trim()', prop)
        for target, animation in (('#enter', 'syn-motion-enter'),
                                  ('#fade', 'syn-motion-fade'),
                                  ('#scale', 'syn-motion-scale'),
                                  ('#reveal', 'syn-motion-reveal')):
            actual = style(target, 'animation-name')
            expected = animation if preference == 'no-preference' else 'none'
            assert actual == expected, (name, preference, target, actual, expected)
        assert style('#outside', 'animation-name') == 'none', (name, preference, 'outside')
        if preference == 'reduce':
            assert style('#loader', 'animation-name') == 'none', (name, preference, 'loader')
            assert style('#reveal', 'clip-path') == 'none', (name, preference, 'reveal clip')
            assert style('#enter', 'opacity') == '1', (name, preference, 'enter opacity')
        else:
            assert style('#loader', 'animation-name') == 'syn-motion-spin', (name, preference, 'loader')
            assert style('#stagger', 'animation-delay') in ('0.13s', '130ms'), (
                name, preference, 'stagger', style('#stagger', 'animation-delay'))
            # After a one-shot effect finishes, native interaction styles must
            # regain control: clipped focus rings and disabled-opacity overrides
            # are regressions even when the entrance itself looked correct.
            page.wait_for_timeout(700)
            page.keyboard.press('Tab')
            page.locator('#reveal-control').focus()
            assert style('#reveal-control', 'clip-path') == 'none', (name, 'focus clip after reveal', style('#reveal-control', 'clip-path'))
            assert style('#reveal-control', 'outline-style') != 'none', (name, 'focus outline after reveal')
            assert abs(float(style('#disabled-control', 'opacity')) - .55) < .01, (name, 'disabled opacity after fade')
            assert style('#enter', 'translate') == 'none', (name, 'released translate')
            assert style('#scale', 'scale') == 'none', (name, 'released scale')
        page.get_by_role('button', name='Menu').click()
        assert page.locator('#menu').evaluate('e => e.matches(":popover-open")'), (name, preference, 'open')
        page.keyboard.press('Escape')
        assert not page.locator('#menu').evaluate('e => e.matches(":popover-open")'), (name, preference, 'close')
        assert not errors, (name, preference, errors)
        page.goto((ROOT / 'examples/motion.html').as_uri())
        assert page.get_by_role('main').count() == 1, (name, preference, 'demo main')
        assert page.locator('.motion-hero .syn-lede').evaluate('e => getComputedStyle(e).opacity') == '1', (name, preference, 'essential description opacity')
        assert page.locator('script').count() == 0, (name, preference, 'demo scripts')
        assert page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1'), (name, preference, 'demo overflow')
        page.get_by_role('button', name='OPEN POPOVER').click()
        assert page.locator('#motion-menu').evaluate('e => e.matches(":popover-open")'), (name, preference, 'demo popover')
        assert not errors, (name, preference, 'demo', errors)
        context.close()
        print(f'PASS {name}: {preference} animation, scoping, stagger, native popover')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--browsers', nargs='+', default=['chromium', 'firefox', 'webkit'])
    args = parser.parse_args()
    failures = 0
    with sync_playwright() as playwright:
        for name in args.browsers:
            try:
                driver = getattr(playwright, name)
                executable = os.environ.get(f'PLAYWRIGHT_{name.upper()}_EXECUTABLE')
                kwargs = dict(headless=True)
                if executable:
                    kwargs['executable_path'] = executable
                browser = driver.launch(**kwargs)
                try:
                    check(browser, name)
                finally:
                    browser.close()
            except Exception as exc:
                print(f'FAILED/BLOCKED {name}: {exc}')
                failures += 1
    return int(failures > 0)


if __name__ == '__main__':
    raise SystemExit(main())
