import sys
from pathlib import Path

import uvicorn

# Add the project root to Python path for imports
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.src.api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
