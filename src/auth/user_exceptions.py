class BaseUserException(Exception):
    def __init__(self, details: str | None = None) -> None:
        if details is None:
            details = "Something went wrong during account operation"
        super().__init__(details)


class UserNotFoundException(BaseUserException):
    """Exception raised when user not found with provided credentials"""
    details = "User not found with provided credentials"


class UserAreLoggedOutException(BaseUserException):
    """Exception raised when user logged out with provided credentials"""
    details = "User logged out with provided credentials"


class UserCreateException(BaseUserException):
    """Exception raised when user create with provided credentials is failed"""
    details = "User create with provided credentials is failed"

class UserAlreadyExistsException(BaseUserException):
    """Exception raised when user already exists with provided credentials"""
    details = "User already exists with provided credentials"