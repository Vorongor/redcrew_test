class BasePlaceError(Exception):
    """Raised when a project failed processing"""

    def __init__(self, details: str | None = None) -> None:
        if details is None:
            details = "Something went wrong during project operation"
        super().__init__(details)


class PlaceAlreadyExistsInProjectError(BasePlaceError):
    """Raised when a place has already been created"""
    details = "The place has already been created"


class ProjectLimitReachedError(BasePlaceError):
    """Raised when reached a requests limit"""
    details = "Raised when reached a requests limit"


class PlaceDoesNotExistError(BasePlaceError):
    """Raised when a place has not been created"""
    details = "The place has not been created"


class InvalidExternalPlaceError(BasePlaceError):
    """Raised when an external place cannot be created"""
    details = "The external id for the place is not valid"
