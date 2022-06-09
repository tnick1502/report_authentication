from passlib.hash import bcrypt
from datetime import datetime, timedelta
from pydantic import ValidationError
from sqlalchemy.future import select
from sqlalchemy import update, delete
from db import tables
from models.users import User, Token, UserCreate, UserUpdate
from jose import jwt, JWTError
from typing import List
from config import configs
from typing import Optional, Dict
from fastapi import status, HTTPException, Depends, Request
#from db.database import get_session
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.orm import Session


__hash__ = lambda obj: id(obj)

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Token]:
        authorization: str = request.cookies.get("Authorization")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is wrong or missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return param


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl='/authorization/sign-in/')


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
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'Authenticate': 'Bearer'},
        )

        try:
            payload = jwt.decode(
                token,
                configs.jwt_secret,
                algorithms=[configs.jwt_algorithm],
            )
        except JWTError:
            raise exception from None

        user_data = payload.get('user')

        try:
            user = User.parse_obj(user_data)
        except ValidationError:
            raise exception from None

        return user

    @classmethod
    def create_token(cls, user: tables.Users) -> Token:
        user_data = User.from_orm(user)
        now = datetime.utcnow()
        payload = {
            'iat': now,
            'nbf': now,
            'exp': now + timedelta(seconds=configs.jwt_expiration),
            'sub': str(user_data.id),
            'user': user_data.dict(),
        }
        token = jwt.encode(
            payload,
            configs.jwt_secret,
            algorithm=configs.jwt_algorithm,
        )
        return Token(access_token=token)

    def __init__(self, session: Session):
        self.session = session

    async def register_new_user(self, user_data: UserCreate, user: User) -> Token:
        if user.is_superuser:
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
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This name or mail or phone is already exist",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            user = tables.Users(
                username=user_data.username,
                password_hash=self.hash_password(user_data.password),
                mail=user_data.mail,
                organization=user_data.organization,
                phone=user_data.phone,
                organization_url=user_data.organization_url,
                limit=user_data.limit,
                is_superuser=user_data.is_superuser
            )

            self.session.add(user)
            await self.session.commit()
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                etail="You don't have enough rights to perform this operation",
                headers={'Authenticate': 'Bearer'})

    async def authenticate_user(self, username: str, password: str) -> Token:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

        user = await self.session.execute(
            select(tables.Users)
            .filter(tables.Users.username == username)
        )

        user = user.scalars().first()

        if not user:
            raise exception

        if not self.verify_password(password, user.password_hash):
            raise exception

        return self.create_token(user)

    async def get_all(self, user: User) -> List[tables.Users]:

        if user.is_superuser:
            users = await self.session.execute(
                select(tables.Users)
            )
            users = users.scalars().all()
            return users
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough rights to perform this operation",
                headers={'Authenticate': 'Bearer'})

    async def update(self, id: int, user_data: UserUpdate, user: User) -> tables.Reports:
        if user.is_superuser == True:
            q = update(tables.Users).where(tables.Users.id == id).values(
                username=user_data.username,
                mail=user_data.mail,
                organization=user_data.organization,
                limit=user_data.limit,
                phone=user_data.phone,
                organization_url=user_data.organization_url,
                password_hash=bcrypt.hash(user_data.password))

            q.execution_options(synchronize_session="fetch")
            await self.session.execute(q)
            await self.session.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough rights to perform this operation",
                headers={'Authenticate': 'Bearer'})

    async def delete(self, id: int, user: User):

        if user.is_superuser == True:
            q = delete(tables.Users).where(tables.Users.id == id)
            q.execution_options(synchronize_session="fetch")
            await self.session.execute(q)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough rights to perform this operation",
                headers={'Authenticate': 'Bearer'})
