"""Pyxis backend package.

The backend can be imported as either ``backend.app`` from the repository root
or ``app`` when commands run from the backend directory.
"""

import sys

from backend import app as _app

sys.modules.setdefault("app", _app)
