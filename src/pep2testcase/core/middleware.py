from typing import Callable, Awaitable, Any, Optional
from langchain.agents.middleware.types import AgentMiddleware, ModelRequest, ModelResponse
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

class SimpleToolLoggerMiddleware(AgentMiddleware):
    """
    Middleware that logs tool calls to a UI manager if provided, 
    otherwise falls back to console printing (or does nothing).
    Tracks:
    1. Plan updates (write_todos)
    2. Sub-agent invocations (task)
    3. Tool usages (fetch_pep_content, internet_search)
    """
    
    def __init__(self, ui_manager: Optional[Any] = None, agent_name: str = "Agent"):
        self.ui = ui_manager
        self.agent_name = agent_name

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """
        Intercepts the model response to log tool calls nicely.
        """
        # Notify UI about active agent context before call
        if self.ui:
            self.ui.set_active_agent(self.agent_name)

        response = await handler(request)
        
        msg = None
        if hasattr(response, "result"):
            msg = response.result
            if isinstance(msg, list) and len(msg) > 0:
                msg = msg[0]
        
        # Check for Sub-Agent Completion (No tools called)
        # If a Sub-Agent finishes (returns text without tool calls), 
        # we optimistically mark the current Lead Task as completed.
        if self.ui and "Sub" in self.agent_name:
            has_tools = msg and hasattr(msg, "tool_calls") and msg.tool_calls
            if not has_tools:
                self.ui.mark_current_lead_task_completed()
        
        if msg and hasattr(msg, "tool_calls") and msg.tool_calls:
            # Reorder tool calls to process 'write_todos' FIRST.
            # This ensures the UI Plan is updated BEFORE we log the actual execution actions.
            # This fixes the race condition where logs show activity for a task that isn't yet marked 'in_progress'.
            tool_calls = sorted(
                msg.tool_calls, 
                key=lambda x: 0 if x.get("name") == "write_todos" else 1
            )
            
            for tc in tool_calls:
                name = tc.get("name")
                args = tc.get("args")
                
                if name == "write_todos":
                    self._handle_plan(args)
                elif name == "task":
                    self._handle_subagent(args)
                    # When Lead Agent delegates, optimistically start the next task
                    if self.ui and "Lead" in self.agent_name:
                        self.ui.mark_next_lead_task_in_progress()
                else:
                    # Log all other tools generically
                    self._handle_tool(name, args) 
                
        return response

    def _handle_plan(self, args: dict):
        """Updates the plan in UI."""
        todos = args.get("todos", [])
        if not todos:
            return

        if self.ui:
            self.ui.update_plan(todos, source=self.agent_name)
        else:
            # Fallback for tests/non-ui mode
            pass

    def _handle_subagent(self, args: dict):
        """Logs sub-agent invocation."""
        sub_type = args.get("subagent_type", "unknown")
        desc = args.get("description", "")
        
        tree = Tree(f"🤖 [bold magenta]Sub-Agent Invocation: {sub_type}[/]")
        tree.add(f"[bold]Instruction:[/]\n{desc}")
        
        if self.ui:
            self.ui.add_log(Panel(tree, border_style="magenta", title=f"[Delegate] by {self.agent_name}", title_align="left"))

    def _handle_tool(self, name: str, args: dict):
        """Logs standard tool call."""
        display_args = args.copy()
        
        title = f"🛠️  Tool Call: {name}"
        color = "cyan"
        
        content = Text()
        for k, v in display_args.items():
            content.append(f"{k}: ", style="bold")
            content.append(f"{v}\n")
            
        if self.ui:
            self.ui.add_log(Panel(content, border_style=color, title=f"[{color}]{title}[/] ({self.agent_name})", title_align="left"))
