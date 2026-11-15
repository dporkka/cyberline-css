# Syntyr multi-page business website starter

Four original, copy-owned HTML pages and one application-specific stylesheet. Uses MIT Syntyr core + recipes; no Node, JavaScript, external fonts, API calls, images or build step. Fictional Northstar Systems company and stories are placeholders, not real offers or verified results.

## Preview

From the repository root:

```sh
python3 -m http.server 8000
```

Visit `http://localhost:8000/examples/business-starter/index.html`. The pages may also be opened as local files with relative CSS intact. To use in another project, copy `examples/business-starter` and `dist/syntyr.core.css` plus `dist/syntyr.recipes.css`, preserving paths or rewriting CSS link URLs.

## What is real and what needs work

- Home, services, case study and contact **navigate as ordinary links**. Active-page labels, headings, anchor targets and responsive layout are real.
- All brand names, services, customers and stories are fictional. No fabricated proof, testimonials, logos or claims should be retained in a deployed business website. Supply actual services, verifiable evidence, contact details, policies and terms.
- The contact form is intentionally disabled and has **no action**. Before enabling it, implement a genuine endpoint with server-side validation, CSRF checks for session-based submissions, bot/rate controls, privacy/retention policy, spam handling, error summary/focus behavior, successful confirmation and observable delivery. Do not ship a form pretending to work.
- Review unique titles/descriptions, canonical URLs, Open Graph/structured data, and sitemap entries for your real domain. The Syntyr gallery explicitly marks these **fictional demo pages noindex**, rather than publishing false business pages into search.
- Review responsive behavior at 320–1440px, keyboard access, 200%/400% zoom, high contrast/forced-colors, mobile browser accessibility and screen readers with your real content.

## Customize

Edit HTML text and `site.css` for your company; use Syntyr tokens (`--syn-*`) for colors, spacing, and density. The default Studio theme is intentionally restrained. Change the root `data-syn-theme` to another available Syntyr theme if warranted, then revalidate contrast and content reflow.

Run checks from repository root: `python3 -m unittest discover -s tests -p test_business_site_starter.py -v`. For optional developer-only browser verification with locally installed Playwright engines, run `python3 tests/business_site_browser.py --browsers chromium,firefox,webkit`. Test infrastructure is never a consumer/runtime dependency. Core CSS and JS-free Syntyr runtime remain unchanged.

License: MIT (same as Syntyr CSS); original HTML and site.css may be freely modified and shipped.
