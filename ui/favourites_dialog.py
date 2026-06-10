"""Command Manager — standalone window replacing favourites_dialog."""
import subprocess
import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, Gdk
from core import favourites
from core.git_ops import run_custom
from core import settings

class CommandManagerWindow(Gtk.Window):
    def __init__(self, parent, project_path=None):
        super().__init__(title="⚡ Command Manager")
        self.set_transient_for(parent)
        self.set_default_size(820, 560)
        self.project_path = project_path
        self.selected_index = None
        self._apply_css()
        self._build()
        self.show_all()

    def _apply_css(self):
        css = b"""
        .cmd-row { border-bottom: 1px solid alpha(white, 0.07); }
        .cmd-row:selected { background: alpha(white, 0.08); }
        .cmd-name { font-size: 13px; font-weight: bold; }
        .cat-badge {
            background: alpha(white, 0.1);
            border-radius: 3px; padding: 0 5px;
            font-size: 10px;
        }
        .cmd-preview {
            font-family: monospace; font-size: 11px;
            opacity: 0.6;
        }
        .output-view { font-family: monospace; font-size: 11px; }
        .toolbar-box {
            background: alpha(white, 0.03);
            border-bottom: 1px solid alpha(white, 0.08);
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
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # ── Toolbar ──
        toolbar = Gtk.Box(spacing=8)
        toolbar.get_style_context().add_class("toolbar-box")

        new_btn = Gtk.Button(label="➕ New Command")
        new_btn.connect("clicked", lambda _: self._open_edit_dialog())
        toolbar.pack_start(new_btn, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search commands…")
        self.search_entry.connect("search-changed", lambda _: self._refresh())
        toolbar.pack_start(self.search_entry, True, True, 0)

        self.cat_combo = Gtk.ComboBoxText()
        self.cat_combo.append_text("All Categories")
        self.cat_combo.set_active(0)
        for cat in favourites.get_categories():
            self.cat_combo.append_text(cat)
        self.cat_combo.connect("changed", lambda _: self._refresh())
        toolbar.pack_start(self.cat_combo, False, False, 0)

        vbox.pack_start(toolbar, False, False, 0)

        # ── Main paned ──
        paned = Gtk.Paned()
        paned.set_position(300)
        vbox.pack_start(paned, True, True, 0)

        # Left — command list
        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.connect("row-selected", self._on_select)
        scroll.add(self.list_box)
        left.pack_start(scroll, True, True, 0)
        paned.pack1(left, resize=False, shrink=False)

        # Right — detail panel
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # Detail header
        self.detail_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.detail_box.set_border_width(12)

        self.detail_name = Gtk.Label()
        self.detail_name.set_markup("<span size='large'><b>Select a command</b></span>")
        self.detail_name.set_halign(Gtk.Align.START)
        self.detail_name.set_line_wrap(True)
        self.detail_box.pack_start(self.detail_name, False, False, 0)

        self.detail_meta = Gtk.Label(label="")
        self.detail_meta.set_halign(Gtk.Align.START)
        self.detail_meta.get_style_context().add_class("dim-label")
        self.detail_box.pack_start(self.detail_meta, False, False, 0)

        # Command preview box
        cmd_frame_lbl = Gtk.Label()
        cmd_frame_lbl.set_markup("<b>Command</b>")
        cmd_frame_lbl.set_halign(Gtk.Align.START)
        self.detail_box.pack_start(cmd_frame_lbl, False, False, 0)

        cmd_scroll = Gtk.ScrolledWindow()
        cmd_scroll.set_min_content_height(70)
        cmd_scroll.set_max_content_height(100)
        self.detail_cmd_view = Gtk.TextView()
        self.detail_cmd_view.set_editable(False)
        self.detail_cmd_view.set_monospace(True)
        self.detail_cmd_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.detail_cmd_buf = self.detail_cmd_view.get_buffer()
        cmd_scroll.add(self.detail_cmd_view)
        self.detail_box.pack_start(cmd_scroll, False, False, 0)

        # Copy command button
        copy_btn = Gtk.Button(label="📋 Copy Command to Clipboard")
        copy_btn.connect("clicked", self._copy_command)
        self.detail_box.pack_start(copy_btn, False, False, 0)

        self.detail_box.pack_start(Gtk.Separator(), False, False, 4)

        # Action buttons
        btn_box = Gtk.Box(spacing=8)

        self.run_btn = Gtk.Button(label="▶ Run Silently")
        self.run_btn.set_sensitive(False)
        self.run_btn.set_tooltip_text("Run in background, output shown below")
        self.run_btn.connect("clicked", self._run_silent)
        btn_box.pack_start(self.run_btn, False, False, 0)

        self.run_term_btn = Gtk.Button(label="🖥 Run in Terminal")
        self.run_term_btn.set_sensitive(False)
        self.run_term_btn.set_tooltip_text("Open Kitty terminal and run there")
        self.run_term_btn.connect("clicked", self._run_in_terminal)
        btn_box.pack_start(self.run_term_btn, False, False, 0)

        self.edit_btn = Gtk.Button(label="✏ Edit")
        self.edit_btn.set_sensitive(False)
        self.edit_btn.connect("clicked", self._edit_selected)
        btn_box.pack_start(self.edit_btn, False, False, 0)

        self.del_btn = Gtk.Button(label="🗑 Delete")
        self.del_btn.set_sensitive(False)
        self.del_btn.connect("clicked", self._delete_selected)
        btn_box.pack_end(self.del_btn, False, False, 0)

        self.detail_box.pack_start(btn_box, False, False, 0)

        # Output log
        out_lbl = Gtk.Label()
        out_lbl.set_markup("<b>Output</b>")
        out_lbl.set_halign(Gtk.Align.START)
        self.detail_box.pack_start(out_lbl, False, False, 0)

        out_scroll = Gtk.ScrolledWindow()
        out_scroll.set_min_content_height(130)
        self.output_buf = Gtk.TextBuffer()
        self.output_view = Gtk.TextView(buffer=self.output_buf)
        self.output_view.set_editable(False)
        self.output_view.set_monospace(True)
        self.output_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.output_view.get_style_context().add_class("output-view")
        out_scroll.add(self.output_view)
        self.detail_box.pack_start(out_scroll, True, True, 0)

        right.pack_start(self.detail_box, True, True, 0)
        paned.pack2(right, resize=True, shrink=False)

        self._refresh()

    def _refresh(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)

        cat_sel = self.cat_combo.get_active_text()
        query = self.search_entry.get_text().strip().lower()
        favs = favourites.load()

        for i, fav in enumerate(favs):
            if cat_sel and cat_sel != "All Categories" and fav.get("category") != cat_sel:
                continue
            if query and query not in fav["name"].lower() and query not in fav["command"].lower():
                continue

            row = Gtk.ListBoxRow()
            row.fav_index = i
            row.get_style_context().add_class("cmd-row")

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            vbox.set_border_width(8)

            # Name + category badge
            top = Gtk.Box(spacing=6)
            name_lbl = Gtk.Label(label=fav["name"])
            name_lbl.set_halign(Gtk.Align.START)
            name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
            name_lbl.set_max_width_chars(24)
            name_lbl.get_style_context().add_class("cmd-name")
            top.pack_start(name_lbl, True, True, 0)

            cat_lbl = Gtk.Label(label=fav.get("category", "General"))
            cat_lbl.get_style_context().add_class("cat-badge")
            top.pack_end(cat_lbl, False, False, 0)

            if fav.get("use_terminal"):
                term_lbl = Gtk.Label(label="🖥")
                term_lbl.set_tooltip_text("Opens in terminal")
                top.pack_end(term_lbl, False, False, 0)

            vbox.pack_start(top, False, False, 0)

            # Command preview
            preview = fav["command"][:60] + ("…" if len(fav["command"]) > 60 else "")
            prev_lbl = Gtk.Label(label=preview)
            prev_lbl.set_halign(Gtk.Align.START)
            prev_lbl.set_ellipsize(Pango.EllipsizeMode.END)
            prev_lbl.get_style_context().add_class("cmd-preview")
            vbox.pack_start(prev_lbl, False, False, 0)

            row.add(vbox)
            self.list_box.add(row)

        self.list_box.show_all()

    def _on_select(self, listbox, row):
        if not row or not hasattr(row, "fav_index"):
            return
        fav = favourites.load()[row.fav_index]
        self.selected_index = row.fav_index
        self.detail_name.set_markup(f"<span size='large'><b>{fav['name']}</b></span>")
        self.detail_cmd_buf.set_text(fav["command"])
        term_str = "Yes — opens in terminal" if fav.get("use_terminal") else "No — runs silently"
        self.detail_meta.set_text(
            f"📂 {fav.get('category','General')}   |   🖥 Terminal: {term_str}"
        )
        for btn in [self.run_btn, self.run_term_btn, self.edit_btn, self.del_btn]:
            btn.set_sensitive(True)

    def _copy_command(self, _):
        if self.selected_index is None:
            return
        fav = favourites.load()[self.selected_index]
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(fav["command"], -1)
        self._log(f"📋 Copied to clipboard: {fav['name']}")

    def _run_silent(self, _):
        if self.selected_index is None:
            return
        fav = favourites.load()[self.selected_index]
        cwd = self.project_path or os.path.expanduser("~")
        ok, out = run_custom(cwd, fav["command"])
        self._log(f"▶ {fav['name']}\n$ {fav['command']}\n{out}\n{'✅ Done' if ok else '❌ Failed'}")

    def _run_in_terminal(self, _):
        if self.selected_index is None:
            return
        fav = favourites.load()[self.selected_index]
        cmd = fav["command"]
        cwd = self.project_path or os.path.expanduser("~")
        # Wrap: run the command, show output, hold window open
        bash_cmd = f'echo "$ {cmd}"; echo; {cmd}; echo; echo "--- Done. Press Enter to close ---"; read'
        term = settings.get("terminal_cmd")
        launched = False
        for t in [term, "kitty", "x-terminal-emulator", "gnome-terminal", "xterm"]:
            try:
                if t == "kitty":
                    subprocess.Popen(
                        ["kitty", "--hold", "bash", "-c", bash_cmd],
                        cwd=cwd
                    )
                elif t == "gnome-terminal":
                    subprocess.Popen(
                        ["gnome-terminal", "--", "bash", "-c", bash_cmd],
                        cwd=cwd
                    )
                else:
                    subprocess.Popen(
                        [t, "--", "bash", "-c", bash_cmd],
                        cwd=cwd
                    )
                self._log(f"🖥 Opened terminal for: {fav['name']}")
                launched = True
                return
            except FileNotFoundError:
                continue
        if not launched:
            self._log("❌ No terminal found — check Settings > terminal_cmd")

    def _log(self, text):
        end = self.output_buf.get_end_iter()
        self.output_buf.insert(end, text + "\n")
        self.output_view.scroll_to_iter(self.output_buf.get_end_iter(), 0, False, 0, 0)

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
            self.selected_index = None
            for btn in [self.run_btn, self.run_term_btn, self.edit_btn, self.del_btn]:
                btn.set_sensitive(False)
            self._refresh()
            self._refresh_cat_combo()
        dlg.destroy()

    def _open_edit_dialog(self, fav=None, index=None):
        dlg = _EditCommandDialog(self, fav)
        if dlg.run() == Gtk.ResponseType.OK:
            data = dlg.get_data()
            if index is not None:
                favourites.update(index, **data)
            else:
                favourites.add(**data)
            self._refresh()
            self._refresh_cat_combo()
        dlg.destroy()

    def _refresh_cat_combo(self):
        self.cat_combo.remove_all()
        self.cat_combo.append_text("All Categories")
        for cat in favourites.get_categories():
            self.cat_combo.append_text(cat)
        self.cat_combo.set_active(0)


class _EditCommandDialog(Gtk.Dialog):
    def __init__(self, parent, fav=None):
        title = "Edit Command" if fav else "New Command"
        super().__init__(title=title, transient_for=parent, flags=0)
        self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_SAVE,   Gtk.ResponseType.OK)
        self.set_default_size(520, 320)
        self.fav = fav or {}
        self._build()
        self.show_all()

    def _build(self):
        box = self.get_content_area()
        box.set_border_width(12)
        box.set_spacing(8)

        grid = Gtk.Grid(column_spacing=12, row_spacing=8)

        def lbl(t):
            l = Gtk.Label(label=t)
            l.set_halign(Gtk.Align.START)
            return l

        self.name_entry = Gtk.Entry()
        self.name_entry.set_text(self.fav.get("name", ""))
        self.name_entry.set_placeholder_text("e.g. Push to Uni Remote")
        grid.attach(lbl("Name:"),    0, 0, 1, 1)
        grid.attach(self.name_entry, 1, 0, 1, 1)

        self.cat_entry = Gtk.Entry()
        self.cat_entry.set_text(self.fav.get("category", "General"))
        self.cat_entry.set_placeholder_text("e.g. Git, System, Dev")
        grid.attach(lbl("Category:"), 0, 1, 1, 1)
        grid.attach(self.cat_entry,   1, 1, 1, 1)
        box.pack_start(grid, False, False, 0)

        box.pack_start(lbl("Command:"), False, False, 0)
        self.cmd_view = Gtk.TextView()
        self.cmd_view.set_monospace(True)
        self.cmd_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.cmd_buf = self.cmd_view.get_buffer()
        self.cmd_buf.set_text(self.fav.get("command", ""))
        cmd_scroll = Gtk.ScrolledWindow()
        cmd_scroll.set_min_content_height(90)
        cmd_scroll.add(self.cmd_view)
        box.pack_start(cmd_scroll, True, True, 0)

        term_box = Gtk.Box(spacing=8)
        term_box.pack_start(lbl("Open in terminal (for passwords/interactive):"), False, False, 0)
        self.term_switch = Gtk.Switch()
        self.term_switch.set_active(self.fav.get("use_terminal", False))
        term_box.pack_start(self.term_switch, False, False, 0)
        box.pack_start(term_box, False, False, 0)

    def get_data(self):
        s, e = self.cmd_buf.get_bounds()
        return {
            "name":         self.name_entry.get_text().strip(),
            "command":      self.cmd_buf.get_text(s, e, False).strip(),
            "category":     self.cat_entry.get_text().strip() or "General",
            "use_terminal": self.term_switch.get_active(),
        }