from src.config import Settings


def get_settings() -> Settings:
    """
        Retrieve the application settings based on the current environment.
    """

    return Settings()