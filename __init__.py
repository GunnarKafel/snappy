import importlib
import pkgutil
from pathlib import Path

def _load_modules():
    package_root = Path(__file__).resolve().parent
    modules_path = package_root / "modules"

    discovered = []
    for module_info in pkgutil.iter_modules([str(modules_path)]):
        if module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f".modules.{module_info.name}", __package__)
        discovered.append(module)

    return discovered


modules = _load_modules()

def hot_reload():
    for module in modules:
        importlib.reload(module)

def register():
    hot_reload()
    for module in modules:
        if hasattr(module, "enable"):
            module.enable()

def unregister():
    for module in modules:
        if hasattr(module, "disable"):
            module.disable()