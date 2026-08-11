#!/usr/bin/env python3
"""Run OpenCode once in headless mode (opencode run) and capture its result."""

from __future__ import annotations

import argparse
import json
import os
import signal
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_bounded(command: list[str], cwd: Path, timeout: float) -> subprocess.CompletedProcess[str]:
    """Run in a process group so a timeout can terminate the whole CLI tree."""
    group_options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True})
    process = subprocess.Popen(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", **group_options)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        exc.stdout, exc.stderr = stdout, stderr
        raise
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def parse_duration(value: str) -> float:
    value = value.strip().lower()
    units = {"s": 1, "m": 60, "h": 3600}
    if value[-1:] in units:
        seconds = float(value[:-1]) * units[value[-1]]
    else:
        seconds = float(value)
    if seconds <= 0:
        raise ValueError("timeout must be greater than zero")
    return seconds


def find_opencode() -> str | None:
    explicit = os.environ.get("OPENCODE_BIN")
    if explicit:
        return explicit
    found = shutil.which("opencode")
    if found:
        return found
    for candidate in (
        Path.home() / ".opencode" / "bin" / "opencode.exe",
        Path.home() / ".opencode" / "bin" / "opencode",
        Path.home() / ".local" / "bin" / "opencode.exe",
        Path.home() / ".local" / "bin" / "opencode",
    ):
        if candidate.is_file():
            return str(candidate)
    return None


def last_text_from_events(stream: str) -> str | None:
    """Best-effort extraction of the final text from an OpenCode JSON event stream."""
    last_text = None
    for line in stream.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        part = event.get("part")
        if isinstance(part, dict) and part.get("type") == "text":
            value = part.get("text")
            if isinstance(value, str) and value.strip():
                last_text = value
        for key in ("text", "content", "message", "output"):
            value = event.get(key)
            if isinstance(value, str) and value.strip():
                last_text = value
    return last_text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cwd", required=True, help="Absolute project directory")
    parser.add_argument("--task", required=True, help="Task to delegate")
    parser.add_argument("--timeout", default="45m", help="Timeout, e.g. 90s, 45m, 2h")
    parser.add_argument("--model", help="Optional model as provider/model")
    parser.add_argument("--session", help="Optional session id to continue")
    parser.add_argument("--continue-session", action="store_true", help="Continue the last session")
    parser.add_argument("--always-approve", action="store_true", help="Auto-approve non-denied permissions (--auto)")
    parser.add_argument("--json", action="store_true", help="Use OpenCode --format json and capture the event stream")
    parser.add_argument("--output-dir", help="Directory for captured output")
    args = parser.parse_args()

    cwd = Path(args.cwd).expanduser().resolve()
    if not cwd.is_dir():
        print(f"error: project directory does not exist: {cwd}", file=sys.stderr)
        return 2

    opencode = find_opencode()
    if not opencode:
        print("error: opencode executable not found; set OPENCODE_BIN or add opencode to PATH", file=sys.stderr)
        return 127
    if not Path(opencode).is_file():
        resolved = shutil.which(opencode)
        if not resolved:
            print("error: opencode executable not found; set OPENCODE_BIN or add opencode to PATH", file=sys.stderr)
            return 127
        opencode = resolved

    try:
        timeout = parse_duration(args.timeout)
    except (TypeError, ValueError) as exc:
        parser.error(f"invalid --timeout: {exc}")

    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else Path(tempfile.mkdtemp(prefix="opencode-delegate-"))
    output_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = output_dir / ("events.jsonl" if args.json else "stdout.txt")
    stderr_path = output_dir / "stderr.log"
    manifest_path = output_dir / "result.json"

    command = [opencode, "run", "--dir", str(cwd)]
    if args.json:
        command.extend(["--format", "json"])
    if args.model:
        command.extend(["--model", args.model])
    if args.session:
        command.extend(["--session", args.session])
    if args.continue_session:
        command.append("--continue")
    if args.always_approve:
        command.append("--auto")
    command.append(args.task)

    try:
        completed = run_bounded(command, cwd, timeout)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        stdout_path.write_text(stdout if isinstance(stdout, str) else stdout.decode("utf-8", "replace"), encoding="utf-8")
        stderr_path.write_text(stderr if isinstance(stderr, str) else stderr.decode("utf-8", "replace"), encoding="utf-8")
        manifest = {"tool": "opencode", "cwd": str(cwd), "exit_code": 124, "timed_out": True, "output_dir": str(output_dir), "stdout": str(stdout_path), "stderr": str(stderr_path)}
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        print(f"error: OpenCode timed out after {args.timeout}; output: {output_dir}", file=sys.stderr)
        return 124
    except OSError as exc:
        print(f"error: could not start OpenCode: {exc}", file=sys.stderr)
        return 126

    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    manifest = {"tool": "opencode", "cwd": str(cwd), "exit_code": completed.returncode, "output_dir": str(output_dir), "stdout": str(stdout_path), "stderr": str(stderr_path)}
    if args.json:
        manifest["events"] = str(stdout_path)
        response = last_text_from_events(completed.stdout)
        if response is not None:
            manifest["response"] = response.strip()
        else:
            manifest["parse_warning"] = "Could not identify a final text event; see events file"
    else:
        manifest["stdout"] = str(stdout_path)
        manifest["response"] = completed.stdout.strip()

    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))

    if completed.returncode == 0 and not manifest.get("response"):
        print(f"error: OpenCode produced no response; output: {stdout_path}", file=sys.stderr)
        return 65
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
