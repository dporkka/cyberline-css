<!doctype html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Projects — Syntyr + Laravel</title>
    <link rel="stylesheet" href="{{ asset('css/syntyr.core.css') }}">
</head>
<body class="syn-root syn-page" data-syn-theme="studio">
    <main class="syn-panel" aria-labelledby="syntyr-projects-title">
        <h1 class="syn-heading" id="syntyr-projects-title">Projects</h1>
        <form class="syn-form" action="{{ route('syntyr.projects') }}" method="get" role="search">
            <div class="syn-field">
                <label class="syn-label" for="syntyr-project-query">Search projects</label>
                <input class="syn-input" id="syntyr-project-query" type="search"
                       name="q" maxlength="100" value="{{ $query }}">
            </div>
            <button class="syn-button syn-button--primary" type="submit">Search</button>
            <a class="syn-button" href="{{ route('syntyr.projects') }}">Clear</a>
        </form>
        <p class="syn-muted" role="status" aria-live="polite">
            {{ $projects->count() }} {{ $projects->count() === 1 ? 'project' : 'projects' }} found
        </p>
        @if ($projects->isNotEmpty())
            <div class="syn-table-wrap">
                <table class="syn-table">
                    <caption>Projects matching your search</caption>
                    <thead>
                        <tr><th scope="col">Project</th><th scope="col">Owner</th><th scope="col">Status</th></tr>
                    </thead>
                    <tbody>
                        @foreach ($projects as $project)
                            <tr>
                                <td>{{ $project['name'] }}</td>
                                <td>{{ $project['owner'] }}</td>
                                <td>{{ $project['status'] }}</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        @else
            <p>No matching projects. Try another search.</p>
        @endif
    </main>
</body>
</html>
