# Real shadcn/ui + Syntyr React compatibility fixture

Generated using the official shadcn CLI's Vite project template with
`--base radix`, then the app was updated to opt into Syntyr in a scoped
`.syn-root.syn-shadcn` region. The UI button in
`src/components/ui/button.tsx` is **CLI-generated shadcn source**,
including Radix's `Slot.Root` implementation for `asChild`.

This optional fixture intentionally does **not** add React, Radix, Tailwind,
or Vite to Syntyr's core CSS package. After generating the real Button source,
the scaffold was reduced to dependencies required to build and run this example
(not the shadcn CLI or unused ESLint/animation utilities). The example's
production/development dependency audit reported **zero vulnerabilities** on
15 November 2026; recheck before upgrading.

```sh
cd examples/syntyr-shadcn-react
npm install
npm run build
npm run dev
```

The fixture uses `"@syntyr/css": "file:../.."` until a real package
release is published. Browser tests should verify Studio, nested Noir,
click handlers, Radix `asChild` semantics, disabled states, and scoped
host isolation.

This example validates one generated button implementation and does
**not** certify all shadcn/ui components or overlay portals. Components
portaled to document.body need explicit scoping/container handling.
