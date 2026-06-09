"""Favourites manager dialog + runner."""
import subprocess
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango
from core import favourites
from core.git_ops import run_custom
from core import settings

class FavouritesDialog(Gtk.Dialog):
    def __init__(self, parent, project_path=None):
        super().__init__(title="⭐ Favourite Commands", transient_for=parent, flags=0)
        self.set_default_size(700, 480)
        self.project_path = project_path
        self._build()
        self.show_all()

    def _build(self):
        box = self.get_content_area()
        box.set_border_width(0)

        # Toolbar
        toolbar = Gtk.Box(spacing=8)
        toolbar.set_border_width(8)

        add_btn = Gtk.Button(label="➕ New Command")
        add_btn.connect("clicked", self._add_favourite)
        toolbar.pack_start(add_btn, False, False, 0)

        self.cat_filter = Gtk.ComboBoxText()
        self.cat_filter.append_text("All Categories")
        self.cat_filter.set_active(0)
        for cat in favourites.get_categories():
            self.cat_filter.append_text(cat)
        self.cat_filter.connect("changed", lambda _: self._refresh())
        toolbar.pack_start(self.cat_filter, False, False, 0)

        box.pack_start(toolbar, False, False, 0)
        box.pack_start(Gtk.Separator(), False, False, 0)

        # Main paned: list left, detail right
        paned = Gtk.Paned()
        paned.set_position(280)
        box.pack_start(paned, True, True, 0)

        # Left — favourites list
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scroll = Gtk.ScrolledWindow()
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.connect("row-selected", self._on_select)
        scroll.add(self.list_box)
        left.pack_start(scroll, True, True, 0)
        paned.pack1(left, resize=False, shrink=False)

        # Right — detail/run panel
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        right.set_border_width(12)

        self.detail_name = Gtk.Label()
        self.detail_name.set_markup("<b>Select a command</b>")
        self.detail_name.set_halign(Gtk.Align.START)
        self.detail_name.set_line_wrap(True)
        right.pack_start(self.detail_name, False, False, 0)

        self.detail_cmd = Gtk.TextView()
        self.detail_cmd.set_editable(False)
        self.detail_cmd.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.detail_cmd.set_monospace(True)
        cmd_scroll = Gtk.ScrolledWindow()
        cmd_scroll.set_min_content_height(60)
        cmd_scroll.set_max_content_height(80)
        cmd_scroll.add(self.detail_cmd)
        right.pack_start(cmd_scroll, False, False, 0)

        self.detail_meta = Gtk.Label(label="")
        self.detail_meta.set_halign(Gtk.Align.START)
        self.detail_meta.get_style_context().add_class("dim-label")
        right.pack_start(self.detail_meta, False, False, 0)

        sep = Gtk.Separator()
        right.pack_start(sep, False, False, 0)

        # Run buttons
        btn_box = Gtk.Box(spacing=8)
        self.run_btn = Gtk.Button(label="▶ Run")
        self.run_btn.set_sensitive(False)
        self.run_btn.connect("clicked", self._run_selected)
        btn_box.pack_start(self.run_btn, False, False, 0)

        self.run_term_btn = Gtk.Button(label="🖥 Run in Terminal")
        self.run_term_btn.set_sensitive(False)
        self.run_term_btn.connect("clicked", lambda _: self._run_selected(None, force_terminal=True))
        btn_box.pack_start(self.run_term_btn, False, False, 0)

        self.edit_btn = Gtk.Button(label="✏ Edit")
        self.edit_btn.set_sensitive(False)
        self.edit_btn.connect("clicked", self._edit_selected)
        btn_box.pack_start(self.edit_btn, False, False, 0)

        self.del_btn = Gtk.Button(label="🗑 Delete")
        self.del_btn.set_sensitive(False)
        self.del_btn.connect("clicked", self._delete_selected)
        btn_box.pack_end(self.del_btn, False, False, 0)

        right.pack_start(btn_box, False, False, 0)

        # Output
        out_lbl = Gtk.Label()
        out_lbl.set_markup("<b>Output</b>")
        out_lbl.set_halign(Gtk.Align.START)
        right.pack_start(out_lbl, False, False, 0)

        out_scroll = Gtk.ScrolledWindow()
        out_scroll.set_min_content_height(120)
        self.output_buf = Gtk.TextBuffer()
        self.output_view = Gtk.TextView(buffer=self.output_buf)
        self.output_view.set_editable(False)
        self.output_view.set_monospace(True)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        out_scroll.add(self.output_view)
        right.pack_start(out_scroll, True, True, 0)

        paned.pack2(right, resize=True, shrink=False)
        self._refresh()

    def _refresh(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)

        cat_sel = self.cat_filter.get_active_text()
        favs = favourites.load()

        for i, fav in enumerate(favs):
            if cat_sel and cat_sel != "All Categories" and fav.get("category") != cat_sel:
                continue
            row = Gtk.ListBoxRow()
            row.fav_index = i
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            vbox.set_border_width(8)

            name_lbl = Gtk.Label(label=fav["name"])
            name_lbl.set_halign(Gtk.Align.START)
            name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
            name_lbl.set_max_width_chars(30)
            vbox.pack_start(name_lbl, False, False, 0)

            meta = f"📂 {fav.get('category','General')}"
            if fav.get("use_terminal"):
                meta += "  🖥 terminal"
            meta_lbl = Gtk.Label(label=meta)
            meta_lbl.set_halign(Gtk.Align.START)
            meta_lbl.get_style_context().add_class("dim-label")
            vbox.pack_start(meta_lbl, False, False, 0)

            row.add(vbox)
            self.list_box.add(row)

        self.list_box.show_all()

    def _on_select(self, listbox, row):
        if not row: return
        fav = favourites.load()[row.fav_index]
        self.selected_index = row.fav_index
        self.detail_name.set_markup(f"<b>{fav['name']}</b>")
        self.detail_cmd.get_buffer().set_text(fav["command"])
        term_str = "Yes — opens in terminal" if fav.get("use_terminal") else "No — runs silently"
        self.detail_meta.set_text(f"Category: {fav.get('category','General')}   |   Terminal: {term_str}")
        for btn in [self.run_btn, self.run_term_btn, self.edit_btn, self.del_btn]:
            btn.set_sensitive(True)

    def _run_selected(self, _, force_terminal=False):
        fav = favourites.load()[self.selected_index]
        cmd = fav["command"]
        use_term = force_terminal or fav.get("use_terminal", False)
        cwd = self.project_path or os.path.expanduser("~")

        if use_term:
            bash_cmd = f"{cmd}; echo; echo '--- Done. Press Enter to close ---'; read"
            term = settings.get("terminal_cmd")
            for t in [term, "kitty", "x-terminal-emulator", "gnome-terminal", "xterm"]:
                try:
                    subprocess.Popen([t, "--", "bash", "-c", bash_cmd], cwd=cwd)
                    self._log(f"🖥 Opened terminal for: {fav['name']}")
                    return
                except FileNotFoundError:
                    continue
        else:
            ok, out = run_custom(cwd, cmd)
            self._log(f"▶ {fav['name']}\n$ {cmd}\n{out}\n{'✅ Done' if ok else '❌ Failed'}")

    def _log(self, text):
        end = self.output_buf.get_end_iter()
        self.output_buf.insert(end, text + "\n")

    def _add_favourite(self, _):
        self._open_edit_dialog()

    def _edit_selected(self, _):
        fav = favourites.load()[self.selected_index]
        self._open_edit_dialog(fav, self.selected_index)

    def _delete_selected(self, _):
        fav = favourites.load()[self.selected_index]
        dlg = Gtk.MessageDialog(
            transient_for=self, flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete '{fav['name']}'?"
        )
        if dlg.run() == Gtk.ResponseType.YES:
            favourites.remove(self.selected_index)
            self._refresh()
        dlg.destroy()

    def _open_edit_dialog(self, fav=None, index=None):
        dlg = _EditFavouriteDialog(self, fav)
        if dlg.run() == Gtk.ResponseType.OK:
            data = dlg.get_data()
            if index is not None:
                favourites.update(index, **data)
            else:
                favourites.add(**data)
            self._refresh()
            # Refresh category filter
            active = self.cat_filter.get_active_text()
            self.cat_filter.remove_all()
            self.cat_filter.append_text("All Categories")
            for cat in favourites.get_categories():
                self.cat_filter.append_text(cat)
            self.cat_filter.set_active(0)
        dlg.destroy()


class _EditFavouriteDialog(Gtk.Dialog):
    def __init__(self, parent, fav=None):
        title = "Edit Command" if fav else "New Favourite Command"
        super().__init__(title=title, transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_SAVE,   Gtk.ResponseType.OK)
        self.set_default_size(500, 300)
        self.fav = fav or {}
        self._build()
        self.show_all()

    def _build(self):
        box = self.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        grid = Gtk.Grid(column_spacing=12, row_spacing=8)

        def lbl(text):
            l = Gtk.Label(label=text)
            l.set_halign(Gtk.Align.START)
            return l

        # Name
        self.name_entry = Gtk.Entry()
        self.name_entry.set_text(self.fav.get("name", ""))
        self.name_entry.set_placeholder_text("e.g. Push to Uni Remote")
        grid.attach(lbl("Name:"),    0, 0, 1, 1)
        grid.attach(self.name_entry, 1, 0, 1, 1)

        # Category
        self.cat_entry = Gtk.Entry()
        self.cat_entry.set_text(self.fav.get("category", "General"))
        self.cat_entry.set_placeholder_text("e.g. Git, System, Dev")
        grid.attach(lbl("Category:"), 0, 1, 1, 1)
        grid.attach(self.cat_entry,   1, 1, 1, 1)

        box.pack_start(grid, False, False, 0)

        # Command (multiline)
        box.pack_start(lbl("Command:"), False, False, 0)
        self.cmd_view = Gtk.TextView()
        self.cmd_view.set_monospace(True)
        self.cmd_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.cmd_buf = self.cmd_view.get_buffer()
        self.cmd_buf.set_text(self.fav.get("command", ""))
        cmd_scroll = Gtk.ScrolledWindow()
        cmd_scroll.set_min_content_height(80)
        cmd_scroll.add(self.cmd_view)
        box.pack_start(cmd_scroll, True, True, 0)

        # Terminal toggle
        term_box = Gtk.Box(spacing=8)
        term_box.pack_start(lbl("Open in terminal (for password prompts etc.):"), False, False, 0)
        self.term_switch = Gtk.Switch()
        self.term_switch.set_active(self.fav.get("use_terminal", False))
        term_box.pack_start(self.term_switch, False, False, 0)
        box.pack_start(term_box, False, False, 0)

    def get_data(self) -> dict:
        start, end = self.cmd_buf.get_bounds()
        return {
            "name":         self.name_entry.get_text().strip(),
            "command":      self.cmd_buf.get_text(start, end, False).strip(),
            "category":     self.cat_entry.get_text().strip() or "General",
            "use_terminal": self.term_switch.get_active(),
        }