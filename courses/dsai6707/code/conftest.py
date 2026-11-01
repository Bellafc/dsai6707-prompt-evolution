import sys
from pathlib import Path

# Make `evo_prompt` importable when pytest is run from the repository root.
sys.path.insert(0, str(Path(__file__).resolve().parent))
