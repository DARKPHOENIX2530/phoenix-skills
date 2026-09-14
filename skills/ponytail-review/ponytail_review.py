"""
Ponytail Review Skill - Code review for over-engineering
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode, Gemini, Qoder, Cursor, Windsurf, Grok
"""
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path


class PonytailReviewSkill:
    """Code review focused exclusively on over-engineering."""
    
    TAGS = {
        "delete": "dead code, unused flexibility, speculative feature. Replacement: nothing.",
        "stdlib": "hand-rolled thing the standard library ships. Name the function.",
        "native": "dependency or code doing what the platform already does. Name the feature.",
        "yagni": "abstraction with one implementation, config nobody sets, layer with one caller.",
        "shrink": "same logic, fewer lines. Show the shorter form."
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def get_format(self) -> str:
        return "L<line>: <tag> <what>. <replacement>., or <file>:L<line>: ... for multi-file diffs."
    
    def get_tags(self) -> Dict[str, str]:
        return self.TAGS
    
    def get_examples(self) -> List[str]:
        return [
            "L12-38: stdlib: 27-line validator class. \"@\" in email, 1 line, real validation is the confirmation mail.",
            "L4: native: moment.js imported for one format call. Intl.DateTimeFormat, 0 deps.",
            "repo.py:L88: yagni: AbstractRepository with one implementation. Inline it until a second one exists.",
            "L52-71: delete: retry wrapper around an idempotent local call. Nothing replaces it.",
            "L30-44: shrink: manual loop builds dict. dict(zip(keys, values)), 1 line."
        ]
    
    def get_scoring_format(self) -> str:
        return "net: -<N> lines possible."
    
    def get_boundaries(self) -> List[str]:
        return [
            "Scope: over-engineering and complexity only.",
            "Correctness bugs, security holes, and performance are explicitly out of scope.",
            "Route them to a normal review pass, not this one.",
            "A single smoke test or assert-based self-check is the ponytail minimum, not bloat, never flag it for deletion.",
            "Does not apply the fixes, only lists them.",
            "\"stop ponytail-review\" or \"normal mode\": revert to verbose review style."
        ]
    
    def review_diff(self, diff_text: str) -> str:
        """Review a diff for over-engineering. Returns formatted findings."""
        # This is a placeholder - real implementation would parse diff
        return "Diff review requires parsing the diff. Provide diff text to analyze."
    
    def get_skill_manifest(self) -> Dict:
        with open(Path(__file__).parent / "skill.json") as f:
            return json.load(f)


def run(action: str, **kwargs) -> str:
    skill = PonytailReviewSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "get_format":
        return skill.get_format()
    elif action == "get_tags":
        return json.dumps(skill.get_tags(), indent=2)
    elif action == "get_examples":
        return "\n".join(skill.get_examples())
    elif action == "get_scoring":
        return skill.get_scoring_format()
    elif action == "get_boundaries":
        return "\n".join(skill.get_boundaries())
    elif action == "review_diff":
        diff = kwargs.get("diff", "")
        return skill.review_diff(diff)
    elif action == "get_manifest":
        return json.dumps(skill.get_skill_manifest(), indent=2)
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ponytail_review.py <action> [key=value ...]")
        sys.exit(1)
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    print(run(action, **kwargs))