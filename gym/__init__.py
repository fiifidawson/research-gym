"""Shared helpers for research-gym modules.

Keep this package small. Anything imported by a module's ``checks.py`` must be
pure Python + NumPy, because the same code runs in the browser under Pyodide.
"""

__version__ = "0.1.0"
