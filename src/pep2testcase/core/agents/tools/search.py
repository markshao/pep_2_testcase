import logging
from tavily import TavilyClient
import os
from pep2testcase.core.agents.tools.fetcher import fetch_pep_content
from pep2testcase.core.config import settings

logger = logging.getLogger(__name__)

def internet_search(query: str) -> str:
    """
    Search the internet for technical details, mailing list discussions, and documentation.
    Useful for finding context about PEPs, resolving ambiguities, or checking referenced implementations.
    """
    api_key = settings.tavily.API_KEY
    if not api_key:
        # Fallback for dev/test without key
        logger.warning(f"No TAVILY_API_KEY found. Mocking search for: {query}")
        return f"Mock search result for '{query}': Found related PEP discussions and documentation."
    
    try:
        client = TavilyClient(api_key=api_key)
        # Using advanced search depth for better technical results
        response = client.search(query=query, search_depth="advanced")
        
        # Format results concisely
        results = response.get("results", [])
        formatted = "\n".join([f"- [{r['title']}]({r['url']}): {r['content'][:200]}..." for r in results])
        return formatted if formatted else "No relevant results found."
    except Exception as e:
        return f"Error during search: {str(e)}"

