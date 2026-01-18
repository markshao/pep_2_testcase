from datetime import datetime
from typing import List, Optional

from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree
from rich.style import Style

class UIManager:
    """
    Manages the TUI layout and state for PEP-2-TestCase.
    """
    def __init__(self, url: str):
        self.url = url
        self.phase = "Initializing"
        self.console = Console()
        self.layout = self._make_layout()
        
        # State
        self.main_todos: List[dict] = [] # Lead Agent's Plan
        self.sub_todos: List[dict] = []  # Sub Agent's Plan
        self.active_agent = "Lead Researcher" # Tracks who is currently executing
        
        self.logs: List[Any] = []  # Stores Renderables (Text, Panels, Trees)
        self.max_logs = 50
        
        # Live Context
        self.live = Live(self.layout, console=self.console, refresh_per_second=4, screen=True)

    def _make_layout(self) -> Layout:
        layout = Layout(name="root")
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body")
        )
        layout["body"].split_row(
            Layout(name="plan", ratio=1),
            Layout(name="logs", ratio=2)
        )
        return layout

    def start(self):
        self.live.start()

    def stop(self):
        self.live.stop()

    def update(self):
        """Re-renders the layout components based on current state."""
        self.layout["header"].update(self._render_header())
        self.layout["plan"].update(self._render_plan())
        self.layout["logs"].update(self._render_logs())

    def set_phase(self, phase: str):
        self.phase = phase
        self.update()

    def set_active_agent(self, agent_name: str):
        """Called by middleware when an agent starts acting."""
        self.active_agent = agent_name
        
        # If Lead Researcher takes back control, clear sub-agent plan
        if "Lead" in agent_name:
            self.sub_todos = []
            
        self.update()

    def update_plan(self, todos: List[dict], source: str = "Lead Researcher"):
        if "Lead" in source:
            self.main_todos = todos
        else:
            self.sub_todos = todos
        self.update()

    def add_log(self, renderable):
        self.logs.append(renderable)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        self.update()

    def _render_header(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        
        grid.add_row(
            f"Phase: [bold magenta]{self.phase}[/]",
            f"Actor: [bold yellow]{self.active_agent}[/]"
        )
        return Panel(
            grid, 
            style="white on black", 
            title=f"[bold blue]PEP-2-TestCase[/] | Target: [cyan]{self.url}[/]",
            title_align="left"
        )

    def _render_plan(self) -> Panel:
        # Decide which plan to show or show both
        # Strategy: Always show Main Plan. If Sub Plan exists, show it below or overlay.
        
        content_group = []
        
        # 1. Main Plan
        if self.main_todos:
            table = Table(box=None, show_header=True, expand=True, title="[bold blue]Lead Plan[/]", title_justify="left")
            table.add_column("S", width=2)
            table.add_column("Task")
            
            for todo in self.main_todos:
                status = todo.get("status", "pending")
                content = todo.get("content", "")
                
                icon = "○"
                style = "dim"
                if status == "completed":
                    icon = "●"
                    style = "green"
                elif status == "in_progress":
                    icon = "▶"
                    style = "bold yellow"
                
                table.add_row(icon, content, style=style)
            content_group.append(table)
        else:
            content_group.append(Text("No Lead Plan yet...", style="dim"))

        # 2. Sub Plan (if active)
        if self.sub_todos:
            content_group.append(Text("\n" + "─" * 30 + "\n", style="dim"))
            
            sub_table = Table(box=None, show_header=True, expand=True, title="[bold magenta]Sub-Agent Plan[/]", title_justify="left")
            sub_table.add_column("S", width=2)
            sub_table.add_column("Task")
            
            for todo in self.sub_todos:
                status = todo.get("status", "pending")
                content = todo.get("content", "")
                
                icon = "○"
                style = "dim"
                if status == "completed":
                    icon = "●"
                    style = "green"
                elif status == "in_progress":
                    icon = "▶"
                    style = "bold yellow"
                
                sub_table.add_row(icon, content, style=style)
            content_group.append(sub_table)

        return Panel(Group(*content_group), title="Execution Plan", border_style="blue")

    def _render_logs(self) -> Panel:
        if not self.logs:
            return Panel("Waiting for activity...", title="Activity Log", border_style="cyan")
            
        return Panel(Group(*self.logs), title="Activity Log", border_style="cyan")
