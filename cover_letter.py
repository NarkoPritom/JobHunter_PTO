from __future__ import annotations

from app.llm.client import LLMClient
from app.services.profile import CandidateProfile

COVER_LETTER_SYSTEM_PROMPT = """Ты помогаешь кандидату написать персональное сопроводительное письмо
работодателю на русском языке. Тон — деловой, уверенный, без штампов и общих фраз.
Пиши от первого лица, от имени кандидата. Длина — 120-180 слов, без markdown-разметки,
готовый текст письма, без дополнительных комментариев."""


async def generate_cover_letter(llm: LLMClient, profile: CandidateProfile, vacancy_text: str) -> str:
    user_prompt = f"""Данные кандидата:
- Имя: {profile.first_name}
- Целевая должность: {profile.target_positions[0]}
- Опыт: {profile.total_experience_years} лет, текущая роль — {profile.current_role}
- Ключевые навыки: {', '.join(profile.key_skills[:6])}
- Главные достижения: {'; '.join(profile.achievements[:3])}

Описание вакансии:
{vacancy_text}

Напиши сопроводительное письмо, которое явно связывает достижения кандидата
с требованиями именно этой вакансии."""

    return await llm.complete(COVER_LETTER_SYSTEM_PROMPT, user_prompt, max_tokens=500)
