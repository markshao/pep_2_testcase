from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class RequirementAtom(BaseModel):
    """
    Represents an atomic, testable requirement extracted from the PEP.
    This is the leaf node of the knowledge graph.
    """
    id: str = Field(..., description="Semantic Unique ID (e.g., REQ-SYNTAX-001)")
    description: str = Field(..., description="The actionable requirement description")
    priority: Literal["Must", "Should", "May"] = Field(..., description="Priority based on RFC 2119")
    source_quote: str = Field(..., description="Verbatim text or rough range from PEP supporting this requirement")
    context_tags: List[str] = Field(default_factory=list, description="Keywords context (e.g., 'Error Handling', 'C-API')")

class FeatureModule(BaseModel):
    """
    Represents a functional module or topic in the PEP.
    This forms the branches of the mind map.
    """
    name: str = Field(..., description="Module name (e.g., 'Assignment Expressions Syntax')")
    description: Optional[str] = Field(None, description="High-level summary of this module")
    
    # Recursive structure
    sub_modules: List['FeatureModule'] = Field(default_factory=list, description="Sub-modules under this topic")
    
    # Requirements attached to this module
    requirements: List[RequirementAtom] = Field(default_factory=list, description="Requirements specific to this module")

class PepKnowledgeGraph(BaseModel):
    """
    The root of the structured PEP understanding (Mind Map).
    """
    pep_number: Optional[int] = Field(None, description="PEP number")
    title: str = Field(..., description="Title of the PEP")
    status: str = Field(..., description="Status of the PEP (e.g., Final, Active)")
    
    # Root branches
    root_modules: List[FeatureModule] = Field(..., description="Top-level modules of the PEP")
    
    # Global info
    global_constraints: List[RequirementAtom] = Field(default_factory=list, description="Constraints that apply globally")
    ambiguities: List[str] = Field(default_factory=list, description="Unclear points requiring clarification")

# Update forward references
FeatureModule.model_rebuild()
