"""Run independently; shared blueprint_core is an explicit installed dependency."""
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from metalens_workflow.cli import main

if __name__ == '__main__':
    raise SystemExit(main())
