"""Left panel — recent projects list with open buttons."""
import os
import subprocess
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, GdkPixbuf
from core import project_manager, settings
from core.git_ops import is_git_repo, get_status, get_current_branch

STATUS_CLEAN    = "🟢"
STATUS_UNSTAGED = "🟡"
STATUS_CONFLICT = "🔴"

def _get_status_icon(path):
    if not is_git_repo(path):
        return ""
    s = get_status(path)
    if not s:
        return STATUS_CLEAN
    if "U" in s or "AA" in s or "DD" in s:
        return STATUS_CONFLICT
    return STATUS_UNSTAGED

class ProjectListPanel(Gtk.Box):
    def __init__(self, on_select):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.on_select = on_select
        self.selected_path = None
        self._apply_css()
        self._build()
        self.refresh()

    def _apply_css(self):
        css = b"""
        .project-row { border-bottom: 1px solid alpha(white, 0.07); }
        .project-row:selected { background: linear-gradient(90deg, #c0392b, #922b21); }
        .project-name { font-size: 13px; font-weight: bold; }
        .project-path { font-size: 10px; opacity: 0.55; }
        .git-badge {
            background: #27ae60; color: white;
            border-radius: 3px; padding: 0 4px;
            font-size: 10px;
        }
        .status-clean    { color: #2ecc71; }
        .status-unstaged { color: #f39c12; }
        .status-conflict { color: #e74c3c; }
        .branch-label { font-size: 10px; color: #3498db; }
        .action-btn {
            padding: 2px 6px; font-size: 11px;
            border-radius: 4px;
            border: 1px solid alpha(white, 0.15);
        }
        .panel-header {
            background: alpha(white, 0.04);
            border-bottom: 1px solid alpha(white, 0.1);
            padding: 8px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            __import__("gi.repository", fromlist=["Gdk"]).Gdk.Screen.get_default(),
            provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _build(self):
        # Header
        hdr = Gtk.Box(spacing=6)
        hdr.get_style_context().add_class("panel-header")
        lbl = Gtk.Label()
        lbl.set_markup("<b>Projects</b>")
        lbl.set_halign(Gtk.Align.START)
        hdr.pack_start(lbl, True, True, 0)

        refresh_btn = Gtk.Button(label="↻")
        refresh_btn.set_tooltip_text("Refresh statuses")
        refresh_btn.set_relief(Gtk.ReliefStyle.NONE)
        refresh_btn.connect("clicked", lambda _: self.refresh())
        hdr.pack_end(refresh_btn, False, False, 0)

        add_btn = Gtk.Button(label="+ Open")
        add_btn.connect("clicked", lambda _: self.open_folder_dialog())
        hdr.pack_end(add_btn, False, False, 0)
        self.pack_start(hdr, False, False, 0)

        # Scrollable list
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.connect("row-selected", self._on_row_selected)
        scroll.add(self.list_box)
        self.pack_start(scroll, True, True, 0)

    def refresh(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)

        projects = project_manager.load_recent()
        if not projects:
            lbl = Gtk.Label(label="No projects yet.\nClick '+ Open' to add one.")
            lbl.set_justify(Gtk.Justification.CENTER)
            lbl.set_margin_top(20)
            row = Gtk.ListBoxRow()
            row.add(lbl)
            row.set_selectable(False)
            self.list_box.add(row)
        else:
            for path in projects:
                self.list_box.add(self._make_row(path))
        self.list_box.show_all()

    def _make_row(self, path):
        row = Gtk.ListBoxRow()
        row.path = path
        row.get_style_context().add_class("project-row")

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        vbox.set_border_width(8)

        # Top line: status icon + name + git badge
        top = Gtk.Box(spacing=6)
        status_icon = _get_status_icon(path)
        status_lbl = Gtk.Label(label=status_icon)
        top.pack_start(status_lbl, False, False, 0)

        name = Gtk.Label(label=os.path.basename(path))
        name.set_halign(Gtk.Align.START)
        name.set_ellipsize(Pango.EllipsizeMode.END)
        name.set_max_width_chars(20)
        name.get_style_context().add_class("project-name")
        top.pack_start(name, True, True, 0)

        if is_git_repo(path):
            badge = Gtk.Label(label=" git ")
            badge.get_style_context().add_class("git-badge")
            top.pack_end(badge, False, False, 0)

            branch = get_current_branch(path)
            branch_lbl = Gtk.Label(label=f"  {branch}")
            branch_lbl.get_style_context().add_class("branch-label")
            top.pack_end(branch_lbl, False, False, 0)

        vbox.pack_start(top, False, False, 0)

        # Path
        path_lbl = Gtk.Label(label=path)
        path_lbl.set_halign(Gtk.Align.START)
        path_lbl.set_ellipsize(Pango.EllipsizeMode.START)
        path_lbl.set_max_width_chars(32)
        path_lbl.get_style_context().add_class("project-path")
        vbox.pack_start(path_lbl, False, False, 0)

        # Action buttons
        btn_box = Gtk.Box(spacing=4)
        btn_box.set_margin_top(4)

        for label, tip, cb in [
            ("📁 Folder",   "Open in file manager", lambda _, p=path: self._open_folder(p)),
            ("💻 VSCode",   "Open in VSCode",        lambda _, p=path: self._open_vscode(p)),
            ("🖥 Terminal", "Open terminal here",    lambda _, p=path: self._open_terminal(p)),
        ]:
            btn = Gtk.Button(label=label)
            btn.set_tooltip_text(tip)
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.get_style_context().add_class("action-btn")
            btn.connect("clicked", cb)
            btn_box.pack_start(btn, False, False, 0)

        rm = Gtk.Button(label="✕")
        rm.set_tooltip_text("Remove from list")
        rm.set_relief(Gtk.ReliefStyle.NONE)
        rm.connect("clicked", lambda _, p=path: self._remove(p))
        btn_box.pack_end(rm, False, False, 0)

        vbox.pack_start(btn_box, False, False, 0)
        row.add(vbox)
        return row

    def _on_row_selected(self, listbox, row):
        if row and hasattr(row, "path"):
            self.selected_path = row.path
            self.on_select(row.path)

    def open_folder_dialog(self):
        dlg = Gtk.FileChooserDialog(
            title="Select Project Folder",
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )
        dlg.set_current_folder(os.path.expanduser("~/Projects"))
        if dlg.run() == Gtk.ResponseType.OK:
            path = dlg.get_filename()
            project_manager.add_recent(path)
            self.refresh()
            self.on_select(path)
        dlg.destroy()

    def _open_folder(self, path):
        subprocess.Popen(["xdg-open", path])

    def _open_vscode(self, path):
        cmd = settings.get("vscode_cmd")
        subprocess.Popen([cmd, path])

    def _open_terminal(self, path):
        term = settings.get("terminal_cmd")
        for t in [term, "kitty", "x-terminal-emulator", "gnome-terminal", "xterm"]:
            try:
                subprocess.Popen([t], cwd=path)
                return
            except FileNotFoundError:
                continue

    def _remove(self, path):
        project_manager.remove_recent(path)
        self.refresh()