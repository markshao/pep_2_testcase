import argparse
import sys
import os
from dotenv import load_dotenv

from pep2testcase.core.graph import create_graph
from pep2testcase.core.schema import TestPlan

# Load environment variables
load_dotenv()

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

def main():
    parser = argparse.ArgumentParser(description="PEP-2-TestCase: Generate test cases from PEP URL.")
    parser.add_argument("url", help="The URL of the PEP (e.g., https://peps.python.org/pep-0008/)")
    parser.add_argument("--output", "-o", help="Output Markdown file path", default="test_plan.md")
    
    args = parser.parse_args()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Please set it in .env file.")
        sys.exit(1)
        
    print(f"Starting workflow for: {args.url}")
    
    app = create_graph()
    
    # Initial State
    initial_state = {"pep_url": args.url}
    
    # Run the graph
    # We use invoke for simple synchronous execution
    try:
        final_state = app.invoke(initial_state)
        
        test_plan = final_state.get("test_plan")
        if test_plan:
            md_content = render_markdown(test_plan)
            with open(args.output, "w") as f:
                f.write(md_content)
            print(f"\nSuccess! Test plan generated at: {args.output}")
        else:
            print("\nWorkflow finished but no test plan was generated.")
            
    except Exception as e:
        print(f"\nWorkflow failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
