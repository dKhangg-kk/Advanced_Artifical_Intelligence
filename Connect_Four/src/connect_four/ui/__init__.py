"""Giao dien demo."""

from __future__ import annotations

__all__ = ["run_gui"]


def run_gui(*args, **kwargs) -> None:
    """Mo giao dien pygame (import tre de `python -m connect_four.ui.gui` khong bi canh bao)."""
    from connect_four.ui.gui import run_gui as _run_gui

    _run_gui(*args, **kwargs)
