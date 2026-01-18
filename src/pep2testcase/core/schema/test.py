from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class TestCase(BaseModel):
    id: str = Field(..., description="Unique ID, e.g., TC-001")
    related_req_ids: List[str] = Field(default_factory=list, description="List of Requirement IDs covered by this test case")
    title: str = Field(..., description="Title of the test case")
    description: str = Field(..., description="Detailed description or objective")
    preconditions: List[str] = Field(default_factory=list, description="Prerequisites for the test")
    steps: List[str] = Field(default_factory=list, description="Step-by-step execution instructions")
    expected_result: str = Field(..., description="Expected outcome")
    test_type: str = Field(..., description="Type of test (Positive, Negative, EdgeCase, Security, Performance)")
    
class TestPlan(BaseModel):
    pep_title: str
    test_cases: List[TestCase]
