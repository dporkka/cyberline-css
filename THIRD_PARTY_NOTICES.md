# Third-party notices

Syntyr core CSS and its original markup, Python scripts, and tests are MIT-licensed and do not require third-party runtime libraries. The **optional static documentation playground** now ships a separately built CodeMirror 6 HTML editor in `docs/playground-editor.js` only. That browser bundle contains CodeMirror, Lezer, and supporting MIT-licensed packages; the complete third-party copyright and permission notices are published in [`docs/playground-editor.licenses.txt`](docs/playground-editor.licenses.txt). The editor is not part of Syntyr core CSS, its npm package exports, or the premium component library. The isolated build and exact dependency lockfile live under `tools/playground-editor/`.

Pico CSS, Chota, Open Props, Tailwind CSS, and Tailwind Plus are *design research references only*. No code has been copied from them. For any future ports, add the relevant source files and preserve the required copyright and license notices here.

Tailwind Plus is proprietary commercial source; no Tailwind Plus code, component markup, screenshots, images, icons, or templates have been copied. General layout ideas and the publicly documented commercial packaging model are referenced in `docs/tailwind-research.md`.
