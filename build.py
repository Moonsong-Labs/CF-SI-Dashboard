#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
HERE = Path(__file__).resolve().parent
ORGS = HERE / "orgs"
PAGE = HERE / "index.html"
KINDS = ["SI", "Dev studio"]
REGIONS = ["APAC", "Americas", "Europe", "MENA", "Global", "Not recorded"]
SEGMENTS = ["Institutional", "DeFi & retail", "Infrastructure & nodes", "Developer education"]
TIERS = ["Core", "Active", "Early", "Pipeline"]
STAGES = ["Building", "Testnet",
          "Delivered demo / POC", "Live / Mainnet"]
TEXT = ["typeDetail", "regionDetail", "segmentBasis", "roles", "firstActivity", "internalStart",
        "strengths", "credibility", "openQuestions"]
ORG_KEYS = {"name", "kind", "region", "segments", "tier", "status", "sources", "projects", "demos", *TEXT}
PROJECT_KEYS = {"name", "stage", "timeline", "description", "notes", "check"}
def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
def check(path, o):
    problems = []
    say = lambda msg: problems.append(f"orgs/{path.name}: {msg}")
    if not isinstance(o, dict):
        return [f"orgs/{path.name}: must be one JSON object"]
    for k in sorted(set(o) - ORG_KEYS):
        say(f"unknown field '{k}' (see orgs/_template.json for the allowed fields)")
    for k, allowed in (("kind", KINDS), ("region", REGIONS), ("tier", TIERS)):
        if o.get(k) not in allowed:
            say(f"'{k}' is '{o.get(k)}'; must be one of: {', '.join(allowed)}")
    for k in ("name", "status"):
        if not isinstance(o.get(k), str) or not o[k].strip():
            say(f"'{k}' is required")
    for k in TEXT:
        if k in o and not isinstance(o[k], str):
            say(f"'{k}' must be text")
    if isinstance(o.get("name"), str) and o["name"].strip() and path.name != slug(o["name"]) + ".json":
        say(f"file should be named '{slug(o['name'])}.json'")
    segs = o.get("segments")
    if not isinstance(segs, list) or any(s not in SEGMENTS for s in segs):
        say(f"'segments' must be a list using only: {', '.join(SEGMENTS)} (or [])")
    elif segs and not str(o.get("segmentBasis", "")).strip():
        say("'segmentBasis' is required when 'segments' is filled in")
    ist = o.get("internalStart", "")
    if ist and not re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", str(ist)):
        say("'internalStart' must look like 2026-03 or 2026-03-15")
        demos = o.get("demos", [])
    if not isinstance(demos, list) or any(not isinstance(d, str) or not d.strip() for d in demos):
        say("'demos' must be a list of short descriptions, e.g. [\"Order book infrastructure\"]")    
    srcs = o.get("sources")
    if not isinstance(srcs, list) or any(not str(u).startswith("https://") for u in srcs):
        say("'sources' must be a list of https:// links (or [])")
    projects = o.get("projects")
    if not isinstance(projects, list):
        say("'projects' must be a list (or [])")
        return problems
    for i, p in enumerate(projects, 1):
        if not isinstance(p, dict):
            say(f"project {i} must be an object")
            continue
        label = f"project '{p.get('name') or i}'"
        if not str(p.get("name", "")).strip():
            say(f"project {i} needs a 'name'")
        if p.get("stage") not in STAGES:
            say(f"{label} has stage '{p.get('stage')}'; must be one of: {', '.join(STAGES)}")
        for k in sorted(set(p) - PROJECT_KEYS):
            say(f"{label} has unknown field '{k}'")
    return problems
def load():
    orgs, problems, seen = [], [], {}
    for path in sorted(ORGS.glob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            o = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"orgs/{path.name}: not valid JSON (line {e.lineno}: {e.msg})")
            continue
        problems += check(path, o)
        if isinstance(o, dict) and isinstance(o.get("name"), str):
            key = o["name"].strip().lower()
            if key in seen:
                problems.append(f"orgs/{path.name}: '{o['name']}' already exists in orgs/{seen[key]}")
            seen[key] = path.name
            orgs.append(o)
    return orgs, problems
def tidy(o):
    out = {k: o.get(k, "") for k in ["name", "kind", "region", "tier", "status", *TEXT]}
    out["segments"] = o.get("segments", [])
    out["demos"] = o.get("demos", [])
    out["sources"] = o.get("sources", [])
    out["projects"] = [{k: p.get(k, "") for k in PROJECT_KEYS} for p in o.get("projects", [])]
    return out
def main():
    orgs, problems = load()
    if problems:
        print(f"{len(problems)} problem(s) to fix:\n")
        print("\n".join(f"  - {p}" for p in problems))
        sys.exit(1)
    if "--check" in sys.argv:
        print(f"All {len(orgs)} organisation files look good.")
        return
    data = {"updated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "orgs": [tidy(o) for o in sorted(orgs, key=lambda o: o["name"].lower())]}
    block = ("/* DATA-START (filled in by build.py from orgs/*.json; do not edit by hand) */\n"
             "window.SI_DIRECTORY = " + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";\n"
             "/* DATA-END */")
    page = PAGE.read_text(encoding="utf-8")
    new, n = re.subn(r"/\* DATA-START.*?/\* DATA-END \*/", lambda _: block, page, flags=re.S)
    if n != 1:
        sys.exit("index.html is missing the DATA-START / DATA-END block")
    PAGE.write_text(new, encoding="utf-8")
    print(f"Updated index.html: {len(orgs)} organisations, "
          f"{sum(len(o.get('projects', [])) for o in orgs)} projects.")
if __name__ == "__main__":
    main()
