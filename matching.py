from __future__ import annotations

from app.services.profile import CandidateProfile


def passes_hard_filters(
    profile: CandidateProfile,
    salary_from: int | None,
    salary_to: int | None,
    city: str | None,
    schedule: str | None,
) -> bool:
    """Hard filters: salary AND location must both pass, matching the
    requirement 'от 220000 на руки ИЛИ эквивалент gross, И (одна из
    районов Москвы ИЛИ гибрид ИЛИ удаленно)'."""

    salary_ok = _salary_ok(profile, salary_from, salary_to)
    location_ok = _location_ok(profile, city, schedule)
    return salary_ok and location_ok


def _salary_ok(profile: CandidateProfile, salary_from: int | None, salary_to: int | None) -> bool:
    if salary_from is None and salary_to is None:
        return False  # no salary info = can't verify, skip by default
    best_known = max(v for v in (salary_from, salary_to) if v is not None)
    return best_known >= profile.min_salary_net_rub


def _location_ok(profile: CandidateProfile, city: str | None, schedule: str | None) -> bool:
    if schedule and schedule.lower() in ("remote", "удаленно", "удалённо"):
        return profile.accepts_remote
    if schedule and schedule.lower() in ("hybrid", "flexible", "гибрид"):
        return profile.accepts_hybrid
    if not city:
        return False
    city_lower = city.lower()
    return any(loc.lower() in city_lower for loc in profile.preferred_locations)
