import sys, subprocess

# Adjust the command if your Auto-GPT fork uses a different start command.
# Common options: python -m autogpt  OR  python scripts/main.py
subprocess.run([sys.executable, "-m", "autogpt"], check=True)
