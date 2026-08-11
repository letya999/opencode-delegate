---
name: opencode-delegate
description: Run OpenCode CLI as a headless delegate. Use when the user names OpenCode or opencode, says "ask OpenCode", wants `opencode run`, wants a provider-agnostic second opinion, or compares coding agents. Do NOT use for interactive sessions, other CLIs, or tasks not meant for delegation.
---

# OpenCode Delegate

Run OpenCode as a bounded headless subprocess (`opencode run`) and hand its final response back to the user. Keep the current project as the working directory unless the user specifies another directory.

## Anti-Rationalization

Trigger this skill when the user explicitly asks for OpenCode, `opencode run`, a provider-agnostic second opinion, or a comparison that needs OpenCode evidence. Do not skip it because another installed CLI is available; the requested value is OpenCode's configured provider and runtime.

Pause instead when OpenCode is missing or unauthenticated, the user wants an interactive TUI, the task requires exposing secrets, or the requested auto-approval/sharing behavior exceeds the user's authorization.

## Runtime Pre-Flight

Read [runtime-setup.md](references/runtime-setup.md) before invoking the wrapper. Verify Python 3.10+ and `opencode` or `OPENCODE_BIN`; stop and report the missing prerequisite instead of inventing an installer or assuming a specific shell.

## Workflow

1. Clarify the delegated objective, scope, and whether OpenCode may edit files or run commands. Do not delegate secrets or expose protected files in the prompt.
2. Resolve the project directory to an absolute path. Prefer the current working directory. Verify it exists before starting.
3. Run the bundled wrapper with the Python command discovered by [runtime-setup.md](references/runtime-setup.md).
4. Read [headless-reference.md](references/headless-reference.md) when flags, sessions, output parsing, or authentication details are needed.

5. Report the wrapper's result, output-file path, exit status, and any stderr warning. A successful process is not proof that the requested change is correct: inspect the diff and run relevant tests independently when the delegated task changed files.
6. If the task is long-running, use a generous explicit timeout. Never create a hidden daemon, polling loop, or unbounded background process.

## Wrapper behavior

- `delegate_opencode.py` invokes `opencode` directly, never through a shell, and supports `OPENCODE_BIN` for an explicit executable path.
- It uses headless mode with `opencode run`, `--dir <cwd>`, and the delegated task as the message; it adds `--auto` (auto-approve non-denied permissions) only when `--always-approve` is requested.
- OpenCode has no final-message file. By default the wrapper captures OpenCode's formatted text output as `response`. Pass `--json` to switch to `--format json`; the raw JSON event stream is then stored and surfaced under `events`, and the last text event is used as `response` when one can be identified.
- Model selection uses `--model provider/model` when `--model` is passed. The active provider is whichever the user configured with `opencode auth`.
- It writes stdout, stderr, and a small result manifest to a temporary output directory, then prints the manifest as JSON.
- It returns nonzero for missing OpenCode, an invalid project directory, timeout, or a failed process. Do not hide these failures.
- Prefer a one-shot invocation. Use `--session` or `--continue` only when the user explicitly asks for a resumable OpenCode session.

## Safety and verification

- Do not read or print provider API keys, OAuth tokens, `~/.local/share/opencode` or `~/.config/opencode` credentials, `.env*`, private keys, or browser profiles.
- Do not add MCP servers, disable repository protections, publish or share sessions, push commits, or delete data unless the user explicitly asks for that exact action. In particular, never pass `--share` unless requested.
- Default to no auto-approval. Only escalate to `--always-approve` when the user authorizes autonomous edits and the directory is trusted.
- Treat OpenCode's report as unverified. Inspect changed files, `git diff`, and tests from the controlling agent.
- If `opencode` is not found, tell the user to verify the official installation and PATH; do not install packages or run an installer automatically.

## Resources

Use `references/runtime-setup.md` for Python and CLI pre-flight, `scripts/delegate_opencode.py` for deterministic invocation, and `references/headless-reference.md` for the documented OpenCode interface.
