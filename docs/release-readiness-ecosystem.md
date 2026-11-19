# Ecosystem distribution release readiness — 15 November 2026

Preparation completed; **no npm, VS Code Marketplace or Figma Community
publication was performed**.

## npm / @syntyr/css

- `npm pack --dry-run --json --ignore-scripts`: succeeded with 17 allowlisted
  files, including the optional Tailwind and shadcn CSS bridges; 46,386-byte
  package at time of verification.
- Public `npm view @syntyr/css version`: returned E404 (no publicly
  retrievable release at the time checked). This is **not proof of reserved
  ownership or confirmed future availability**.
- `npm whoami` on Gertrude: ENEEDAUTH. Registry publishing is blocked until
  the authorized owner authenticates and verifies scoped-package rights.
- `package.json` contains no application runtime dependencies. Do not
  combine the new CSS bridge with the default package entrypoint implicitly.
- Required release owner checks: verified registry control, package name,
  version/tag consistency, audit of tarball contents, release approval and
  account 2FA/token policy. No secret should be copied into Git.

## VS Code

- Local VSIX package succeeds via `@vscode/vsce package --no-dependencies`
  (8 files in the local preview).
- `integrations/vscode/package.json` uses placeholder publisher
  `syntyr-local`. VS Code Marketplace publisher ownership has **not** been
  established, and no Marketplace publication has been attempted.
- Publisher identity, manifest branding, listing metadata, extension logo
  rights, public changelog and install-time completion tests remain release
  gates. Preserve the extension-host-free metadata approach.

## Figma

- Editable kit exists at
  https://www.figma.com/design/Lj8uKUtgJfXMyzVb96x5Q1 .
- Figma Starter caps each variable collection at one mode; seven separate
  collections are in the file, not seven switchable modes.
- The design kit contains additional native component variants but requires
  parity/accessibility review. The Figma MCP quota was exhausted before
  completing those checks.

## Safe next action

Merge only after PR checks and review. Publish the npm package and editor
extension in separately approved, authenticated release operations. Never
label a Figma kit or VSIX as published merely because an export/package
was produced locally.
