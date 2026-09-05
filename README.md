<p align="center">
  <strong>English</strong> · <a href="README.ru.md">Русский</a>
</p>

<p align="center">
  <h1 align="center">OpenCode Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/opencode-delegate"><img src="https://img.shields.io/badge/status-active-brightgreen" alt="status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License: MIT"></a>
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/skills.sh-discoverable-black" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-opencode-purple" alt="CLI: opencode">
</p>

Headless OpenCode CLI delegate skill by [Artem Letyushev](https://github.com/letya999).

The command is `scripts/delegate_opencode.py`. The primary consumer is the controlling agent or orchestrator: every execution runs OpenCode once as a bounded, non-interactive subprocess (`opencode run`) and returns one structured JSON envelope.

---

## One objective, bounded subprocess, zero trust

The wrapper acts as a deterministic isolation layer between your controlling agent and the OpenCode CLI:

- **Single non-interactive execution:** Invokes `opencode run` directly via `subprocess.run(..., shell=False)` without TUI interaction.
- **Provider-agnostic execution:** Supports any provider configured in OpenCode (`openai`, `anthropic`, `ollama`, `openrouter`, etc.).
- **Strict workspace scoping:** Scopes execution to the target project directory via `--dir <cwd>`.
- **Zero-trust verification:** Outputs are unverified until independently confirmed by diffs and tests.
- **Credential isolation:** Never inspects or prints provider API keys, `~/.config/opencode` credentials, or `.env` files.

## Capability matrix

| Capability / Setting | Specification | Behavior & Guarantees |
|---|---|---|
| **Headless command** | `opencode run "<task>"` | Non-interactive execution in run mode |
| **Workspace scoping** | `--dir <cwd>` | Restricts OpenCode to the target project directory |
| **Model selection** | `--model <provider/model>` | Forwards specified model string to OpenCode |
| **Output formats** | Formatted text or `--json` | Captures formatted text or detailed JSON event stream |
| **Autonomous edits** | `--always-approve` | Passes `--auto` to approve non-denied operations |
| **Anti-sharing** | `--share` prevented | Never publishes sessions publicly unless explicitly requested |
| **Session resumption** | `--session <id>` / `--continue` | Resumes existing conversation when requested |
| **Executable override** | `OPENCODE_BIN` env var | Custom executable path before searching PATH |
| **Standard exit codes** | `0, 2, 65, 124, 126, 127` | Predictable error routing for orchestrators |

## Install

With `npx skills`:

```bash
npx skills add letya999/opencode-delegate
```

Or clone into an agent skill directory:

```bash
git clone https://github.com/letya999/opencode-delegate.git .agents/skills/opencode-delegate
```

## Quick Start

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_opencode.py \
  --cwd "$PWD" \
  --task "Review this repository and report the highest-risk issue." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_opencode.py `
  --cwd (Get-Location).Path `
  --task "Review this repository and report the highest-risk issue." `
  --timeout 45m
```

---

<details>
<summary>JSON Manifest Schema & Agent Integration</summary>

The wrapper writes `stdout.txt` (or `events.jsonl`), `stderr.log`, and `result.json` into a temporary directory:

```json
{
  "tool": "opencode",
  "cwd": "C:\\work\\repo",
  "exit_code": 0,
  "output_dir": "C:\\Temp\\opencode-delegate-xyz",
  "stdout": "C:\\Temp\\opencode-delegate-xyz\\stdout.txt",
  "stderr": "C:\\Temp\\opencode-delegate-xyz\\stderr.log",
  "response": "Final extracted text answer from OpenCode"
}
```

If OpenCode completes with exit code 0 but returns an empty response, the wrapper returns code `65`.

</details>

<details>
<summary>CLI Flags & Configuration Reference</summary>

| Flag | Type | Description |
|---|---|---|
| `--cwd` | Path (required) | Target project directory. Exits with `2` if missing. |
| `--task` | String (required) | Delegated instruction / task for OpenCode. |
| `--timeout` | Duration (default: `45m`) | Timeout formatted as `90s`, `45m`, `2h`, or integer seconds. |
| `--model` | String | Model string (e.g. `anthropic/claude-3-7-sonnet`). |
| `--json` | Flag | Captures full JSON event stream instead of formatted text. |
| `--always-approve` | Flag | Passes `--auto` to auto-approve non-denied tool permissions. |
| `--session` | String | Session ID to resume an existing session. |
| `--continue` | Flag | Continues the previous session. |
| `--output-dir` | Path | Custom artifact directory. |

</details>

<details>
<summary>Safety Posture & Credential Guardrails</summary>

- **No credential leaks:** Never reads or logs API keys, OAuth tokens, or `~/.local/share/opencode` credentials.
- **No auto-sharing:** Never passes `--share` unless specifically requested.
- **Anti-recursion rule:** Delegated OpenCode instances must not recursively spawn further delegate wrappers.

</details>

<details>
<summary>Independent Verification Protocol</summary>

Outputs are unverified evidence. After delegated file modifications:

1. Check changes independently: `git diff --stat` and `git diff`.
2. Run test suites outside the delegated environment: `pytest`, `npm test`, etc.
3. Verify newly generated files and imports.

</details>

<details>
<summary>Test Suite & Quality Checks</summary>

Run the test suite with standard library `unittest`:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Agent Skill Entry Points</summary>

- [SKILL.md](SKILL.md) — Skill instruction specification for coding agents.
- [QUICKSTART.md](QUICKSTART.md) — Quick command reference.
- [references/runtime-setup.md](references/runtime-setup.md) — Cross-platform pre-flight checks.
- [references/headless-reference.md](references/headless-reference.md) — OpenCode CLI headless reference.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Discovery index for skills.sh.
- [dist/opencode-delegate.zip](dist/opencode-delegate.zip) — Discoverable archive artifact.

</details>

<details>
<summary>License</summary>

MIT License. See [LICENSE](LICENSE) for full text. Copyright (c) 2026 Artem Letyushev.

</details>
