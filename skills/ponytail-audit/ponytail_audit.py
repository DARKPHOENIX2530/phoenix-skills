"""
Ponytail Audit Skill - Whole-repo over-engineering audit
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode, Gemini, Qoder, Cursor, Windsurf, Grok
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class PonytailAuditSkill:
    """Whole-repo audit for over-engineering."""
    
    TAGS = {
        "delete": "dead code, unused flexibility, speculative feature. Replacement: nothing.",
        "stdlib": "hand-rolled thing the standard library ships. Name the function.",
        "native": "dependency or code doing what the platform already does. Name the feature.",
        "yagni": "abstraction with one implementation, config nobody sets, layer with one caller.",
        "shrink": "same logic, fewer lines. Show the shorter form."
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def get_tags(self) -> Dict[str, str]:
        return self.TAGS
    
    def get_hunt_targets(self) -> List[str]:
        return [
            "Deps the stdlib or platform already ships",
            "Single-implementation interfaces",
            "Factories with one product",
            "Wrappers that only delegate",
            "Files exporting one thing",
            "Dead flags and config",
            "Hand-rolled stdlib"
        ]
    
    def get_output_format(self) -> str:
        return "One line per finding, ranked: `<tag> <what to cut>. <replacement>. [path]`. End with `net: -<N> lines, -<M> deps possible.` Nothing to cut: `Lean already. Ship.`"
    
    def get_boundaries(self) -> List[str]:
        return [
            "Scope: over-engineering and complexity only.",
            "Correctness bugs, security holes, and performance are explicitly out of scope.",
            "Route them to a normal review pass.",
            "Lists findings, applies nothing. One-shot."
        ]
    
    def get_skill_manifest(self) -> Dict:
        with open(Path(__file__).parent / "skill.json") as f:
            return json.load(f)


def run(action: str, **kwargs) -> str:
    skill = PonytailAuditSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "get_tags":
        return json.dumps(skill.get_tags(), indent=2)
    elif action == "get_hunt":
        return "\n".join(skill.get_hunt_targets())
    elif action == "get_output":
        return skill.get_output_format()
    elif action == "get_boundaries":
        return "\n".join(skill.get_boundaries())
    elif action == "get_manifest":
        return json.dumps(skill.get_skill_manifest(), indent=2)
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ponytail_audit.py <action> [key=value ...]")
        sys.exit(1)
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    print(run(action, **kwargs))