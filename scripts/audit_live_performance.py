"""Opt-in deployed Syntyr mobile performance and accessibility audit.

Requires developer-only Playwright + Chromium. No Syntyr runtime dependency.

  /tmp/syntyr-browser-venv/bin/python scripts/audit_live_performance.py \
    --runs 7 --axe-file /tmp/axe.min.js \
    --output /tmp/syntyr-live-audit.json

The default 150 ms RTT + 1.6 Mbps download + 4x CPU slowdown is **synthetic**,
not representative field data. This explicitly audits the deployed site and
performs a cold context and warm repeat navigation for each sample.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
from urllib.parse import urlsplit

from perf_benchmark import INIT_JS

ROUTES = ("/examples/business", "/examples/saas")
NETWORK = {"offline": False, "latency": 150,
           "downloadThroughput": 200000, "uploadThroughput": 93750}
METRICS = ("fcp_ms", "lcp_ms", "cls", "ttfb_ms", "page_load_ms",
           "css_requests", "css_transfer_bytes", "total_transfer_bytes")


def validate_origin(url: str) -> str:
    parsed = urlsplit(url)
    if (parsed.scheme not in ("http", "https") or not parsed.hostname
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("Expected a plain HTTP(S) origin without credentials/path/query")
    if parsed.hostname not in ("syntyr-css.pages.dev", "localhost", "127.0.0.1"):
        raise ValueError("Origin must be the Syntyr site or loopback")
    if parsed.hostname == "syntyr-css.pages.dev" and parsed.scheme != "https":
        raise ValueError("Production site requires HTTPS")
    return url.rstrip("/")


def audit_headers(headers: dict) -> dict:
    cache = headers.get("cache-control", "").lower()
    return {
        "cache_control": headers.get("cache-control"),
        "etag": headers.get("etag"),
        "enforced_csp": bool(headers.get("content-security-policy")),
        "report_only_csp": bool(headers.get("content-security-policy-report-only")),
        "csp": headers.get("content-security-policy"),
        "cache_requires_revalidation": ("must-revalidate" in cache or "max-age=0" in cache),
        "nosniff": headers.get("x-content-type-options", "").lower() == "nosniff",
    }


def metric(values: list[dict], name: str) -> dict:
    nums = sorted(record[name] for record in values
                  if isinstance(record.get(name), (float, int))
                  and not isinstance(record[name], bool))
    if not nums:
        return {"median": None, "p75": None, "samples": 0}
    return {"median": round(statistics.median(nums), 2),
            "p75": round(nums[(3 * len(nums) + 3) // 4 - 1], 2),
            "samples": len(nums)}


def summarize(records: list[dict]) -> dict:
    return {key: metric(records, key) for key in METRICS}


def page_metrics(page, css_responses: list) -> dict:
    snapshot = page.evaluate("""() => {
      const paint = performance.getEntriesByType('paint').find(x => x.name === 'first-contentful-paint');
      const nav = performance.getEntriesByType('navigation')[0];
      const state = window.__syntyrPerf || {};
      state.flush?.();
      const resources = performance.getEntriesByType('resource');
      const css = resources.filter(x => x.initiatorType === 'link' &&
        x.name.includes('.css'));
      return {
        fcp_ms: paint?.startTime ?? null,
        lcp_ms: state.lcp ?? null,
        cls: state.cls ?? null,
        ttfb_ms: nav ? nav.responseStart - nav.requestStart : null,
        page_load_ms: nav?.loadEventEnd || null,
        css_transfer_bytes: css.reduce((n, r) => n + r.transferSize, 0),
        total_transfer_bytes: (nav?.transferSize || 0) +
           resources.reduce((n, r) => n + r.transferSize, 0),
      };
    }""")
    snapshot["css_requests"] = len(css_responses)
    return snapshot


def run_single(browser, origin: str, route: str, *, css_file: Path | None,
               screenshot: Path | None, cpu_rate: int, latency_ms: int,
               download_kbps: int, enable_a11y: bool) -> dict:
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        device_scale_factor=1, is_mobile=True, has_touch=True,
        reduced_motion="reduce")
    page = context.new_page()
    page.add_init_script(INIT_JS)
    session = context.new_cdp_session(page)
    session.send("Network.enable")
    session.send("Network.emulateNetworkConditions", {
        **NETWORK, "latency": latency_ms,
        "downloadThroughput": download_kbps * 1000 / 8})
    session.send("Emulation.setCPUThrottlingRate", {"rate": cpu_rate})
    css_responses = []
    failed_requests = []
    page_errors = []
    page.on("response", lambda response: css_responses.append(response)
            if response.request.resource_type == "stylesheet" else None)
    page.on("requestfailed", lambda req: failed_requests.append(req.url))
    page.on("pageerror", lambda err: page_errors.append(str(err)))
    stats = {}
    try:
        for cache in ("cold", "warm"):
            css_responses.clear()
            response = page.goto(origin + route, wait_until="load", timeout=60000)
            if response is None or not response.ok:
                raise RuntimeError(f"{route} navigation HTTP {response.status if response else 'missing'}")
            page.evaluate("() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
            # Allow LCP observer to collect the final painted eager hero.
            page.wait_for_timeout(100)
            stats[cache] = page_metrics(page, css_responses)
            if cache == "cold":
                stats["headers"] = audit_headers(response.headers)
                stats["css_headers"] = {
                    item.url.split("/")[-1]: audit_headers(item.headers)
                    for item in css_responses
                    if item.url.startswith(origin)}
                stats["layout"] = page.evaluate("""() => ({
                    horizontal_overflow_px:
                      document.documentElement.scrollWidth - document.documentElement.clientWidth,
                    main_count: document.querySelectorAll('main').length,
                    h1_count: document.querySelectorAll('h1').length,
                    scripts: document.querySelectorAll('script').length,
                    inline_styles: document.querySelectorAll('[style]').length,
                    stylesheet_links: document.querySelectorAll('link[rel=stylesheet]').length,
                })""")
        if screenshot:
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot), animations="disabled", full_page=True)
        stats["failed_requests"] = failed_requests
        stats["page_errors"] = page_errors
        if enable_a11y and css_file:
            page.add_script_tag(path=str(css_file))
            # Developer-injected axe is not an application dependency.
            axe_result = page.evaluate("""async () => axe.run(document, {
              runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21aa','wcag22aa']}
            })""")
            stats["axe"] = {
                "violations": [
                    {"id": item["id"], "impact": item.get("impact"),
                     "nodes": [node["target"] for node in item["nodes"]]}
                    for item in axe_result["violations"]
                ],
                "incomplete": [item["id"] for item in axe_result["incomplete"]],
                "passes": len(axe_result["passes"]),
            }
        return stats
    finally:
        context.close()


def run(origin: str, runs: int, *, axe_file: Path | None, screenshot_dir: Path | None,
        cpu_rate: int, latency_ms: int, download_kbps: int) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Install Playwright in an optional developer environment") from exc
    report = {
        "origin": origin,
        "profile": {"viewport": "390x844", "cpu_rate": cpu_rate,
                    "rtt_ms": latency_ms, "download_kbps": download_kbps,
                    "note": "Synthetic, not field Core Web Vitals or actual phone/network conditions"},
        "runs_per_route": runs,
        "routes": [],
    }
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            for route in ROUTES:
                records = []
                axe = None
                for i in range(runs):
                    screen = (screenshot_dir / (route.strip("/").replace("/", "-") + ".png")
                              if i == 0 and screenshot_dir else None)
                    record = run_single(browser, origin, route, css_file=axe_file,
                                        screenshot=screen, cpu_rate=cpu_rate,
                                        latency_ms=latency_ms,
                                        download_kbps=download_kbps,
                                        enable_a11y=i == 0)
                    if i == 0:
                        axe = record.get("axe")
                    records.append(record)
                report["routes"].append({
                    "path": route, "headers": records[0]["headers"],
                    "css_headers": records[0]["css_headers"],
                    "layout": records[0]["layout"],
                    "cold": summarize([r["cold"] for r in records]),
                    "warm": summarize([r["warm"] for r in records]),
                    "axe": axe,
                    "request_failures": sum(len(r["failed_requests"]) for r in records),
                    "page_errors": sorted(set(e for r in records for e in r["page_errors"])),
                })
        finally:
            browser.close()
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default="https://syntyr-css.pages.dev")
    parser.add_argument("--runs", type=int, default=7)
    parser.add_argument("--cpu-rate", type=int, default=4)
    parser.add_argument("--latency-ms", type=int, default=150)
    parser.add_argument("--download-kbps", type=int, default=1600)
    parser.add_argument("--axe-file", type=Path)
    parser.add_argument("--screenshots", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if (args.runs < 1 or args.runs > 30 or args.cpu_rate < 1 or args.cpu_rate > 20
            or args.latency_ms < 0 or args.latency_ms > 2000
            or args.download_kbps < 64 or args.download_kbps > 100000):
        parser.error("Invalid performance profile or run count")
    if args.axe_file and not args.axe_file.is_file():
        parser.error("Axe must be an existing, local JavaScript file")
    try:
        origin = validate_origin(args.origin)
        results = run(origin, args.runs, axe_file=args.axe_file,
                      screenshot_dir=args.screenshots, cpu_rate=args.cpu_rate,
                      latency_ms=args.latency_ms,
                      download_kbps=args.download_kbps)
    except (RuntimeError, OSError, ValueError) as exc:
        parser.error(str(exc))
    body = json.dumps(results, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(body, end="")


if __name__ == "__main__":
    main()
