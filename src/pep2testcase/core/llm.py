import os
from langchain_openai import ChatOpenAI
from pep2testcase.core.config import settings

def get_model(temperature: float = 0) -> ChatOpenAI:
    """
    Returns a configured ChatOpenAI instance based on environment variables.
    Supports Kimi, DeepSeek, etc. via OPENAI_BASE_URL.
    
    Configuration is loaded from pep2testcase.core.config.settings
    """
    api_key = settings.model.API_KEY
    base_url = settings.model.BASE_URL
    model_name = settings.model.MODEL_NAME

    # Ensure we don't pass None to base_url if it's not set, 
    # though ChatOpenAI handles None by using default.
    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature
    )
