import sys
from pathlib import Path

# Ensure the backend root is on sys.path so `pipeline` and `api` are importable
sys.path.insert(0, str(Path(__file__).parent))
