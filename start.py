import os, sys, subprocess, time, shutil

# Prefer unbuffered output on Render logs
os.environ.setdefault("PYTHONUNBUFFERED", "1")

# Detect which entry file exists and build command accordingly
candidates = []

# Common “classic” entry
if os.path.exists("scripts/main.py"):
    candidates.append([sys.executable, "scripts/main.py"])

# Some forks expose a console script after install
if shutil.which("autogpt"):
    candidates.append(["autogpt", "run"])

# Fallback: module import (older releases installed as a package)
candidates.append([sys.executable, "-m", "autogpt"])

if not candidates:
    print("No known Auto-GPT entry found. Repo layout might differ.", flush=True)
    print("Top-level files:", os.listdir("."), flush=True)
    sys.exit(1)

while True:
    started_one = False
    for cmd in candidates:
        try:
            print("Starting:", " ".join(cmd), flush=True)
            subprocess.run(cmd, check=True)
            print("Process exited cleanly; restarting in 5s...", flush=True)
            time.sleep(5)
            started_one = True
            break
        except FileNotFoundError as e:
            print(f"Command not found: {cmd} ({e})", flush=True)
            continue
        except subprocess.CalledProcessError as e:
            print(f"Process crashed ({e}); restarting in 5s...", flush=True)
            time.sleep(5)
            started_one = True
            break

    if not started_one:
        print("No candidate commands could be executed. Listing repo tree:", flush=True)
        for root, dirs, files in os.walk(".", topdown=True):
            level = root.count(os.sep)
            indent = "  " * level
            print(f"{indent}{root}/", flush=True)
            for f in files[:50]:
                print(f"{indent}  {f}", flush=True)
        sys.exit(1)
