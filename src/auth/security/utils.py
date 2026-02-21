from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.auth.security import JWTAuthManagerInterface
from src.auth.security.exceptions import TokenExpiredError, InvalidTokenError
from src.auth.user_exceptions import (
    UserNotFoundException,
    UserAreLoggedOutException
)
from src.auth.security.token_manager import get_jwt_manager
from src.database import get_db
from src.database.models import UserModel


security_scheme = HTTPBearer()


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    auth: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    jwt_manager: Annotated[JWTAuthManagerInterface, Depends(get_jwt_manager)],
) -> int:
    token = auth.credentials
    try:
        user_data = jwt_manager.decode_access_token(token)

    except (TokenExpiredError, InvalidTokenError):
        raise

    user_id = user_data.get("user_id")

    result = await db.execute(
        select(UserModel)
        .options(joinedload(UserModel.refresh_tokens))
        .where(UserModel.id == user_id)
    )
    auth_user = result.unique().scalar_one_or_none()

    if not auth_user:
        raise UserNotFoundException()

    if not auth_user.refresh_tokens:
        raise UserAreLoggedOutException()

    return auth_user.id
