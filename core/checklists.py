"""Per-project checklist/roadmap storage — ~/.config/multi-commit/checklists.json"""
import json
import os
import re
from datetime import datetime

CONFIG_DIR = os.path.expanduser("~/.config/multi-commit")
CHECKLIST_FILE = os.path.join(CONFIG_DIR, "checklists.json")


def _ensure():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_all() -> dict:
    """Load the full checklist store: {project_path: {stages: [...], updated: ...}}"""
    _ensure()
    if not os.path.exists(CHECKLIST_FILE):
        return {}
    try:
        with open(CHECKLIST_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_all(data: dict):
    _ensure()
    with open(CHECKLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_project_data(project_path: str) -> dict:
    """Return the checklist data for a project, or a fresh empty structure."""
    data = load_all()
    key = os.path.abspath(project_path)
    return data.get(key, {"stages": [], "created": None, "updated": None})


def save_project_data(project_path: str, project_data: dict):
    data = load_all()
    key = os.path.abspath(project_path)

    now = datetime.now().isoformat(timespec="seconds")
    if not project_data.get("created"):
        project_data["created"] = now
    project_data["updated"] = now

    data[key] = project_data
    save_all(data)


# ── Stage / item helpers ──────────────────────────────────────────────────

def new_stage(title: str, notes: str = "") -> dict:
    return {"title": title, "notes": notes, "items": []}


def new_item(text: str, done: bool = False) -> dict:
    return {"text": text, "done": done}


def progress_for_stage(stage: dict) -> tuple:
    items = stage.get("items", [])
    total = len(items)
    done = sum(1 for i in items if i.get("done"))
    return done, total


def progress_for_project(project_data: dict) -> tuple:
    total = 0
    done = 0
    for stage in project_data.get("stages", []):
        d, t = progress_for_stage(stage)
        total += t
        done += d
    return done, total


# ── Markdown roadmap parser ─────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
_BULLET_RE = re.compile(r"^\s*[-*]\s+(.*)$")


def parse_markdown_roadmap(text: str) -> list:
    """
    Parse a markdown roadmap into a list of stage dicts.

    Rules:
    - Lines starting with #, ##, ### etc. start a new stage (title = heading text).
    - Numbered list items (1. Task) and bullet items (* Task / - Task) become
      checklist items in the current stage.
    - Any other non-empty, non-list paragraph text is appended to the
      current stage's "notes".
    - If list items or text appear before any heading, they go into a
      default "General" stage.
    """
    stages = []
    current = None

    def ensure_current():
        nonlocal current
        if current is None:
            current = new_stage("General")
            stages.append(current)
        return current

    for raw_line in text.splitlines():
        line = raw_line.rstrip()

        if not line.strip():
            continue

        heading_match = _HEADING_RE.match(line)
        if heading_match:
            title = heading_match.group(2).strip()
            if not title:
                continue
            current = new_stage(title)
            stages.append(current)
            continue

        numbered_match = _NUMBERED_RE.match(line)
        bullet_match = _BULLET_RE.match(line)

        if numbered_match:
            item_text = numbered_match.group(1).strip()
            if item_text:
                ensure_current()["items"].append(new_item(item_text))
            continue

        if bullet_match:
            item_text = bullet_match.group(1).strip()
            if item_text:
                ensure_current()["items"].append(new_item(item_text))
            continue

        # Plain paragraph text — append to current stage's notes
        stage = ensure_current()
        if stage["notes"]:
            stage["notes"] += "\n" + line.strip()
        else:
            stage["notes"] = line.strip()

    return stages


def merge_imported_stages(project_data: dict, imported_stages: list, replace: bool = False) -> dict:
    """
    Merge freshly-imported stages into existing project data.

    If replace=True, the existing stages are discarded entirely.
    Otherwise imported stages are appended after existing ones.
    """
    if replace or "stages" not in project_data:
        project_data["stages"] = imported_stages
    else:
        project_data["stages"].extend(imported_stages)
    return project_data