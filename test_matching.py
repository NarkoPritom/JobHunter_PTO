from app.services.matching import passes_hard_filters
from app.services.profile import load_profile


def test_salary_below_minimum_rejected():
    profile = load_profile()
    assert not passes_hard_filters(profile, salary_from=150_000, salary_to=180_000, city="Москва", schedule="office")


def test_remote_and_good_salary_accepted():
    profile = load_profile()
    assert passes_hard_filters(profile, salary_from=250_000, salary_to=None, city=None, schedule="remote")


def test_wrong_city_office_rejected():
    profile = load_profile()
    assert not passes_hard_filters(profile, salary_from=300_000, salary_to=None, city="Новосибирск", schedule="office")


def test_preferred_city_office_accepted():
    profile = load_profile()
    assert passes_hard_filters(profile, salary_from=250_000, salary_to=None, city="Люберцы", schedule="office")
