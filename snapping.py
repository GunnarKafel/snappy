import bpy
from . import utility

class ScaleGrid(bpy.types.Operator):
    """Scale the grid by an amount"""
    
    bl_idname = "view3d.scale_grid"
    bl_label = "Scale grid"

    scale: bpy.props.FloatProperty(name="Scale", default=0.5, min=0, max=4)

    def execute(self, context):
        context.space_data.overlay.grid_scale *= self.scale
        return {'FINISHED'}

def draw_header(self, context):
    if not context.scene.tool_settings.use_snap:
        return
    
    layout: bpy.types.UILayout = self.layout
    layout = layout.box();
    # layout.emboss = "PULLDOWN_MENU"

    row = layout.row(align=True)
    row.scale_x = 0

    formatted_scale = f"{context.space_data.overlay.grid_scale:.3f}"
    formatted_scale = formatted_scale.rstrip('0').rstrip('.')
    row.label(text=f"{formatted_scale}{utility.unit()}".rjust(10), translate=False)

    decrement = row.operator(operator=ScaleGrid.bl_idname, text="", icon='REMOVE')
    decrement.scale = 0.5;

    increment = row.operator(operator=ScaleGrid.bl_idname, text="", icon='ADD')
    increment.scale = 2;

_addon_keymaps = []

def add_scale_keymap(keymaps, key, scale):
    kmi = keymaps.keymap_items.new(ScaleGrid.bl_idname, key, 'PRESS', shift=False)
    kmi.properties.scale = scale
    return kmi


def enable():
    bpy.utils.register_class(ScaleGrid)
    bpy.types.VIEW3D_HT_header.append(draw_header)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    # Only way to make this work is to have two separate keymaps?
    if kc:
        km = kc.keymaps.new(name='Object Mode', region_type='WINDOW')
        _addon_keymaps.append((km, add_scale_keymap(km, 'RIGHT_BRACKET', 2)))
        _addon_keymaps.append((km, add_scale_keymap(km, 'LEFT_BRACKET', 0.5)))

        km = kc.keymaps.new(name='Mesh', region_type='WINDOW')
        _addon_keymaps.append((km, add_scale_keymap(km, 'RIGHT_BRACKET', 2)))
        _addon_keymaps.append((km, add_scale_keymap(km, 'LEFT_BRACKET', 0.5)))

def disable():
    for km, kmi in _addon_keymaps:
        km.keymap_items.remove(kmi)

    _addon_keymaps.clear()
    bpy.types.VIEW3D_HT_header.remove(draw_header)
    bpy.utils.unregister_class(ScaleGrid)