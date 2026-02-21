from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.security.exceptions import BaseSecurityException
from src.auth.user_exceptions import BaseUserException
from src.auth.crud import (
    create_new_user,
    login_user,
    logout_user,
    refresh_token
)
from src.auth.security.token_manager import get_jwt_manager
from src.config import Settings, get_settings
from src.database import get_db
from src.auth.schemas import (
    UserReadSchema,
    UserCreateSchema,
    LoginResponseSchema,
    LoginRequestSchema,
    RefreshTokenResponseSchema,
    RefreshTokenSchema,
    CommonResponseSchema,
)
from src.auth.security import JWTAuthManagerInterface
from src.auth.security.utils import get_current_user

auth_router = APIRouter(tags=["Authentication"])


@auth_router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserReadSchema,
    summary="Register a new user",
    responses={
        400: {"description": "User already exists or validation error"},
        422: {"description": "Validation Error"},
    },
)
async def register(
        user_data: UserCreateSchema,
        db: Annotated[AsyncSession, Depends(get_db)]
) -> UserReadSchema:
    """
    Register a new user in the system.

    - **email**: Must be unique
    - **password**: Should be strong (minimum 6 characters,
    1 uppercase letter, 1 digit, 1 special character)
    - **name/surname**: User's personal details
    """
    try:
        return await create_new_user(
            db=db,
            user_data=user_data,
        )
    except BaseUserException as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        )


@auth_router.post(
    "/sessions",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponseSchema,
    summary="Authenticate user and get tokens",
    responses={
        400: {"description": "Invalid credentials"},
        401: {"description": "Unauthorized"},
    },
)
async def login(
        login_data: LoginRequestSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        jwt_manager: Annotated[
            JWTAuthManagerInterface, Depends(get_jwt_manager)
        ],
        settings: Annotated[Settings, Depends(get_settings)],
) -> LoginResponseSchema:
    """
    Authenticate a user and return JWT tokens.

    - **email**: Registered user email
    - **password**: Valid password
    - **Returns**: Access and Refresh tokens
    """
    try:
        result = await login_user(
            db=db,
            jwt_manager=jwt_manager,
            settings=settings,
            login_data=login_data,
        )
        return result
    except (BaseUserException, BaseSecurityException):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password",
        )


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=CommonResponseSchema,
    summary="Logout user",
    description="Invalidates user sessions by deleting "
                "all refresh tokens from the database.",
)
async def logout(
        db: Annotated[AsyncSession, Depends(get_db)],
        auth_user: Annotated[UserReadSchema, Depends(get_current_user)],
) -> CommonResponseSchema:
    """
    Logout the current user:
    - **Authorization**: Bearer token required
    - **Action**: Deletes all refresh tokens associated with the user ID
    """
    try:
        return await logout_user(db=db, auth_user=auth_user)
    except BaseUserException as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
        )


@auth_router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=RefreshTokenResponseSchema,
    summary="Refresh access token",
    responses={
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh(
        token_data: RefreshTokenSchema,
        db: Annotated[AsyncSession, Depends(get_db)],
        jwt_manager: Annotated[
            JWTAuthManagerInterface, Depends(get_jwt_manager)],
        settings: Annotated[Settings, Depends(get_settings)],
) -> RefreshTokenResponseSchema:
    """
    Get a new access token using a refresh token:
    - **refresh_token**: Must be token previously issued and present in DB
    - **Returns**: A new access token (JWT)
    """
    try:
        return await refresh_token(
            token=token_data, db=db, jwt_manager=jwt_manager, settings=settings
        )
    except BaseUserException as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err)
        )
