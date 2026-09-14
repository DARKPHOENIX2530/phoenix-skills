# Phoenix Skills

**Cross-agent skills repository** — Use with Phoenix, Claude Code, Codex, Hermes, OpenCode, and any agent that supports Python skills.

## Quick Start

```bash
# Clone the repo
git clone https://github.com/DARKPHOENIX2530/phoenix-skills.git
cd phoenix-skills

# List available skills
python install.py list

# Install a skill
python install.py install web-search

# Install all skills
python install.py install-all
```

## Available Skills

| Skill | Version | Description | Tags |
|-------|---------|-------------|------|
| **nemo-rl-auto-research** | 1.0.0 | Automated RL research workflow with Nemo | rl, research, nemo, automation |
| **web-search** | 1.0.0 | Live web search via DuckDuckGo (no API key) | search, web, research |
| **github** | 1.0.0 | GitHub operations - issues, PRs, repos, actions | github, git, ci-cd, issues, prs |
| **code-review** | 1.0.0 | Automated code review - security, style, complexity | code-review, security, linting, quality |

## Skill Structure

Each skill is self-contained:

```
skills/<skill-name>/
├── skill.json          # Metadata (name, version, entry_point, requires, tags)
├── <skill_name>.py     # Main implementation (agent-agnostic)
├── requirements.txt    # Optional dependencies
└── README.md           # Skill-specific docs
```

## Using Skills in Your Agent

### Phoenix
```python
# In assistant.py or tools.py
from skills.web_search import WebSearchSkill
skill = WebSearchSkill()
results = skill.search("query")
```

### Claude Code / Codex / Hermes / OpenCode
```python
# Direct import (skills are pure Python)
from skills.github import GitHubSkill
skill = GitHubSkill()
result = skill.issue_list("owner/repo")
```

### Command Line (any agent)
```bash
# Run skill directly
python -m skills.web_search.web_search "search query"
python -m skills.github.github issue_list repo=owner/repo
python -m skills.code_review.code_review analyze_file file_path=myfile.py
```

## Skill Manifest (skill.json)

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "description": "What this skill does",
  "author": "DARKPHOENIX2530",
  "entry_point": "module:ClassName",
  "requires": ["dependency1", "dependency2"],
  "compatible_agents": ["phoenix", "claude-code", "codex", "hermes", "opencode"],
  "tags": ["tag1", "tag2"],
  "license": "MIT"
}
```

## Adding New Skills

1. Create `skills/your-skill-name/`
2. Add `skill.json` manifest
3. Implement `<skill_name>.py` with `run(action, **kwargs)` entry point
3. Add `requirements.txt` if needed
4. Update `registry.json`
5. Submit PR

## License

MIT — Free for personal and commercial use with attribution.

## Author

**DARKPHOENIX2530** — https://github.com/DARKPHOENIX2530