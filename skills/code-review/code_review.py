"""
Code Review Skill - Security, style, complexity analysis
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode
"""
import subprocess
import json
import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path


class CodeReviewSkill:
    """Automated code review with multiple analyzers."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.checks = self.config.get("checks", ["security", "complexity", "style"])
        self.max_issues = self.config.get("max_issues", 50)
    
    def _run_tool(self, cmd: List[str], cwd: str = None, input_data: str = None) -> Dict:
        """Run a CLI tool and return structured result."""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60,
                input=input_data
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {"error": "Tool timed out", "returncode": -1}
        except Exception as e:
            return {"error": str(e), "returncode": -1}
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a single Python file."""
        results = {}
        
        # Security - bandit
        if "security" in self.checks:
            results["security"] = self._run_bandit(file_path)
        
        # Complexity - radon
        if "complexity" in self.checks:
            results["complexity"] = self._run_radon(file_path)
        
        # Style - pylint
        if "style" in self.checks:
            results["style"] = self._run_pylint(file_path)
        
        return results
    
    def _run_bandit(self, file_path: str) -> Dict:
        """Run bandit security linter."""
        result = self._run_tool(["bandit", "-f", "json", file_path])
        if result.get("error"):
            return {"error": result["error"]}
        try:
            data = json.loads(result["stdout"])
            issues = data.get("results", [])
            return {
                "tool": "bandit",
                "issue_count": len(issues),
                "issues": issues[:self.max_issues]
            }
        except:
            return {"raw": result["stdout"][:2000]}
    
    def _run_radon(self, file_path: str) -> Dict:
        """Run radon complexity analyzer."""
        result = self._run_tool(["radon", "cc", "-j", file_path])
        if result.get("error"):
            return {"error": result["error"]}
        try:
            data = json.loads(result["stdout"])
            return {
                "tool": "radon",
                "functions": data.get(file_path, [])
            }
        except:
            return {"raw": result["stdout"][:2000]}
    
    def _run_pylint(self, file_path: str) -> Dict:
        """Run pylint style checker."""
        result = self._run_tool(["pylint", "--output-format=json", file_path])
        if result.get("error"):
            return {"error": result["error"]}
        try:
            data = json.loads(result["stdout"])
            return {
                "tool": "pylint",
                "issue_count": len(data),
                "issues": data[:self.max_issues]
            }
        except:
            return {"raw": result["stdout"][:2000]}
    
    def analyze_directory(self, dir_path: str, pattern: str = "*.py") -> Dict:
        """Analyze all matching files in directory."""
        files = list(Path(dir_path).rglob(pattern))
        results = {"files_analyzed": len(files), "files": {}}
        
        for f in files[:20]:  # Limit to 20 files
            results["files"][str(f)] = self.analyze_file(str(f))
        
        return results
    
    def review_diff(self, diff_text: str) -> Dict:
        """Review a git diff (for PR review)."""
        # Write diff to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.diff', delete=False) as f:
            f.write(diff_text)
            diff_file = f.name
        
        try:
            # Use a simple approach: extract changed files and analyze them
            results = {"review": "Diff analysis - extract changed hunks and run per-file checks"}
            # For now, return structured placeholder
            return results
        finally:
            os.unlink(diff_file)
    
    def format_report(self, results: Dict) -> str:
        """Format analysis results as human-readable report."""
        lines = ["=" * 60, "CODE REVIEW REPORT", "=" * 60, ""]
        
        for file_path, file_results in results.get("files", {}).items():
            lines.append(f"\n📄 {file_path}")
            lines.append("-" * 40)
            
            for check_type, check_result in file_results.items():
                if isinstance(check_result, dict) and "error" in check_result:
                    lines.append(f"  ⚠️ {check_type}: {check_result['error']}")
                    continue
                
                tool = check_result.get("tool", check_type)
                count = check_result.get("issue_count", 0)
                
                if count == 0:
                    lines.append(f"  ✅ {tool}: No issues")
                else:
                    lines.append(f"  ⚠️ {tool}: {count} issues")
                    for issue in check_result.get("issues", [])[:5]:
                        if isinstance(issue, dict):
                            msg = issue.get("message", issue.get("text", str(issue)))
                            line = issue.get("line_number", issue.get("lineno", "?"))
                            lines.append(f"    Line {line}: {msg[:100]}")
        
        return "\n".join(lines)


# Agent-agnostic entry point
def run(action: str, **kwargs) -> str:
    """Main entry point.
    
    Actions:
    - analyze_file: file_path=...
    - analyze_directory: dir_path=..., pattern=*.py
    - review_diff: diff=...
    """
    skill = CodeReviewSkill(kwargs.get("config", {}))
    kwargs.pop("config", None)
    
    if action == "analyze_file":
        results = skill.analyze_file(kwargs["file_path"])
        return skill.format_report({"files": {kwargs["file_path"]: results}})
    
    elif action == "analyze_directory":
        results = skill.analyze_directory(kwargs["dir_path"], kwargs.get("pattern", "*.py"))
        return skill.format_report(results)
    
    elif action == "review_diff":
        return json.dumps(skill.review_diff(kwargs.get("diff", "")), indent=2)
    
    else:
        return f"Unknown action: {action}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python code_review.py <action> [key=value ...]")
        sys.exit(1)
    
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    
    print(run(action, **kwargs))