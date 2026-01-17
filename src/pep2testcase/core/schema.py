from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class RequirementPoint(BaseModel):
    """Represents a single atomic requirement extracted from the PEP."""
    id: str = Field(..., description="Unique ID, e.g., REQ-001")
    category: Literal["Functional", "Constraint", "Interface", "Performance", "Security"] = Field(..., description="Category of the requirement")
    description: str = Field(..., description="Clear, concise description of the requirement")
    source_quote: str = Field(..., description="Original text from PEP supporting this requirement")
    priority: Literal["Must", "Should", "May"] = Field(..., description="Priority level based on RFC 2119")

class PepSpecification(BaseModel):
    """Structured understanding of the PEP."""
    pep_number: Optional[int] = Field(None, description="PEP number")
    title: str = Field(..., description="Title of the PEP")
    status: str = Field(..., description="Status of the PEP (e.g., Final, Active)")
    requirements: List[RequirementPoint] = Field(default_factory=list, description="List of extracted requirements")
    ambiguities: List[str] = Field(default_factory=list, description="List of ambiguous points requiring further clarification")

class TestCase(BaseModel):
    """Represents a single test case derived from requirements."""
    id: str = Field(..., description="Unique ID, e.g., TC-001")
    related_req_ids: List[str] = Field(..., description="List of Requirement IDs covered by this test case")
    title: str = Field(..., description="Title of the test case")
    description: str = Field(..., description="Detailed description or objective")
    preconditions: List[str] = Field(default_factory=list, description="Prerequisites for the test")
    steps: List[str] = Field(..., description="Step-by-step execution instructions")
    expected_result: str = Field(..., description="Expected outcome")
    test_type: Literal["Positive", "Negative", "EdgeCase", "Security", "Performance"] = Field(..., description="Type of test")
    
class TestPlan(BaseModel):
    """Collection of test cases."""
    pep_title: str
    test_cases: List[TestCase]
