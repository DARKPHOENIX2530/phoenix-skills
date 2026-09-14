"""
Ponytail Gain Skill - Measured impact scoreboard
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode, Gemini, Qoder, Cursor, Windsurf, Grok
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class PonytailGainSkill:
    """Show ponytail's measured impact as a compact scoreboard."""
    
    BENCHMARK_DATA = {
        "lines_of_code": {
            "no_skill": 100,
            "ponytail_range": "6-20%",
            "reduction": "80-94%"
        },
        "cost": {
            "no_skill": 100,
            "ponytail_range": "23-53%",
            "reduction": "47-77%"
        },
        "speed": {
            "improvement": "3-6x faster"
        }
    }
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def get_scoreboard(self) -> str:
        return """  ponytail gain                     benchmark median · 5 tasks · 3 models

  Lines of code   no-skill  ████████████████████  100%
                  ponytail  ██▌·················    6-20%   ▼ 80-94%
  Cost            no-skill  ████████████████████  100%
                  ponytail  █████▌··············   23-53%  ▼ 47-77%
  Speed           ponytail  ▸ 3-6x faster

  This repo:  /ponytail-debt  (shortcuts you deferred)
              /ponytail-audit (what's still cuttable)"""
    
    def get_honesty_boundary(self) -> str:
        return (
            "These are benchmark medians, not this repo. NEVER print a per-repo savings "
            "number (\"you saved X lines/tokens here\"): the unbuilt version was never "
            "written, so there is no real baseline to subtract from in a live repo. The "
            "only real per-repo figures come from `/ponytail-debt` (a counted ledger), "
            "and this card points there instead of inventing one."
        )
    
    def get_benchmark_details(self) -> Dict:
        return {
            "tasks": ["email validator", "debounce", "CSV sum", "countdown timer", "rate limiter"],
            "models": ["Haiku", "Sonnet", "Opus"],
            "source": "benchmarks/ and README"
        }
    
    def get_boundaries(self) -> List[str]:
        return [
            "One-shot display. Edits nothing, changes no mode.",
            "Benchmark medians only - never per-repo numbers.",
            "Points to /ponytail-debt for real per-repo figures."
        ]
    
    def get_skill_manifest(self) -> Dict:
        with open(Path(__file__).parent / "skill.json") as f:
            return json.load(f)


def run(action: str, **kwargs) -> str:
    skill = PonytailGainSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "get_scoreboard":
        return skill.get_scoreboard()
    elif action == "get_honesty":
        return skill.get_honesty_boundary()
    elif action == "get_benchmark":
        return json.dumps(skill.get_benchmark_details(), indent=2)
    elif action == "get_boundaries":
        return "\n".join(skill.get_boundaries())
    elif action == "get_manifest":
        return json.dumps(skill.get_skill_manifest(), indent=2)
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ponytail_gain.py <action> [key=value ...]")
        sys.exit(1)
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    print(run(action, **kwargs))