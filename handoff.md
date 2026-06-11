# Multi-Commit — Project Handoff
> Last updated: 2026-06-10

---

## Machine Info
- **OS:** Linux Mint 22.3 Zena (Cinnamon 6.6.7), Ubuntu Noble base
- **User:** sam
- **Hostname:** SS-Mint
- **GPU:** AMD RX 6400 (low profile, Dell Precision Tower 3420 SFF)
- **CPU:** Intel Core i7-7700 (Kaby Lake, 4c/8t)
- **RAM:** 32GB
- **Storage:** 512GB Toshiba NVMe (~352GB used after cleanup)
- **Audio:** PipeWire 1.0.5 (running as PulseAudio)

---

## Bluetooth Audio Fix
- **Headset:** PLYR — MAC: `88:08:94:B0:EF:E2`
- **Alias:** `btfix` in `~/.bashrc`
- **Also saved as a Favourite** in Multi-Commit under System category
```bash
bluetoothctl connect 88:08:94:B0:EF:E2 && sleep 5 && pactl set-card-profile bluez_card.88_08_94_B0_EF_E2 a2dp-sink-sbc_xq && pactl set-default-sink bluez_output.88_08_94_B0_EF_E2.1
```

---

## GitHub
- **Account:** Pixsl-Labs
- **Auth:** Personal Access Token (PAT) stored via `git config --global credential.helper store`
- **PAT note:** `ghp_xxxx` — stored permanently, never needs re-entering
- **Multi-Commit repo:** https://github.com/Pixsl-Labs/Multi-Commit

---

## Multi-Commit Project

### Location
```
~/Projects/multi-commit/
```

### Run
```bash
python3 ~/Projects/multi-commit/main.py
```

### Project Structure
```
multi-commit/
├── main.py                    # Entry point, Ctrl+Q handler
├── install.sh                 # Installer — deps, .desktop, app menu
├── PANEL_SETUP.md             # How to add to Cinnamon taskbar
├── HANDOFF.md                 # This file
├── README.md                  # GitHub README with badges
├── multi-commit.desktop       # Desktop/panel launcher
├── assets/
│   └── icon.png               # Official Git logo (Flaticon, pocike)
├── core/
│   ├── __init__.py
│   ├── git_ops.py             # All git subprocess calls
│   ├── project_manager.py     # Recent projects — ~/.config/multi-commit/recent.json
│   ├── settings.py            # User settings — ~/.config/multi-commit/settings.json
│   ├── favourites.py          # Commands — ~/.config/multi-commit/favourites.json
│   └── code_review.py         # Code review generator (adapted from code_reviewer.py)
└── ui/
    ├── __init__.py
    ├── main_window.py          # Main window + restructured menubar
    ├── project_list.py         # Left panel — projects with status icons
    ├── commit_panel.py         # Right panel — add/commit/push + tools
    ├── branch_panel.py         # Branch manager (collapsible card)
    ├── stash_panel.py          # Stash manager (collapsible card)
    ├── command_manager.py      # Command Manager standalone window
    ├── appearance_dialog.py    # Live theme editor standalone window
    └── settings_dialog.py      # Preferences + Remotes/Accounts tabs
```

### Config files
| File | Contents |
|------|----------|
| `~/.config/multi-commit/settings.json` | App preferences, theme |
| `~/.config/multi-commit/recent.json` | Recent project paths |
| `~/.config/multi-commit/favourites.json` | Saved commands |

### Git remotes for Multi-Commit
```bash
origin  https://github.com/Pixsl-Labs/Multi-Commit.git
```
Uni remote to be added once uni GitHub username is confirmed:
```bash
git remote add uni https://github.com/UNI-USERNAME/Multi-Commit.git
```

---

## Features Built (v1.0.0)

### Core Workflow
- Step-by-step: git add → commit → push with Enter key on each
- ⚡ Quick Commit (Ctrl+Enter) — add → commit → push all in one
- Push All Remotes — one click for all configured remotes
- 🔐 Push with Auth — opens Kitty terminal (`kitty --hold`) for password remotes

### Project Sidebar
- Recent projects list, most recent top, max 20
- 🟢🟡🔴 git status indicators per project
- Branch name + git badge per row
- Per-project buttons: 📁 Folder, 💻 VSCode, 🖥 Terminal, 📋 Review
- ↻ Refresh button to re-scan all statuses

### Git Tools (right panel)
- 🔍 Diff viewer — coloured git diff HEAD (green adds, red removes)
- 📜 Commit history — last 8 commits, collapsible
- ⎇ Branch manager — create, switch, delete, create & switch
- 📦 Stash manager — save with description, pop, apply, drop
- Custom command runner with output log
- Timestamped output log [HH:MM:SS]

### Command Manager (⚡ Commands menu)
- Standalone window — search, category filter
- 📋 Copy command to clipboard
- ▶ Run Silently — background, output in panel
- 🖥 Run in Terminal — Kitty with `--hold`, echoes command first
- Add/edit/delete commands with multiline editor
- Pre-seeded with btfix command

### Appearance (Settings menu)
- 7 built-in presets: Red/Black, Ocean Blue, Purple Haze, Hacker Green, Burnt Orange, Midnight Silver, Neon Pink
- Live preview — changes apply instantly to main window
- Colour picker + hex entry per colour
- Gradient preview bar
- Save closes window, Reset to default

### Settings dialog
- Preferences tab: auto add/push toggles, VSCode cmd, terminal cmd, default remote
- Remotes/Accounts tab: view/add/update remotes, credential cache with timeout

### Menubar structure
- **Left:** File | ⚡ Commands | Git
- **Right:** Settings | Help
- Git menu: pull, fetch, status, Generate Code Review
- Commands menu: Command Manager + quick-run all favourites by category

### Code Review
- Button per project in sidebar (📋 Review)
- Also in Git menu
- Saves to `~/Projects/Code Reviews/`
- Opens in VSCode automatically after generation

---

## Key Design Decisions
- GTK3 Python — native Linux feel, fits Cinnamon perfectly
- All git ops go through `core/git_ops._run()` — single subprocess wrapper
- Theme stored in `settings.json` under key `"theme"` as dict
- CSS applied globally via `Gtk.StyleContext.add_provider_for_screen`
- Kitty terminal uses `--hold` flag to keep window open after command
- Command Manager is a `Gtk.Window` (not dialog) so it stays open alongside main
- Appearance dialog is also standalone `Gtk.Window` for live preview
- Favourites seeded with btfix on first run if no config exists

---

## Other Projects

### log-analyser
- **Path:** `/home/sam/Projects/log-analyser`
- **Repo:** https://github.com/Pixsl-Labs/Log-Analyser
- **Stack:** Python 3, colorama, pytest
- **Run:** `python3 -m app.main brute_force.log`
- **Tests:** `pytest` (75+ passing)
- **venv:** `source venv/bin/activate`

---

## Tools & Aliases
```bash
btfix     # Bluetooth headset fix
review    # Runs ~/Projects/code_reviewer.py
multi-commit  # alias to launch Multi-Commit (if added to ~/.bashrc)
```

---

## Desktop Setup
- **Terminal:** Kitty — `~/.config/kitty/kitty.conf`
- **Launcher:** Ulauncher — `Ctrl+Space`
- **Conky:** Red neon clock/stats — `~/.conkyrc`
- **Browser:** Brave (Flatpak) — `flatpak run com.brave.Browser`
- **Multi-Commit:** Pinned to Cinnamon taskbar via `.desktop` file
- **Plank:** Was installed, then REMOVED — do not reinstall

---

## World of Tanks on Linux
- Installed via Steam, Proton
- Required launch option (adjust core count to match CPU):
```
WINE_CPU_TOPOLOGY=8:0,1,2,3,4,5,6,7 %command%
```
- Audio fix if crackling: `PULSE_LATENCY_MSEC=60`
- Download server: set to **Amsterdam** for full speed (was 37Mbps → 373Mbps)

---

## Recently Added (this session)

### New files
| File | Purpose |
|------|---------|
| `ui/appearance_dialog.py` | Live theme editor — 7 presets, colour picker, hex input, gradient bar, saves + closes |
| `ui/command_manager.py` | Replaces favourites_dialog — standalone window, search, clipboard copy, fixed Kitty terminal (`--hold`) |
| `ui/pull_panel.py` | Pull/Fetch collapsible card — pull, pull --rebase, fetch all, fetch origin |
| `core/code_review.py` | Programmatic code review generator, adapted from `code_reviewer.py` |
| `core/notes.py` | Per-project sticky notes — auto-saved with 800ms debounce |
| `core/notify.py` | Desktop notifications via `notify-send` — push success/fail, commit, code review |

### Key fixes this session
- `kitty --hold` flag for Run in Terminal — keeps window open after command finishes, echoes command first
- Appearance dialog now closes on Save Theme
- GitHub PAT auth — `git config --global credential.helper store`, token stored permanently
- `.gitignore` added — `__pycache__/`, `*.pyc` excluded from commits

### commit_panel.py changes
- Conventional commit template chips: feat, fix, docs, style, refactor, test, chore, perf, ci, revert
- Smart template apply — replaces existing prefix or prepends to current text
- Pull panel wired in as collapsible card
- Notes panel wired in — loads/saves per project path
- Desktop notifications on commit, push success, push fail
- Notification on code review save

### menubar restructure
- **Left:** File | ⚡ Commands | Git
- **Right:** Settings | Help
- Git menu: pull, fetch --all, status, Generate Code Review
- Settings menu: Preferences, 🎨 Appearance
- Commands menu: Command Manager + quick-run favourites by category

---

## brainstorm_ideas

### 🔥 High Priority — Most Useful Next
1. **Commit message templates** — dropdown of conventional commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`) that prepend to the message box. One click to format properly.

2. **git pull panel** — dedicated pull/fetch card in commit_panel alongside push. Fetch all, pull current branch, pull with rebase option. Currently can only pull via Git menu or custom command.

3. **Repo health dashboard** — click a project to see: total commits, last push date, open/untracked files count, repo size, contributors. Could be a tab in the right panel.

4. **Desktop notification on push** — use `notify-send` to fire a Linux desktop notification when a push succeeds or fails. `notify-send "Multi-Commit" "✅ Pushed to origin"`. Non-intrusive feedback.

5. **Per-project notes** — a small sticky-note text area saved per project path. Useful for "TODO before next commit" or leaving yourself reminders. Saved to `~/.config/multi-commit/notes.json`.

### 🎯 Medium Priority — Quality of Life
6. **Conventional commit linter** — warn if commit message doesn't follow `type: description` format. Soft warning, not a hard block. Could add a toggle in settings.

7. **SSH key manager** — generate new SSH key, view existing keys, copy public key to clipboard, one-click to open GitHub SSH settings page. Lives in Settings dialog as a new tab.

8. **Export / import config** — backup your entire Multi-Commit config (settings, favourites, recent projects) to a `.zip`. Useful when moving to a new machine. Simple button in Settings.

9. **Tag manager** — create lightweight/annotated tags, push tags to remotes, delete tags. Collapsible card in commit_panel alongside branch/stash.

10. **Unsaved changes warning** — when switching projects in the sidebar while there's a commit message typed, show a "you have an unsaved commit message" dialog. Small but prevents losing work.

### 🚀 Bigger Features — V2
11. **Git log visualiser** — a proper branch graph view showing commit tree with branch divergences. Would need a custom GTK canvas or embed a matplotlib figure. Big but impressive.

12. **Cinnamon applet wrapper** — a JavaScript Cinnamon applet that adds Multi-Commit as a tray icon with a right-click menu to quick-commit from anywhere without opening the full app. Would be a separate repo.

13. **Multi-window mode** — open two projects side by side in split panes. Useful when coordinating commits across related repos (e.g. frontend + backend that need matching versions).

14. **Auto-update checker** — on startup, ping the GitHub releases API to check if a newer version exists and show a subtle banner if so.

15. **Conflict resolver** — when `git status` shows merge conflicts (UU), show a visual side-by-side diff of the conflicting file with Accept Ours / Accept Theirs / Edit buttons. Hard but very useful.

### 💡 Wild Cards
16. **Time-based theme switching** — automatically switch to a darker/lighter preset based on time of day (e.g. Ocean Blue during day, Red & Black at night).

17. **Command scheduler** — run a favourite command on a cron-like schedule (e.g. auto git pull every 30 minutes). Saved per-command in favourites.json.

18. **VSCode extension companion** — a VSCode extension that talks to Multi-Commit via a local socket, so you can trigger a quick commit from inside VSCode without switching windows.

19. **Project templates** — when creating a new project folder, offer to scaffold it with a `.gitignore`, `README.md`, `venv` etc. based on detected language.

20. **Audit log** — a persistent log file of every git operation ever run through Multi-Commit with timestamps. Useful for "what did I push last Tuesday?" type questions.