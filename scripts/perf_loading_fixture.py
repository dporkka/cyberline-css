"""Generate an offline, route-specific CSS loading experiment (stdlib only).

Usage:
  python3 scripts/perf_loading_fixture.py --output /tmp/syntyr-loading-fixture
  cd /tmp/syntyr-loading-fixture && python3 -m http.server 8954

Three variants use identical DOM and assets:
- baseline: regular Syntyr core + recipes CSS links
- selective: one smaller, module-selected external stylesheet
- inline: precisely the same selective stylesheet inlined in <head>

The inline variant is NOT a browser-extracted minimal critical CSS subset.
It is a repeatable route-specific inlining experiment, not production advice.
No JavaScript is used by any variant.
"""
from __future__ import annotations

import argparse
import gzip
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import time
import json
from pathlib import Path
import shutil

from build import ROOT, assemble
from build_selective import choose_sources

CORE_LINK = '<link rel="stylesheet" href="../dist/syntyr.core.css">'
RECIPES_LINK = '<link rel="stylesheet" href="../dist/syntyr.recipes.css">'


def generate(output: Path) -> dict:
    output = output.expanduser()
    if output.is_symlink():
        raise ValueError("Cannot write through a symlink output directory")
    output = output.resolve()
    if output == ROOT or ROOT in output.parents:
        raise ValueError("Experiment output must be outside repository")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Experiment output must be empty (use a new directory)")
    template = (ROOT / "examples/performance-first.html").read_text(encoding="utf-8")
    assert template.count(CORE_LINK) == 1 and template.count(RECIPES_LINK) == 1
    paths = choose_sources(components="layout,typography,buttons", modules="recipes")
    selected = assemble(paths)
    if "</style" in selected.lower():
        raise ValueError("Cannot safely inline a CSS string containing a style close tag")

    shared = template.replace("../assets/og-syntyr.png", "assets/og-syntyr.png")
    shared = shared.replace("../docs/previews/studio-overview.webp", "previews/studio-overview.webp")
    # Remaining hyperlinks are documentation navigation; the identical body is
    # deliberately shared, rather than used to compare functional navigation.
    baseline = shared.replace("../dist/", "dist/")
    selective = baseline.replace(
        '<link rel="stylesheet" href="dist/syntyr.core.css">\n  '
        '<link rel="stylesheet" href="dist/syntyr.recipes.css">',
        '<link rel="stylesheet" href="dist/syntyr.route.css">')
    if selective == baseline or "syntyr.core.css" in selective:
        raise ValueError("Could not replace the two baseline stylesheet links")
    inline = selective.replace(
        '<link rel="stylesheet" href="dist/syntyr.route.css">',
        '<style data-syn-experiment="inline">' + selected + '</style>')
    output.mkdir(parents=True, exist_ok=True)
    (output / "dist").mkdir()
    (output / "assets").mkdir()
    (output / "previews").mkdir()
    for filename, html in (("baseline.html", baseline),
                           ("selective.html", selective),
                           ("inline.html", inline)):
        (output / filename).write_text(html, encoding="utf-8")
    for name in ("syntyr.core.css", "syntyr.recipes.css"):
        shutil.copyfile(ROOT / "dist" / name, output / "dist" / name)
    (output / "dist/syntyr.route.css").write_text(selected, encoding="utf-8")
    shutil.copyfile(ROOT / "assets/og-syntyr.png", output / "assets/og-syntyr.png")
    shutil.copyfile(ROOT / "docs/previews/studio-overview.webp",
                    output / "previews/studio-overview.webp")
    baseline_css = (ROOT / "dist/syntyr.core.css").read_bytes() + (ROOT / "dist/syntyr.recipes.css").read_bytes()
    report = {
        "experiment": "route-selective-vs-inline",
        "source_modules": list(paths),
        "bytes": {
            "baseline_css_raw": len(baseline_css),
            "baseline_css_gzip_sum": sum(len(gzip.compress((ROOT / "dist" / name).read_bytes(), mtime=0))
                                         for name in ("syntyr.core.css", "syntyr.recipes.css")),
            "selective_css_raw": len(selected.encode("utf-8")),
            "selective_css_gzip": len(gzip.compress(selected.encode("utf-8"), mtime=0)),
            "baseline_html_raw": len(baseline.encode("utf-8")),
            "inline_html_raw": len(inline.encode("utf-8")),
        },
        "caveat": "Route-specific whole stylesheet, not automatic critical CSS extraction",
    }
    (output / "fixture.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def make_handler(output: Path, *, css_delay_ms: int = 0):
    """Local-only experiment server; gzip + realistic HTML/CSS caching.

    Every HTML visit transfers a fresh document. CSS assets can be reused from
    the same browser context. A deliberate CSS delay models request latency,
    not real packet loss or network throughput.
    """
    if css_delay_ms < 0 or css_delay_ms > 3000:
        raise ValueError("CSS delay must be between 0 and 3000 ms")

    class ExperimentHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(output), **kwargs)

        def do_GET(self):
            request_path = self.path.split("?", 1)[0]
            is_css = request_path.endswith(".css")
            is_html = request_path.endswith(".html")
            if not (is_css or is_html):
                return super().do_GET()
            file = Path(self.translate_path(self.path))
            if not file.is_file():
                self.send_error(404)
                return
            if is_css and css_delay_ms:
                time.sleep(css_delay_ms / 1000)
            content = file.read_bytes()
            gzip_ok = "gzip" in self.headers.get("Accept-Encoding", "")
            payload = gzip.compress(content, mtime=0) if gzip_ok else content
            self.send_response(200)
            self.send_header("Content-Type", "text/css" if is_css else "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            if gzip_ok:
                self.send_header("Content-Encoding", "gzip")
                self.send_header("Vary", "Accept-Encoding")
            self.send_header("Cache-Control", "public, max-age=86400" if is_css else "no-store")
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format, *args):
            pass

    return ExperimentHandler


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--serve", action="store_true",
                        help="serve generated files on loopback for browser tests")
    parser.add_argument("--port", type=int, default=8955)
    parser.add_argument("--css-delay-ms", type=int, default=0,
                        help="optional artificial delay on uncached CSS requests")
    args = parser.parse_args()
    try:
        if args.serve:
            if not args.output.is_dir() or not (args.output / "fixture.json").is_file():
                raise ValueError("Generate the fixture first, then start --serve")
            if args.port < 1 or args.port > 65535:
                raise ValueError("Invalid port")
            handler = make_handler(args.output, css_delay_ms=args.css_delay_ms)
            with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
                print(f"Experiment server http://127.0.0.1:{args.port}/; CSS delay {args.css_delay_ms} ms", flush=True)
                server.serve_forever()
        else:
            print(json.dumps(generate(args.output), indent=2))
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
