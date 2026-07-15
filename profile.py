"""
Candidate profile module.

Extracted from the uploaded resume (Семенова Даша Игоревна). This is a static
profile — edit the fields below directly if your resume changes, or replace
`load_profile()` with a real PDF/DOCX parser (see resume_parser.py stub) if
you want automatic re-extraction.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CandidateProfile:
    first_name: str = "Дарья"
    full_name: str = "Семенова Дарья Игоревна"
    target_positions: list[str] = field(
        default_factory=lambda: [
            "Руководитель ПТО",
            "Начальник ПТО",
            "Руководитель сметного отдела",
        ]
    )
    total_experience_years: float = 5.3
    current_role: str = "Руководитель сметного отдела, Самолет Девелопмент"
    key_skills: list[str] = field(
        default_factory=lambda: [
            "руководство ПТО",
            "руководство сметным отделом",
            "управление отделами (до 19 человек)",
            "исполнительная документация (АОСР, АСОР, КС-2, КС-3, КС-6)",
            "сметное дело",
            "договорная работа",
            "строительство жилой недвижимости",
            "девелопмент",
            "оптимизация бизнес-процессов",
            "внедрение систем отчетности",
            "MS Excel, MS Word, AutoCAD, 1С:Предприятие, СБИС, Диадок",
        ]
    )
    achievements: list[str] = field(
        default_factory=lambda: [
            "Сократила сроки подготовки смет на 15% за счет реорганизации процессов",
            "Обеспечила обработку ~1500 задач (сметы, ДС, договоры) за 8 месяцев",
            "Сократила срок контрактации в 2 раза (до 7 рабочих дней)",
            "Сформировала отдел ПТО внутреннего подрядчика с нуля",
        ]
    )
    min_salary_net_rub: int = 220_000
    preferred_locations: list[str] = field(
        default_factory=lambda: [
            "Москва",
            "ЮВАО",
            "Люберцы",
            "Котельники",
            "Жулебино",
            "Некрасовка",
            "Октябрьский",
        ]
    )
    accepts_hybrid: bool = True
    accepts_remote: bool = True
    accepts_relocation: bool = False
    accepts_business_trips: bool = True
    languages: list[str] = field(default_factory=lambda: ["Русский (родной)", "Английский C2"])


def load_profile() -> CandidateProfile:
    """Entry point used across the app. Swap this out for a real parser later."""
    return CandidateProfile()
