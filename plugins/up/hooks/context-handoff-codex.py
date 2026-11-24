"""Suggest an Ultrapack handoff when the active Codex context grows too large."""

import json
from contextlib import suppress
import os
from pathlib import Path
import sys
import tempfile
from uuid import UUID


def read_usage(transcript, session_id):
    with transcript.open("rb") as stream:
        metadata = json.loads(stream.readline())["payload"]
        if UUID(metadata["id"]) != session_id or isinstance(metadata.get("source"), dict):
            return None
        # Keep the lookup bounded even for long sessions.
        start = max(stream.tell(), stream.seek(0, os.SEEK_END) - 1024 * 1024)
        stream.seek(start)
        for line in reversed(stream.read().splitlines()):
            try:
                record = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            if record.get("type") == "compacted":
                return (0, 1)
            if record.get("type") != "event_msg":
                continue
            payload = record["payload"]
            if payload.get("type") == "token_count" and payload.get("info"):
                info = payload["info"]
                return info["last_token_usage"]["total_tokens"], info["model_context_window"]
    return None


def check(payload):
    event = payload.get("hook_event_name")
    if event not in {"PostToolUse", "Stop"} or payload.get("agent_id"):
        return
    if event == "Stop" and payload.get("stop_hook_active"):
        return
    session_id = UUID(payload["session_id"])
    usage = read_usage(Path(payload["transcript_path"]), session_id)
    if usage is None:
        return
    used, window = usage
    if not isinstance(used, int) or not isinstance(window, int) or window <= 0:
        return
    limit = window * 3 // 4
    marker = Path(tempfile.gettempdir()) / f"ultrapack-handoff-{os.getuid()}-{session_id}"
    if used < limit:
        with suppress(FileNotFoundError):
            marker.rmdir()
        return
    try:
        marker.mkdir(mode=0o700)
    except FileExistsError:
        return

    message = (
        f"Context handoff reminder: this session is using {used:,} tokens "
        f"(handoff threshold: {limit:,}). Briefly suggest a handoff to a new session in "
        "the user's language at the next natural pause. Keep the current work going "
        "and prepare the handoff only if the user asks."
    )
    if event == "Stop":
        print(json.dumps({"decision": "block", "reason": message}))
    else:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": event, "additionalContext": message,
        }}))


if __name__ == "__main__":
    try:
        check(json.load(sys.stdin))
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        # An absent or changed transcript must never interrupt the session.
        pass
