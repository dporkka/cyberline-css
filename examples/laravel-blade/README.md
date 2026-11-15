# Syntyr + Laravel (plain Blade, no Livewire required)

A copyable **GET-only project search** for an existing Laravel app. It works
without Livewire, Alpine, Tailwind, Vite or any JavaScript. Syntyr adds no
PHP or JS dependency.

1. Copy `dist/syntyr.core.css` from the same Syntyr commit into your
   Laravel app's `public/css/syntyr.core.css`. The alpha.5 npm package is
   not assumed to be published.
2. Copy `resources/views/syntyr/projects.blade.php` into the matching
   location in your Laravel app. If you already have a layout, migrate
   its body into your layout and include the CSS once in the main head.
3. Add the route from `routes/syntyr-projects.php` to your existing
   `routes/web.php`, and add only imports not already present. Do **not**
   paste a second opening `<?php` tag or overwrite the existing routes.
4. Optionally copy `tests/Feature/SyntyrProjectsTest.php` into the
   matching test path and run `php artisan test --filter=SyntyrProjectsTest`.
5. Run `php artisan serve` and visit `/syntyr/projects?q=airport`.
   Search, clear, and check the empty-results state with JavaScript off.

The route is a read-only demo using in-memory rows. `is_string` handles
array-shaped input, and `substr` limits excessive query text. In a real
app, enforce authorization and query your data rather than using demo rows.
Blade's `{{ }}` syntax HTML-escapes input and project fields.
There is no CSRF token on this read-only GET form; use Laravel's `@csrf`
and server-side validation for state-changing methods.

**Livewire:** If you prefer Livewire 3/4, see
[`examples/server-rendered/livewire.blade.php`](../server-rendered/livewire.blade.php).
The optional `syntyr.server.css` can display request-state styles; it is
not needed here, and Syntyr does not own the Livewire runtime.

**Validation:** The included Laravel feature tests check filtering and
escaping when run inside a Laravel application. Repository checks only
verify the static copy contract; Laravel was not booted here. Add real
data/permission tests and accessibility coverage in your host app.
