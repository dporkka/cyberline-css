# Syntyr + shadcn/ui token compatibility

This is **a scoped semantic-token interoperability fixture**, not a copy of
shadcn/ui components and not a claim of complete shadcn compatibility.

Run against the local Syntyr source:
```sh
npm install
npm run build
python3 -m http.server 8000
```

The host app keeps its Tailwind + shadcn `@theme inline` mappings. Load
`@syntyr/css/shadcn.css` after Syntyr core, and add `syn-shadcn` only to the
region you want to theme. The bridge maps standard shadcn semantic roles to
scoped Syntyr variables. Nested `data-syn-theme` regions rebind aliases.
No global `:root`, `.dark`, reset, or runtime JS changes.

This fixture exercises generated shadcn-style Tailwind classes, not a live
React/Radix/shadcn component. Test actual production components, portals,
contrast, keyboard states and CSS layer order in the host before adoption.
