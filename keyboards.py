from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            ["🔎 Найти вакансии", "⭐ Избранное"],
            ["📊 Статистика", "⚙ Настройки"],
            ["👤 Профиль"],
        ],
        resize_keyboard=True,
    )


def vacancy_card_keyboard(vacancy_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📄 Подробнее", callback_data=f"details:{vacancy_id}"),
                InlineKeyboardButton("⭐ Сохранить", callback_data=f"save:{vacancy_id}"),
            ],
            [
                InlineKeyboardButton("✉️ Откликнуться", callback_data=f"apply:{vacancy_id}"),
                InlineKeyboardButton("➡️ Пропустить", callback_data=f"skip:{vacancy_id}"),
            ],
        ]
    )


def confirm_apply_keyboard(vacancy_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Отправить письмо", callback_data=f"confirm_apply:{vacancy_id}"),
                InlineKeyboardButton("❌ Отмена", callback_data=f"cancel_apply:{vacancy_id}"),
            ]
        ]
    )
