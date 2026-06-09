"""Git operations — all subprocess calls live here."""
import subprocess

def _run(cmd, cwd):
    """Run a shell command in the given directory. Returns (success, output)."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, shell=True,
            capture_output=True, text=True
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)

def git_add(path, target="."):
    return _run(f"git add {target}", path)

def git_commit(path, message):
    safe = message.replace('"', '\\"')
    return _run(f'git commit -m "{safe}"', path)

def git_push(path, remote="origin", branch=""):
    cmd = f"git push {remote} {branch}".strip()
    return _run(cmd, path)

def run_custom(path, command):
    return _run(command, path)

def get_remotes(path):
    """Return list of configured git remotes."""
    ok, out = _run("git remote", path)
    if ok and out:
        return out.splitlines()
    return []

def get_current_branch(path):
    ok, out = _run("git branch --show-current", path)
    return out if ok else "main"

def is_git_repo(path):
    ok, _ = _run("git rev-parse --is-inside-work-tree", path)
    return ok

def get_status(path):
    ok, out = _run("git status --short", path)
    return out if ok else ""