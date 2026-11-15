"""Environment-configurable Playwright launch options for developer-only suites.

The actual browser versions and dependencies are managed by the developer's
Playwright installation, not downloaded or shipped with Syntyr.
"""
import os
import shutil


def launch_options(engine: str) -> dict:
    if engine not in ('chromium', 'firefox', 'webkit'):
        raise ValueError(f'Unsupported browser engine: {engine}')
    opts = {'headless': True}
    binary = os.environ.get(f'PLAYWRIGHT_{engine.upper()}_EXECUTABLE')
    if engine == 'chromium':
        binary = binary or shutil.which('chromium') or shutil.which('chromium-browser')
    if binary:
        opts['executable_path'] = binary
        if engine == 'chromium':
            opts['args'] = ['--no-sandbox']
    return opts
