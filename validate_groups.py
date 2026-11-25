#!/usr/bin/env python3
"""Validate static account-to-group configuration; does not launch or control gameplay."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
accounts = json.loads((BASE / "accounts.json").read_text(encoding="utf-8"))
config = json.loads((BASE / "account_groups.json").read_text(encoding="utf-8"))
team_size = int(config.get("team_size", 4))
known = [str(a.get("uid", "")) for a in accounts]
if any(not uid for uid in known):
    raise SystemExit("ERROR: accounts.json contains an empty UID")
if len(known) != len(set(known)):
    raise SystemExit("ERROR: duplicate UID in accounts.json")
seen = []
for group in config.get("groups", []):
    name = group.get("group", "(unnamed)")
    uids = [str(uid) for uid in group.get("uids", [])]
    if len(uids) > team_size:
        raise SystemExit(f"ERROR: {name} has {len(uids)} accounts; max is {team_size}")
    if len(uids) != len(set(uids)):
        raise SystemExit(f"ERROR: duplicate UID inside {name}")
    unknown = sorted(set(uids) - set(known))
    if unknown:
        raise SystemExit(f"ERROR: {name} contains unknown UID(s): {unknown}")
    seen.extend(uids)
    print(f"{name}: {len(uids)}/{team_size} accounts | " + ", ".join(uids))
if len(seen) != len(set(seen)):
    raise SystemExit("ERROR: one or more accounts appear in multiple groups")
missing = sorted(set(known) - set(seen))
if missing:
    raise SystemExit(f"ERROR: accounts not assigned to any group: {missing}")
print(f"OK: {len(config.get('groups', []))} isolated groups; {len(seen)} accounts assigned exactly once.")
