"""
Ponytail Skill - Lazy senior dev mode for AI agents
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode, Gemini, Qoder, Cursor, Windsurf, Grok
Based on: https://github.com/DietrichGebert/ponytail (MIT License)
"""
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum


class PonytailLevel(Enum):
    LITE = "lite"
    FULL = "full"
    ULTRA = "ultra"
    OFF = "off"


class PonytailSkill:
    """Ponytail - Lazy senior dev mode. Forces the simplest solution that works."""
    
    LADDER = [
        "Does this need to exist at all? (YAGNI)",
        "Already in this codebase? Reuse it.",
        "Stdlib does it? Use it.",
        "Native platform feature covers it? Use it.",
        "Already-installed dependency solves it? Use it.",
        "Can it be one line? One line.",
        "Only then: the minimum code that works."
    ]
    
    NEVER_LAZY = [
        "input validation at trust boundaries",
        "error handling that prevents data loss",
        "security measures",
        "accessibility basics",
        "anything explicitly requested"
    ]
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.level = self.config.get("level", PonytailLevel.FULL.value)
        self.active = self.level != PonytailLevel.OFF.value
    
    def get_ladder(self) -> List[str]:
        """Return the decision ladder."""
        return self.LADDER
    
    def get_rules(self) -> List[str]:
        """Return the core rules."""
        return [
            "No unrequested abstractions: no interface with one implementation, no factory for one product, no config for a value that never changes.",
            "No boilerplate, no scaffolding 'for later', later can scaffold for itself.",
            "Deletion over addition. Boring over clever, clever is what someone decodes at 3am.",
            "Fewest files possible. Shortest working diff wins — but only once you understand the problem.",
            "Complex request? Ship the lazy version and question it in the same response.",
            "Two stdlib options, same size? Take the one that's correct on edge cases.",
            "Mark deliberate simplifications with a `ponytail:` comment naming the ceiling and upgrade path."
        ]
    
    def get_output_pattern(self) -> str:
        """Return the output pattern."""
        return "[code] → skipped: [X], add when [Y]."
    
    def get_intensity_info(self) -> Dict:
        """Return intensity level descriptions."""
        return {
            PonytailLevel.LITE.value: "Build what's asked, but name the lazier alternative in one line. User picks.",
            PonytailLevel.FULL.value: "The ladder enforced. Stdlib and native first. Shortest diff, shortest explanation. Default.",
            PonytailLevel.ULTRA.value: "YAGNI extremist. Deletion before addition. Ship the one-liner and challenge the rest of the requirement in the same breath."
        }
    
    def get_never_lazy(self) -> List[str]:
        """Return things never to be lazy about."""
        return self.NEVER_LAZY
    
    def set_level(self, level: str) -> bool:
        """Set the intensity level."""
        if level in [l.value for l in PonytailLevel]:
            self.level = level
            self.active = level != PonytailLevel.OFF.value
            return True
        return False
    
    def get_current_level(self) -> str:
        return self.level
    
    def should_apply(self, task_type: str) -> bool:
        """Determine if ponytail should apply to this task."""
        coding_tasks = ["writing", "adding", "refactoring", "fixing", "reviewing", "designing", 
                       "choosing libraries", "choosing dependencies"]
        return self.active and any(t in task_type.lower() for t in coding_tasks)
    
    def get_skill_manifest(self) -> Dict:
        with open(Path(__file__).parent / "skill.json") as f:
            return json.load(f)


# Agent-agnostic entry point
def run(action: str, **kwargs) -> str:
    """Main entry point.
    
    Actions:
    - get_ladder: returns decision ladder
    - get_rules: returns core rules
    - get_intensity: returns intensity levels
    - get_output_pattern: returns output pattern
    - get_never_lazy: returns things never to be lazy about
    - set_level: level=...
    - get_level: returns current level
    - should_apply: task_type=...
    - get_manifest: returns skill.json
    """
    skill = PonytailSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "get_ladder":
        return json.dumps(skill.get_ladder(), indent=2)
    elif action == "get_rules":
        return json.dumps(skill.get_rules(), indent=2)
    elif action == "get_intensity":
        return json.dumps(skill.get_intensity_info(), indent=2)
    elif action == "get_output_pattern":
        return skill.get_output_pattern()
    elif action == "get_never_lazy":
        return json.dumps(skill.get_never_lazy(), indent=2)
    elif action == "set_level":
        level = kwargs.get("level", "")
        success = skill.set_level(level)
        return f"Level set to {level}" if success else f"Invalid level: {level}"
    elif action == "get_level":
        return skill.get_current_level()
    elif action == "should_apply":
        task_type = kwargs.get("task_type", "")
        return str(skill.should_apply(task_type)).lower()
    elif action == "get_manifest":
        return json.dumps(skill.get_skill_manifest(), indent=2)
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ponytail.py <action> [key=value ...]")
        sys.exit(1)
    
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    
    print(run(action, **kwargs))