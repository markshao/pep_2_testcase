from pep2testcase.core.graph import create_graph
from pep2testcase.core.agents.tools.fetcher import fetch_pep_content

def test_graph_construction():
    app = create_graph()
    assert app is not None

def test_fetch_pep_callable():
    # Simple check that the function is importable and callable
    assert callable(fetch_pep_content)
