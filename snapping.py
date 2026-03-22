import bpy
from . import utility

class ScaleGrid(bpy.types.Operator):
    """Scale the grid by an amount"""
    
    bl_idname = "view3d.scale_grid"
    bl_label = "Scale grid"

    scale: bpy.props.FloatProperty(name="Scale", default=0.5, min=0, max=2)

    def execute(self, context):
        context.space_data.overlay.grid_scale *= self.scale
        return {'FINISHED'}

class GridPresetsMenu(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_grid_presets"
    bl_label = "Presets"

    snap_values = [0.25, 0.5, 1, 2, 4, 8, 16, 32]

    def draw(self, context):
        layout = self.layout

        for value in self.snap_values:
            op = layout.operator("wm.context_set_float", text=str(value) + utility.unit())
            op.data_path = "space_data.overlay.grid_scale"
            op.value = value

def draw_header(self, context):
    layout: bpy.types.UILayout = self.layout
    layout = layout.box()

    row = layout.row(align=True)
    pivot = row.operator(operator=ScaleGrid.bl_idname, text="", icon='OBJECT_ORIGIN')

    formatted_scale = f"{context.space_data.overlay.grid_scale:.3f}"
    formatted_scale = formatted_scale.rstrip('0').rstrip('.')
    grid_text = f"{formatted_scale}{utility.unit()}"

    row.ui_units_x = 6
    row.menu(menu=GridPresetsMenu.bl_idname, text=grid_text, translate=False, icon='NONE')

    decrement = row.operator(operator=ScaleGrid.bl_idname, text="", icon='REMOVE')
    decrement.scale = 0.5

    increment = row.operator(operator=ScaleGrid.bl_idname, text="", icon='ADD')
    increment.scale = 2

_addon_keymaps = []

def add_scale_keymap(keymaps, key, scale):
    kmi = keymaps.keymap_items.new(ScaleGrid.bl_idname, key, 'PRESS', shift=False)
    kmi.properties.scale = scale
    return kmi


def enable():
    bpy.utils.register_class(GridPresetsMenu)
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
    # bpy.types.VIEW3D_HT_header.remove(draw_header)
    bpy.types.VIEW3D_HT_tool_header.remove(draw_header)

    bpy.utils.unregister_class(GridPresetsMenu)
    bpy.utils.unregister_class(ScaleGrid)