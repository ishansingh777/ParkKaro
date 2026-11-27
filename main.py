import importlib.util
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")

# Ensure backend directory is in sys.path so relative imports work
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Explicitly load backend/main.py without module name collision with root "main"
spec = importlib.util.spec_from_file_location("backend_app_module", os.path.join(BACKEND_DIR, "main.py"))
backend_module = importlib.util.module_from_spec(spec)
sys.modules["backend_app_module"] = backend_module
spec.loader.exec_module(backend_module)

app = backend_module.app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
