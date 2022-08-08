import datetime
from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy import update, delete
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.license import License, LicenseCreate, LicenseUpdate
import db.tables as tables

class LicensesService:
    def __init__(self, session: Session):
        self.session = session

    async def _get(self, user_id: str) -> Optional[tables.Licenses]:
        licenses = await self.session.execute(
            select(tables.Licenses).
            filter_by(user_id=user_id)
        )
        license = licenses.scalars().first()

        if not license:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Cant find license")
        return license

    async def get(self, user_id: str) -> tables.Licenses:
        license = await self._get(user_id)
        return license

    async def update(self, user_id, license_data: LicenseUpdate) -> LicenseUpdate:
        await self._get(user_id)

        q = update(tables.Licenses).where(tables.Licenses.user_id == user_id).values(
            user_id=license_data.user_id,
            license_level=license_data.license_level,
            license_end_date=license_data.license_end_date,
            license_update_date=datetime.date.today(),
            limit=license_data.limit
        )
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        await self.session.commit()

        return License(
            user_id=license_data.user_id,
            license_level=license_data.license_level,
            license_end_date=license_data.license_end_date,
            license_update_date=datetime.date.today(),
            limit=license_data.limit
        )

    async def delete(self, user_id: str):
        await self._get(user_id)
        q = delete(tables.Licenses).where(tables.Licenses.user_id == user_id)
        q.execution_options(synchronize_session="fetch")

        await self.session.execute(q)
        await self.session.commit()

    async def create(self, user: str, license_data: LicenseCreate) -> tables.Licenses:
        license = tables.Licenses(
            **license_data.dict(),
            user_id=user.id)
        self.session.add(license)
        await self.session.commit()

        return license

    async def get_all(self) -> Optional[List[tables.Licenses]]:
        licenses = await self.session.execute(
            select(tables.Licenses)
        )
        licenses = licenses.scalars().all()

        if not licenses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cant find licenses")

        return licenses


