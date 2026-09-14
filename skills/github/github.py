"""
GitHub Skill - Repo, Issue, PR, Action operations via gh CLI or API
Compatible with: Phoenix, Claude Code, Codex, Hermes, OpenCode
"""
import subprocess
import json
import os
from typing import Dict, List, Optional, Any
import shlex


class GitHubSkill:
    """GitHub operations via gh CLI (preferred) or direct API."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.use_cli = self.config.get("use_cli", True)
        self.token = self.config.get("token") or os.environ.get("GITHUB_TOKEN")
    
    def _run_gh(self, args: List[str]) -> Dict:
        """Run gh CLI command and return parsed JSON."""
        cmd = ["gh"] + args
        if self.token:
            env = os.environ.copy()
            env["GITHUB_TOKEN"] = self.token
        else:
            env = os.environ
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            if result.returncode != 0:
                return {"error": result.stderr.strip() or "gh command failed"}
            return json.loads(result.stdout) if result.stdout.strip() else {"success": True}
        except json.JSONDecodeError:
            return {"output": result.stdout.strip()}
        except Exception as e:
            return {"error": str(e)}
    
    # Repository operations
    def repo_create(self, name: str, private: bool = False, description: str = "") -> Dict:
        args = ["repo", "create", name]
        if private:
            args.append("--private")
        else:
            args.append("--public")
        if description:
            args.extend(["--description", description])
        args.extend(["--json", "name,url,sshUrl"])
        return self._run_gh(args)
    
    def repo_view(self, repo: str) -> Dict:
        return self._run_gh(["repo", "view", repo, "--json", "name,description,url,stars,forks,issues,primaryLanguage"])
    
    def repo_list(self, owner: str = "", limit: int = 20) -> Dict:
        args = ["repo", "list", "--limit", str(limit), "--json", "name,description,url,stars,updatedAt"]
        if owner:
            args.insert(2, owner)
        return self._run_gh(args)
    
    # Issue operations
    def issue_create(self, repo: str, title: str, body: str = "", labels: List[str] = None) -> Dict:
        args = ["issue", "create", "--repo", repo, "--title", title, "--body", body]
        if labels:
            for label in labels:
                args.extend(["--label", label])
        args.extend(["--json", "number,title,url"])
        return self._run_gh(args)
    
    def issue_list(self, repo: str, state: str = "open", limit: int = 20) -> Dict:
        return self._run_gh([
            "issue", "list", "--repo", repo, "--state", state,
            "--limit", str(limit), "--json", "number,title,state,labels,url,createdAt"
        ])
    
    def issue_view(self, repo: str, number: int) -> Dict:
        return self._run_gh(["issue", "view", str(number), "--repo", repo, "--json", "number,title,body,state,labels,comments,url"])
    
    # PR operations
    def pr_create(self, repo: str, title: str, body: str = "", base: str = "main", head: str = "") -> Dict:
        args = ["pr", "create", "--repo", repo, "--title", title, "--body", body, "--base", base]
        if head:
            args.extend(["--head", head])
        args.extend(["--json", "number,title,url"])
        return self._run_gh(args)
    
    def pr_list(self, repo: str, state: str = "open", limit: int = 20) -> Dict:
        return self._run_gh([
            "pr", "list", "--repo", repo, "--state", state,
            "--limit", str(limit), "--json", "number,title,state,url,headRefName,baseRefName"
        ])
    
    def pr_view(self, repo: str, number: int) -> Dict:
        return self._run_gh(["pr", "view", str(number), "--repo", repo, "--json", "number,title,body,state,url,headRefName,baseRefName,commits"])
    
    def pr_merge(self, repo: str, number: int, method: str = "merge") -> Dict:
        return self._run_gh(["pr", "merge", str(number), "--repo", repo, f"--{method}"])
    
    # Action/Workflow operations
    def workflow_list(self, repo: str) -> Dict:
        return self._run_gh(["workflow", "list", "--repo", repo, "--json", "id,name,state,path"])
    
    def workflow_run(self, repo: str, workflow: str, ref: str = "main", inputs: Dict = None) -> Dict:
        args = ["workflow", "run", workflow, "--repo", repo, "--ref", ref]
        if inputs:
            for k, v in inputs.items():
                args.extend(["-f", f"{k}={v}"])
        return self._run_gh(args)
    
    def run_list(self, repo: str, limit: int = 10) -> Dict:
        return self._run_gh(["run", "list", "--repo", repo, "--limit", str(limit), "--json", "id,name,conclusion,status,headBranch,createdAt"])
    
    def run_view(self, repo: str, run_id: int) -> Dict:
        return self._run_gh(["run", "view", str(run_id), "--repo", repo, "--json", "id,name,conclusion,status,jobs,logsUrl"])
    
    # Generic command pass-through
    def run_command(self, command: str) -> Dict:
        """Run arbitrary gh command string."""
        args = shlex.split(command)
        if args[0] != "gh":
            args = ["gh"] + args
        return self._run_gh(args[1:])


# Agent-agnostic entry point
def run(action: str, **kwargs) -> str:
    """Main entry point for any agent.
    
    Actions: repo_create, repo_view, repo_list, issue_create, issue_list, issue_view,
             pr_create, pr_list, pr_view, pr_merge, workflow_list, workflow_run,
             run_list, run_view, run_command
    """
    skill = GitHubSkill(kwargs.get("config", {}))
    method = getattr(skill, action, None)
    
    if not method:
        return f"Unknown action: {action}"
    
    # Remove config from kwargs
    kwargs.pop("config", None)
    result = method(**kwargs)
    
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python github.py <action> [key=value ...]")
        sys.exit(1)
    
    action = sys.argv[1]
    kwargs = {}
    for arg in sys.argv[2:]:
        if "=" in arg:
            k, v = arg.split("=", 1)
            kwargs[k] = v
    
    print(run(action, **kwargs))