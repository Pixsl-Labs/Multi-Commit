"""Settings dialog with Preferences + Remotes/Accounts tabs."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from core import settings
from core.git_ops import run_custom, get_remotes
import os

class SettingsDialog(Gtk.Dialog):
    def __init__(self, parent, project_path=None):
        super().__init__(title="Settings", transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                        Gtk.STOCK_SAVE,   Gtk.ResponseType.OK)
        self.set_default_size(480, 360)
        self.project_path = project_path
        self.s = settings.load()
        self._build()
        self.connect("response", self._on_response)

    def _build(self):
        box = self.get_content_area()
        notebook = Gtk.Notebook()
        notebook.set_border_width(8)
        box.add(notebook)

        notebook.append_page(self._prefs_tab(),   Gtk.Label(label="⚙ Preferences"))
        notebook.append_page(self._remotes_tab(), Gtk.Label(label="🔗 Remotes / Accounts"))
        box.show_all()

    # ── Preferences tab ──

    def _prefs_tab(self):
        grid = Gtk.Grid(column_spacing=16, row_spacing=10)
        grid.set_border_width(16)

        def row(r, lbl_text, widget, hint=None):
            lbl = Gtk.Label(label=lbl_text)
            lbl.set_halign(Gtk.Align.START)
            grid.attach(lbl, 0, r, 1, 1)
            grid.attach(widget, 1, r, 1, 1)
            if hint:
                h = Gtk.Label(label=hint)
                h.get_style_context().add_class("dim-label")
                h.set_halign(Gtk.Align.START)
                grid.attach(h, 0, r+1, 2, 1)

        self.auto_add  = Gtk.Switch(); self.auto_add.set_active(self.s["auto_git_add"])
        self.auto_push = Gtk.Switch(); self.auto_push.set_active(self.s["auto_git_push"])
        self.add_target  = Gtk.Entry(); self.add_target.set_text(self.s["default_add_target"])
        self.vscode_cmd  = Gtk.Entry(); self.vscode_cmd.set_text(self.s["vscode_cmd"])
        self.terminal_cmd = Gtk.Entry(); self.terminal_cmd.set_text(self.s["terminal_cmd"])
        self.code_review_dir = Gtk.Entry()
        self.code_review_dir.set_text(self.s.get("code_review_output_dir", "~/Projects/Code Reviews"))

        browse_btn = Gtk.Button(label="Browse")
        browse_btn.connect("clicked", self._choose_code_review_dir)

        code_review_box = Gtk.Box(spacing=6)
        code_review_box.pack_start(self.code_review_dir, True, True, 0)
        code_review_box.pack_start(browse_btn, False, False, 0)
        self.code_review_box = code_review_box
        self.default_remote = Gtk.Entry(); self.default_remote.set_text(self.s["default_remote"])
        self.code_review_dir = Gtk.Entry()
        self.code_review_dir.set_text(self.s.get("code_review_output_dir", "~/Projects/Code Reviews"))

        browse_btn = Gtk.Button(label="Browse")
        browse_btn.connect("clicked", self._choose_code_review_dir)

        code_review_box = Gtk.Box(spacing=6)
        code_review_box.pack_start(self.code_review_dir, True, True, 0)
        code_review_box.pack_start(browse_btn, False, False, 0)
        self.code_review_box = code_review_box

        row(0, "Auto git add on project select", self.auto_add)
        row(1, "Auto push after commit",         self.auto_push)
        row(2, "Default git add target",         self.add_target)
        row(3, "VSCode command",                 self.vscode_cmd)
        row(4, "Terminal command",               self.terminal_cmd)
        row(5, "Default remote",                 self.default_remote)
        row(6, "Code review output folder",       self.code_review_box)
        return grid
    
    def _choose_code_review_dir(self, _):
        dlg = Gtk.FileChooserDialog(
            title="Choose Code Review Output Folder",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )

        current = os.path.expanduser(
            self.code_review_dir.get_text().strip() or "~/Projects/Code Reviews"
        )
        os.makedirs(current, exist_ok=True)
        dlg.set_current_folder(current)

        if dlg.run() == Gtk.ResponseType.OK:
            self.code_review_dir.set_text(dlg.get_filename())

        dlg.destroy()

    # ── Remotes tab ──

    def _remotes_tab(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_border_width(12)

        info = Gtk.Label()
        info.set_markup("Add git remotes to the <b>currently selected project</b>.\nCredential caching is set globally.")
        info.set_halign(Gtk.Align.START)
        info.set_line_wrap(True)
        vbox.pack_start(info, False, False, 0)

        # Existing remotes list
        self.remotes_store = Gtk.ListStore(str, str)  # name, url
        tv = Gtk.TreeView(model=self.remotes_store)
        tv.append_column(Gtk.TreeViewColumn("Remote", Gtk.CellRendererText(), text=0))
        tv.append_column(Gtk.TreeViewColumn("URL",    Gtk.CellRendererText(), text=1))
        tv.set_headers_visible(True)

        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(100)
        scroll.add(tv)
        vbox.pack_start(scroll, True, True, 0)

        self._refresh_remotes_list()

        # Add new remote
        sep = Gtk.Separator()
        vbox.pack_start(sep, False, False, 4)

        add_lbl = Gtk.Label()
        add_lbl.set_markup("<b>Add / Update Remote</b>")
        add_lbl.set_halign(Gtk.Align.START)
        vbox.pack_start(add_lbl, False, False, 0)

        grid = Gtk.Grid(column_spacing=8, row_spacing=6)
        self.new_remote_name = Gtk.Entry()
        self.new_remote_name.set_placeholder_text("e.g. uni")
        self.new_remote_url  = Gtk.Entry()
        self.new_remote_url.set_placeholder_text("e.g. https://github.com/UNI-USER/repo.git")
        self.new_remote_url.set_width_chars(40)

        grid.attach(Gtk.Label(label="Name:"), 0, 0, 1, 1)
        grid.attach(self.new_remote_name,     1, 0, 1, 1)
        grid.attach(Gtk.Label(label="URL:"),  0, 1, 1, 1)
        grid.attach(self.new_remote_url,      1, 1, 1, 1)
        vbox.pack_start(grid, False, False, 0)

        add_btn = Gtk.Button(label="➕ Add Remote")
        add_btn.connect("clicked", self._add_remote)
        vbox.pack_start(add_btn, False, False, 0)

        # Credential caching section
        sep2 = Gtk.Separator()
        vbox.pack_start(sep2, False, False, 4)

        cred_lbl = Gtk.Label()
        cred_lbl.set_markup("<b>Credential Caching</b>")
        cred_lbl.set_halign(Gtk.Align.START)
        vbox.pack_start(cred_lbl, False, False, 0)

        cred_hint = Gtk.Label(label="Cache your password so you don't type it every push.")
        cred_hint.set_halign(Gtk.Align.START)
        cred_hint.get_style_context().add_class("dim-label")
        vbox.pack_start(cred_hint, False, False, 0)

        timeout_box = Gtk.Box(spacing=8)
        timeout_box.pack_start(Gtk.Label(label="Cache timeout (seconds):"), False, False, 0)
        self.cache_timeout = Gtk.SpinButton.new_with_range(300, 86400, 300)
        self.cache_timeout.set_value(3600)
        timeout_box.pack_start(self.cache_timeout, False, False, 0)
        vbox.pack_start(timeout_box, False, False, 0)

        cache_btn = Gtk.Button(label="💾 Enable Credential Cache")
        cache_btn.connect("clicked", self._enable_credential_cache)
        self.cred_result = Gtk.Label(label="")
        self.cred_result.set_halign(Gtk.Align.START)
        vbox.pack_start(cache_btn, False, False, 0)
        vbox.pack_start(self.cred_result, False, False, 0)

        return vbox

    def _refresh_remotes_list(self):
        self.remotes_store.clear()
        if not self.project_path:
            self.remotes_store.append(["(no project selected)", ""])
            return
        ok, out = run_custom(self.project_path, "git remote -v")
        seen = set()
        if ok and out:
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 2 and parts[0] not in seen:
                    self.remotes_store.append([parts[0], parts[1]])
                    seen.add(parts[0])

    def _add_remote(self, _):
        if not self.project_path:
            return
        name = self.new_remote_name.get_text().strip()
        url  = self.new_remote_url.get_text().strip()
        if not name or not url:
            return
        # Try add, fall back to set-url if already exists
        ok, out = run_custom(self.project_path, f"git remote add {name} {url}")
        if not ok:
            ok, out = run_custom(self.project_path, f"git remote set-url {name} {url}")
        self._refresh_remotes_list()
        self.new_remote_name.set_text("")
        self.new_remote_url.set_text("")

    def _enable_credential_cache(self, _):
        timeout = int(self.cache_timeout.get_value())
        ok, out = run_custom("~", f"git config --global credential.helper 'cache --timeout={timeout}'")
        self.cred_result.set_text("✅ Credential cache enabled!" if ok else f"❌ {out}")

    def _on_response(self, dlg, response):
        if response == Gtk.ResponseType.OK:
            settings.save({
                "auto_git_add":      self.auto_add.get_active(),
                "auto_git_push":     self.auto_push.get_active(),
                "default_add_target": self.add_target.get_text(),
                "vscode_cmd":        self.vscode_cmd.get_text(),
                "terminal_cmd":      self.terminal_cmd.get_text(),
                "default_remote":    self.default_remote.get_text(),
                "code_review_output_dir": self.code_review_dir.get_text()
            })