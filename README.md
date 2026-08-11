# OpenCode Delegate

Headless OpenCode CLI delegate skill by [Artem Letyushev](https://github.com/letya999).

This repository packages a cross-platform agent skill that lets a controlling agent run `opencode run` once, non-interactively, capture the result, and verify the work outside the delegated agent.

## What It Does

- Runs `opencode run` through `scripts/delegate_opencode.py`
- Captures stdout, stderr, exit code, output files, and the final response
- Supports macOS, Linux, WSL, and Windows
- Uses `OPENCODE_BIN` when the executable is not on `PATH`
- Supports optional OpenCode JSON event capture
- Keeps delegated output untrusted until the controlling agent checks diffs and tests

## Install

With `npx skills`:

```sh
npx skills add letya999/opencode-delegate
```

Or copy this repository into an agent skill directory such as `.agents/skills/`, `.claude/skills/`, or `~/.codex/skills/`.

## Quick Start

```sh
python3 scripts/delegate_opencode.py \
  --cwd "$PWD" \
  --task "Review this repository and report the highest-risk issue." \
  --timeout 45m
```

Windows users can run the same wrapper with `py -3`. See [QUICKSTART.md](QUICKSTART.md) and [references/runtime-setup.md](references/runtime-setup.md) for the full cross-platform pre-flight.

## Agent Skill Entry Points

- [SKILL.md](SKILL.md) is the skill instruction file.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) is the discovery index.
- [dist/opencode-delegate.zip](dist/opencode-delegate.zip) is the archive artifact referenced by the index.

## License

MIT License. See [LICENSE](LICENSE).
