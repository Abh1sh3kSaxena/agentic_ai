import sys
from pathlib import Path

# Ensure project root is on sys.path so tests can import top-level modules
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
