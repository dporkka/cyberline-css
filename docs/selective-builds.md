# Optional selective CSS builds

Syntyr ships ready-to-use CSS. **A build step is never required.** If an application
uses only a few components, the developer-only Python standard-library script
can compose a deterministic stylesheet from explicit source modules.

```sh
python3 scripts/build_selective.py \
  --components buttons,forms \
  --modules semantic,print \
  --output ./build/syntyr.custom.css \
  --report ./build/syntyr.custom.json
```

The script includes **tokens and base styles** automatically. Without
`--components`, it includes every core component; without `--modules`,
it includes no optional modules. Pass `--components none` to exclude all
core components. Any selection keeps canonical source/cascade order.

The component names are `layout`, `typography`, `buttons`, `forms`,
`form-composition`, `overlays`, `data`, and `patterns`. Selecting
`form-composition` also includes the required base `forms` module.
Optional module names are taken from the standard distribution registry,
including `semantic`, `recipes`, `geometry`, `symbols`, `effects`,
`viz`, `utilities`, and `print`.

## Intentional limits

- **No automatic class scanning or selector purging.** Template engines,
  HTMX, React, Rust, Go, and dynamically constructed class names make
  source-level inference incomplete. Select modules deliberately.
- There is no arbitrary CSS size gate. The optional JSON report provides
  deterministic raw and gzip sizes, plus the list of included source files.
- Generated CSS can be self-hosted anywhere, but the tool refuses to
  overwrite Syntyr's checked-in `src/` and `dist/` files.
- Some optional recipes refer to component classes. Include those
  components explicitly when your pages need their styling.
- No JavaScript, npm, CSS parser, minifier, or remote API is involved.
  Standard `python3 scripts/build.py --check` and versioned release assets
  remain unchanged.

This is **whole-file composition**, not automatic detection of unused CSS.
For most applications, the released `syntyr.core.css` and opt-in stylesheets
are simpler to maintain than a custom build.
