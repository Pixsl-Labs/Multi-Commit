"""Code review generator — adapted from Sam's original code_reviewer.py"""
import os
from datetime import datetime

SKIP_DIRS = {
    "__pycache__", ".git", "venv", ".env", "node_modules",
    ".vscode", ".idea", "Code Reviews"
}
SKIP_FILES = {
    ".gitignore", ".DS_Store", "Progress_Notes.md",
    "mimeinfo.cache", "mimeapps.list"
}
SKIP_EXTENSIONS = {
    ".pyc", ".pyo", ".egg-info", ".lock", ".png",
    ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".zip", ".tar", ".gz", ".log"
}

EXT_LANG = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".html": "html", ".css": "css", ".sh": "bash",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".md": "markdown", ".txt": "", ".ini": "ini",
    ".toml": "toml", ".c": "c", ".cpp": "cpp",
    ".java": "java", ".rs": "rust", ".go": "go",
}

def get_structure(path, prefix=""):
    lines = []
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return lines
    entries = [e for e in entries if e not in SKIP_DIRS and e not in SKIP_FILES]
    for i, entry in enumerate(entries):
        full = os.path.join(path, entry)
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(full):
            ext = "    " if is_last else "│   "
            lines.extend(get_structure(full, prefix + ext))
    return lines

def get_files(path):
    result = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in sorted(dirs) if d not in SKIP_DIRS]
        for f in sorted(files):
            if f in SKIP_FILES:
                continue
            if os.path.splitext(f)[1].lower() in SKIP_EXTENSIONS:
                continue
            full = os.path.join(root, f)
            rel  = os.path.relpath(full, path)
            result.append((rel, full))
    return result

def read_file(fp):
    try:
        with open(fp, encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"[Could not read: {e}]"

def generate(project_path: str, output_dir: str) -> str:
    """Generate a code review markdown file. Returns the output path."""
    name = os.path.basename(project_path)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# {name} — Code Review",
        f"> Generated: {date_str}",
        "",
        "## Project Structure",
        "",
        "```",
        f"{name}/",
        *get_structure(project_path),
        "```",
        "",
        "---",
        "",
        "## Files",
        "",
    ]

    for rel, full in get_files(project_path):
        lang = EXT_LANG.get(os.path.splitext(full)[1].lower(), "")
        content = read_file(full)
        lines += [
            f"### `{rel}`",
            "",
            f"```{lang}",
            content,
            "```",
            "",
            "---",
            "",
        ]

    os.makedirs(output_dir, exist_ok=True)
    filename = f"{name.lower().replace(' ', '_')}_code_review.md"
    out_path = os.path.join(output_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return out_path