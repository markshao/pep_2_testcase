import logging
import pytest
import os
from pep2testcase.core.agents.researcher.node import research_node
from pep2testcase.core.state import AgentState
from pep2testcase.core.config import settings
from pep2testcase.core.schema import PepKnowledgeGraph

logger = logging.getLogger(__name__)

@pytest.mark.skipif(
    not settings.model.API_KEY or not settings.tavily.API_KEY,
    reason="Requires OPENAI_API_KEY and TAVILY_API_KEY"
)
@pytest.mark.asyncio
async def test_research_node_integration():
    """
    Integration test for the research node.
    This runs the actual agent workflow, so it costs money and time.
    """
    # 1. Setup State
    pep_url = "https://peps.python.org/pep-0338/"
    state = AgentState(pep_url=pep_url)
    
    logger.info(f"Starting research on {pep_url}")
    
    # 2. Invoke Node
    # The node returns a dict of updates
    updates = await research_node(state)
    
    # 3. Validation
    assert updates is not None
    assert updates["current_phase"] == "research_done"
    assert updates["raw_pep_content"] is not None
    assert len(updates["raw_pep_content"]) > 1000
    
    kg = updates.get("knowledge_graph")
    assert kg is not None
    assert isinstance(kg, PepKnowledgeGraph)
    
    # Check graph content
    assert len(kg.root_modules) > 0
    logger.info(f"Generated {len(kg.root_modules)} root modules.")
    
    first_module = kg.root_modules[0]
    logger.info(f"Sample Module: {first_module.name}")
    assert first_module.name
    assert len(first_module.requirements) >= 0 # Might be 0 if sub-modules have them
