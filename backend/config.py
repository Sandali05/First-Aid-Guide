"""Application configuration utilities.

All sensitive settings are loaded from environment variables (optionally via a
``.env`` file). No production secrets should be committed to source control.
"""

from __future__ import annotations

import os
