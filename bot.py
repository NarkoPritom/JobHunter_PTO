from __future__ import annotations

import structlog
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.config.settings import settings
from app.database.db import get_session
from app.hh.client import HHClient
from app.llm.client import LLMClient
from app.llm.cover_letter import generate_cover_letter
from app.repositories.vacancy_repo import VacancyRepository
from app.services.profile import load_profile
from app.telegram_bot.keyboards import confirm_apply_keyboard, main_menu, vacancy_card_keyboard

logger = structlog.get_logger(__name__)


def _owner_only(update: Update) -> bool:
    return update.effective_chat is not None and update.effective_chat.id == settings.telegram_owner_chat_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _owner_only(update):
        return
    await update.message.reply_text(
        "Привет! Я JobHunter AI — ищу вакансии под твой профиль и помогаю откликаться.",
        reply_markup=main_menu(),
    )


async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _owner_only(update):
        return
    text = update.message.text

    if text == "🔎 Найти вакансии":
        await send_recent_vacancies(update, context)
    elif text == "⭐ Избранное":
        await send_favorites(update, context)
    elif text == "📊 Статистика":
        await send_stats(update, context)
    elif text == "⚙ Настройки":
        await update.message.reply_text(
            f"Мин. ЗП: {settings.min_match_score_to_notify}% порог уведомлений\n"
            f"Интервал поиска: {settings.search_interval_minutes} мин\n"
            "Меняются через переменные окружения (.env)."
        )
    elif text == "👤 Профиль":
        profile = load_profile()
        await update.message.reply_text(
            f"{profile.full_name}\n"
            f"Цель: {', '.join(profile.target_positions)}\n"
            f"Опыт: {profile.total_experience_years} лет\n"
            f"От {profile.min_salary_net_rub}₽ на руки\n"
            f"Локации: {', '.join(profile.preferred_locations)} / гибрид / удаленно"
        )


async def send_recent_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with get_session() as session:
        repo = VacancyRepository(session)
        vacancies = await repo.recent(limit=5)

    if not vacancies:
        await update.message.reply_text("Пока новых подходящих вакансий нет. Проверю снова по расписанию.")
        return

    for v in vacancies:
        await _send_vacancy_card(update.effective_chat.id, context, v)


async def _send_vacancy_card(chat_id: int, context: ContextTypes.DEFAULT_TYPE, v) -> None:
    salary = ""
    if v.salary_from or v.salary_to:
        salary = f"{v.salary_from or '?'}–{v.salary_to or '?'} {v.salary_currency or 'RUB'}"
    text = (
        f"<b>{v.title}</b>\n"
        f"{v.company} · {v.city}\n"
        f"{salary}\n"
        f"Формат: {v.schedule}\n"
        f"Оценка ИИ: {v.match_score}%\n"
        f"Почему подходит: {v.match_reasons}\n"
        f"<a href='{v.url}'>Ссылка на вакансию</a>"
    )
    await context.bot.send_message(
        chat_id, text, parse_mode="HTML", reply_markup=vacancy_card_keyboard(v.id), disable_web_page_preview=True
    )


async def send_favorites(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with get_session() as session:
        repo = VacancyRepository(session)
        favorites = await repo.list_favorites()
    if not favorites:
        await update.message.reply_text("В избранном пока пусто.")
        return
    for v in favorites:
        await _send_vacancy_card(update.effective_chat.id, context, v)


async def send_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with get_session() as session:
        repo = VacancyRepository(session)
        stats = await repo.stats()
    await update.message.reply_text(
        f"Всего найдено вакансий: {stats['total_vacancies']}\n"
        f"В избранном: {stats['favorites']}\n"
        f"Откликов отправлено: {stats['responses']}"
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action, vacancy_id_str = query.data.split(":")
    vacancy_id = int(vacancy_id_str)

    async with get_session() as session:
        repo = VacancyRepository(session)
        vacancy = await repo.get(vacancy_id)
        if not vacancy:
            await query.message.reply_text("Вакансия не найдена (возможно, устарела).")
            return

        if action == "save":
            await repo.add_favorite(vacancy_id)
            await query.message.reply_text("Сохранено в избранное ⭐")

        elif action == "skip":
            await query.message.reply_text("Пропущено.")

        elif action == "details":
            await query.message.reply_text(vacancy.description[:3500] or "Описание недоступно.")

        elif action == "apply":
            llm = LLMClient()
            try:
                profile = load_profile()
                letter = await generate_cover_letter(llm, profile, vacancy.description)
            finally:
                await llm.close()
            context.chat_data[f"draft_letter:{vacancy_id}"] = letter
            await query.message.reply_text(
                f"Черновик письма:\n\n{letter}\n\nОтправить?",
                reply_markup=confirm_apply_keyboard(vacancy_id),
            )

        elif action == "confirm_apply":
            letter = context.chat_data.get(f"draft_letter:{vacancy_id}", "")
            await repo.save_response(vacancy_id, letter)
            hh = HHClient()
            try:
                sent = await hh.submit_response(vacancy.external_id, letter)
            finally:
                await hh.close()
            if sent:
                await query.message.reply_text("Отклик отправлен ✅")
            else:
                await query.message.reply_text(
                    "Не удалось отправить автоматически (нет HH_ACCESS_TOKEN/HH_RESUME_ID "
                    "или ошибка API). Письмо сохранено — можешь отправить вручную по ссылке на вакансию."
                )

        elif action == "cancel_apply":
            await query.message.reply_text("Отменено.")


def build_application() -> Application:
    app = Application.builder().token(settings.telegram_bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
    app.add_handler(CallbackQueryHandler(handle_callback))
    return app
