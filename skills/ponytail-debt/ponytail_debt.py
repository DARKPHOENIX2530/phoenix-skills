"""
Ponytail Debt Skill - Harvest ponytail: comments into a debt ledger
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode, Gemini, Qoder, Cursor, Windsurf, Grok
"""
import json
import subprocess
import re
from typing import Dict, List, Optional, Any
from pathlib import Path


class PonytailDebtSkill:
    """Harvest ponytail: comments into a debt ledger."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.comment_patterns = self.config.get("comment_patterns", [
            r"#\s*ponytail:",
            r"//\s*ponytail:",
            r"/\*\s*ponytail:",
            r";\s*ponytail:",
            r"--\s*ponytail:"
        ])
        self.exclude_dirs = self.config.get("exclude_dirs", [
            "node_modules", ".git", "dist", "build", "__pycache__",
            ".venv", "venv", "target", "out", "bin", "obj"
        ])
    
    def get_scan_command(self) -> str:
        return 'grep -rnE \'(#|//) ?ponytail:\' .'
    
    def get_exclude_dirs(self) -> List[str]:
        return self.exclude_dirs
    
    def get_output_format(self) -> str:
        return (
            "One row per marker, grouped by file:\n"
            "`<file>:<line>, <what was simplified>. ceiling: <the limit named>. upgrade: <the trigger to revisit>.`\n"
            "Convention: `ponytail: <ceiling>, <upgrade path>`\n"
            "Flag rot risk: markers with no upgrade path get `no-trigger` tag.\n"
            "End with `<N> markers, <M> with no trigger.` Nothing found: `No ponytail: debt. Clean ledger.`"
        )
    
    def get_comment_convention(self) -> str:
        return "ponytail: <ceiling>, <upgrade path>"
    
    def scan(self, root: str = ".") -> Dict:
        """Scan for ponytail: comments."""
        all_matches = []
        no_trigger_count = 0
        total_count = 0
        
        for pattern in self.comment_patterns:
            try:
                cmd = ["grep", "-rnE", pattern, root]
                for exclude in self.exclude_dirs:
                    cmd.extend(["--exclude-dir", exclude])
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout:
                    for line in result.stdout.strip().split('\n'):
                        if line:
                            total_count += 1
                            # Check for upgrade path
                            if "upgrade" not in line.lower() and "trigger" not in line.lower():
                                no_trigger_count += 1
                            all_matches.append(line)
            except Exception as e:
                pass
        
        return {
            "total_markers": total_count,
            "no_trigger_count": no_trigger_count,
            "matches": all_matches[:100]  # Limit output
        }
    
    def get_skill_manifest(self) -> Dict:
        with open(Path(__file__).parent / "skill.json") as f:
            return json.load(f)


def run(action: str, **kwargs) -> str:
    skill = PonytailDebtSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "get_scan_cmd":
        return skill.get_scan_command()
    elif action == "get_excludes":
        return "\n".join(skill.get_exclude_dirs())
    elif action == "get_output":
        return skill.get_output_format()
    elif action == "get_convention":
        return skill.get_comment_convention()
    elif action == "scan":
        root = kwargs.get("root", ".")
        return json.dumps(skill.scan(root), indent=2)
    elif action == "get_manifest":
        return json.dumps(skill.get_skill_manifest(), indent=2)
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ponytail_debt.py <action> [key=value ...]")
        sys.exit(1)
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    print(run(action, **kwargs))