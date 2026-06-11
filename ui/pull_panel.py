"""Pull / Fetch panel."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from core.git_ops import run_custom


class PullPanel(Gtk.Box):
    def __init__(self, on_done=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.set_border_width(10)
        self.project_path = None
        self.on_done = on_done
        self._build()

    def _build(self):
        row = Gtk.Box(spacing=6)

        for label, cmd in [
            ("Pull", "git pull"),
            ("Pull --rebase", "git pull --rebase"),
            ("Fetch All", "git fetch --all"),
            ("Fetch Origin", "git fetch origin"),
        ]:
            btn = Gtk.Button(label=label)
            btn.connect("clicked", self._run, cmd)
            row.pack_start(btn, False, False, 0)

        self.pack_start(row, False, False, 0)

        self.result_lbl = Gtk.Label(label="")
        self.result_lbl.set_halign(Gtk.Align.START)
        self.pack_start(self.result_lbl, False, False, 0)

    def refresh(self, path=None):
        if path:
            self.project_path = path

    def _run(self, _, cmd):
        if not self.project_path:
            self.result_lbl.set_text("❌ No project selected")
            return

        ok, out = run_custom(self.project_path, cmd)
        self.result_lbl.set_text(("✅ " if ok else "❌ ") + (out or cmd))

        if ok and self.on_done:
            self.on_done()