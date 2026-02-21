class BaseProjectError(Exception):
    """Raised when a project failed processing"""

    def __init__(self, details: str | None = None) -> None:
        if details is None:
            details = "Something went wrong during project operation"
        super().__init__(details)


class ProjectDoesNotExistError(BaseProjectError):
    """Raised when a project does not exist"""
    details = "Project does not exist"

class ProjectHasVisitedPlacesError(BaseProjectError):
    """Raised when a project may be deleted with visited places"""
    details = "If project has visited places, it cannot be deleted"
