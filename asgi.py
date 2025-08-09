import pkgutil, importlib, inspect
from fastapi import FastAPI

PACKAGE = "autogpt_platform.backend.backend"

def find_app():
    # 1) Try common direct module first (app.py)
    try:
        mod = importlib.import_module(f"{PACKAGE}.app")
        for name in ("app", "api", "application"):
            obj = getattr(mod, name, None)
            if isinstance(obj, FastAPI):
                print(f"[asgi] Found FastAPI instance: {PACKAGE}.app:{name}", flush=True)
                return obj
        for name in ("create_app", "get_app", "make_app", "build_app", "init_app"):
            fn = getattr(mod, name, None)
            if callable(fn):
                obj = fn()
                if isinstance(obj, FastAPI):
                    print(f"[asgi] Built FastAPI via {PACKAGE}.app:{name}()", flush=True)
                    return obj
    except Exception as e:
        print(f"[asgi] Failed importing {PACKAGE}.app: {e}", flush=True)

    # 2) Scan the whole package for any FastAPI instance or factory
    pkg = importlib.import_module(PACKAGE)
    for m in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
        name = m.name
        try:
            module = importlib.import_module(name)

            # any FastAPI instance as a module attribute?
            for attr_name, attr_val in inspect.getmembers(module):
                if isinstance(attr_val, FastAPI):
                    print(f"[asgi] Found FastAPI at {name}:{attr_name}", flush=True)
                    return attr_val

            # any factory function returning FastAPI?
            for fn_name, fn in inspect.getmembers(module, inspect.isfunction):
                if fn_name in {"create_app", "get_app", "make_app", "build_app", "init_app"}:
                    try:
                        built = fn()
                        if isinstance(built, FastAPI):
                            print(f"[asgi] Built FastAPI via {name}:{fn_name}()", flush=True)
                            return built
                    except Exception as e:
                        print(f"[asgi] Factory {name}:{fn_name}() failed: {e}", flush=True)
        except Exception as e:
            print(f"[asgi] Skipping {name}: {e}", flush=True)

    # 3) Fallback app so service stays up
    print("[asgi] No FastAPI app found; using fallback.", flush=True)
    app = FastAPI()

    @app.get("/")
    def root():
        return {"status": "ok", "note": f"No FastAPI app found under {PACKAGE}. Using fallback."}

    return app

app = find_app()

