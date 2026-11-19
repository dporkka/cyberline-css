# Syntyr commercialization strategy — working hypothesis, November 2026

**Core license: MIT, permanently for versions already released under MIT.** The entire public CSS component system, its accessibility fixes, its Grid and Noir themes, the gallery, and the example pages remain free to use, fork, embed, redistribute, and commercialize, subject only to the MIT notice condition. Do not add licensing checks, telemetry, API keys, phone-home behavior, or paid-only runtime requirements to the open-source package.

## Positioning

> Futuristic UI without the frontend framework: accessible, semantic, zero-runtime-JavaScript styling for server-rendered HTML, Go/templ, HTMX, Astro, React and static sites.

The design alone is easy to imitate. Buyers pay for **complete production-shaped page designs** and time saved integrating them into real products, not for a handful of CSS variables. The strongest initial niche is a modern cyberpunk SaaS/operations dashboard or developer-tool marketing site where the common alternatives are React/Tailwind dependent. Avoid describing it as an official TRON or Blade Runner product. Grid/Noir themes are original and non-affiliated.

## Free versus paid: clear contract

| Always free, MIT | Potentially paid, separately authored and licensed |
| --- | --- |
| Base CSS, tokens, all essential components | Finished 8–15 page HTML dashboard kit with sample data and complete layouts |
| Grid and Noir palettes | Additional original theme collections and page-level visual systems |
| Semantic mode, forms, tables, navigation, overlays | Premium hero, pricing, onboarding, settings, billing, CRM and analytics *layouts* |
| Accessibility and compatibility improvements | Figma UI kit, carefully produced icon/illustration assets if owned/licensed |
| Baseline documentation and starter examples | Ready-made Go/templ, Astro, static HTML, and HTMX starter applications |
| Community support and bug reports | Contract support, customization, integration and training |

Do **not** charge users for a missing keyboard fix, HTML semantics, security patch, or maintenance of MIT APIs. Premium value should be composition and workflow completeness, not crippled primitives.

## First product (validate before building a catalog)

**Syntyr Console Kit**: one cohesive, original, polished, paid dashboard pack: overview, list/detail, filters, settings, analytics, empty/loading/error states, login, billing, and mobile layouts. Two theme variations. Ship HTML/CSS first with an optional Go/templ edition if buyers request it. No JavaScript should be *required for its presentation*; actual data filtering, authentication and mutation need application logic. Add example design tokens and dark/light contrast evidence.

A second product only if there is demand: **Syntyr Launch Kit** for developer tools, security companies, AI/robotics sites, games (landing, docs, pricing, changelog, contact).

## Proposed price tests (USD, NOT verified demand or current sale listings)

| Offer | Pilot price | Fulfillment | Conditions |
| --- | ---: | --- | --- |
| MIT core | $0 | Download / GitHub | No signup, unrestricted commercial use under MIT |
| Console Kit pilot (after readiness gates) | $59 | Proposed one-time purchase; NOT for sale | 1 named developer, unlimited end products, 12 months updates (terms still under review) |
| Console Kit regular | $99 | Later price hypothesis, not launched | Test only after actual pilot buyers and integration feedback |
| Studio multi-kit bundle | Deferred | Do not list for purchase | Only worth offering if multiple distinct paid products ship |
| Team license | $249 candidate | Deferred | Test if actual teams request multi-developer use |
| Implementation / custom theme | Quote individually (often $1,500+) | Scoped service agreement | Separate quote, clear deliverables, IP and support terms |

Use perpetual rights for purchased *versions* while keeping updates time-limited rather than promising lifetime maintenance. Team pricing and support can change after validation. Business/service clients may value a $1,500+ scoped integration more than dozens of low-ticket kit sales; actual quotes depend on scope.

See [commercial launch gates](commercial-launch-gates.md) for the current publication, qualification, accessibility and pre-sale requirements. No price hypothesis represents an available product or verified willingness to pay.

## Revenue math, not a forecast

At $59 per kit and 2% **qualified visitor-to-purchase** conversion, 35 monthly sales yield $2,065 gross and require about 1,750 qualified landing-page visitors/month. To approach $10,000 gross at a hypothetical $99 standard-kit price takes 102 monthly orders and ~5,100 qualified visitors at 2%. These are hypothetical conversion rates and *exclude refunds, taxes, processing fees, paid acquisition, support, and time spent producing products*. A new niche brand may convert substantially worse. Do not treat this as near-term reliable recurring income.

## Distribution channels to test

1. A free live, no-JS gallery with a fast Lighthouse score; clear MIT GitHub link and buyable demo screenshots/preview of the paid kit.
2. Developer-oriented search pages demonstrating `HTML + CSS`, `HTMX + Go/templ`, `Astro`, and `cyberpunk dashboard CSS`, each with a usable free example, not generic SEO filler.
3. Publish technically substantive examples: keyboard navigation, native dialogs, CSS layer overrides, and performance comparisons against a *clearly identified* alternative with reproducible methodology.
4. Relevant developer communities and GitHub discovery, respecting community self-promotion policies. Do not build a viral content machine before repeatable paid demand.
5. Direct developer-tool/indie-SaaS design services for early cash and design-partner feedback.

## Competitive benchmark context

Tailwind Plus historically sold for $299 one-time, but **new customer signups closed on September 9, 2026**, when Tailwind Labs announced it was joining Shopify. It is not a live purchasable pricing anchor. Shadcnblocks and Preline are category comparisons, not verified evidence of Syntyr willingness to pay; always recheck current prices before making customer-facing claims. Sources:
- https://tailwindcss.com/blog/tailwind-is-joining-shopify
- https://www.shadcnblocks.com/pricing
- https://preline.co/pricing/

## Why not subscriptions or paid core?

A monthly subscription for CSS files creates retention pressure and license complexity without ongoing hosted value. A hosted theme editor or commercial support retainer could justify recurring charges *after* a real usage pattern emerges. MIT cannot be retroactively withdrawn from already released versions. Premium assets must not contain copied MIT code with conflicting license claims: the original MIT library stays MIT within any paid kit, with required notices; only separable original premium content uses the commercial license.

## Decision rules

- Build one paid kit, not an entire marketplace; seek at least 10 actual paid preorders or similarly strong commitments before building dozens of premium screens.
- If 30 qualified demos generate no concrete intent, interview buyers and reconsider the niche/offer.
- Do not launch subscriptions, client-side license validation, or license-management infrastructure for downloadable kits in v0.x.
- Favor direct service revenue if the audience is too small; open source can be a credibility and acquisition tool, not necessarily the primary income generator.
