from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from pep2testcase.core.state import AgentState
from pep2testcase.core.schema import TestPlan, PepSpecification

# Global constant for prompt
TESTER_SYSTEM_PROMPT = """You are a Senior QA Architect.
Your goal is to design a comprehensive Test Plan based on the provided PEP Specification.

Strategies:
1. Cover every Requirement Point identified in the spec.
2. Use Equivalence Partitioning and Boundary Value Analysis.
3. Include Positive, Negative, and Edge Case tests.
4. If a requirement is "SHOULD", ensure there's a test for when it is NOT met (if applicable) or verification of the recommendation.

Output a structured Test Plan.
"""

def tester_node(state: AgentState):
    """
    Agent node that designs test cases based on the specification.
    """
    # Initialize LLM inside the node to avoid import-time errors if API key is missing
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    
    print("--- [Phase 2] Starting Test Case Design ---")
    
    spec = state.specification
    if not spec:
        print("Error: No specification found in state.")
        return {"current_phase": "error"}
    
    # Prepare context from spec
    spec_text = f"PEP Title: {spec.title}\nStatus: {spec.status}\n\nRequirements:\n"
    for req in spec.requirements:
        spec_text += f"- [{req.id}] ({req.priority}) {req.category}: {req.description}\n"
    
    if spec.ambiguities:
        spec_text += "\nAmbiguities (Handle carefully):\n" + "\n".join(spec.ambiguities)
        
    print(f"Designing tests for {len(spec.requirements)} requirements...")
    
    structured_llm = llm.with_structured_output(TestPlan)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", TESTER_SYSTEM_PROMPT),
        ("user", "Here is the Requirement Specification:\n\n{spec_text}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        test_plan = chain.invoke({"spec_text": spec_text})
        print(f"Successfully designed {len(test_plan.test_cases)} test cases.")
        return {
            "test_plan": test_plan,
            "current_phase": "done"
        }
    except Exception as e:
        print(f"Error in testing phase: {e}")
        return {"current_phase": "error"}
