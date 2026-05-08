#!/home/hermes/.venv/bin/python3
"""Generate Mermaid PNG from /tmp/mermaid.mmd. Output: /tmp/mermaid-diagram.png"""
import base64, shutil, subprocess, sys
from pathlib import Path

INPUT  = "/tmp/mermaid.mmd"
OUTPUT = "/tmp/mermaid-diagram.png"

mermaid_source = Path(INPUT).read_text().strip()

def _path_exists(p):
    try:
        return Path(p).exists()
    except (PermissionError, OSError):
        return False

def try_mmdc():
    for candidate in [shutil.which("mmdc"), "/usr/local/bin/mmdc", "/usr/bin/mmdc",
                      "/root/.npm-global/bin/mmdc", str(Path.home() / ".npm-global/bin/mmdc")]:
        if candidate and _path_exists(candidate):
            r = subprocess.run([candidate, "-i", INPUT, "-o", OUTPUT, "-b", "white"],
                               capture_output=True, text=True)
            if r.returncode == 0: return True, f"mmdc ({candidate})"
    return False, None

def try_install_mmdc():
    npm = shutil.which("npm")
    if not npm: return False, None
    subprocess.run([npm, "install", "-g", "@mermaid-js/mermaid-cli"],
                   capture_output=True, timeout=120)
    return try_mmdc()

def try_mermaid_ink():
    encoded = base64.urlsafe_b64encode(mermaid_source.encode()).decode()
    url = f"https://mermaid.ink/img/{encoded}"
    try:
        import httpx
        r = httpx.get(url, timeout=30, follow_redirects=True)
        if r.status_code == 200:
            Path(OUTPUT).write_bytes(r.content)
            return True, "mermaid.ink API"
    except Exception as e:
        print(f"mermaid.ink error: {e}", file=sys.stderr)
    return False, None

for fn in [try_mmdc, try_install_mmdc, try_mermaid_ink]:
    ok, method = fn()
    if ok:
        print(f"PNG written to {OUTPUT} ({Path(OUTPUT).stat().st_size} bytes, method: {method})")
        sys.exit(0)
print("ERROR: all methods failed", file=sys.stderr)
sys.exit(1)
