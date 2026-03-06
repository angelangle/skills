#!/usr/bin/env python3
"""
Skill-Refiner + NotebookLM Integration Demo
演示 skill-refiner 如何与 NotebookLM 集成进行深度技能分析
"""

import subprocess
import json
import sys
from pathlib import Path

SKILLS_BASE_DIR = Path.home() / ".claude" / "skills"
NOTEBOOKLM_SKILL_DIR = SKILLS_BASE_DIR / "notebooklm-skill"

class NotebookLMIntegrationDemo:
    """
    Demonstrates the integration between skill-refiner and notebooklm-skill
    """

    def __init__(self):
        self.target_skill = None
        self.analysis_results = {}

    def phase1_local_discovery(self, skill_name: str):
        """
        Phase 1: Local skill discovery using skill_discovery.py
        """
        print("=" * 70)
        print("PHASE 1: Local Skill Discovery (skill_discovery.py)")
        print("=" * 70)

        self.target_skill = skill_name

        # Run local skill discovery
        discovery_script = SKILLS_BASE_DIR / "skill-refiner" / "scripts" / "skill_discovery.py"

        if discovery_script.exists():
            result = subprocess.run(
                [sys.executable, str(discovery_script), "--target", skill_name, "--find-similar", "--top-k", "5"],
                capture_output=True,
                text=True
            )
            print(f"\nDiscovery command: python3 skill_discovery.py --target {skill_name} --find-similar")
            print(f"\nDiscovery result:\n{result.stdout}")
            if result.stderr:
                print(f"Errors: {result.stderr}")
        else:
            print(f"Discovery script not found at {discovery_script}")

        print("\n✓ Local discovery completed")
        print("-" * 70)

    def phase2_external_discovery(self, query: str):
        """
        Phase 2: External skill discovery using find-skills (npx skills)
        """
        print("\n" + "=" * 70)
        print("PHASE 2: External Skill Discovery (find-skills / npx skills)")
        print("=" * 70)

        print(f"\nCommand: npx skills find {query}")
        print("\nExpected output format:")
        print("""
Install with npx skills add <owner/repo@skill>

vercel-labs/agent-skills@react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/react-best-practices

anthropic-labs/agent-skills@debug-patterns
└ https://skills.sh/anthropic-labs/agent-skills/debug-patterns
        """)

        # Simulate npx skills find execution
        try:
            result = subprocess.run(
                ["npx", "skills", "find", query],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                print(f"\nActual results:\n{result.stdout}")
            else:
                print(f"\nNote: npx skills not available in demo environment")
                print("In production, this would search skills.sh ecosystem")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("\nNote: npx skills requires Node.js and internet connection")
            print("This is a demonstration of the integration workflow")

        print("\n✓ External discovery workflow demonstrated")
        print("-" * 70)

    def phase3_notebooklm_analysis(self, skill_name: str):
        """
        Phase 3: Deep document analysis using NotebookLM
        """
        print("\n" + "=" * 70)
        print("PHASE 3: Deep Document Analysis (NotebookLM)")
        print("=" * 70)

        skill_path = SKILLS_BASE_DIR / skill_name / "SKILL.md"

        if not skill_path.exists():
            print(f"Skill {skill_name} not found at {skill_path}")
            return

        print(f"\nTarget skill: {skill_name}")
        print(f"Document path: {skill_path}")

        # Step 1: Check NotebookLM authentication
        print("\n--- Step 3.1: Check NotebookLM Authentication ---")
        print("Command: python scripts/run.py auth_manager.py status")
        print("""
Expected output:
{
  "authenticated": true,
  "method": "google_auth",
  "last_verified": "2026-03-05T10:30:00Z"
}
        """)

        # Step 2: Add skill document to NotebookLM (Smart Add pattern)
        print("\n--- Step 3.2: Add Skill Document to NotebookLM ---")
        print("Using Smart Add pattern:")
        print("1. First query to discover document content")
        print("2. Then add with discovered metadata")

        print(f"""
# Step 2a: Query to discover content
python scripts/run.py ask_question.py \\
    --question "What is the content of this skill? What are its main capabilities?" \\
    --notebook-url "file://{skill_path}"

# Step 2b: Add to library with discovered metadata
python scripts/run.py notebook_manager.py add \\
    --url "file://{skill_path}" \\
    --name "{skill_name}" \\
    --description "Operating system scheduler development expert skill" \\
    --topics "scheduler,os-dev,edf,cfs,real-time"
        """)

        # Step 3: Analyze with NotebookLM
        print("\n--- Step 3.3: Deep Analysis Questions ---")

        analysis_questions = [
            "Analyze the structure of this skill document. What are its strengths and weaknesses?",
            "What are the key capabilities of this skill? Are there any gaps?",
            "Compare this skill with general OS development best practices. What could be improved?",
            "What are the trigger keywords and scenarios for this skill? Are they comprehensive?",
            "Does this skill have sufficient practical examples and code snippets?"
        ]

        for i, question in enumerate(analysis_questions, 1):
            print(f"\nQ{i}: {question}")
            print(f"Command: python scripts/run.py ask_question.py --question \"{question}\" --notebook-id {skill_name}")

        print("\n✓ NotebookLM analysis workflow demonstrated")
        print("-" * 70)

    def phase4_synthesis(self):
        """
        Phase 4: Synthesize findings into improvement recommendations
        """
        print("\n" + "=" * 70)
        print("PHASE 4: Synthesis & Improvement Recommendations")
        print("=" * 70)

        print("""
Based on the three-phase analysis:

1. **Local Discovery**: Found related skills in local ecosystem
2. **External Discovery**: Identified similar skills from skills.sh
3. **NotebookLM Analysis**: Deep document analysis with source-grounded answers

Synthesis workflow:
┌─────────────────────────────────────────────────────────────────┐
│  Local Discovery     External Discovery     NotebookLM Analysis │
│       ↓                    ↓                       ↓           │
│  Similar skills      Best practices         Document insights  │
│       └────────────────┬───────────────────────┘               │
│                        ↓                                       │
│              Generate Improvement Plan                         │
│              ├─ Content gaps to fill                           │
│              ├─ Structure improvements                         │
│              ├─ Keyword optimizations                          │
│              └─ Tool/script additions                          │
└─────────────────────────────────────────────────────────────────┘
        """)

        print("\n✓ Synthesis workflow demonstrated")
        print("-" * 70)

    def run_full_demo(self, skill_name: str = "os-scheduler-dev"):
        """
        Run the complete integration demonstration
        """
        print("\n" + "=" * 70)
        print("SKILL-REFINER + NOTEBOOKLM INTEGRATION DEMO")
        print("=" * 70)
        print(f"\nTarget: Analyzing and improving '{skill_name}' skill")
        print("\nThis demo shows how skill-refiner integrates with:")
        print("  1. Local skill_discovery.py (Phase 1)")
        print("  2. External find-skills via npx skills (Phase 2)")
        print("  3. NotebookLM for deep document analysis (Phase 3)")

        self.phase1_local_discovery(skill_name)
        self.phase2_external_discovery("scheduler os-dev")
        self.phase3_notebooklm_analysis(skill_name)
        self.phase4_synthesis()

        print("\n" + "=" * 70)
        print("DEMO COMPLETE")
        print("=" * 70)
        print("""
Summary:
────────
This demonstration showed the integration workflow between skill-refiner
and external tools (find-skills, NotebookLM).

Key Integration Points:
1. skill-discovery.py → Local skill scanning and similarity analysis
2. npx skills find → External skill discovery from skills.sh
3. NotebookLM → Deep document analysis with source-grounded Q&A

In production, this would:
- Actually execute npx skills to find external skills
- Open browser for NotebookLM authentication
- Upload documents and retrieve analysis
- Generate concrete improvement recommendations

For now, the skill-refiner SKILL.md has been updated with these
integration capabilities and workflows.
        """)


def main():
    demo = NotebookLMIntegrationDemo()
    demo.run_full_demo("os-scheduler-dev")


if __name__ == "__main__":
    main()
