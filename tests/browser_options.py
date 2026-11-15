"""Resolve opt-in developer browser executables for Playwright harnesses.

No browser or Python package is required by Syntyr CSS consumers.
"""
import os
import shutil

_ALLOWED = frozenset(("chromium", "firefox", "webkit"))

def launch_options(engine, *, env=None, which=None):
    if engine not in _ALLOWED:
        raise ValueError(f"Unsupported browser engine: {engine}")
    env = os.environ if env is None else env
    which = shutil.which if which is None else which
    executable = env.get(f"PLAYWRIGHT_{engine.upper()}_EXECUTABLE")
    if not executable and engine == "chromium":
        executable = which("chromium") or which("chromium-browser")
    options = {"headless": True}
    if executable:
        options["executable_path"] = executable
        if engine == "chromium":
            options["args"] = ["--no-sandbox"]
    return options
