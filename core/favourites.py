"""Favourite commands — persisted to ~/.config/multi-commit/favourites.json"""
import json
import os

CONFIG_DIR = os.path.expanduser("~/.config/multi-commit")
FAV_FILE   = os.path.join(CONFIG_DIR, "favourites.json")

# Each favourite: {"name": str, "command": str, "use_terminal": bool, "category": str}

def _ensure():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def load() -> list:
    _ensure()
    if not os.path.exists(FAV_FILE):
        # Seed with Sam's btfix command!
        defaults = [
            {
                "name": "btfix — PLYR Headset",
                "command": "bluetoothctl connect 88:08:94:B0:EF:E2 && sleep 5 && pactl set-card-profile bluez_card.88_08_94_B0_EF_E2 a2dp-sink-sbc_xq && pactl set-default-sink bluez_output.88_08_94_B0_EF_E2.1",
                "use_terminal": False,
                "category": "System",
            }
        ]
        save(defaults)
        return defaults
    try:
        with open(FAV_FILE) as f:
            return json.load(f)
    except Exception:
        return []

def save(favs: list):
    _ensure()
    with open(FAV_FILE, "w") as f:
        json.dump(favs, f, indent=2)

def add(name: str, command: str, use_terminal: bool = False, category: str = "General"):
    favs = load()
    favs.append({"name": name, "command": command,
                "use_terminal": use_terminal, "category": category})
    save(favs)

def remove(index: int):
    favs = load()
    if 0 <= index < len(favs):
        favs.pop(index)
    save(favs)

def update(index: int, **kwargs):
    favs = load()
    if 0 <= index < len(favs):
        favs[index].update(kwargs)
    save(favs)

def get_categories() -> list:
    favs = load()
    return sorted(set(f.get("category", "General") for f in favs))