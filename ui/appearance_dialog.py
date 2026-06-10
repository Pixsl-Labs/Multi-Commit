"""Appearance dialog — live theme editor with presets + custom hex."""
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
from core import settings

# ── Built-in presets ──
PRESETS = {
    "🔴 Red & Black (Default)": {
        "accent":      "#c0392b",
        "accent_dark": "#922b21",
        "highlight":   "#e74c3c",
        "sidebar_sel": "linear-gradient(90deg, #c0392b, #922b21)",
    },
    "🔵 Ocean Blue": {
        "accent":      "#2980b9",
        "accent_dark": "#1a5276",
        "highlight":   "#3498db",
        "sidebar_sel": "linear-gradient(90deg, #2980b9, #1a5276)",
    },
    "🟣 Purple Haze": {
        "accent":      "#8e44ad",
        "accent_dark": "#6c3483",
        "highlight":   "#9b59b6",
        "sidebar_sel": "linear-gradient(90deg, #8e44ad, #6c3483)",
    },
    "🟢 Hacker Green": {
        "accent":      "#27ae60",
        "accent_dark": "#1e8449",
        "highlight":   "#2ecc71",
        "sidebar_sel": "linear-gradient(90deg, #27ae60, #1e8449)",
    },
    "🟠 Burnt Orange": {
        "accent":      "#d35400",
        "accent_dark": "#a04000",
        "highlight":   "#e67e22",
        "sidebar_sel": "linear-gradient(90deg, #d35400, #a04000)",
    },
    "⚪ Midnight Silver": {
        "accent":      "#566573",
        "accent_dark": "#2c3e50",
        "highlight":   "#7f8c8d",
        "sidebar_sel": "linear-gradient(90deg, #566573, #2c3e50)",
    },
    "🩷 Neon Pink": {
        "accent":      "#c0392b",
        "accent_dark": "#76448a",
        "highlight":   "#e91e8c",
        "sidebar_sel": "linear-gradient(90deg, #e91e8c, #76448a)",
    },
}

def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def _rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

def build_css(theme: dict) -> bytes:
    a  = theme["accent"]
    ad = theme["accent_dark"]
    h  = theme["highlight"]
    ss = theme["sidebar_sel"]
    return f"""
    .quick-commit-btn {{
        background: linear-gradient(135deg, {a}, {ad});
        color: white; font-weight: bold;
        border-radius: 6px; padding: 6px 16px; border: none;
    }}
    .project-row:selected {{ background: {ss}; }}
    .git-badge {{ background: {a}; color: white; border-radius: 3px; padding: 0 4px; font-size: 10px; }}
    .result-ok {{ color: #2ecc71; font-size: 11px; }}
    .result-fail {{ color: {h}; font-size: 11px; }}
    .branch-label {{ font-size: 10px; color: {h}; }}
    .step-card {{
        background: alpha(white, 0.04); border-radius: 6px;
        border: 1px solid alpha(white, 0.08); padding: 10px; margin: 4px 0;
    }}
    .tool-card {{
        background: alpha(white, 0.03); border-radius: 6px;
        border: 1px solid alpha(white, 0.06); margin: 4px 0;
    }}
    .commit-header {{ padding: 12px 16px 8px 16px; border-bottom: 1px solid alpha(white,0.08); }}
    .step-title {{ font-size: 12px; font-weight: bold; opacity: 0.7; }}
    .history-view {{ font-size: 11px; font-family: monospace; opacity: 0.8; }}
    .output-view  {{ font-size: 11px; font-family: monospace; }}
    .shortcut-hint {{ font-size: 10px; opacity: 0.45; }}
    .remote-auth-btn {{ color: {h}; }}
    .project-name {{ font-size: 13px; font-weight: bold; }}
    .project-path {{ font-size: 10px; opacity: 0.55; }}
    .action-btn {{ padding: 2px 6px; font-size: 11px; border-radius: 4px; border: 1px solid alpha(white, 0.15); }}
    .panel-header {{ background: alpha(white, 0.04); border-bottom: 1px solid alpha(white, 0.1); padding: 8px; }}
    .project-row {{ border-bottom: 1px solid alpha(white, 0.07); }}
    """.encode()

_provider = None

def apply_theme(theme: dict):
    global _provider
    screen = Gdk.Screen.get_default()
    if _provider:
        Gtk.StyleContext.remove_provider_for_screen(screen, _provider)
    _provider = Gtk.CssProvider()
    _provider.load_from_data(build_css(theme))
    Gtk.StyleContext.add_provider_for_screen(
        screen, _provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
    settings.set_value("theme", theme)

def load_theme():
    t = settings.get("theme")
    if not t:
        return PRESETS["🔴 Red & Black (Default)"]
    return t


class AppearanceDialog(Gtk.Window):
    """Standalone window so user can see main window change live."""
    def __init__(self, parent):
        super().__init__(title="🎨 Appearance")
        self.set_transient_for(parent)
        self.set_default_size(420, 560)
        self.set_border_width(0)
        self.current_theme = dict(load_theme())
        self._build()
        self.show_all()

    def _build(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Header
        hdr = Gtk.Box(spacing=8)
        hdr.set_border_width(12)
        title = Gtk.Label()
        title.set_markup("<b>Appearance</b>  <small>Changes apply live</small>")
        title.set_halign(Gtk.Align.START)
        hdr.pack_start(title, True, True, 0)
        vbox.pack_start(hdr, False, False, 0)
        vbox.pack_start(Gtk.Separator(), False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        inner = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        inner.set_border_width(12)

        # ── Presets ──
        inner.pack_start(self._section("Presets"), False, False, 0)
        preset_flow = Gtk.FlowBox()
        preset_flow.set_max_children_per_line(2)
        preset_flow.set_selection_mode(Gtk.SelectionMode.NONE)
        preset_flow.set_row_spacing(6)
        preset_flow.set_column_spacing(6)

        for name, theme in PRESETS.items():
            btn = self._preset_btn(name, theme)
            preset_flow.add(btn)
        inner.pack_start(preset_flow, False, False, 0)

        inner.pack_start(Gtk.Separator(), False, False, 0)

        # ── Custom colours ──
        inner.pack_start(self._section("Custom Colours"), False, False, 0)

        grid = Gtk.Grid(column_spacing=12, row_spacing=10)
        grid.set_border_width(4)

        def colour_row(r, label, key):
            lbl = Gtk.Label(label=label)
            lbl.set_halign(Gtk.Align.START)
            grid.attach(lbl, 0, r, 1, 1)

            btn = Gtk.ColorButton()
            try:
                rgba = Gdk.RGBA()
                rgba.parse(self.current_theme.get(key, "#c0392b"))
                btn.set_rgba(rgba)
            except Exception:
                pass
            btn.connect("color-set", self._on_colour_set, key)
            grid.attach(btn, 1, r, 1, 1)

            hex_entry = Gtk.Entry()
            hex_entry.set_text(self.current_theme.get(key, "#c0392b"))
            hex_entry.set_width_chars(10)
            hex_entry.connect("activate", self._on_hex_entry, key, btn)
            grid.attach(hex_entry, 2, r, 1, 1)
            return hex_entry

        self.hex_accent      = colour_row(0, "Accent colour",      "accent")
        self.hex_accent_dark = colour_row(1, "Accent dark",         "accent_dark")
        self.hex_highlight   = colour_row(2, "Highlight / links",   "highlight")
        inner.pack_start(grid, False, False, 0)

        # Gradient preview strip
        inner.pack_start(self._section("Gradient Preview"), False, False, 0)
        self.preview_bar = Gtk.DrawingArea()
        self.preview_bar.set_size_request(-1, 32)
        self.preview_bar.connect("draw", self._draw_preview)
        inner.pack_start(self.preview_bar, False, False, 0)

        inner.pack_start(Gtk.Separator(), False, False, 0)

        # ── Buttons ──
        btn_box = Gtk.Box(spacing=8)
        reset_btn = Gtk.Button(label="↩ Reset to Default")
        reset_btn.connect("clicked", self._reset)
        btn_box.pack_start(reset_btn, False, False, 0)

        save_btn = Gtk.Button(label="💾 Save Theme")
        save_btn.connect("clicked", self._save)
        btn_box.pack_end(save_btn, False, False, 0)
        inner.pack_start(btn_box, False, False, 0)

        scroll.add(inner)
        vbox.pack_start(scroll, True, True, 0)

    def _section(self, text):
        lbl = Gtk.Label()
        lbl.set_markup(f"<b>{text}</b>")
        lbl.set_halign(Gtk.Align.START)
        return lbl

    def _preset_btn(self, name, theme):
        btn = Gtk.Button(label=name)
        btn.set_relief(Gtk.ReliefStyle.NONE)

        def on_click(_):
            self.current_theme = dict(theme)
            apply_theme(self.current_theme)
            self._sync_entries()
            self.preview_bar.queue_draw()

        btn.connect("clicked", on_click)
        return btn

    def _on_colour_set(self, btn, key):
        rgba = btn.get_rgba()
        hex_col = _rgb_to_hex(rgba.red, rgba.green, rgba.blue)
        self.current_theme[key] = hex_col
        if key in ("accent", "accent_dark"):
            self.current_theme["sidebar_sel"] = (
                f"linear-gradient(90deg, {self.current_theme['accent']}, {self.current_theme['accent_dark']})"
            )
        apply_theme(self.current_theme)
        self.preview_bar.queue_draw()

    def _on_hex_entry(self, entry, key, colour_btn):
        val = entry.get_text().strip()
        if not val.startswith("#") or len(val) not in (4, 7):
            return
        try:
            rgba = Gdk.RGBA()
            rgba.parse(val)
            colour_btn.set_rgba(rgba)
            self.current_theme[key] = val
            if key in ("accent", "accent_dark"):
                self.current_theme["sidebar_sel"] = (
                    f"linear-gradient(90deg, {self.current_theme['accent']}, {self.current_theme['accent_dark']})"
                )
            apply_theme(self.current_theme)
            self.preview_bar.queue_draw()
        except Exception:
            pass

    def _draw_preview(self, widget, cr):
        a = self.current_theme.get("accent", "#c0392b")
        ad = self.current_theme.get("accent_dark", "#922b21")
        try:
            r1, g1, b1 = _hex_to_rgb(a)
            r2, g2, b2 = _hex_to_rgb(ad)
        except Exception:
            return
        w = widget.get_allocated_width()
        h = widget.get_allocated_height()
        grad = __import__("cairo", fromlist=["LinearGradient"]).LinearGradient(0, 0, w, 0)
        grad.add_color_stop_rgb(0, r1, g1, b1)
        grad.add_color_stop_rgb(1, r2, g2, b2)
        cr.set_source(grad)
        cr.rectangle(0, 0, w, h)
        cr.fill()

    def _sync_entries(self):
        self.hex_accent.set_text(self.current_theme.get("accent", ""))
        self.hex_accent_dark.set_text(self.current_theme.get("accent_dark", ""))
        self.hex_highlight.set_text(self.current_theme.get("highlight", ""))

    def _reset(self, _):
        self.current_theme = dict(PRESETS["🔴 Red & Black (Default)"])
        apply_theme(self.current_theme)
        self._sync_entries()
        self.preview_bar.queue_draw()

    def _save(self, _):
        settings.set_value("theme", self.current_theme)
        self.destroy()