"""Repeatable, offline, opt-in Chromium performance measurements for SYNTYR.

Run with developer-only Playwright installed:
  python3 scripts/perf_benchmark.py --runs 5 --rows 1000 --sections 60
  PLAYWRIGHT_CHROMIUM_EXECUTABLE=/path/to/chrome python3 scripts/perf_benchmark.py
No npm/build/runtime dependency. Do not compare these scores directly with other
CSS frameworks until each is given equivalent markup and equivalent components.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import statistics
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]


def make_fixture(css: str, rows: int, sections: int, deferred: bool) -> str:
    """Generate identical DOM for variants, toggling only the opt-in render hint."""
    if rows < 0 or sections < 0:
        raise ValueError("fixture counts must be non-negative")
    table_rows = "".join(
        f'<tr><td>Customer {n:04d}</td><td>Campaign {n:04d}</td>'
        f'<td><span class="syn-status syn-status--success">Active</span></td>'
        f'<td class="syn-cell--numeric">{n * 18:,}</td></tr>'
        for n in range(rows)
    )
    hint = ' class="syn-defer-section"' if deferred else ""
    detail_sections = "".join(
        f'<section{hint} style="--syn-defer-size: 26rem">'
        f'<h2>Segment {n}</h2><div class="syn-feature-grid">'
        + "".join(
            f'<article class="syn-feature-card"><h3>Card {n}-{i}</h3>'
            '<p>Representative dense application content with multiple tokens and layout styles.</p>'
            '<button class="syn-button">Inspect</button></article>'
            for i in range(8)
        ) + '</div></section>'
        for n in range(sections)
    )
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SYNTYR Offline Benchmark</title><style>{css}</style>
</head><body class="syn-root syn-page" data-syn-theme="studio">
<main class="syn-shell"><header class="syn-header"><h1>Operations</h1>
<nav class="syn-nav"><a href="#customers">Customers</a></nav></header>
<div class="syn-kpi-grid">{''.join(
    f'<article class="syn-app-card"><h2>Metric {i}</h2><p>{i*79:,}</p></article>'
    for i in range(12))}</div>
<section id="customers"><h2>Customers</h2><div class="syn-table-wrap">
<table class="syn-table"><thead><tr class="header"><th>Customer</th><th>Campaign</th>
<th>Status</th><th>Revenue</th></tr></thead><tbody>{table_rows}</tbody></table>
</div></section>{detail_sections}</main></body></html>"""


def summarize(samples: dict, *, rows: int, sections: int, runs: int, browser: str) -> dict:
    return {
        "browser": browser,
        "fixture": {"rows": rows, "sections": sections},
        "runs": runs,
        "unit": "milliseconds",
        "method": "offline inline CSS; medians; cold navigation + forced theme re-style",
        "results": {
            name: {key: round(statistics.median(item[key] for item in values), 3)
                   for key in values[0]}
            for name, values in samples.items()
        },
    }


def trial_order(names: list[str], index: int) -> list[str]:
    """Rotate variant positions so cold/warm browser effects aren't systematic."""
    if not names:
        return []
    shift = index % len(names)
    return names[shift:] + names[:shift]


def metric_snapshot(session) -> dict:
    return {item["name"]: item["value"]
            for item in session.send("Performance.getMetrics")["metrics"]}


def benchmark(browser, path: Path, cpu_rate: float) -> dict:
    context = browser.new_context(viewport={"width": 1365, "height": 900},
                                  reduced_motion="reduce", device_scale_factor=1)
    page = context.new_page()
    cdp = context.new_cdp_session(page)
    cdp.send("Performance.enable")
    if cpu_rate != 1:
        cdp.send("Emulation.setCPUThrottlingRate", {"rate": cpu_rate})
    try:
        start = time.perf_counter()
        page.goto(path.as_uri(), wait_until="load")
        page.evaluate("() => document.body.offsetHeight")
        navigation = (time.perf_counter() - start) * 1000
        before = metric_snapshot(cdp)
        # One write/read turn per toggle deliberately forces style recalculation.
        # This measures *cost of theme switching*, not CSS parsing/network fetch.
        toggling = page.evaluate("""() => {
          const root = document.body;
          const cell = document.querySelector('tbody tr:last-child td:last-child')
                    || document.querySelector('.syn-app-card');
          const start = performance.now();
          for (let i = 0; i < 10; i++) {
            root.dataset.synTheme = i % 2 ? 'studio' : 'noir';
            void getComputedStyle(cell).color;
            void root.offsetHeight;
          }
          return (performance.now() - start) / 10;
        }""")
        after = metric_snapshot(cdp)
        return {
            "navigation_ms": navigation,
            "theme_toggle_ms": toggling,
            "style_recalc_ms": max(0, after.get("RecalcStyleDuration", 0) -
                                     before.get("RecalcStyleDuration", 0)) * 1000,
            "layout_ms": max(0, after.get("LayoutDuration", 0) -
                               before.get("LayoutDuration", 0)) * 1000,
        }
    finally:
        context.close()


def run(args) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError("Playwright is optional: install into a developer venv, "
                           "then run this tool with that Python interpreter") from error
    core = (ROOT / "dist/syntyr.core.css").read_text(encoding="utf-8")
    recipes = (ROOT / "dist/syntyr.recipes.css").read_text(encoding="utf-8")
    all_css = (ROOT / "dist/syntyr.all.css").read_text(encoding="utf-8")
    styles = {
        "unstyled": ("", False),
        "core": (core, False),
        "core+recipes": (core + "\n" + recipes, False),
        "all": (all_css, False),
        "core+recipes+defer": (core + "\n" + recipes, True),
    }
    samples = {name: [] for name in styles}
    with tempfile.TemporaryDirectory(prefix="syntyr-perf-") as tmp:
        files = {}
        for name, (css, defer) in styles.items():
            path = Path(tmp) / (name.replace("+", "-") + ".html")
            path.write_text(make_fixture(css, args.rows, args.sections, defer),
                            encoding="utf-8")
            files[name] = path
        with sync_playwright() as p:
            kwargs = {"headless": True}
            executable = (os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                          or shutil.which("chromium") or shutil.which("chromium-browser"))
            if executable:
                kwargs.update(executable_path=executable, args=["--no-sandbox"])
            browser = p.chromium.launch(**kwargs)
            try:
                variants = list(files)
                browser_version = browser.version
                for trial in range(args.runs + 1):
                    for name in trial_order(variants, trial):
                        result = benchmark(browser, files[name], args.cpu_rate)
                        # First round warms the browser process and is discarded.
                        if trial:
                            samples[name].append(result)
            finally:
                browser.close()
    report = summarize(samples, rows=args.rows, sections=args.sections,
                       runs=args.runs, browser="chromium")
    report["browser_version"] = browser_version
    report["cpu_throttle_rate"] = args.cpu_rate
    report["notes"] = [
        "Local navigation is noisy; use many runs and compare medians.",
        "Style recalculation and layout are Chrome DevTools metrics over ten forced theme toggles.",
        "Deferred sections change rendering behavior; compare only on long independent content.",
        "Benchmarks do not test CDN RTT, real-user Core Web Vitals, or other frameworks.",
    ]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--rows", type=int, default=1000)
    parser.add_argument("--sections", type=int, default=40)
    parser.add_argument("--cpu-rate", type=float, default=1.0)
    parser.add_argument("--output", type=Path, help="optional output report JSON path")
    args = parser.parse_args()
    if args.runs < 1 or args.rows < 1 or args.sections < 0 or args.cpu_rate < 1:
        parser.error("runs and rows must be positive; sections >= 0; cpu-rate >= 1")
    try:
        result = run(args)
    except Exception as error:
        print(f"BENCHMARK BLOCKED: {error}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
