from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Favorite, Response, Vacancy


class VacancyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists(self, external_id: str) -> bool:
        result = await self.session.execute(
            select(Vacancy.id).where(Vacancy.external_id == external_id)
        )
        return result.scalar_one_or_none() is not None

    async def save(self, vacancy: Vacancy) -> Vacancy:
        self.session.add(vacancy)
        await self.session.commit()
        await self.session.refresh(vacancy)
        return vacancy

    async def get(self, vacancy_id: int) -> Vacancy | None:
        return await self.session.get(Vacancy, vacancy_id)

    async def mark_notified(self, vacancy_id: int) -> None:
        vacancy = await self.get(vacancy_id)
        if vacancy:
            vacancy.notified = True
            await self.session.commit()

    async def recent(self, limit: int = 20) -> list[Vacancy]:
        result = await self.session.execute(
            select(Vacancy).order_by(Vacancy.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def add_favorite(self, vacancy_id: int) -> None:
        self.session.add(Favorite(vacancy_id=vacancy_id))
        await self.session.commit()

    async def list_favorites(self) -> list[Vacancy]:
        result = await self.session.execute(
            select(Vacancy).join(Favorite, Favorite.vacancy_id == Vacancy.id)
        )
        return list(result.scalars().all())

    async def save_response(self, vacancy_id: int, cover_letter: str) -> Response:
        response = Response(vacancy_id=vacancy_id, cover_letter=cover_letter, status="draft")
        self.session.add(response)
        await self.session.commit()
        await self.session.refresh(response)
        return response

    async def mark_response_sent(self, response_id: int) -> None:
        response = await self.session.get(Response, response_id)
        if response:
            import datetime as dt

            response.status = "sent"
            response.sent_at = dt.datetime.utcnow()
            await self.session.commit()

    async def stats(self) -> dict:
        total = await self.session.execute(select(Vacancy.id))
        favorites = await self.session.execute(select(Favorite.id))
        responses = await self.session.execute(select(Response.id))
        return {
            "total_vacancies": len(total.all()),
            "favorites": len(favorites.all()),
            "responses": len(responses.all()),
        }
