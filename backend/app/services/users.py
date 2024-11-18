from passlib.hash import bcrypt
from datetime import datetime, timedelta, date
from pydantic import ValidationError
from sqlalchemy.future import select
from sqlalchemy import update, delete
from jose import jwt, JWTError
from typing import List
from typing import Optional, Dict
from fastapi import Depends, Request
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from config import configs
from models.users import LicenseUpdate
from modules.exceptions import exception_token, exception_registration_data, exception_user_form
from db import tables
from models.users import User, Token, UserCreate, UserUpdate

__hash__ = lambda obj: id(obj)

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        scopes = scopes or {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Token]:
        authorization = request.cookies.get("Authorization") or request.headers.get("Authorization")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise exception_token

        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl='/auth/sign-in/')


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    return UsersService.verify_token(token)


class UsersService:
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.verify(plain_password, hashed_password)

    @classmethod
    def hash_password(cls, password: str) -> str:
        return bcrypt.hash(password)

    @classmethod
    def verify_token(cls, token: str) -> User:
        try:
            payload = jwt.decode(
                token,
                configs.jwt_secret,
                algorithms=[configs.jwt_algorithm],
            )
        except JWTError:
            raise exception_token from None

        user_data = payload.get('user')

        user_data['license_end_date'] = datetime.strptime(user_data['license_end_date'], "%d.%m.%Y").date()
        user_data['license_update_date'] = datetime.strptime(user_data['license_update_date'], "%d.%m.%Y").date()

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise exception_token from None

        return user

    @classmethod
    def create_token(cls, user: tables.Users, exp=None) -> Token:
        user_data = User.from_orm(user)
        user_data = user_data.dict()
        user_data['license_level'] = user_data['license_level'].value
        user_data['license_end_date'] = user_data['license_end_date'].strftime("%d.%m.%Y")
        user_data['license_update_date'] = user_data['license_update_date'].strftime("%d.%m.%Y")
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(hours=configs.jwt_expiration) if not exp else exp,
            'sub': str(user_data['id']),
            'user': user_data,
        }
        token = jwt.encode(
            payload,
            configs.jwt_secret,
            algorithm=configs.jwt_algorithm,
        )
        return Token(access_token=token)

    def __init__(self, session: Session):
        self.session = session

    async def get(self, id: int) -> tables.Users:
        users = await self.session.execute(
            select(tables.Users).
            filter_by(id=id)
        )
        user = users.scalars().first()
        return user

    async def register_new_user(self, user_data: UserCreate) -> Token:
        user_names = await self.session.execute(
            select(tables.Users).
            filter_by(username=user_data.username)
        )

        mails = await self.session.execute(
            select(tables.Users).
            filter_by(mail=user_data.mail)
        )

        phones = await self.session.execute(
            select(tables.Users).
            filter_by(phone=user_data.phone)
        )

        user_names = user_names.scalars().first()
        mails = mails.scalars().first()
        phones = phones.scalars().first()

        if user_names or mails or phones:
            raise exception_registration_data

        result = await self.session.execute(select(func.max(tables.Users.id)))
        max_id = int(result.scalar())

        user = tables.Users(
            id=max_id + 1,
            username=user_data.username,
            active=user_data.active,
            password_hash=self.hash_password(user_data.password),
            mail=user_data.mail,
            organization=user_data.organization,
            phone=user_data.phone,
            organization_url=user_data.organization_url,
            is_superuser=user_data.is_superuser,
            license_level=user_data.license_level,
            license_end_date=user_data.license_end_date,
            license_update_date=user_data.license_update_date,
            limit=user_data.limit
        )

        self.session.add(user)
        return user

    async def authenticate_user(self, username: str, password: str) -> Token:
        user = await self.session.execute(
            select(tables.Users)
            .filter(tables.Users.username == username)
        )

        user = user.scalars().first()

        if not user:
            raise exception_user_form

        if not self.verify_password(password, user.password_hash):
            raise exception_user_form

        return self.create_token(user)

    async def get_token(self, user_id) -> Token:
        user = await self.session.execute(
            select(tables.Users)
            .filter(tables.Users.id == user_id)
        )

        user = user.scalars().first()

        if not user:
            raise exception_user_form

        return self.create_token(user, datetime(year=user.license_end_date.year, month=user.license_end_date.month,
                                                day=user.license_end_date.day, hour=0, minute=0, second=0))

    async def get_all(self) -> List[tables.Users]:
        users = await self.session.execute(
            select(tables.Users)
        )
        users = users.scalars().all()
        return users

    async def update(self, id: int, user_data: UserUpdate) -> tables.Users:
        q = update(tables.Users).where(tables.Users.id == id).values(
            username=user_data.username,
            mail=user_data.mail,
            active=user_data.active,
            organization=user_data.organization,
            phone=user_data.phone,
            is_superuser=user_data.is_superuser,
            organization_url=user_data.organization_url,
            password_hash=bcrypt.hash(user_data.password),
            license_level=user_data.license_level,
            license_end_date=user_data.license_end_date,
            license_update_date=user_data.license_update_date,
            limit=user_data.limit
        )

        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)
        return user_data

    async def delete(self, id: int):
        q = delete(tables.Users).where(tables.Users.id == id)
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)

    async def update_license(self, user_id, license_data: LicenseUpdate) -> LicenseUpdate:
        await self.get(user_id)

        q = update(tables.Users).where(tables.Users.id == user_id).values(
            license_level=license_data.license_level,
            license_end_date=license_data.license_end_date,
            license_update_date=date.today(),
            limit=license_data.limit
        )
        q.execution_options(synchronize_session="fetch")
        await self.session.execute(q)

        return license_data

