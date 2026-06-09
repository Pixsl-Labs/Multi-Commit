"""Main GTK window — two panel layout."""
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from ui.project_list import ProjectListPanel
from ui.commit_panel import CommitPanel
from ui.settings_dialog import SettingsDialog
from ui.favourites_dialog import FavouritesDialog
from core import favourites

ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Multi-Commit")
        self.set_default_size(960, 640)
        self.set_border_width(0)

        # App icon
        try:
            self.set_icon_from_file(os.path.abspath(ICON_PATH))
        except Exception:
            pass

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        vbox.pack_start(self._build_menubar(), False, False, 0)

        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        paned.set_position(320)
        vbox.pack_start(paned, True, True, 0)

        self.commit_panel = CommitPanel()
        self.project_list = ProjectListPanel(on_select=self._on_project_selected)
        paned.pack1(self.project_list, resize=False, shrink=False)
        paned.pack2(self.commit_panel, resize=True,  shrink=False)

        # Status bar
        self.statusbar = Gtk.Statusbar()
        self.statusbar.push(0, "Ready — select a project to begin")
        vbox.pack_end(self.statusbar, False, False, 0)

    def _build_menubar(self):
        menubar = Gtk.MenuBar()

        # ── File ──
        file_menu = Gtk.Menu()
        file_item = Gtk.MenuItem(label="File")
        file_item.set_submenu(file_menu)

        open_item = Gtk.MenuItem(label="Open Project Folder")
        open_item.connect("activate", lambda _: self.project_list.open_folder_dialog())
        file_menu.append(open_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda _: Gtk.main_quit())
        file_menu.append(quit_item)

        # ── Favourites ──
        fav_menu = Gtk.Menu()
        fav_item = Gtk.MenuItem(label="⭐ Favourites")
        fav_item.set_submenu(fav_menu)

        manage_item = Gtk.MenuItem(label="Manage Favourite Commands…")
        manage_item.connect("activate", self._open_favourites)
        fav_menu.append(manage_item)

        fav_menu.append(Gtk.SeparatorMenuItem())

        # Quick-run favourites inline in menu
        self._populate_fav_menu(fav_menu)

        # ── Settings ──
        settings_menu = Gtk.Menu()
        settings_item = Gtk.MenuItem(label="Settings")
        settings_item.set_submenu(settings_menu)

        prefs_item = Gtk.MenuItem(label="Preferences…")
        prefs_item.connect("activate", self._open_settings)
        settings_menu.append(prefs_item)

        # ── Help ──
        help_menu = Gtk.Menu()
        help_item = Gtk.MenuItem(label="Help")
        help_item.set_submenu(help_menu)

        shortcuts_item = Gtk.MenuItem(label="Keyboard Shortcuts")
        shortcuts_item.connect("activate", self._show_shortcuts)
        help_menu.append(shortcuts_item)

        about_item = Gtk.MenuItem(label="About Multi-Commit")
        about_item.connect("activate", self._show_about)
        help_menu.append(about_item)

        menubar.append(file_item)
        menubar.append(fav_item)
        menubar.append(settings_item)
        menubar.append(help_item)
        return menubar

    def _populate_fav_menu(self, fav_menu):
        """Add each favourite as a quick-run menu item."""
        favs = favourites.load()
        # Group by category
        cats = {}
        for i, fav in enumerate(favs):
            cat = fav.get("category", "General")
            cats.setdefault(cat, []).append((i, fav))

        for cat, items in sorted(cats.items()):
            cat_item = Gtk.MenuItem(label=f"  {cat}")
            cat_item.set_sensitive(False)
            fav_menu.append(cat_item)
            for i, fav in items:
                mi = Gtk.MenuItem(label=f"    ▶ {fav['name']}")
                mi.connect("activate", self._quick_run_fav, i)
                fav_menu.append(mi)

    def _quick_run_fav(self, _, index):
        """Run a favourite directly from the menu."""
        from ui.favourites_dialog import FavouritesDialog
        import subprocess
        from core.git_ops import run_custom
        from core import settings as s
        fav = favourites.load()[index]
        cmd = fav["command"]
        cwd = self.commit_panel.project_path or os.path.expanduser("~")

        if fav.get("use_terminal"):
            bash_cmd = f"{cmd}; echo; echo '--- Done. Press Enter to close ---'; read"
            term = s.get("terminal_cmd")
            for t in [term, "kitty", "x-terminal-emulator", "gnome-terminal", "xterm"]:
                try:
                    subprocess.Popen([t, "--", "bash", "-c", bash_cmd], cwd=cwd)
                    self.statusbar.push(0, f"🖥 Running in terminal: {fav['name']}")
                    return
                except FileNotFoundError:
                    continue
        else:
            ok, out = run_custom(cwd, cmd)
            self.statusbar.push(0, f"{'✅' if ok else '❌'} {fav['name']}: {out[:80]}")

    def _on_project_selected(self, path):
        self.commit_panel.set_project(path)
        self.statusbar.push(0, f"Project: {path}")

    def _open_favourites(self, _):
        dlg = FavouritesDialog(self, project_path=self.commit_panel.project_path)
        dlg.run()
        dlg.destroy()

    def _open_settings(self, _):
        dlg = SettingsDialog(self, project_path=self.commit_panel.project_path)
        dlg.run()
        dlg.destroy()

    def _show_shortcuts(self, _):
        dlg = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Keyboard Shortcuts"
        )
        dlg.format_secondary_markup(
            "<b>Ctrl+Enter</b>  —  Quick Commit (add → commit → push all)\n"
            "<b>Enter</b>       —  Confirm current step\n"
            "<b>Ctrl+Q</b>      —  Quit\n"
        )
        dlg.run()
        dlg.destroy()

    def _show_about(self, _):
        dlg = Gtk.AboutDialog()
        dlg.set_transient_for(self)
        dlg.set_program_name("Multi-Commit")
        dlg.set_version("1.0.0")
        dlg.set_comments("Git GUI for multiple remotes on Linux")
        dlg.set_website("https://github.com/Pixsl-Labs/multi-commit")
        dlg.set_authors(["Sam (Pixsl-Labs)"])
        try:
            dlg.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_size(
                os.path.abspath(ICON_PATH), 64, 64))
        except Exception:
            pass
        dlg.run()
        dlg.destroy()