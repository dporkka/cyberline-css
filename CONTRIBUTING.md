# Contributing to Syntyr CSS

Thank you for helping make Syntyr more useful and reliable. Syntyr is an
MIT-licensed, **CSS-first** design system. Changes should improve native HTML
and CSS without requiring a JavaScript runtime, package manager, remote assets,
or framework-specific component package.

## Before proposing changes

- Search the existing issues and pull requests to avoid duplicating work.
- Start from the current `main` branch, use a focused feature branch, and
  describe the user-facing behavior, compatibility impact, and test evidence.
- Follow [ARCHITECTURE.md](ARCHITECTURE.md) and
  [docs/api-stability.md](docs/api-stability.md). Document changes to the
  `syn-*` class API, `--syn-*` variables, and `data-syn-*` attributes.
- Do not assume the unreleased alpha.5 source candidate's features exist
  in the published immutable alpha.4 stylesheet. Do not overwrite a tagged
  release when fixing a prerelease bug.
- Use original work or assets with documented permission and attribution.
  A visual reference does not authorize copying a third-party design system.

## Source and generated files

Edit `src/*.css` and `src/components/*.css`. The Python standard-library
build scripts produce the checked-in `dist/` assets; do not hand-edit built
stylesheets. Preserve scoped `.syn-root` behavior, opt-in semantic styling,
accessibility states, and the separation of core and optional modules.

Documentation changes must keep the curated `llms.txt` index discoverable
when relevant, then regenerate `llms-full.txt` using the repo's script.
For public guide changes, edit the Markdown source, update the explicit
`PUBLIC_DOCS` allowlist in `scripts/build_cloudflare_site.py` for new guides,
and run `python3 scripts/build_doc_pages.py` to regenerate the committed HTML
and documentation index. This requires the **maintainer-only** dependency in
`requirements-docs.txt`. Run `python3 scripts/build_doc_pages.py --check`
to detect stale HTML, and rebuild `llms-full.txt` with
`python3 scripts/build_agent_docs.py`. Check browser navigation and local
relative links; do not maintain duplicate hand-written HTML for guides.

Public documentation and examples require deliberate updates to the
Cloudflare site allowlist; never publish internal test artifacts, credentials,
business notes, or entire source directories.

## Verify a proposed change

From the repository root, with Python 3 installed:

```sh
python3 scripts/build.py
python3 scripts/build.py --check
python3 scripts/export_api_metadata.py --check
python3 scripts/build_agent_docs.py
python3 scripts/build_agent_docs.py --check
python3 -m unittest discover -s tests -v
python3 scripts/build_cloudflare_site.py
python3 scripts/build_cloudflare_site.py --check
python3 scripts/package_release.py
```

After committing regenerated `dist/` artifacts, verify the checked-in
distribution matches the generated files:

```sh
git status --porcelain -- dist/
```

This must produce **no output**. A successful `build.py --check` run after
`build.py` alone is insufficient: the first command may have already
rewritten files you forgot to commit.

If you changed optional integrations, also check the relevant export scripts
and tests documented in their guides. Browser tests use optional Playwright
and browser engines **only in development or CI**; consumers do not install
these tools. See [docs/accessibility.md](docs/accessibility.md) for browser,
reflow, keyboard, focus, screen-reader and contrast checks.

For behavior changes, add a regression test that fails before the fix,
then verify it passes afterward. Report any unrun or unavailable browser
engines explicitly. A clean automated axe result is not a WCAG certification.

## Review and release

Use the actual current-head Woodpecker quality and merge checks before
merging; a passing stale branch or a YAML file is not execution evidence.
Document unresolved accessibility, compatibility, and review concerns.
Release publication, naming clearance, and commercial licensing are separate
decisions from accepting an MIT code contribution.

**For vulnerabilities**, do not file a public issue containing exploit
details; follow [SECURITY.md](SECURITY.md) instead.
