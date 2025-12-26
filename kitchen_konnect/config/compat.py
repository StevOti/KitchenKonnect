"""Compatibility shim to patch Django template BaseContext.__copy__ for
Python 3.14 compatibility issues.

This patch is applied at import time when the `config` package is imported,
so it avoids editing files in the virtualenv site-packages.

It attempts to call the original __copy__ implementation and falls back to a
safe shallow-copy implementation if the original raises an exception (the
"super object has no attribute 'dicts'" error seen on Python 3.14).
"""
from __future__ import annotations

try:
    # Import lazily so this module can be imported even if Django isn't
    # available at development time (avoids hard import-time errors).
    from django.template.context import BaseContext
    import copy as _copy

    _orig_copy = getattr(BaseContext, "__copy__", None)

    def _patched_copy(self):
        # Try the original implementation first.
        if _orig_copy is not None:
            try:
                return _orig_copy(self)
            except Exception:
                # fall through to safe behavior
                pass

        # Safe fallback: construct a new instance of the same class and
        # shallow-copy the `dicts` list. Also attempt to shallow-copy
        # render_context if present.
        dup = self.__class__.__new__(self.__class__)
        try:
            dup.dicts = self.dicts[:]
        except Exception:
            dup.dicts = list(getattr(self, 'dicts', []))

        # Copy render_context if present, otherwise set to a sensible default
        if hasattr(self, 'render_context'):
            try:
                dup.render_context = _copy.copy(self.render_context)
            except Exception:
                dup.render_context = getattr(self, 'render_context', None)
        else:
            dup.render_context = None

        # Ensure attributes expected by Context/RequestContext exist.
        dup.template = None
        dup.template_name = getattr(self, 'template_name', 'unknown')
        dup.autoescape = getattr(self, 'autoescape', True)
        dup.use_l10n = getattr(self, 'use_l10n', None)
        dup.use_tz = getattr(self, 'use_tz', None)

        return dup

    # Apply the patch
    BaseContext.__copy__ = _patched_copy
except Exception:
    # If anything fails here (Django not installed or unexpected API),
    # don't crash import — the patch is best-effort.
    pass
