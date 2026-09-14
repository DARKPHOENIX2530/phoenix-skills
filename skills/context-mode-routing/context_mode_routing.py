"""
Context-Mode Routing Skill - Token optimization via context-mode MCP tools
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class ContextModeRoutingSkill:
    """Context-mode routing rules for token optimization."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.pinned_version = "1.0.169"
    
    def get_routing_rules(self) -> Dict:
        """Return the context-mode routing rules."""
        return {
            "core_tools": {
                "ctx_execute": "Run code, count/parse/filter - console.log() ONLY the answer",
                "ctx_batch_execute": "Many commands, one question",
                "ctx_search": "Prior work, decisions, indexed docs - batch all questions in ONE call",
                "ctx_index": "Store notes for later with descriptive source label",
                "ctx_fetch_and_index": "Web content then ctx_search",
                "ctx_stats": "Savings check"
            },
            "on_demand_tools": {
                "ctx_doctor": "Something broken (runtimes, hooks, FTS5)",
                "ctx_execute_file": "File too big to even reference",
                "ctx_upgrade": "Only when user explicitly approves version move",
                "ctx_purge": "Only with explicit user approval; wipes knowledge base",
                "ctx_insight": "Opens commercial dashboard; default NEVER"
            },
            "thresholds": {
                "output_lines": 20,
                "output_kb": 2,
                "shell_commands": 3,
                "description": "Use ctx_* tools when ANY threshold is met"
            }
        }
    
    def should_use_context_mode(self, task_description: str, expected_output_lines: int = 0, 
                                 expected_output_kb: float = 0, shell_command_count: int = 0,
                                 analyzes_files: bool = False, fetches_urls: bool = False,
                                 after_resume: bool = False) -> Dict:
        """Determine if context-mode tools should be used for a task."""
        reasons = []
        
        if expected_output_lines > 20:
            reasons.append(f"Expected output > 20 lines ({expected_output_lines})")
        if expected_output_kb > 2:
            reasons.append(f"Expected output > 2KB ({expected_output_kb})")
        if shell_command_count >= 3:
            reasons.append(f"3+ shell commands ({shell_command_count})")
        if analyzes_files:
            reasons.append("Analyzing/counting/filtering file content")
        if fetches_urls:
            reasons.append("Fetching URL content")
        if after_resume:
            reasons.append("After resume/compact - user asking about prior work")
        
        return {
            "use_context_mode": len(reasons) > 0,
            "reasons": reasons,
            "recommended_tools": self._recommend_tools(reasons)
        }
    
    def _recommend_tools(self, reasons: List[str]) -> List[str]:
        """Recommend specific context-mode tools based on reasons."""
        tools = []
        reason_text = " ".join(reasons).lower()
        
        if "shell commands" in reason_text or "many commands" in reason_text:
            tools.append("ctx_batch_execute")
        if "analyzing" in reason_text or "filtering" in reason_text or "counting" in reason_text:
            tools.append("ctx_execute")
        if "prior work" in reason_text or "decisions" in reason_text or "indexed docs" in reason_text:
            tools.append("ctx_search")
        if "web" in reason_text or "url" in reason_text or "fetching" in reason_text:
            tools.append("ctx_fetch_and_index")
        if "store" in reason_text or "notes" in reason_text:
            tools.append("ctx_index")
        
        # Always useful
        if not tools:
            tools = ["ctx_search", "ctx_stats"]
        
        return tools
    
    def get_skill_manifest(self) -> Dict:
        """Return the skill manifest matching skill.json."""
        with open(Path(__file__).parent / "skill.json") as f:
            return json.load(f)
    
    def get_version(self) -> str:
        return self.pinned_version


# Agent-agnostic entry point
def run(action: str, **kwargs) -> str:
    """Main entry point.
    
    Actions:
    - get_rules: returns routing rules
    - check_task: task_description=..., expected_output_lines=..., etc.
    - get_version: returns pinned version
    - get_manifest: returns skill.json content
    """
    skill = ContextModeRoutingSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "get_rules":
        return json.dumps(skill.get_routing_rules(), indent=2)
    
    elif action == "check_task":
        task_desc = kwargs.get("task_description", "")
        expected_lines = kwargs.get("expected_output_lines", 0)
        expected_kb = kwargs.get("expected_output_kb", 0)
        shell_count = kwargs.get("shell_command_count", 0)
        analyzes_files = kwargs.get("analyzes_files", False)
        fetches_urls = kwargs.get("fetches_urls", False)
        after_resume = kwargs.get("after_resume", False)
        
        result = skill.should_use_context_mode(
            task_desc, expected_lines, expected_kb, shell_count,
            analyzes_files, fetches_urls, after_resume
        )
        return json.dumps(result, indent=2)
    
    elif action == "get_version":
        return skill.get_version()
    
    elif action == "get_manifest":
        return json.dumps(skill.get_skill_manifest(), indent=2)
    
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python context_mode_routing.py <action> [key=value ...]")
        sys.exit(1)
    
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # Try to parse numbers/booleans
            if v.lower() in ("true", "false"):
                v = v.lower() == "true"
            elif v.isdigit():
                v = int(v)
            elif v.replace(".", "", 1).isdigit():
                v = float(v)
            kwargs[k] = v
    
    print(run(action, **kwargs))