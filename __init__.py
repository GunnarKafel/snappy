# Make sure to register all modules that way they refresh 
from . import (dimensions, snapping, draw, utility)
modules = [dimensions, snapping, draw, utility]

def hot_reload():
    # Refresh submodules during development
    import importlib
    for module in modules:
        print("Reloading module", module)
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