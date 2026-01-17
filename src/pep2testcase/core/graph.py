from langgraph.graph import StateGraph, END
from pep2testcase.core.state import AgentState
from pep2testcase.core.agents.researcher import research_node
from pep2testcase.core.agents.tester import tester_node

def create_graph():
    """
    Constructs the LangGraph workflow for PEP-2-TestCase.
    """
    workflow = StateGraph(AgentState)
    
    # Define Nodes
    workflow.add_node("researcher", research_node)
    workflow.add_node("tester", tester_node)
    
    # Define Edges
    # Start -> Researcher -> Tester -> End
    # In a more complex version, we would have conditional edges for loops/reviews
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "tester")
    workflow.add_edge("tester", END)
    
    # Compile
    app = workflow.compile()
    return app
