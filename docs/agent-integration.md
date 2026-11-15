# Using Syntyr with coding agents

Syntyr works with ChatGPT, Codex, Claude Code, Cursor and other agents that generate HTML or framework markup. No Syntyr-specific service, account, MCP server or runtime JavaScript is required.

## Recommended context to supply an agent

1. Specify **the exact Syntyr release and CSS modules installed** (published `0.3.0-alpha.4` versus unreleased source `0.3.0-alpha.5`).
2. Link to [AI quickstart](ai-quickstart.md) and the relevant [component reference](components.md). If the agent can fetch websites, include [`/llms.txt`](../llms.txt).
3. For complex UI, supply [recipes](recipes.md), [framework integrations](framework-integrations.md) and the [component manifest](../metadata/components.json). For unreleased alpha.5 source-only form patterns, use [copy-owned form recipes](component-recipes.md) and the optional [Radix styling adapter](radix-integration.md); do not attribute these to published alpha.4.
4. Ask it to state which stylesheets it used, avoid undocumented classes and verify keyboard/form semantics.

Suggested prompt for an existing application:

> Use Syntyr CSS to build a responsive, accessible account dashboard. My app uses the published v0.3.0-alpha.4 core and recipes CSS, with Studio as the theme. Read the Syntyr AI quickstart and relevant component docs. Generate semantic HTML compatible with my framework. Use only classes present in those stylesheets; if a needed component is unavailable, compose native HTML with application CSS instead. Keep data, auth and actions in the host app. Return the necessary markup, CSS links and a list of any custom styles.

## Project-level integration

A consumer may copy [`agents/syntyr/SKILL.md`](../agents/syntyr/SKILL.md) as an optional local skill in agent tooling that supports Skills. It is a portable instruction document, **not a published package, automatic installation, or guaranteed discovery mechanism**.

The repository's root `AGENTS.md` guides agents contributing to Syntyr itself. It does **not** automatically become instructions in a separate application repository.

## Optional local MCP adapter

An optional **read-only local MCP server** can now expose the checked-in
component catalog and CSS API to supported coding agents. It is not needed to
use Syntyr CSS, is not installed by the npm package, and does not expose a
hosted endpoint. See the [MCP adapter source and installation guide](https://github.com/dporkka/syntyr-css/tree/main/agent_mcp)
for the separate Python SDK installation, version-safe tools, and limits.
It defaults to the published immutable `0.3.0-alpha.4` CSS rather than
silently offering source-only `0.3.0-alpha.5` selectors. The read-only
`validate_markup` tool reuses the [static checker](editor-integration.md#optional-static-html-diagnostics)
for source-located, machine-readable errors, available class suggestions, and
valid theme/state values. Responses are constrained to the selected release's
checked-in CSS rather than presenting candidate-only selectors as fixes.

## Documents and machine-readable inventory

- [`llms.txt`](../llms.txt): small navigation file following the community `llms.txt` convention; it is useful when deliberately retrieved, but not a universal automatic-discovery protocol.
- [`llms-full.txt`](../llms-full.txt): generated, version-stamped concatenation of selected public technical docs, for tools that benefit from one context file.
- [`metadata/components.json`](../metadata/components.json): small **curated, non-exhaustive** inventory with the CSS modules required by the included classes. Do not infer that a class is unavailable solely because this catalog omits it.
- [`metadata/syntyr-contract.json`](../metadata/syntyr-contract.json): full source-discovered Syntyr classes, tokens, known stylesheet distributions, themes, literal state values and curated component recipes. This candidate-version manifest is suitable for LLM tooling and optional [static HTML checks](editor-integration.md#optional-static-html-diagnostics); it is not a compiler or an accessibility certification.

Documentation follows the current source candidate; always check [release boundaries](api-stability.md) and the [distribution guide](distribution.md) before using candidate-only features.

## Documentation formats: HTML for people, Markdown for agents

Every approved public guide is published at two stable paths. Use the readable HTML page (for example, [`/docs/components.html`](components.html)) in browser navigation, search results and links to end users. Use the original Markdown (`/docs/components.md`) for coding-agent retrieval, repository editing and `llms.txt` references. The [complete HTML guide directory](reference.html) is the human entry point. Both formats contain the same authored guide content; the HTML is rendered ahead of time, not by client-side JavaScript.

These are **different representations of the same public documentation**, not user-agent cloaking. Anyone can request Markdown directly; agents can also read HTML. Markdown responses have a `text/markdown` content type and `X-Robots-Tag: noindex` so search engines favor HTML, while `robots.txt` and the sitemap advertise public HTML pages. Do not disallow Markdown in `robots.txt`: agents need to fetch it explicitly. HTML has canonical URLs and points back to its Markdown source via `rel="alternate" type="text/markdown"`.

When adding a guide for public consumption, review the explicit `PUBLIC_DOCS` allowlist in `scripts/build_cloudflare_site.py`. Regenerate the committed HTML with the maintainer-only generator (`python3 scripts/build_doc_pages.py`), and verify it with `--check`. The core static-site and CI builds require no Markdown parsing package or client runtime.

## Validation and maintenance

The repository uses Python standard-library scripts:

```sh
python3 scripts/build_agent_docs.py --check
python3 scripts/build.py --check
python3 -m unittest discover -s tests -v
python3 scripts/build_cloudflare_site.py --check
```

The consolidated reference is deterministic and checked in CI through the Python test suite. The Cloudflare publisher uses a strict allowlist, so exposing new documentation does not expose internal files or business planning documents.

## What Syntyr does not do

Syntyr styles browser HTML/CSS. It does not supply a JavaScript component runtime, chart rendering engine, AI API, CRUD handlers, form submission or remote data access. The optional local read-only MCP adapter is a separate developer tool, never a CSS runtime dependency. Use your existing application technology for those responsibilities.

## Complete pages from existing validated blocks (alpha.5 source)

The versioned **source candidate**, not published alpha.4, contains
[`metadata/agent-compositions.json`](../metadata/agent-compositions.json): two
small, agent-readable page recipes. Each references existing MIT-licensed block
IDs in [`blocks/manifest.json`](https://github.com/dporkka/syntyr-css/blob/main/blocks/manifest.json), rather than
introducing a second CSS class vocabulary. The checked-in deterministic
builder derives CSS modules directly from each block's metadata and removes
per-block fixed Studio themes so the page root controls the palette.

The examples can be copied or adapted in any framework:

- [Operations dashboard](../examples/composition-operations-dashboard.html):
  KPIs, server-ready GET filter form, accessible records table, activity feed.
- [Product marketing](../examples/composition-product-marketing.html):
  hero, feature grid, illustrative pricing and FAQ disclosures.

To rebuild and validate **locally**, using only Python's standard library:

```sh
python3 scripts/build_agent_compositions.py --check
python3 scripts/syntyr_check.py examples/composition-*.html
python3 -m unittest discover -s tests -p 'test_design_lab_compositions.py'
```

For an AI coding agent: load this manifest and the referenced
`blocks/snippets/<block-id>.html` files, derive the required stylesheets
from `blocks/manifest.json`, and choose one page-level theme. Start from the
corresponding full-page example, but preserve unique IDs and label references.
After changing markup, run `syntyr_check.py` with the **actual installed**
stylesheets; verify interactive behavior with browser tests. Replace example
routes, illustrative data and checkout links with real handlers. Do not claim
that these static compositions implement filtering, analytics or payments.

The [Design Lab](playground.html) compares the same editable HTML under two
palettes at exact CSS viewport widths. Its JavaScript and iframe previews are
**docs-only**, and the CSS core remains JS-free. It is for design exploration,
not a substitute for end-to-end host-application testing.
