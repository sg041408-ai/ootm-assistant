"""Urgency comes from the calendar, not from how the question is worded."""
from __future__ import annotations

from datetime import date

from .models import Urgency


def urgency_for(tournament: date | None, today: date) -> Urgency:
    if tournament is None:
        return Urgency.LATER
    days = (tournament - today).days
    if days <= 7:
        return Urgency.IMMEDIATE
    if days <= 21:
        return Urgency.WITHIN_48H
    return Urgency.LATER
