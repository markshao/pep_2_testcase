import logging
from langchain_core.prompts import ChatPromptTemplate

from pep2testcase.core.state import AgentState
from pep2testcase.core.schema import TestPlan, PepKnowledgeGraph, FeatureModule
from pep2testcase.core.llm import get_model

logger = logging.getLogger(__name__)

# Global constant for prompt
TESTER_SYSTEM_PROMPT = """You are a Senior QA Architect.
Your goal is to design a comprehensive Test Plan based on the provided PEP Knowledge Graph (Mind Map).

Strategies:
1. Cover every Requirement Point identified in the spec.
2. Use Equivalence Partitioning and Boundary Value Analysis.
3. Include Positive, Negative, and Edge Case tests.
4. If a requirement is "SHOULD", ensure there's a test for when it is NOT met (if applicable) or verification of the recommendation.
5. Pay attention to Global Constraints and Ambiguities.

Output a structured Test Plan containing a list of Test Cases.
Each Test Case MUST have:
- id: A unique identifier (e.g., TC-001)
- related_req_ids: A list of Requirement IDs (REQ-...) that this test covers.
- title: A short title.
- description: Detailed objective.
- preconditions: List of prerequisites.
- steps: List of execution steps.
- expected_result: The expected outcome.
- test_type: One of Positive, Negative, EdgeCase, Security, Performance.
"""

def format_module(module: FeatureModule, level: int = 1) -> str:
    """Recursively formats a feature module and its requirements."""
    indent = "#" * level
    text = f"{indent} Module: {module.name}\n"
    if module.description:
        text += f"Description: {module.description}\n"
    
    if module.requirements:
        text += "Requirements:\n"
        for req in module.requirements:
            text += f"- [{req.id}] ({req.priority}) {req.description}\n"
            text += f"  Quote: {req.source_quote}\n"
    
    text += "\n"
    
    for sub in module.sub_modules:
        text += format_module(sub, level + 1)
        
    return text

def format_knowledge_graph(kg: PepKnowledgeGraph) -> str:
    """Formats the entire Knowledge Graph into a string for the prompt."""
    text = f"PEP Title: {kg.title}\nStatus: {kg.status}\n\n"
    
    if kg.global_constraints:
        text += "Global Constraints:\n"
        for req in kg.global_constraints:
            text += f"- [{req.id}] ({req.priority}) {req.description}\n"
        text += "\n"
        
    if kg.ambiguities:
        text += "Ambiguities (Handle carefully):\n"
        for amb in kg.ambiguities:
            text += f"- {amb}\n"
        text += "\n"
        
    text += "--- Feature Modules ---\n"
    for module in kg.root_modules:
        text += format_module(module, 1)
        
    return text

async def tester_node(state: AgentState):
    """
    Agent node that designs test cases based on the specification.
    """
    # Initialize LLM from factory
    llm = get_model(temperature=0.2)
    
    # Update UI if available
    if hasattr(state, "ui_manager") and state.ui_manager:
        state.ui_manager.set_phase("Phase 2: Test Case 生成 Agent")
    
    logger.info("--- [Phase 2] Starting Test Case Design ---")
    
    kg = state.knowledge_graph
    if not kg:
        logger.error("Error: No Knowledge Graph found in state. Did the Researcher fail?")
        return {"current_phase": "error"}
    
    # Prepare context from KG
    spec_text = format_knowledge_graph(kg)
        
    # Count requirements for logging (rough count)
    req_count = spec_text.count("REQ-")
    logger.info(f"Designing tests for approx {req_count} requirements...")
    
    structured_llm = llm.with_structured_output(TestPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", TESTER_SYSTEM_PROMPT),
        ("user", "Here is the PEP Knowledge Graph:\n\n{spec_text}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        test_plan = await chain.ainvoke({"spec_text": spec_text})
        logger.info(f"Successfully designed {len(test_plan.test_cases)} test cases.")
        return {
            "test_plan": test_plan,
            "current_phase": "done"
        }
    except Exception as e:
        logger.error(f"Error in testing phase: {e}", exc_info=True)
        return {"current_phase": "error"}
