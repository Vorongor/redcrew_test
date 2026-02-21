from datetime import date

from src.auth.validators import validate_password_strength as validate_password
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_corporate_email(cls, v: str) -> str:
        if "temporary-mail.com" in v:
            raise ValueError("Temporary mails are not allowed")
        return str(v.lower())

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        try:
            return validate_password(password=v)
        except ValueError:
            raise


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr


class LoginRequestSchema(BaseModel):
    email: EmailStr
    password: str


class LoginResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class CommonResponseSchema(BaseModel):
    message: str


class RefreshTokenSchema(BaseModel):
    refresh_token: str


class RefreshTokenResponseSchema(BaseModel):
    access_token: str
