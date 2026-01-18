import logging
import pytest

@pytest.fixture(autouse=True, scope="session")
def configure_logging():
    """
    Suppress verbose logs from libraries during tests.
    """
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
