import pytest
from pep2testcase.core.agents.tools.fetcher import fetch_pep_content

def test_fetch_pep_content_real():
    """
    Integration test using real requests to fetch PEP 8 content.
    """
    url = "https://peps.python.org/pep-0718/"
    
    result = fetch_pep_content(url)
    
    # Basic Validation
    assert isinstance(result, str)
    assert len(result) > 100 # Should contain substantial content
    
    # Verify key content from PEP 8
    # Using specific phrases likely to be in the text
    assert "PEP 8" in result
    assert "Style Guide for Python Code" in result
    
    # Verify we stripped HTML tags effectively (simple check)
    assert "<html>" not in result
    assert "<body>" not in result

def test_fetch_pep_content_error_real():
    """
    Integration test for error handling with a real 404 URL.
    """
    url = "https://peps.python.org/pep-9999-invalid-url/"
    
    result = fetch_pep_content(url)
    
    assert "Error fetching PEP content" in result
    # Requests usually includes the status code in the exception message for 404
    assert "404" in result
