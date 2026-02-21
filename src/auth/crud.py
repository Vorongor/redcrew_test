from datetime import timedelta
from typing import Annotated

from fastapi.params import Depends
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security.exceptions import (
    SessionExpiredError,
    InvalidRefreshTokenError
)
from src.config import Settings
from src.config import get_settings
from src.auth.security.token_manager import  get_jwt_manager
from src.database import get_db
from src.database.models import UserModel, RefreshTokenModel
from src.auth.user_exceptions import (
    UserCreateException,
    UserNotFoundException,
    UserAlreadyExistsException,
)
from src.auth.schemas import (
    UserCreateSchema,
    UserReadSchema,
    LoginRequestSchema,
    LoginResponseSchema,
    CommonResponseSchema,
    RefreshTokenSchema,
    RefreshTokenResponseSchema,
)
from src.auth.security import JWTAuthManagerInterface
from src.auth.security.utils import get_current_user


async def _get_user_by_email(email: str, db: AsyncSession) -> UserModel:
    """
    Internal helper to fetch a user from the database by their email address.

    Args:
        email (str): The unique email address to search for.
        db (AsyncSession): The database session.

    Returns:
        Optional[UserModel]: The user instance if found, otherwise None.
    """
    user = await db.execute(select(UserModel).where(UserModel.email == email))
    return user.scalar_one_or_none()


async def create_new_user(
        user_data: UserCreateSchema,
        db: Annotated[AsyncSession, Depends(get_db)]
) -> UserReadSchema:
    """
    Registers a new user in the system.

    Performs a check for email uniqueness, hashes the password,
    and persists the user record.

    Args:
        user_data (UserCreateSchema): Data for the new user.
        db (DBDep): Async database session.

    Raises:
        UserAlreadyExistsException: If the email is already registered.
        UserCreateException: If a database error occurs during commitment.

    Returns:
        UserReadSchema: The newly created user's public information.
    """

    existing_user = await _get_user_by_email(user_data.email, db)
    if existing_user:
        raise UserAlreadyExistsException()

    user = UserModel.create(
        email=user_data.email,
        raw_password=user_data.password,
    )
    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except SQLAlchemyError:
        await db.rollback()
        raise UserCreateException()
    return UserReadSchema.model_validate(user)


async def login_user(
        login_data: LoginRequestSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        jwt_manager: Annotated[
            JWTAuthManagerInterface, Depends(get_jwt_manager)],
        settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponseSchema:
    """
    Authenticates a user and generates access/refresh tokens.

    Verifies credentials, issues JWT tokens, and stores the
    refresh token in the database for session persistence.

    Args:
        login_data (LoginRequestSchema): Login credentials (email/password).
        db (DBDep): Async database session.
        jwt_manager (JWTManagerDep): Service for token generation.
        settings (SettingsDep): Application configuration.

    Raises:
        UserNotFoundException: If credentials do not match any user.
        AuthException: If a database error occurs while saving refresh tokens.

    Returns:
        LoginResponseSchema: A set of JWT tokens and token type.
    """
    user = await _get_user_by_email(login_data.email, db)
    if not user or not user.check_password(login_data.password):
        raise UserNotFoundException()

    await db.execute(
        delete(RefreshTokenModel).where(RefreshTokenModel.user_id == user.id)
    )

    token_data = {
        "user_id": user.id,
        "email": user.email,
    }
    access_token = jwt_manager.create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_KEY_TIMEDELTA_MINUTES),
    )
    refresh_token = jwt_manager.create_refresh_token(
        data=token_data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_DAYS),
    )
    db_token = RefreshTokenModel.create(
        token=refresh_token,
        user_id=user.id,
    )
    db.add(db_token)
    try:
        await db.commit()
        return LoginResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
    except SQLAlchemyError:
        await db.rollback()
        raise SessionExpiredError()


async def logout_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        auth_user: Annotated[UserReadSchema, Depends(get_current_user)],
) -> CommonResponseSchema:
    """
    Invalides user sessions by deleting refresh tokens.

    Args:
        db (AsyncSession): Database session.
        auth_user (UserReadSchema): Currently authenticated user.

    Returns:
        CommonResponseSchema: Success message.
    """
    stmt = delete(RefreshTokenModel).where(
        RefreshTokenModel.user_id == auth_user.id
    )

    try:
        await db.execute(stmt)
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        raise
    return CommonResponseSchema(
        message="Successfully logged out from all devices",
    )


async def refresh_token(
        token: RefreshTokenSchema,
        jwt_manager: Annotated[
            JWTAuthManagerInterface, Depends(get_jwt_manager)],
        db: Annotated[AsyncSession, Depends(get_db)],
        settings: Annotated[Settings, Depends(get_settings)],
) -> RefreshTokenResponseSchema:
    """
    Issues a new access token using a valid refresh token.

    Args:
        token_data (RefreshTokenSchema): The refresh token.
        db (AsyncSession): Database session for token validation.
        jwt_manager (JWTAuthManagerInterface): Token manager.
        settings (BaseAppSettings): App configuration.

    Returns:
        RefreshTokenResponseSchema: New access token.

    Raises:
        InvalidRefreshTokenError: If token is invalid or not found in DB.
    """
    stmt = select(RefreshTokenModel).where(
        RefreshTokenModel.token == token.refresh_token
    )

    result = await db.execute(stmt)
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise InvalidRefreshTokenError()

    try:
        payload = jwt_manager.decode_refresh_token(token.refresh_token)
    except Exception as e:
        await db.delete(db_token)
        await db.commit()
        raise InvalidRefreshTokenError()

    user_id = payload.get("user_id")
    email = payload.get("email")

    if not user_id or not email:
        raise InvalidRefreshTokenError()

    new_token = jwt_manager.create_access_token(
        data={
            "user_id": user_id,
            "email": email,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_KEY_TIMEDELTA_MINUTES),
    )

    return RefreshTokenResponseSchema(access_token=new_token)
