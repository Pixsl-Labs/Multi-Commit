"""Desktop notifications via notify-send."""
import subprocess
import os

ICON = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "assets", "icon.png")
)

def _send(title: str, body: str, urgency: str = "normal"):
    try:
        subprocess.Popen([
            "notify-send",
            "--icon", ICON,
            "--urgency", urgency,
            "--app-name", "Multi-Commit",
            title, body
        ])
    except FileNotFoundError:
        pass  # notify-send not installed — silently skip

def success(title: str, body: str = ""):
    _send(f"✅ {title}", body, urgency="normal")

def error(title: str, body: str = ""):
    _send(f"❌ {title}", body, urgency="critical")

def info(title: str, body: str = ""):
    _send(title, body, urgency="low")

# ── Convenience wrappers ──

def pushed(remote: str, project: str):
    success("Push successful", f"{project} → {remote}")

def push_failed(remote: str, project: str, reason: str = ""):
    error("Push failed", f"{project} → {remote}\n{reason[:80]}")

def committed(message: str, project: str):
    info("Committed", f"{project}: {message[:60]}")

def code_review_done(path: str):
    success("Code review saved", os.path.basename(path))