# OpenCode headless reference

This skill follows the OpenCode CLI (verified against opencode 1.18.x on 2026-08-11):

- Headless invocation: `opencode run "<message>"` (the `run` subcommand; the bare `opencode` command starts the TUI)
- Working directory: `--dir <DIR>`
- Output format: `--format default` (formatted text) or `--format json` (raw JSON events); default is `default`
- Model selection: `--model provider/model` (`-m`)
- Agent selection: `--agent <NAME>`
- Auto-approval: `--auto` (auto-approve permissions that are not explicitly denied; dangerous)
- Resumable sessions: `-c` / `--continue` (last session), `-s` / `--session <ID>`, `--fork`
- Attach files: `-f` / `--file <PATH>` (repeatable)
- Session title: `--title <TEXT>`
- Sharing: `--share` (publishes the session; never use unless explicitly requested)
- Reasoning variant: `--variant high|max|minimal` (provider-specific)

Authentication is expected to be preconfigured by the user through `opencode auth` (provider API keys or OAuth). The active provider determines which models are available. Never inspect or print credentials. If authentication fails, return OpenCode's error and ask the user to authenticate separately.

Notes:

- OpenCode has no final-message file. The wrapper defaults to `--format default` and captures the formatted text output as `response`. This is the most reliable way to return a human-readable answer.
- With `--json`, the wrapper stores the raw JSON event stream and makes a best-effort extraction of the last text event as `response`; the event schema is not guaranteed stable, so prefer the default text mode unless the caller needs the structured stream.
- OpenCode is provider-agnostic: the same wrapper drives whichever model the user configured, which makes it useful for a cross-provider second opinion.

Primary sources:

- Local help: `opencode --help`, `opencode run --help`
- `opencode models` for available models, `opencode auth` for provider setup
- [OpenCode documentation](https://opencode.ai/docs/)
