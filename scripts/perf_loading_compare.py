"""Compare two independently deployed CSS loading strategies in real browsers.

Optional maintainer tool (requires Playwright); Syntyr apps require neither
Playwright nor client JavaScript. Both URLs must contain the same content and
assets to isolate loading-strategy changes. Compare real cold and warm visits,
not just CSS gzip sizes. This tool does NOT extract or defer critical CSS.

Example:
  python3 scripts/perf_loading_compare.py --baseline http://localhost:8000/base.html \
    --candidate http://localhost:8000/critical.html --runs 10 \
    --output /tmp/loading-comparison.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import sys
from urllib.parse import urlsplit

from perf_benchmark import INIT_JS, VIEWPORTS, BROWSERS, trial_order

METRICS = ("fcp_ms", "lcp_ms", "cls", "css_requests", "html_transfer_bytes", "css_transfer_bytes", "total_transfer_bytes")


def validate_urls(baseline: str, candidate: str) -> None:
    if baseline == candidate:
        raise ValueError("Baseline and candidate URLs must differ")
    for label, url in (("baseline", baseline), ("candidate", candidate)):
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValueError(f"{label} must be an absolute HTTP(S) URL")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError(f"{label} URL must not contain credentials")
        if parsed.fragment:
            raise ValueError(f"{label} URL must not contain a fragment")


def metric_stats(records: list[dict], metric: str) -> dict:
    numbers = sorted(record[metric] for record in records
                     if record.get(metric) is not None
                     and not isinstance(record[metric], bool))
    if not numbers:
        return {"median": None, "p75": None, "samples": 0}
    # Nearest-rank p75: meaningful even with one sample, without extrapolation.
    rank = (3 * len(numbers) + 3) // 4
    return {
        "median": round(statistics.median(numbers), 3),
        "p75": round(numbers[rank - 1], 3),
        "samples": len(numbers),
    }


def summarize(samples: dict, *, browser: str, viewport: str, runs: int) -> dict:
    return {
        "browser": browser,
        "viewport": viewport,
        "requested_runs": runs,
        "results": {
            variant: {
                cache: {metric: metric_stats(records, metric) for metric in METRICS}
                for cache, records in caches.items()
            }
            for variant, caches in samples.items()
        },
        "limitations": [
            "Synthetic browser data, not field Core Web Vitals or a real-user INP measurement.",
            "Missing FCP, LCP or CLS support is null, never inferred as zero.",
            "Cold means a fresh browser context; warm means a repeat navigation in that context.",
            "CSS requests count response events; cached requests can still produce events.",
            "Transfer sizes are browser Resource Timing values (including headers), not server-side asset byte accounting.",
            "Resource Timing may report zero for cached/cross-origin resources; inspect headers and traces.",
            "Absolute values are machine, browser, page and network dependent.",
            "Compare only equivalent HTML/content/assets, CSS cascade results and server headers.",
        ],
    }


def snapshot(page, stylesheet_responses: list) -> dict:
    measured = page.evaluate("""() => {
      const paint = performance.getEntriesByType('paint')
        .find(e => e.name === 'first-contentful-paint');
      const state = window.__syntyrPerf || {};
      state.flush?.();
      return {
        fcp_ms: paint ? paint.startTime : null,
        lcp_ms: state.lcp ?? null,
        cls: state.cls ?? null,
        // transferSize includes HTTP headers; cross-origin without Timing-Allow-Origin
        // may expose zero. Zero can also mean cached. Inspect network traces.
        html_transfer_bytes: performance.getEntriesByType('navigation')[0]?.transferSize ?? null,
        css_transfer_bytes: (() => {
          const entries = performance.getEntriesByType('resource')
            .filter(e => e.initiatorType === 'link' && /\\.css(?:\\?|$)/.test(e.name));
          return entries.length ? entries.reduce((acc, entry) => acc + entry.transferSize, 0) : 0;
        })(),
        total_transfer_bytes: (() => {
          const entries = performance.getEntriesByType('resource');
          const nav = performance.getEntriesByType('navigation')[0];
          return (nav?.transferSize ?? 0) + entries.reduce((acc, entry) => acc + entry.transferSize, 0);
        })(),
      };
    }""")
    measured["css_requests"] = len(stylesheet_responses)
    return measured


def sample_variant(browser, url: str, viewport: str, screenshot: Path | None = None) -> dict:
    context = browser.new_context(viewport=VIEWPORTS[viewport], reduced_motion="reduce")
    page = context.new_page()
    page.add_init_script(INIT_JS)
    stylesheet_responses = []
    page.on("response", lambda response: stylesheet_responses.append(response)
            if response.request.resource_type == "stylesheet" else None)
    results = {}
    try:
        for cache in ("cold", "warm"):
            stylesheet_responses.clear()
            response = page.goto(url, wait_until="load", timeout=60000)
            if response is None or response.status >= 400:
                status = response.status if response else "missing"
                raise RuntimeError(f"Navigation failed: {url} ({status})")
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            results[cache] = snapshot(page, stylesheet_responses)
            if screenshot and cache == "warm":
                screenshot.parent.mkdir(parents=True, exist_ok=True)
                # Capture only after both navigations to avoid warming lazy assets for the warm sample.
                page.screenshot(path=str(screenshot), full_page=True, animations="disabled")
        return results
    finally:
        context.close()


def compare(baseline: str, candidate: str, *, browsers: list[str],
            viewports: list[str], runs: int, screenshots: Path | None) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright, Error as PlaywrightError
    except ImportError as exc:
        raise RuntimeError("Playwright is optional; install it in a developer environment") from exc

    reports = []
    with sync_playwright() as playwright:
        for browser_name in browsers:
            # A browser that cannot launch is an error, not a passing/skipped lane.
            try:
                browser = getattr(playwright, browser_name).launch()
            except PlaywrightError as exc:
                raise RuntimeError(
                    f"{browser_name} browser launch blocked; check Playwright browser and system dependencies: {str(exc).splitlines()[0]}"
                ) from exc
            try:
                for viewport in viewports:
                    samples = {variant: {"cold": [], "warm": []}
                               for variant in ("baseline", "candidate")}
                    for iteration in range(runs):
                        for variant in trial_order(list(samples), iteration):
                            page_url = baseline if variant == "baseline" else candidate
                            screen = (screenshots / f"{browser_name}-{viewport}-{variant}.png"
                                      if screenshots and iteration == 0 else None)
                            data = sample_variant(browser, page_url, viewport, screen)
                            for cache, metrics in data.items():
                                samples[variant][cache].append(metrics)
                    reports.append(summarize(samples, browser=browser_name,
                                             viewport=viewport, runs=runs))
            finally:
                browser.close()
    return reports


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="baseline HTTP(S) page URL")
    parser.add_argument("--candidate", required=True, help="candidate HTTP(S) page URL")
    parser.add_argument("--browsers", default="chromium", help="comma list: chromium,firefox,webkit")
    parser.add_argument("--viewports", default="mobile,desktop", help="comma list: mobile,desktop")
    parser.add_argument("--runs", type=int, default=10, help="cold/warm pairs per variant, default 10")
    parser.add_argument("--screenshots", type=Path, help="optional PNG comparison directory")
    parser.add_argument("--output", type=Path, help="optional JSON report destination")
    args = parser.parse_args()
    try:
        validate_urls(args.baseline, args.candidate)
        browser_names = args.browsers.split(",")
        viewport_names = args.viewports.split(",")
        if (args.runs <= 0 or not browser_names or not viewport_names
                or len(set(browser_names)) != len(browser_names)
                or len(set(viewport_names)) != len(viewport_names)
                or any(name not in BROWSERS for name in browser_names)
                or any(name not in VIEWPORTS for name in viewport_names)):
            raise ValueError("Invalid browser, viewport or --runs selection")
        reports = compare(args.baseline, args.candidate, browsers=browser_names,
                          viewports=viewport_names, runs=args.runs,
                          screenshots=args.screenshots)
        result = {
            "baseline": args.baseline,
            "candidate": args.candidate,
            "reports": reports,
        }
        rendered = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
            print(f"Wrote {args.output}")
        else:
            print(rendered, end="")
        return 0
    except (ValueError, RuntimeError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    sys.exit(main())
