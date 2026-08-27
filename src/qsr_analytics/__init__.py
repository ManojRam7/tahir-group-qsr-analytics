"""QSR analytics utilities for synthetic restaurant operations data."""

from .metrics import add_kpis
from .did import manual_did, fit_twfe_did

__all__ = ["add_kpis", "manual_did", "fit_twfe_did"]
