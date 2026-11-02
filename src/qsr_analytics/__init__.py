"""QSR analytics utilities for synthetic restaurant operations data."""

from .did import fit_twfe_did, manual_did
from .metrics import add_kpis

__all__ = ["add_kpis", "manual_did", "fit_twfe_did"]
