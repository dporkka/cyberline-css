# Syntyr + Ruby on Rails (ERB + optional Turbo)

A copyable **GET-only project search** for an existing Rails app. It returns
a complete server-rendered page without JavaScript; if the host app already
uses Turbo, the form updates only the matching results frame. Syntyr adds
**zero JavaScript and zero Ruby dependencies**.

1. Copy `dist/syntyr.core.css` from the same Syntyr commit you use into
   your Rails app's `public/css/syntyr.core.css`. Alpha.5 is still
   prerelease source; don't assume its package is published.
2. Add `<%= stylesheet_link_tag "/css/syntyr.core.css" %>` **once** in
   `app/views/layouts/application.html.erb`, inside its `<head>`.
   Self-host CSS, rather than using a floating CDN version.
3. Copy `app/controllers/syntyr_projects_controller.rb` and
   `app/views/syntyr_projects/index.html.erb` into the matching paths
   within your Rails app.
4. Add this line **inside your existing** `Rails.application.routes.draw do`
   in `config/routes.rb` (do not replace your app's routes):

   ```ruby
   get "/syntyr/projects", to: "syntyr_projects#index", as: :syntyr_projects
   ```

5. Optionally copy `test/controllers/syntyr_projects_controller_test.rb` into
   your Rails app's `test/controllers/` directory. Run
   `bin/rails test test/controllers/syntyr_projects_controller_test.rb`.
6. Run `bin/rails server` and open `/syntyr/projects?q=airport`.
   Try an unmatched query and disable JavaScript to verify full-page fallback.

**DOM ownership:** The `.syn-root` theme boundary stays outside
`<turbo-frame id="syntyr-project-results">`; Turbo only morphs the frame.
`data-turbo-frame="_top"` on Clear ensures the form's query field resets
as well. Turbo is optional, not bundled by Syntyr. The controller uses
hard-coded demonstration rows, no database, no writes, and truncates the
query; replace it with a scoped/authorized query for real data.

**Escaping:** Rails' `h(...)` escapes user input and row strings.
The GET route does not need an anti-CSRF token; any state-changing POST
or PATCH route must use Rails' normal CSRF, authorization and validation.

**Validation:** The included Rails request tests check search, escaping and
result markup when run inside a Rails app; Syntyr's own repository checks
only check the copy contract. The sample was not booted against Rails here.
Add system tests for your Rails/Turbo version and keyboard/AT flows.
