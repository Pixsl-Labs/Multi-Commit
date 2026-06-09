"""Stash manager panel."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango
from core.git_ops import run_custom

class StashPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_border_width(10)
        self.project_path = None
        self._build()

    def _build(self):
        # Save stash row
        top = Gtk.Box(spacing=6)
        self.stash_msg_entry = Gtk.Entry()
        self.stash_msg_entry.set_placeholder_text("Stash description (optional)…")
        self.stash_msg_entry.connect("activate", self._save_stash)
        top.pack_start(self.stash_msg_entry, True, True, 0)

        save_btn = Gtk.Button(label="💾 Stash")
        save_btn.set_tooltip_text("Save current changes to stash")
        save_btn.connect("clicked", self._save_stash)
        top.pack_start(save_btn, False, False, 0)
        self.pack_start(top, False, False, 0)

        # Stash list
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(100)
        scroll.set_max_content_height(140)
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scroll.add(self.list_box)
        self.pack_start(scroll, True, True, 0)

        # Action buttons for selected stash
        btn_row = Gtk.Box(spacing=6)
        self.pop_btn = Gtk.Button(label="⬆ Pop")
        self.pop_btn.set_tooltip_text("Apply and remove stash")
        self.pop_btn.set_sensitive(False)
        self.pop_btn.connect("clicked", self._pop_stash)
        btn_row.pack_start(self.pop_btn, False, False, 0)

        self.apply_btn = Gtk.Button(label="↩ Apply")
        self.apply_btn.set_tooltip_text("Apply stash but keep it")
        self.apply_btn.set_sensitive(False)
        self.apply_btn.connect("clicked", self._apply_stash)
        btn_row.pack_start(self.apply_btn, False, False, 0)

        self.drop_btn = Gtk.Button(label="🗑 Drop")
        self.drop_btn.set_sensitive(False)
        self.drop_btn.connect("clicked", self._drop_stash)
        btn_row.pack_end(self.drop_btn, False, False, 0)
        self.pack_start(btn_row, False, False, 0)

        self.result_lbl = Gtk.Label(label="")
        self.result_lbl.set_halign(Gtk.Align.START)
        self.pack_start(self.result_lbl, False, False, 0)

        self.list_box.connect("row-selected", self._on_select)

    def refresh(self, path=None):
        if path:
            self.project_path = path
        if not self.project_path:
            return

        for child in self.list_box.get_children():
            self.list_box.remove(child)

        ok, out = run_custom(self.project_path, "git stash list")
        if not ok or not out:
            lbl = Gtk.Label(label="No stashes")
            lbl.get_style_context().add_class("dim-label")
            lbl.set_margin_top(8)
            row = Gtk.ListBoxRow()
            row.add(lbl)
            row.set_selectable(False)
            self.list_box.add(row)
        else:
            for i, line in enumerate(out.splitlines()):
                row = Gtk.ListBoxRow()
                row.stash_ref = f"stash@{{{i}}}"
                lbl = Gtk.Label(label=line)
                lbl.set_halign(Gtk.Align.START)
                lbl.set_ellipsize(Pango.EllipsizeMode.END)
                lbl.set_border_width(6)
                row.add(lbl)
                self.list_box.add(row)

        self.list_box.show_all()
        for btn in [self.pop_btn, self.apply_btn, self.drop_btn]:
            btn.set_sensitive(False)

    def _on_select(self, listbox, row):
        if row and hasattr(row, "stash_ref"):
            self.selected_ref = row.stash_ref
            for btn in [self.pop_btn, self.apply_btn, self.drop_btn]:
                btn.set_sensitive(True)

    def _save_stash(self, _):
        if not self.project_path:
            return
        msg = self.stash_msg_entry.get_text().strip()
        cmd = f'git stash push -m "{msg}"' if msg else "git stash push"
        ok, out = run_custom(self.project_path, cmd)
        self.result_lbl.set_text(("✅ " if ok else "❌ ") + (out or "Stashed"))
        self.stash_msg_entry.set_text("")
        self.refresh()

    def _pop_stash(self, _):
        ok, out = run_custom(self.project_path, f"git stash pop {self.selected_ref}")
        self.result_lbl.set_text(("✅ Popped" if ok else "❌ ") + (out if not ok else ""))
        self.refresh()

    def _apply_stash(self, _):
        ok, out = run_custom(self.project_path, f"git stash apply {self.selected_ref}")
        self.result_lbl.set_text(("✅ Applied" if ok else "❌ ") + (out if not ok else ""))
        self.refresh()

    def _drop_stash(self, _):
        ok, out = run_custom(self.project_path, f"git stash drop {self.selected_ref}")
        self.result_lbl.set_text(("✅ Dropped" if ok else "❌ ") + (out if not ok else ""))
        self.refresh()