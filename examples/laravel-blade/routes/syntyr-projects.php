<?php
// Copy these imports and Route::get into your existing routes/web.php.
// Demonstration data only; authorize and query your application database in production.
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

Route::get('/syntyr/projects', function (Request $request) {
    $raw = $request->query('q', '');
    $query = is_string($raw) ? substr(trim($raw), 0, 100) : '';

    $projects = collect([
        ['name' => 'Station expansion', 'owner' => 'Operations', 'status' => 'In progress'],
        ['name' => 'Airport displays', 'owner' => 'Sales', 'status' => 'Review'],
        ['name' => 'Downtown refresh', 'owner' => 'Production', 'status' => 'Planned'],
    ])->filter(fn (array $project) => stripos($project['name'], $query) !== false)->values();

    return view('syntyr.projects', compact('query', 'projects'));
})->name('syntyr.projects');
