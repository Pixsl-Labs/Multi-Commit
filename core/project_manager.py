"""Manages recent projects list, persisted to ~/.config/multi-commit/recent.json"""
import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/multi-commit")
RECENT_FILE = os.path.join(CONFIG_DIR, "recent.json")
MAX_RECENT = 20

def _ensure_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load_recent():
    _ensure_config()
    if not os.path.exists(RECENT_FILE):
        return []
    try:
        with open(RECENT_FILE) as f:
            return json.load(f)
    except Exception:
        return []

def save_recent(projects: list):
    _ensure_config()
    with open(RECENT_FILE, "w") as f:
        json.dump(projects[:MAX_RECENT], f, indent=2)

def add_recent(path: str):
    """Add a project path to the top of the recent list."""
    projects = load_recent()
    path = os.path.abspath(path)
    if path in projects:
        projects.remove(path)
    projects.insert(0, path)
    save_recent(projects)
    return projects

def remove_recent(path: str):
    projects = load_recent()
    path = os.path.abspath(path)
    if path in projects:
        projects.remove(path)
    save_recent(projects)
    return projects