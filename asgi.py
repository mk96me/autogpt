import importlib
from fastapi import FastAPI

MODULE = "autogpt_platform.backend.backend.app"

def _load():
    mod = importlib.import_module(MODULE)

    # common attribute names
    for name in ("app", "api", "application"):
        obj = getattr(mod, name, None)
        if isinstance(obj, FastAPI):
            return obj

    # common factory functions
    for name in ("create_app", "get_app", "make_app", "build_app", "init_app"):
        fn = getattr(mod, name, None)
        if callable(fn):
            app = fn()
            if isinstance(app, FastAPI):
                return app

    # fallback so service still comes up
    app = FastAPI()

    @app.get("/")
    def root():
        return {"status": "ok", "note": f"No FastAPI app found in {MODULE}, using fallback."}

    return app

app = _load()
