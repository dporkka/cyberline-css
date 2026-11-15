# Syntyr block installer: runnable Go consumer

An original, minimal **Go standard-library** app that adapts the free
`metric-overview` HTML block as a server-rendered `html/template` page.
The stylesheet is installed from this repository via the new optional
Python standard-library CLI; there are no Go module dependencies, client
JavaScript, authentication, or external requests.

From this directory, in a Syntyr **alpha.5 source checkout**:

```sh
python3 ../../scripts/blocks_cli.py install metric-overview --output . --dry-run
python3 ../../scripts/blocks_cli.py install metric-overview --output .
go test ./...
go run .
```

Open http://127.0.0.1:8080/ and try
http://127.0.0.1:8080/?account=Example%20Company .
`html/template` escapes untrusted account text. The operations metrics are
synthetic placeholders; replace them with authorized backend data.
The source block is copied to `syntyr/blocks/metric-overview.html` for
inspection; `templates/dashboard.html` demonstrates the necessary adaptation
from static HTML to bound Go template expressions. Production projects
must apply their own authentication, CSRF protection, business logic, and
secure serving policies.

`syntyr/` is an **ignored generated directory**, not committed to Syntyr.
The exact MIT license notice and file integrity metadata are included.
No free core source is made commercial by this example.
