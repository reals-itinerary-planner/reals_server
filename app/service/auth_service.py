from datetime import datetime, timedelta
from jose import jwt
from typing import Optional
from app.models.user_model import User
from app.core.security import verify_password
from app.repositories.base_repository import BaseRepository
from dist.packages.sqlalchemy.ext.asyncio.session import AsyncSession
from app.core.config import settings
from dist.packages.sqlalchemy.orm.strategy_options import joinedload


class AuthService:
    def __init__(self, db: AsyncSession):
        # self.db = db
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.token_expire_days = settings.JWT_EXPIRE_DAYS
        self.user_repo = BaseRepository(User, db)

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = (
            await (
                self.user_repo.get_first(
                    filters={"filter_by[email][equals]": email},
                    include=["login_sessions"],
                )
                # self.db.query(User)
                # .filter(User.email == email)
                # .first()
                # .options(joinedload(User.login_sessions))
            )
        )
        print("user he", user.hashed_password)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_token(self, user: User) -> str:
        expires_at = datetime.now() + timedelta(days=self.token_expire_days)

        token_data = {"sub": str(user.uuid), "email": user.email, "exp": expires_at}

        token = jwt.encode(token_data, self.secret_key, algorithm=self.algorithm)
        await self.user_repo.get_first(
            filters={"id": user.id}, include=["login_sessions"]
        )
        await self.user_repo.update(
            user.id, {"login_sessions": {"token": token, "expires_at": expires_at}}
        )
        # Store token in database
        # user_token = UserToken(user_id=user.id, token=token, expires_at=expires_at)
        # self.db.add(user_token)
        # self.db.commit()

        return token

    async def verify_token(self, token: str) -> Optional[dict]:
        try:
            user = await self.user_repo.get_first(
                {
                    "filter_by[token][equals]": token,
                    "filter_by[expires_at][gt]": datetime.now(),
                }
            )

            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
