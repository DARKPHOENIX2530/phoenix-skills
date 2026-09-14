"""
Ponytail Help Skill - Quick-reference card for all ponytail modes, skills, and commands
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode, Gemini, Qoder, Cursor, Windsurf, Grok
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class PonytailHelpSkill:
    """Quick-reference card for all ponytail modes, skills, and commands."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
    
    def get_levels(self) -> Dict:
        return {
            "Lite": {
                "trigger": "/ponytail lite",
                "description": "Build what's asked, name the lazier alternative in one line."
            },
            "Full": {
                "trigger": "/ponytail",
                "description": "The ladder enforced: YAGNI → stdlib → native → one line → minimum. Default."
            },
            "Ultra": {
                "trigger": "/ponytail ultra",
                "description": "YAGNI extremist. Deletion before addition. Challenges requirements before building."
            }
        }
    
    def get_skills(self) -> Dict:
        return {
            "ponytail": {
                "trigger": "/ponytail",
                "description": "Lazy mode itself. Simplest solution that works."
            },
            "ponytail-review": {
                "trigger": "/ponytail-review",
                "description": "Over-engineering review: `L42: yagni: factory, one product. Inline.`"
            },
            "ponytail-audit": {
                "trigger": "/ponytail-audit",
                "description": "Whole-repo over-engineering audit: ranked list of what to delete."
            },
            "ponytail-debt": {
                "trigger": "/ponytail-debt",
                "description": "Harvest `ponytail:` shortcut comments into a tracked ledger."
            },
            "ponytail-gain": {
                "trigger": "/ponytail-gain",
                "description": "Measured-impact scoreboard: less code, less cost, more speed."
            },
            "ponytail-help": {
                "trigger": "/ponytail-help",
                "description": "This card."
            }
        }
    
    def get_deactivate(self) -> List[str]:
        return [
            "Say \"stop ponytail\" or \"normal mode\".",
            "Resume anytime with `/ponytail`.",
            "`/ponytail off` also works."
        ]
    
    def get_config_defaults(self) -> Dict:
        return {
            "environment_variable": {
                "name": "PONYTAIL_DEFAULT_MODE",
                "values": ["lite", "full", "ultra", "off"],
                "description": "Highest priority. Example: export PONYTAIL_DEFAULT_MODE=ultra"
            },
            "config_file": {
                "path": "~/.config/ponytail/config.json",
                "windows_path": "%APPDATA%\\ponytail\\config.json",
                "example": {"defaultMode": "lite"},
                "description": "Set \"off\" to disable auto-activation on session start."
            },
            "resolution_order": [
                "Environment variable",
                "Config file",
                "Default: full"
            ]
        }
    
    def get_update_info(self) -> str:
        return (
            "Enable auto-update: open `/plugin`, go to Marketplaces, pick ponytail, Enable auto-update. "
            "Claude Code then pulls new versions at startup (run `/reload-plugins` when it prompts). "
            "Manual refresh: `/plugin marketplace update ponytail` then `/reload-plugins`."
        )
    
    def get_codex_info(self) -> str:
        return (
            "Codex uses `@ponytail`, `@ponytail-review`, and `@ponytail-help`; "
            "Claude Code and OpenCode use the slash-command forms above. "
            "OpenCode ships all six as slash commands."
        )
    
    def get_full_card(self) -> str:
        """Return the complete help card."""
        lines = ["# Ponytail Help", "", "Display this reference card when invoked. One-shot, do NOT change mode,", "write flag files, or persist anything.", ""]
        
        lines.append("## Levels")
        lines.append("")
        lines.append("| Level | Trigger | What change |")
        lines.append("|-------|---------|-------------|")
        for level, info in self.get_levels().items():
            lines.append(f"| **{level}** | `{info['trigger']}` | {info['description']} |")
        lines.append("")
        lines.append("Level sticks until changed or session end.")
        lines.append("")
        
        lines.append("## Skills")
        lines.append("")
        lines.append("| Skill | Trigger | What it does |")
        lines.append("|-------|---------|--------------|")
        for skill, info in self.get_skills().items():
            lines.append(f"| **{skill}** | `{info['trigger']}` | {info['description']} |")
        lines.append("")
        lines.append("Codex uses `@ponytail`, `@ponytail-review`, and `@ponytail-help`;")
        lines.append("Claude Code and OpenCode use the slash-command forms above.")
        lines.append("OpenCode ships all six as slash commands.")
        lines.append("")
        
        lines.append("## Deactivate")
        for item in self.get_deactivate():
            lines.append(item)
        lines.append("")
        
        lines.append("## Configure Default Mode")
        config = self.get_config_defaults()
        lines.append(f"**Environment variable** (highest priority):")
        lines.append(f"```bash")
        lines.append(f"export PONYTAIL_DEFAULT_MODE=ultra")
        lines.append(f"```")
        lines.append(f"**Config file** (`{config['config_file']['path']}`, Windows: `{config['config_file']['windows_path']}`):")
        lines.append(f"```json")
        lines.append(f'{{ "defaultMode": "lite" }}')
        lines.append(f"```")
        lines.append(f"Set `\"off\"` to disable auto-activation on session start, activate manually")
        lines.append(f"with `/ponytail` when wanted.")
        lines.append(f"")
        lines.append(f"Resolution: {' > '.join(config['resolution_order'])}.")
        lines.append(f"")
        
        lines.append("## Update")
        lines.append(self.get_update_info())
        lines.append("")
        
        lines.append("## More")
        lines.append("Full docs + examples: https://github.com/DietrichGebert/ponytail")
        
        return "\n".join(lines)
    
    def get_skill_manifest(self) -> Dict:
        with open(Path(__file__).parent / "skill.json") as f:
            return json.load(f)


def run(action: str, **kwargs) -> str:
    skill = PonytailHelpSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "get_levels":
        return json.dumps(skill.get_levels(), indent=2)
    elif action == "get_skills":
        return json.dumps(skill.get_skills(), indent=2)
    elif action == "get_deactivate":
        return "\n".join(skill.get_deactivate())
    elif action == "get_config":
        return json.dumps(skill.get_config_defaults(), indent=2)
    elif action == "get_update":
        return skill.get_update_info()
    elif action == "get_codex":
        return skill.get_codex_info()
    elif action == "get_card":
        return skill.get_full_card()
    elif action == "get_manifest":
        return json.dumps(skill.get_skill_manifest(), indent=2)
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ponytail_help.py <action> [key=value ...]")
        sys.exit(1)
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    print(run(action, **kwargs))