from __future__ import annotations

from app.llm.client import LLMClient
from app.services.profile import CandidateProfile

ANALYSIS_SYSTEM_PROMPT = """Ты — опытный HR-консультант, оценивающий соответствие вакансии кандидату.
Отвечай ТОЛЬКО валидным JSON, без markdown-обрамления и без пояснений вне JSON.
Формат ответа:
{
  "score": <целое число 0-100>,
  "reasons": "<краткое объяснение оценки>",
  "pros": ["<плюс 1>", "<плюс 2>"],
  "cons": ["<минус 1>", "<минус 2>"],
  "red_flags": ["<красный флаг, если есть>"]
}"""


def _profile_block(profile: CandidateProfile) -> str:
    return f"""Профиль кандидата:
- Целевые должности: {', '.join(profile.target_positions)}
- Опыт: {profile.total_experience_years} лет, текущая роль: {profile.current_role}
- Ключевые навыки: {', '.join(profile.key_skills)}
- Достижения: {'; '.join(profile.achievements)}
- Минимальная ЗП на руки: {profile.min_salary_net_rub} руб.
- Локации: {', '.join(profile.preferred_locations)}; гибрид: {profile.accepts_hybrid}; удаленно: {profile.accepts_remote}"""


async def analyze_vacancy(llm: LLMClient, profile: CandidateProfile, vacancy_text: str) -> dict:
    user_prompt = f"""{_profile_block(profile)}

Вакансия:
{vacancy_text}

Оцени вероятность успешного прохождения интервью и общее соответствие (0-100%),
совпадение опыта и навыков, уровень компании. Верни JSON строго по формату."""

    result = await llm.complete_json(ANALYSIS_SYSTEM_PROMPT, user_prompt, max_tokens=800)
    result.setdefault("score", 0)
    result.setdefault("reasons", "")
    result.setdefault("pros", [])
    result.setdefault("cons", [])
    result.setdefault("red_flags", [])
    return result
