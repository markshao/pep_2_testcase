from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

from pep2testcase.core.schema import PepSpecification, TestPlan

class AgentState(BaseModel):
    """
    Global state for the PEP-2-TestCase workflow.
    """
    # Input
    pep_url: str = Field(..., description="The URL of the PEP to process")
    
    # Internal Processing
    messages: Annotated[List[BaseMessage], add_messages] = Field(default_factory=list, description="Chat history for context")
    raw_pep_content: Optional[str] = Field(None, description="The raw text content of the PEP")
    
    # Phase 1 Output
    specification: Optional[PepSpecification] = Field(None, description="Structured requirements")
    
    # Phase 2 Output
    test_plan: Optional[TestPlan] = Field(None, description="Generated test plan")
    
    # Control Flow
    iteration_count: int = Field(0, description="Counter for research iterations")
    current_phase: str = Field("init", description="Current phase of the workflow")
