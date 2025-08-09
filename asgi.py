import importlib, pkgutil, inspect
from fastapi import FastAPI

PACKAGE = "autogpt_platform.backend.backend"

def try_module(mod_name: str):
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        print(f"[asgi] import failed: {mod_name} ({e})", flush=True)
        return None

    for candidate in ("app", "api", "application"):
        obj = getattr(mod, candidate, None)
        if isinstance(obj, FastAPI):
            print(f"[asgi] Found FastAPI instance: {mod_name}:{candidate}", flush=True)
            return obj

    for factory in ("create_app", "get_app", "make_app", "build_app", "init_app"):
        fn = getattr(mod, factory, None)
        if callable(fn):
            try:
                obj = fn()
                if isinstance(obj, FastAPI):
                    print(f"[asgi] Built FastAPI via {mod_name}:{factory}()", flush=True)
                    return obj
            except Exception as e:
                print(f"[asgi] Factory failed: {mod_name}:{factory}() -> {e}", flush=True)
    return None

def find_app():
    # Try most likely modules first
    for suffix in ("app", "ws", "api", "main", "server"):
        app = try_module(f"{PACKAGE}.{suffix}")
        if app:
            return app

    # Scan entire package as fallback
    pkg = importlib.import_module(PACKAGE)
    for m in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
        app = try_module(m.name)
        if app:
            return app

    # Last-resort fallback
    print("[asgi] No FastAPI app found; using fallback.", flush=True)
    app = FastAPI()

    @app.get("/")
    def root():
        return {"status": "ok", "note": f"No FastAPI app found under {PACKAGE}. Using fallback."}

    return app

app = find_app()


