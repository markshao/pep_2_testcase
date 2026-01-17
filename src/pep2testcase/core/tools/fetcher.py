import requests
from bs4 import BeautifulSoup
import re

def fetch_pep_content(url: str) -> str:
    """
    Fetches and parses the text content of a PEP from its URL.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find the main content article
        content = soup.find('article', class_='content')
        if not content:
            content = soup.find('div', class_='document')
            
        if content:
            text = content.get_text(separator='\n')
        else:
            # Fallback to body
            text = soup.body.get_text(separator='\n')
            
        # Basic cleanup: remove excessive newlines
        clean_text = re.sub(r'\n{3,}', '\n\n', text)
        return clean_text.strip()
    except Exception as e:
        return f"Error fetching PEP content: {str(e)}"
