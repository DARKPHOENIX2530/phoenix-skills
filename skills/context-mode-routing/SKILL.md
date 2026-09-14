# Context-Mode Routing (soft-trim, all tools stay enabled)

All 11 `context-mode` MCP tools are enabled. Prefer CORE, reach for ON-DEMAND any time mid-session without asking — no re-enable, no restart.

## Hard thresholds — use ctx_* when ANY is true

- Expected output > 20 lines or > 2KB
- 3+ shell commands for one question (use ONE `ctx_batch_execute`)
- Analyzing/counting/filtering file content (never raw-Read to analyze)
- Fetching any URL (never raw WebFetch/curl into context)
- After resume/compact and user asks about prior work (use `ctx_search` first, never ask "what were we doing?")

Otherwise raw tools (Read/Bash) are fine — no overhead where it does not pay.

## CORE (default)

| Need | Call |
|---|---|
| Run code, count/parse/filter | `ctx_execute(language, code)` — `console.log()` ONLY the answer |
| Many commands, one question | `ctx_batch_execute(commands, queries)` |
| Prior work, decisions, indexed docs | `ctx_search(queries: [...])` — batch all questions in ONE call |
| Store notes for later | `ctx_index(content, source)` with descriptive source label |
| Web content | `ctx_fetch_and_index(url)` then `ctx_search` |
| Savings check | `ctx_stats` |

Think-in-code is MANDATORY for analysis: program it, do not paste raw data into context.

## ON-DEMAND (enabled, use freely mid-session)

- `ctx_doctor` — something broken (runtimes, hooks, FTS5)
- `ctx_execute_file(path, language, code)` — file too big to even reference
- `ctx_upgrade` — ONLY when user explicitly approves a version move (pinned: 1.0.169)
- `ctx_purge(confirm:true)` — ONLY with explicit user approval; wipes knowledge base
- `ctx_insight` — opens commercial dashboard; default NEVER (local-only policy, ELv2)

## Safety

- `ctx_execute` for read-only analysis by default; destructive shell (rm, mass mv, deploys) needs the user's explicit word.
- Never exfiltrate: code, prompts, and file contents stay local. Only `ctx_fetch_and_index` hits the network, only for user-requested URLs.
- `ctx_upgrade`/`ctx_purge` always need explicit approval — they are enabled, not forbidden, just gated.

## Maintenance

- Pinned version: context-mode@1.0.169. Rebuild if native binding breaks: `npm install -g --allow-scripts=context-mode,better-sqlite3 context-mode`.
- Monthly: `ctx_stats` — if stored content looks heavy, propose `ctx_purge` of stale raw sources (keep decisions/summaries 90 days, raw dumps 7). Propose, do not auto-wipe.