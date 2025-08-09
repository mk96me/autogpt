import importlib
from fastapi import FastAPI

MODULE = "autogpt_platform.backend.backend.app"

def _load_app():
    mod = importlib.import_module(MODULE)

    # Try common attribute names first
    for name in ("app", "api", "application"):
        obj = getattr(mod, name, None)
        if isinstance(obj, FastAPI):
            return obj

    # Try common factory function names
    for name in ("create_app", "get_app", "make_app", "build_app", "init_app"):
        fn = getattr(mod, name, None)
        if callable(fn):
            obj = fn()
            if isinstance(obj, FastAPI):
                return obj

    # Fallback minimal app so service stays live (you can add routes later)
    fallback = FastAPI()

    @fallback.get("/")
    def _root():
        return {"status": "ok", "note": f"Could not find FastAPI app in {MODULE}. Using fallback."}

    return fallback

app = _load_app()
