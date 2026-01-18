import os
from datetime import date
from deepagents import create_deep_agent
from langchain_core.messages import HumanMessage

from pep2testcase.core.state import AgentState
from pep2testcase.core.schema import PepKnowledgeGraph
from pep2testcase.core.agents.tools.fetcher import fetch_pep_content
from pep2testcase.core.llm import get_model

from .prompts import LEAD_RESEARCHER_PROMPT, SUB_RESEARCHER_PROMPT
from pep2testcase.core.agents.tools.search import internet_search
from pep2testcase.core.middleware import SimpleToolLoggerMiddleware

import logging

logger = logging.getLogger(__name__)

async def research_node(state: AgentState):
    """
    Agent node that performs deep research on the PEP content using a Multi-Agent system.
    """
    logger.info("--- [Phase 1] Starting Deep Research (Multi-Agent) ---")
    
    # Update UI if available
    if hasattr(state, "ui_manager") and state.ui_manager:
        state.ui_manager.set_phase("Phase 1: 需求分析 Agent")
    
    # 1. Prepare Context & Prompts
    today = date.today().isoformat()
    pep_url = state.pep_url
    
    # Fetch content upfront if possible to give context, 
    # but the agent can also fetch it.
    # Let's fetch it if missing so we can provide a snippet in the initial message.
    raw_content = state.raw_pep_content
    if not raw_content:
        logger.info(f"Fetching PEP from {pep_url}...")
        # Since fetch_pep_content is sync, we run it directly. 
        # In a fully async world, we might want to run_in_executor or make it async.
        raw_content = fetch_pep_content(pep_url)
        # Store back in state later
    
    # Format Prompts
    lead_prompt = LEAD_RESEARCHER_PROMPT.format(
        date=today,
        pep_url=pep_url,
        raw_content=raw_content,
        max_iterations=3,
        max_concurrent=3
    )
    
    sub_prompt = SUB_RESEARCHER_PROMPT.format(
        date=today
    )
    
    # Initialize Model from factory
    model_instance = get_model()
    
    # Retrieve UI Manager from state if available (injected by graph config)
    ui_manager = state.ui_manager if hasattr(state, "ui_manager") else None
    
    # Create Middleware
    lead_middleware = SimpleToolLoggerMiddleware(ui_manager=ui_manager, agent_name="Lead Researcher")
    sub_middleware = SimpleToolLoggerMiddleware(ui_manager=ui_manager, agent_name="Sub Researcher")
    
    # 2. Define Sub Agent
    research_subagent_config = {
        "name": "research_subagent",
        "description": "Used to research specific in-depth questions, check dependencies, or verify edge cases.",
        "system_prompt": sub_prompt,
        "tools": [internet_search, fetch_pep_content],
        "model": model_instance,
        "middleware": [sub_middleware], # Specific middleware for Sub Agent
    }
    
    # 3. Create Deep Agent (Lead)
    # response_format=PepKnowledgeGraph ensures the final output is structured
    
    agent = create_deep_agent(
        model=model_instance,
        subagents=[research_subagent_config],
        system_prompt=lead_prompt,
        tools=[fetch_pep_content], # Lead can also fetch directly
        response_format=PepKnowledgeGraph,
        name="lead_researcher",
        middleware=[lead_middleware], # Specific middleware for Lead Agent
        debug=False
    )
    
    # 4. Invoke Agent
    # We provide the initial instruction.
    initial_instruction = (
        f"Please research the PEP at {pep_url}.\n"
        f"The full content is provided in your system prompt.\n"
        f"Analyze it first, then use Sub-Researchers to investigate references or ambiguities.\n"
        f"Please generate the complete PepKnowledgeGraph."
    )
    
    logger.info("Invoking Deep Research Agent...")
    try:
        # invoke returns a dict with keys like 'messages', 'structured_response' (if configured)
        # Note: compiled graph output keys depend on the graph definition in deepagents.
        # Assuming deepagents standard output.
        result = await agent.ainvoke({
            "messages": [HumanMessage(content=initial_instruction)]
        })
        
        # 5. Extract Result
        knowledge_graph = result.get("structured_response")
        
        # Fallback if structured_response is missing but present in messages
        if not knowledge_graph:
            logger.warning("No 'structured_response' found directly. Checking artifacts...")
            # deepagents might return it differently. 
            # If strictly typed, it might be in 'final_output' or similar.
            # For now, let's assume it works or we catch the error.
        
        if knowledge_graph:
            logger.info(f"Research Complete. Found {len(knowledge_graph.root_modules)} root modules.")
        
        return {
            "raw_pep_content": raw_content,
            "knowledge_graph": knowledge_graph,
            "current_phase": "research_done",
            # We don't overwrite messages to keep the main state clean, or we can append summary.
        }
        
    except Exception as e:
        logger.error(f"Error in Deep Research Agent: {e}", exc_info=True)
        return {"current_phase": "error"}
