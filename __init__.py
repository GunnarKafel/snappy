# Make sure to register all modules that way they refresh 
from . import (fly, dimensions, snapping, draw, utility, nudging, pivot, view3d_ui)
modules = [fly, dimensions, snapping, draw, utility, nudging, pivot, view3d_ui]

def hot_reload():
    import importlib
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