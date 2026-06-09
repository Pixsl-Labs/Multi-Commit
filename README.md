# Multi-Commit — Project Structure

```
~/Projects/multi-commit/
├── main.py                  # Entry point
├── install.sh               # Installer (desktop shortcut, dependencies)
├── uninstall.sh
├── requirements.txt
├── README.md
│
├── core/
│   ├── __init__.py
│   ├── git_ops.py           # All git commands (add, commit, push, custom)
│   ├── project_manager.py   # Recent projects list, persistence
│   └── settings.py          # Load/save user settings (JSON)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # Main GTK window
│   ├── project_list.py      # Left panel — project list + open buttons
│   ├── commit_panel.py      # Right panel — git add, commit, push flow
│   ├── settings_dialog.py   # Settings popup
│   └── dialogs.py           # Reusable input dialogs
│
├── assets/
│   └── icon.png             # App icon (for panel shortcut)
│
└── multi-commit.desktop     # Desktop/panel launcher file
```

## Module Responsibilities

### core/git_ops.py
- `git_add(path, target=".")` 
- `git_commit(path, message)`
- `git_push(path)`
- `run_custom(path, command)`
- `get_remotes(path)` — detects available remotes

### core/project_manager.py
- Stores recently opened project paths
- Persists to `~/.config/multi-commit/recent.json`
- Max 20 recent projects, most recent at top

### core/settings.py
- `auto_git_add` — bool
- `auto_git_push` — bool  
- `default_add_target` — string (default ".")
- `vscode_cmd` — string (default "code")
- Persists to `~/.config/multi-commit/settings.json`

### ui/main_window.py
- Two-panel layout (project list left, commit panel right)
- Menubar with Settings

### ui/project_list.py
- "Open Folder" file dialog button
- Project list (most recent top)
- Per-project buttons: 📁 Folder | 💻 VSCode | 🖥️ Terminal
- Click project to select it for committing

### ui/commit_panel.py
- git add input (default ".") — Enter to confirm
- Commit message input — Enter to confirm  
- Push step — Enter to confirm
- Custom command input at any step
- Auto-mode toggle respects settings

# Adding Multi-Commit to the Cinnamon Panel

## Method 1 — Easiest: Drag from Menu (recommended)

1. Click the **Menu** button (bottom-left of taskbar)
2. Find **Multi-Commit** under Programming or search for it
3. **Right-click** it → **Add to panel**

Done! It'll appear as the git icon in your panel.

---

## Method 2 — Panel Launcher Applet

1. **Right-click** the Cinnamon panel → **Add applets to the panel**
2. Search for **"Panel Launcher"** → click **Add to panel**
3. The launcher applet appears in your panel
4. **Right-click** the applet → **Configure...**
5. Click **Add** → navigate to:
   ```
   /home/sam/.local/share/applications/multi-commit.desktop
   ```
6. Click **OK**

---

## Method 3 — Manual via terminal

```bash
# Copy .desktop to panel launchers folder
cp ~/Projects/multi-commit/multi-commit.desktop \
   ~/.local/share/cinnamon/panel-launchers/

# Then right-click panel → Add applets → Panel Launcher → configure
```

---

## Pinning to taskbar (like Windows-style)

1. Launch Multi-Commit once: `python3 ~/Projects/multi-commit/main.py`
2. It appears in the taskbar while running
3. **Right-click** the taskbar icon → **Add to panel** or **Pin**

---

## Keyboard launcher (Ulauncher)

Already works after install! Press `Ctrl+Space` and type `Multi` — it'll appear instantly.

---

## Making it launchable from anywhere (optional)

```bash
# Add a global alias
echo "alias multi-commit='python3 ~/Projects/multi-commit/main.py'" >> ~/.bashrc
source ~/.bashrc

# Now just type:
multi-commit
```

---

## Setting the correct icon

Make sure your icon is at:
```
~/Projects/multi-commit/assets/icon.png
```

If the panel shows a blank/gear icon, run:
```bash
update-desktop-database ~/.local/share/applications/
```
Then log out and back in.