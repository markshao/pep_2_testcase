import pytest
from unittest.mock import MagicMock, AsyncMock
from pep2testcase.core.middleware import SimpleToolLoggerMiddleware
from langchain.agents.middleware.types import ModelRequest, ModelResponse

@pytest.mark.asyncio
async def test_middleware_generic_tool_logging():
    # Mock UI Manager
    mock_ui = MagicMock()
    middleware = SimpleToolLoggerMiddleware(ui_manager=mock_ui)
    
    # Mock Handler
    async def mock_handler(request):
        # Create a dummy response structure that mimics what DeepAgents/LangChain might return
        # The middleware looks for response.result.tool_calls
        
        # We need a result object that has tool_calls attribute
        mock_result = MagicMock()
        mock_result.tool_calls = [
            {"name": "unknown_tool", "args": {"foo": "bar"}},
            {"name": "fetch_pep_content", "args": {"url": "http://example.com"}}
        ]
        
        response = MagicMock()
        response.result = [mock_result] # Middleware expects a list and takes first element
        return response

    # Mock Request
    request = MagicMock()
    
    # Run middleware
    await middleware.awrap_model_call(request, mock_handler)
    
    # Verify UI was called for both tools
    assert mock_ui.add_log.call_count == 2
    
    # Verify "unknown_tool" was logged
    # add_log is called with a Panel. We can inspect the Panel content if needed,
    # but checking call count is enough to prove the "else" branch was taken.
