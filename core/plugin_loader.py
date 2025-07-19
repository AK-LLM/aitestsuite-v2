import importlib.util
import os

PLUGIN_FOLDERS = ["core", "plugins"]

def discover_plugins():
    registry = []
    for folder in PLUGIN_FOLDERS:
        if not os.path.isdir(folder):
            print(f"[Plugin Loader] Folder missing: {folder}")
            continue
        for fname in os.listdir(folder):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            path = os.path.join(folder, fname)
            module_name = f"{folder}.{fname[:-3]}"
            spec = importlib.util.spec_from_file_location(module_name, path)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                if hasattr(mod, "run") and hasattr(mod, "METADATA"):
                    registry.append({
                        "module": mod,
                        "name": mod.METADATA.get("name", fname),
                        "category": mod.METADATA.get("category", "uncategorized"),
                        "description": mod.METADATA.get("description", ""),
                        "risk": mod.METADATA.get("risk", ""),
                        "references": mod.METADATA.get("references", []),
                        "file": fname
                    })
                else:
                    print(f"[Plugin Loader] Skipped {fname} (missing METADATA or run)")
            except Exception as e:
                print(f"[Plugin Loader] Error loading plugin {fname}: {e}")
    if not registry:
        print("[Plugin Loader] No valid plugins found!")
    return registry
