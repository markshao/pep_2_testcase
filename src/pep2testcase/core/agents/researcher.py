import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from pep2testcase.core.state import AgentState
from pep2testcase.core.schema import PepSpecification
from pep2testcase.core.tools.fetcher import fetch_pep_content

# Global constant for prompt
RESEARCH_SYSTEM_PROMPT = """You are a Senior Technical Analyst specialized in Python Enhancement Proposals (PEPs).
Your goal is to deeply understand the provided PEP content and extract a structured specification.

Focus on:
1. Identifying all normative requirements (MUST, SHOULD, MAY).
2. Identifying constraints and edge cases.
3. flagging any ambiguities that might affect implementation or testing.

Do not summarize generic info; focus on testable points.
"""

def research_node(state: AgentState):
    """
    Agent node that performs deep research on the PEP content.
    """
    # Initialize LLM inside the node to avoid import-time errors if API key is missing
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    print("--- [Phase 1] Starting Deep Requirement Research ---")
    
    # 1. Fetch content if not already present
    pep_content = state.raw_pep_content
    if not pep_content:
        print(f"Fetching PEP from {state.pep_url}...")
        pep_content = fetch_pep_content(state.pep_url)
    
    # 2. Analyze with LLM
    print("Analyzing PEP content...")
    structured_llm = llm.with_structured_output(PepSpecification)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESEARCH_SYSTEM_PROMPT),
        ("user", "Here is the PEP content:\n\n{pep_text}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        specification = chain.invoke({"pep_text": pep_content})
        print(f"Successfully extracted {len(specification.requirements)} requirements.")
        return {
            "raw_pep_content": pep_content,
            "specification": specification,
            "current_phase": "research_done"
        }
    except Exception as e:
        print(f"Error in research phase: {e}")
        # In a real system, we might retry or return an error state
        return {"current_phase": "error"}
