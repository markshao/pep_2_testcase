import argparse
import sys
import os
import logging
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.markdown import Markdown

from pep2testcase.core.graph import create_graph
from pep2testcase.core.schema import TestPlan, PepKnowledgeGraph
from pep2testcase.cli.ui import UIManager

# Load environment variables
load_dotenv()

# Configure logging to use Rich
# We remove the global console handler because UIManager will handle display
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[logging.NullHandler()] # Suppress default handlers to avoid UI conflict
)

# Suppress noisy logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger("pep2tc")
# Use a fallback console for non-UI output (like errors before UI starts)
fallback_console = Console()

def render_markdown(plan: TestPlan) -> str:
    """Renders the TestPlan to a Markdown string."""
    md = [f"# Test Plan: {plan.pep_title}", ""]
    
    md.append(f"**Total Test Cases:** {len(plan.test_cases)}")
    md.append("")
    
    for tc in plan.test_cases:
        md.append(f"## {tc.id}: {tc.title}")
        md.append(f"**Type:** {tc.test_type} | **Related Reqs:** {', '.join(tc.related_req_ids)}")
        md.append("")
        md.append(f"**Description:** {tc.description}")
        md.append("")
        
        if tc.preconditions:
            md.append("**Preconditions:**")
            for pre in tc.preconditions:
                md.append(f"- {pre}")
            md.append("")
            
        md.append("**Steps:**")
        for i, step in enumerate(tc.steps, 1):
            md.append(f"{i}. {step}")
        md.append("")
        
        md.append(f"**Expected Result:** {tc.expected_result}")
        md.append("")
        md.append("---")
        md.append("")
        
    return "\n".join(md)

def save_artifacts(pep_url: str, final_state: dict, output_dir: Path):
    """Saves intermediate and final artifacts to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Save Knowledge Graph
    kg = final_state.get("knowledge_graph")
    if kg and isinstance(kg, PepKnowledgeGraph):
        kg_path = output_dir / "knowledge_graph.json"
        with open(kg_path, "w") as f:
            f.write(kg.model_dump_json(indent=2))
        fallback_console.print(f"[green]✅ Saved Knowledge Graph to:[/green] {kg_path}")
    
    # 2. Save Test Plan (JSON)
    plan = final_state.get("test_plan")
    if plan and isinstance(plan, TestPlan):
        plan_json_path = output_dir / "test_plan.json"
        with open(plan_json_path, "w") as f:
            f.write(plan.model_dump_json(indent=2))
        fallback_console.print(f"[green]✅ Saved Test Plan (JSON) to:[/green] {plan_json_path}")
        
        # 3. Save Test Plan (Markdown)
        md_content = render_markdown(plan)
        plan_md_path = output_dir / "test_plan.md"
        with open(plan_md_path, "w") as f:
            f.write(md_content)
        fallback_console.print(f"[green]✅ Saved Test Plan (Markdown) to:[/green] {plan_md_path}")
        
        # Show summary
        fallback_console.print(Panel(
            f"Successfully generated {len(plan.test_cases)} test cases.",
            title="[bold green]Workflow Complete[/]",
            border_style="green"
        ))

async def run_workflow(url: str, output_dir: str):
    # Initialize UI Manager
    ui = UIManager(url)
    
    # Extract PEP number for folder name if possible
    pep_id = url.rstrip("/").split("-")[-1]
    if not pep_id.isdigit():
        pep_id = "output"
    
    artifact_dir = Path(output_dir) / f"pep-{pep_id}"
    
    app = create_graph()
    
    # Initial State with UI Manager injected
    initial_state = {
        "pep_url": url,
        "ui_manager": ui
    }
    
    ui.start()
    try:
        ui.set_phase("Starting Workflow...")
        
        # We invoke the graph. The middleware inside nodes will update UI via ui_manager
        final_state = await app.ainvoke(initial_state)
        
        ui.stop()
        
        save_artifacts(url, final_state, artifact_dir)
            
    except Exception as e:
        ui.stop()
        logger.error(f"Workflow failed: {e}", exc_info=True)
        fallback_console.print(f"[bold red]Workflow failed:[/bold red] {e}")
        sys.exit(1)
    finally:
        # Ensure UI is stopped if something crashes hard
        try:
            ui.stop()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description="PEP-2-TestCase: Generate test cases from PEP URL.")
    parser.add_argument("url", help="The URL of the PEP (e.g., https://peps.python.org/pep-0008/)")
    parser.add_argument("--output-dir", "-o", help="Directory to save artifacts", default="artifacts")
    
    args = parser.parse_args()
    
    if not os.getenv("OPENAI_API_KEY"):
        fallback_console.print("[bold red]Error:[/] OPENAI_API_KEY not found. Please set it in .env file.")
        sys.exit(1)
        
    asyncio.run(run_workflow(args.url, args.output_dir))

if __name__ == "__main__":
    main()
