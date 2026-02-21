class BaseSecurityException(Exception):
    def __init__(self, details: str | None = None) -> None:
        if details is None:
            details = "Something went wrong during security operation"
        super().__init__(details)


class TokenExpiredError(BaseSecurityException):
    """Exception raised when a token is expired"""
    details = "Token has expired"


class InvalidTokenError(BaseSecurityException):
    """Exception raised when a token is invalid"""
    details = "Invalid token"


class PasswordChangeError(BaseSecurityException):
    """Exception raised when a password is incorrect"""
    details = "Password is incorrect"

class InvalidRefreshTokenError(BaseSecurityException):
    """Exception raised when a refresh token is invalid"""
    details = "Invalid refresh token or expired"


class SessionExpiredError(BaseSecurityException):
    """Exception raised when a session is expired"""
    details = "Could not establish secure session. Please try again"

