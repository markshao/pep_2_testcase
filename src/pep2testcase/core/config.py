import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class ModelSettings:
    @property
    def API_KEY(self) -> str | None:
        return os.getenv("OPENAI_API_KEY")

    @property
    def BASE_URL(self) -> str | None:
        return os.getenv("OPENAI_BASE_URL")

    @property
    def MODEL_NAME(self) -> str:
        return os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

class TavilySettings:
    @property
    def API_KEY(self) -> str | None:
        return os.getenv("TAVILY_API_KEY")

class Settings:
    """
    Application configuration settings.
    Reads from environment variables dynamically to support runtime changes and easy testing.
    """
    def __init__(self):
        self.model = ModelSettings()
        self.tavily = TavilySettings()

settings = Settings()
