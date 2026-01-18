import pytest
import os
from unittest.mock import MagicMock, patch
from pep2testcase.core.agents.tools.search import internet_search
from pep2testcase.core.config import settings

def test_internet_search_real_integration():
    """
    Integration test using the real Tavily API key from .env.
    This test requires a valid TAVILY_API_KEY in the environment or .env file.
    """
    # Ensure we have a key (loaded from .env by config.py)
    # Note: settings are loaded at module level, so we check the property
    api_key = settings.tavily.API_KEY
    if not api_key or api_key.startswith("tvly-..."):
        pytest.skip("Skipping integration test: No valid TAVILY_API_KEY found in .env")

    # Perform a real search
    query = "Python PEP 8 summary"
    result = internet_search(query)
    
    # Verify we got a string back
    assert isinstance(result, str)
    # Verify it's not the mock fallback message
    assert "Mock search result" not in result
    # Verify it contains relevant content (Tavily usually finds these)
    # We use lower() to be case-insensitive
    assert "pep" in result.lower() or "python" in result.lower()
    assert "8" in result

@patch.dict('os.environ', {}, clear=True)
def test_internet_search_no_key_fallback():
    # We need to reload settings or patch the settings object because settings might have cached the env var
    # But our Settings class reads os.getenv every time in the property, so patch.dict on os.environ works!
    
    # However, we must ensure the key is actually gone.
    # The @patch.dict clears os.environ for the duration of this test.
    
    result = internet_search("PEP 8")
    assert "Mock search result" in result
    assert "PEP 8" in result

@patch('pep2testcase.core.agents.tools.search.TavilyClient')
def test_internet_search_error_handling(mock_tavily_cls):
    # We still mock the error case to ensure our try/except block works
    # This doesn't hit the network, which is fine for testing error handling logic
    
    # We need to ensure settings returns a key so it tries to use the client
    with patch.dict('os.environ', {'TAVILY_API_KEY': 'test-key'}):
        mock_client = MagicMock()
        mock_tavily_cls.return_value = mock_client
        mock_client.search.side_effect = Exception("Simulated API Error")
        
        result = internet_search("PEP 8")
        assert "Error during search" in result
        assert "Simulated API Error" in result
