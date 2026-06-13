# Multi-Commit — Handoff
> Updated: 2026-06-13

## Purpose
GTK3 Python Linux desktop app (Linux Mint Cinnamon, g-tiles WM). A "project cockpit": multi-remote git workflow, per-project commands, notes, checklists/roadmaps, branch/stash/tag/pull tools.

## Architecture
- `core/` — storage, logic, subprocess helpers (JSON in `~/.config/multi-commit/`)
- `ui/` — GTK windows/panels
- Checklist data: `~/.config/multi-commit/checklists.json`, keyed by `os.path.abspath(project_path)`

## Recently changed files
- `core/checklists.py` — added `export_markdown()` and `delete_project_data()` (just added, untested)
- `ui/checklist_window.py` — major additions:
  - autosave toggle + colour-changing Save button (green/orange)
  - unsaved-changes close warning, with main-window restore
  - "Hide Main Window" / "Show Main Window" toggle (non-transient window)
  - "Always on Top" toggle
  - right-click context menus on stage list (rename, duplicate, move up/down, mark all done/undone, clear completed) and item list (edit, toggle done, copy, duplicate, move up/down, move to another stage)
  - window sizing iterated multiple times for g-tiles compatibility (currently `set_default_size(640,480)` + `set_size_request(260,200)`, toolbar wrapped in horizontally-scrolling `Gtk.ScrolledWindow` with `EXTERNAL` policy)
- `ui/project_list.py` — added "✅ Checklist" button per row, imports `ChecklistWindow`
- `ui/main_window.py` — added Checklist menu item under Git menu

## Checklist manager status
Feature-complete for: stages, items, notes, markdown import/parse, autosave, hide-main-window, always-on-top, right-click reordering/editing. **Export button and Delete-All button are NOT yet wired into the UI** — only the core functions (`export_markdown`, `delete_project_data`) were added to `core/checklists.py` in the last message, no `ui/checklist_window.py` changes yet for toolbar buttons/dialogs.

## Known bugs / open issues
- Checklist window sizing on g-tiles: previous fixes (forced resize, monitor-geometry sizing) were reverted; current approach is default_size+min_size+scrollable toolbar — **not yet confirmed fixed by user**.
- No drag-and-drop reordering (deliberately deferred; right-click move up/down implemented instead).

## Unfinished tasks (from approved staged plan)
Stage 1 (in progress):
1. ✅ Stage/item reordering via right-click — done
2. ⏳ Export Checklist button → markdown (core fn done, UI button + dialog not done)
3. ⏳ Delete All Checklist Data button → **must have 2 confirmations**, deletes only current project (core fn done, UI not done)

Stage 2 (not started): Code review output directory setting (settings dialog + `core/code_review.py` + `main_window.py`)

Stage 3 (not started): Terminal launch fix — commands should open in terminal with command typed/ready, user presses Enter; fix Command Manager "Run in Terminal" which currently may not type/run correctly with Kitty.

Stage 4 (not started): Per-project commands panel — new `core/project_commands.py`, JSON per project path, UI panel (likely right side) with name/command/copy/run-silent/run-terminal/edit/delete, separate from global Favourites.

Stage 5 (not started): Project sidebar — rename/update project path after folder rename, right-click menu (folder/terminal/vscode/review/checklist/rename path/remove), reorder projects (move up/down, drag-and-drop if safe).

Also requested: resizable sidebar/layout review (paned widths).

## Exact next recommended steps
1. Finish Stage 1: add toolbar buttons in `ui/checklist_window.py`:
   - "📤 Export" → opens a dialog showing `checklists.export_markdown()` output in a read-only/copyable TextView (or saves to file + copy to clipboard)
   - "🗑 Delete All" → two sequential `Gtk.MessageDialog` confirmations, then `checklists.delete_project_data()`, clear `self.project_data`, refresh UI
2. Then proceed to Stage 2 (code review directory setting) — touches `core/settings.py` DEFAULTS, `ui/settings_dialog.py`, `core/code_review.py` signature, `ui/main_window.py` `_run_code_review`.
3. Then Stage 3 (terminal fix), Stage 4 (project commands panel), Stage 5 (sidebar improvements).

## User preferences / constraints
- Incremental, file-by-file, small patches; explain plan before code; no full-file rewrites unless necessary.
- Linux Mint Cinnamon, g-tiles tiling WM — window sizing must respect WM tiling, avoid forced `resize()`.
- Terminal = Kitty (`kitty --hold` pattern used elsewhere); keep terminal fallback chain (`kitty`, `x-terminal-emulator`, `gnome-terminal`, `xterm`).
- Keep global Favourites (`core/favourites.py`) separate from new per-project commands.
- Defensive error handling; avoid big dependencies; avoid over-engineering.
- Max 1 feature/fix per response; group large idea lists into stages and confirm before proceeding.

## Testing commands
```bash
python3 ~/Projects/multi-commit/main.py
```
Manual checklist test flow: open project → ✅ Checklist → import markdown roadmap → toggle items → right-click reorder/rename/duplicate → toggle autosave → close window (check unsaved warning) → reopen and verify persistence in `~/.config/multi-commit/checklists.json`.

## Git commit style
- `feat: ...`, `fix: ...`, `refactor: ...`, `docs: ...`, `chore: ...`
- End every completed patch with:
```bash
git add <files>
git commit -m "<commit message>"
```