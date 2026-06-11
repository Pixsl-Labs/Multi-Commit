"""Tag manager panel."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

from core.git_ops import run_custom


class TagPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_border_width(10)
        self.project_path = None
        self.selected_tag = None
        self._build()

    def _build(self):
        top = Gtk.Box(spacing=6)

        self.tag_entry = Gtk.Entry()
        self.tag_entry.set_placeholder_text("Tag name e.g. v1.0.0")
        self.tag_entry.connect("activate", self._create_tag)
        top.pack_start(self.tag_entry, True, True, 0)

        create_btn = Gtk.Button(label="＋ Create")
        create_btn.connect("clicked", self._create_tag)
        top.pack_start(create_btn, False, False, 0)

        push_btn = Gtk.Button(label="⬆ Push Tag")
        push_btn.connect("clicked", self._push_selected_tag)
        top.pack_start(push_btn, False, False, 0)

        self.pack_start(top, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(100)
        scroll.set_max_content_height(150)

        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.list_box.connect("row-selected", self._on_select)

        scroll.add(self.list_box)
        self.pack_start(scroll, True, True, 0)

        btn_row = Gtk.Box(spacing=6)

        refresh_btn = Gtk.Button(label="↻ Refresh")
        refresh_btn.connect("clicked", lambda _: self.refresh())
        btn_row.pack_start(refresh_btn, False, False, 0)

        push_all_btn = Gtk.Button(label="⬆ Push All Tags")
        push_all_btn.connect("clicked", self._push_all_tags)
        btn_row.pack_start(push_all_btn, False, False, 0)

        delete_btn = Gtk.Button(label="🗑 Delete Selected")
        delete_btn.connect("clicked", self._delete_selected_tag)
        btn_row.pack_end(delete_btn, False, False, 0)

        self.pack_start(btn_row, False, False, 0)

        self.result_lbl = Gtk.Label(label="")
        self.result_lbl.set_halign(Gtk.Align.START)
        self.result_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        self.pack_start(self.result_lbl, False, False, 0)

    def refresh(self, path=None):
        if path:
            self.project_path = path

        if not self.project_path:
            return

        self.selected_tag = None

        for child in self.list_box.get_children():
            self.list_box.remove(child)

        ok, out = run_custom(self.project_path, "git tag --sort=-creatordate")

        if not ok or not out:
            row = Gtk.ListBoxRow()
            row.set_selectable(False)
            lbl = Gtk.Label(label="No tags yet")
            lbl.get_style_context().add_class("dim-label")
            lbl.set_margin_top(8)
            row.add(lbl)
            self.list_box.add(row)
        else:
            for tag in out.splitlines():
                row = Gtk.ListBoxRow()
                row.tag_name = tag.strip()

                lbl = Gtk.Label(label=tag.strip())
                lbl.set_halign(Gtk.Align.START)
                lbl.set_border_width(6)
                row.add(lbl)

                self.list_box.add(row)

        self.list_box.show_all()

    def _on_select(self, _, row):
        if row and hasattr(row, "tag_name"):
            self.selected_tag = row.tag_name

    def _create_tag(self, _):
        if not self.project_path:
            return

        tag = self.tag_entry.get_text().strip()

        if not tag:
            self.result_lbl.set_text("❌ Tag name is empty")
            return

        ok, out = run_custom(self.project_path, f"git tag {tag}")
        self.result_lbl.set_text(("✅ Created " if ok else "❌ ") + (tag if ok else out))

        if ok:
            self.tag_entry.set_text("")
            self.refresh()

    def _push_selected_tag(self, _):
        if not self.project_path:
            return

        if not self.selected_tag:
            self.result_lbl.set_text("❌ Select a tag first")
            return

        ok, out = run_custom(self.project_path, f"git push origin {self.selected_tag}")
        self.result_lbl.set_text(("✅ Pushed " if ok else "❌ ") + (self.selected_tag if ok else out))

    def _push_all_tags(self, _):
        if not self.project_path:
            return

        ok, out = run_custom(self.project_path, "git push origin --tags")
        self.result_lbl.set_text("✅ Pushed all tags" if ok else f"❌ {out}")

    def _delete_selected_tag(self, _):
        if not self.project_path:
            return

        if not self.selected_tag:
            self.result_lbl.set_text("❌ Select a tag first")
            return

        ok, out = run_custom(self.project_path, f"git tag -d {self.selected_tag}")
        self.result_lbl.set_text(("✅ Deleted " if ok else "❌ ") + (self.selected_tag if ok else out))

        if ok:
            self.refresh()