"""Per-project sticky notes — ~/.config/multi-commit/notes.json"""
import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/multi-commit")
NOTES_FILE = os.path.join(CONFIG_DIR, "notes.json")

def _ensure():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load() -> dict:
    _ensure()
    if not os.path.exists(NOTES_FILE):
        return {}
    try:
        with open(NOTES_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def get(project_path: str) -> str:
    return load().get(os.path.abspath(project_path), "")

def save_note(project_path: str, note: str):
    notes = load()
    key = os.path.abspath(project_path)
    if note.strip():
        notes[key] = note
    elif key in notes:
        del notes[key]  # clean up empty notes
    _ensure()
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=2)