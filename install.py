#!/usr/bin/env python3
"""
Phoenix Skills Installer
Installs skills for Phoenix, Claude Code, Codex, Hermes, OpenCode, etc.
"""
import json
import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class SkillInstaller:
    def __init__(self, skills_dir: str = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path(__file__).parent / "skills"
        self.registry_file = self.skills_dir.parent / "registry.json"
    
    def load_registry(self) -> Dict:
        if self.registry_file.exists():
            with open(self.registry_file) as f:
                return json.load(f)
        return {"skills": []}
    
    def list_skills(self) -> List[Dict]:
        registry = self.load_registry()
        return registry.get("skills", [])
    
    def get_skill_info(self, name: str) -> Optional[Dict]:
        for skill in self.list_skills():
            if skill["name"] == name:
                return skill
        return None
    
    def install_skill(self, name: str, target_dir: str = None) -> bool:
        """Install a skill to target directory."""
        skill_info = self.get_skill_info(name)
        if not skill_info:
            print(f"Skill '{name}' not found in registry")
            return False
        
        skill_path = self.skills_dir / skill_info["path"]
        if not skill_path.exists():
            print(f"Skill source not found: {skill_path}")
            return False
        
        # Default target: current dir / .skills / name
        if target_dir is None:
            target_dir = Path.cwd() / ".skills" / name
        else:
            target_dir = Path(target_dir) / name
        
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy skill
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(skill_path, target_dir)
        
        # Install dependencies if requirements.txt exists
        req_file = target_dir / "requirements.txt"
        if req_file.exists():
            print(f"Installing dependencies for {name}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=False)
        
        print(f"✅ Installed '{name}' to {target_dir}")
        return True
    
    def install_all(self, target_dir: str = None) -> int:
        """Install all skills from registry."""
        count = 0
        for skill in self.list_skills():
            if self.install_skill(skill["name"], target_dir):
                count += 1
        return count


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Phoenix Skills Installer")
    parser.add_argument("action", choices=["list", "install", "install-all", "info"], nargs="?", default="list")
    parser.add_argument("skill", nargs="?", help="Skill name to install")
    parser.add_argument("--target", "-t", help="Target directory")
    parser.add_argument("--skills-dir", help="Skills source directory")
    
    args = parser.parse_args()
    
    installer = SkillInstaller(args.skills_dir)
    
    if args.action == "list":
        skills = installer.list_skills()
        print("Available skills:")
        for s in skills:
            print(f"  {s['name']} v{s['version']} - {s['description']}")
            print(f"    Tags: {', '.join(s['tags'])}")
    
    elif args.action == "info":
        if not args.skill:
            print("Specify skill name")
            return 1
        skill = installer.get_skill_info(args.skill)
        if skill:
            print(json.dumps(skill, indent=2))
        else:
            print(f"Skill '{args.skill}' not found")
            return 1
    
    elif args.action == "install":
        if not args.skill:
            print("Specify skill name")
            return 1
        success = installer.install_skill(args.skill, args.target)
        return 0 if success else 1
    
    elif args.action == "install-all":
        count = installer.install_all(args.target)
        print(f"Installed {count} skills")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())