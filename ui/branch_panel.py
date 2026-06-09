"""Branch manager panel — embedded in commit panel as a revealer."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango
from core.git_ops import run_custom, get_current_branch

class BranchPanel(Gtk.Box):
    def __init__(self, on_branch_change=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_border_width(10)
        self.project_path = None
        self.on_branch_change = on_branch_change
        self._build()

    def _build(self):
        # Top row: new branch entry
        top = Gtk.Box(spacing=6)
        self.new_branch_entry = Gtk.Entry()
        self.new_branch_entry.set_placeholder_text("New branch name…")
        self.new_branch_entry.connect("activate", self._create_branch)
        top.pack_start(self.new_branch_entry, True, True, 0)

        create_btn = Gtk.Button(label="＋ Create")
        create_btn.connect("clicked", self._create_branch)
        top.pack_start(create_btn, False, False, 0)

        create_switch_btn = Gtk.Button(label="＋ Create & Switch")
        create_switch_btn.connect("clicked", lambda _: self._create_branch(None, switch=True))
        top.pack_start(create_switch_btn, False, False, 0)
        self.pack_start(top, False, False, 0)

        # Branch list
        scroll = Gtk.ScrolledWindow()
        scroll.set_min_content_height(120)
        scroll.set_max_content_height(160)
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scroll.add(self.list_box)
        self.pack_start(scroll, True, True, 0)

        # Result label
        self.result_lbl = Gtk.Label(label="")
        self.result_lbl.set_halign(Gtk.Align.START)
        self.pack_start(self.result_lbl, False, False, 0)

    def refresh(self, path=None):
        if path:
            self.project_path = path
        if not self.project_path:
            return

        for child in self.list_box.get_children():
            self.list_box.remove(child)

        ok, out = run_custom(self.project_path, "git branch -a")
        if not ok:
            return

        current = get_current_branch(self.project_path)

        for line in out.splitlines():
            line = line.strip()
            is_current = line.startswith("*")
            name = line.lstrip("* ").strip()
            is_remote = name.startswith("remotes/")

            row = Gtk.ListBoxRow()
            row.branch_name = name
            hbox = Gtk.Box(spacing=8)
            hbox.set_border_width(6)

            # Current indicator
            indicator = Gtk.Label(label="●" if is_current else "○")
            if is_current:
                indicator.set_markup('<span foreground="#2ecc71">●</span>')
            hbox.pack_start(indicator, False, False, 0)

            # Branch name
            lbl = Gtk.Label(label=name)
            lbl.set_halign(Gtk.Align.START)
            lbl.set_ellipsize(Pango.EllipsizeMode.END)
            if is_current:
                lbl.set_markup(f"<b>{name}</b>")
            hbox.pack_start(lbl, True, True, 0)

            if is_remote:
                remote_badge = Gtk.Label(label="remote")
                remote_badge.get_style_context().add_class("dim-label")
                hbox.pack_end(remote_badge, False, False, 0)
            elif not is_current:
                # Switch button
                sw_btn = Gtk.Button(label="Switch")
                sw_btn.set_relief(Gtk.ReliefStyle.NONE)
                sw_btn.connect("clicked", lambda _, n=name: self._switch_branch(n))
                hbox.pack_end(sw_btn, False, False, 0)

                # Delete button (not for current)
                del_btn = Gtk.Button(label="✕")
                del_btn.set_relief(Gtk.ReliefStyle.NONE)
                del_btn.set_tooltip_text("Delete branch")
                del_btn.connect("clicked", lambda _, n=name: self._delete_branch(n))
                hbox.pack_end(del_btn, False, False, 0)

            row.add(hbox)
            self.list_box.add(row)

        self.list_box.show_all()

    def _create_branch(self, _, switch=False):
        if not self.project_path:
            return
        name = self.new_branch_entry.get_text().strip()
        if not name:
            return
        if switch:
            ok, out = run_custom(self.project_path, f"git checkout -b {name}")
        else:
            ok, out = run_custom(self.project_path, f"git branch {name}")
        self.result_lbl.set_text(("✅ " if ok else "❌ ") + (out or f"Branch '{name}' created"))
        self.new_branch_entry.set_text("")
        self.refresh()
        if ok and self.on_branch_change:
            self.on_branch_change()

    def _switch_branch(self, name):
        if not self.project_path:
            return
        ok, out = run_custom(self.project_path, f"git checkout {name}")
        self.result_lbl.set_text(("✅ Switched to " if ok else "❌ ") + name + (f": {out}" if not ok else ""))
        self.refresh()
        if ok and self.on_branch_change:
            self.on_branch_change()

    def _delete_branch(self, name):
        dlg = Gtk.MessageDialog(
            transient_for=self.get_toplevel(), flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Delete branch '{name}'?"
        )
        if dlg.run() == Gtk.ResponseType.YES:
            ok, out = run_custom(self.project_path, f"git branch -d {name}")
            if not ok:
                ok, out = run_custom(self.project_path, f"git branch -D {name}")
            self.result_lbl.set_text(("✅ Deleted " if ok else "❌ ") + name)
            self.refresh()
        dlg.destroy()