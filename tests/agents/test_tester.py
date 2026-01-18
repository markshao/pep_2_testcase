import pytest
import logging
from pep2testcase.core.agents.tester.node import tester_node
from pep2testcase.core.state import AgentState
from pep2testcase.core.schema import PepKnowledgeGraph, FeatureModule, RequirementAtom

# Configure logging to see output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_tester_node_integration():
    """
    Integration test for the Tester Agent Node using a mock Knowledge Graph.
    This verifies that the prompt construction and LLM structured output work correctly.
    """
    
    # 1. Construct a Mock Knowledge Graph (simulating Researcher output)
    mock_kg = PepKnowledgeGraph(
        title="PEP 9999 - Mock Feature for Testing",
        status="Draft",
        root_modules=[
            FeatureModule(
                name="Core Syntax",
                description="Defines the new syntax for the feature.",
                sub_modules=[],
                requirements=[
                    RequirementAtom(
                        id="REQ-SYNTAX-001",
                        description="The feature MUST use the '=>' operator for mapping.",
                        priority="Must",
                        source_quote="Use '=>' for mapping.",
                        context_tags=["Syntax"]
                    ),
                    RequirementAtom(
                        id="REQ-SYNTAX-002",
                        description="The left operand SHOULD be a string literal.",
                        priority="Should",
                        source_quote="Left operand should be a string.",
                        context_tags=["Syntax"]
                    )
                ]
            ),
            FeatureModule(
                name="Error Handling",
                description="How to handle invalid inputs.",
                sub_modules=[],
                requirements=[
                    RequirementAtom(
                        id="REQ-ERROR-001",
                        description="Raise SyntaxError if '=>' is missing.",
                        priority="Must",
                        source_quote="Raise SyntaxError if missing.",
                        context_tags=["Error"]
                    )
                ]
            )
        ],
        global_constraints=[
            RequirementAtom(
                id="REQ-GLOBAL-001",
                description="Must be backward compatible.",
                priority="Must",
                source_quote="Backward compatible.",
                context_tags=["Compatibility"]
            )
        ],
        ambiguities=["It is unclear if '=>' can be overloaded."]
    )
    
    # 2. Create Agent State
    state = AgentState(
        pep_url="http://mock-url",
        knowledge_graph=mock_kg
    )
    
    # 3. Invoke the Tester Node
    logger.info("Invoking Tester Node...")
    result = await tester_node(state)
    
    # 4. Verify Results
    assert result["current_phase"] == "done"
    test_plan = result["test_plan"]
    
    assert test_plan is not None
    assert test_plan.pep_title == "PEP 9999 - Mock Feature for Testing"
    assert len(test_plan.test_cases) > 0
    
    logger.info(f"Generated {len(test_plan.test_cases)} test cases.")
    
    # Check coverage of requirements
    covered_reqs = set()
    for tc in test_plan.test_cases:
        covered_reqs.update(tc.related_req_ids)
        logger.info(f"TestCase [{tc.id}]: {tc.title} (Covers: {tc.related_req_ids})")
        
    assert "REQ-SYNTAX-001" in covered_reqs
    assert "REQ-ERROR-001" in covered_reqs
    
    # Check if ambiguity was noticed (optional, depends on LLM)
    # But we can check if any test case mentions ambiguity in description
