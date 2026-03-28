import bpy
from . import utility

class SetSnapMode(bpy.types.Operator):
    """Set active snapping mode"""
    bl_idname = "view3d.set_snap_mode"
    bl_label = "Set Snap Mode"

    mode: bpy.props.EnumProperty(
        name="Snap Mode",
        items=(
            ('VERTEX', "Vertex", "Snap to vertices"),
            ('GRID', "Grid", "Absolute grid snapping"),
            ('INCREMENT', "Increment", "Incremental snapping"),
            ('FACE', "Face", "Snap to faces"),
            ('EDGE', "Edge", "Snap to edges"),
            ('VOLUME', "Volume", "Snap to volume"),
        ),
        default='GRID',
    )

    def execute(self, context):
        tool_settings = context.scene.tool_settings
        tool_settings.snap_elements = {self.mode}

        self.report({'INFO'}, f"{self.mode.title()}")
        return {'FINISHED'}

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

    snap_values = [0.125, 0.25, 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256]

    def draw(self, context):
        layout = self.layout

        for value in self.snap_values:
            op = layout.operator("wm.context_set_float", text=str(value) + utility.unit())
            op.data_path = "space_data.overlay.grid_scale"
            op.value = value

class VIEW3D_MT_snap_target_pie_menu(bpy.types.Menu):
    bl_label = "Snap Target Pie Menu"
    bl_idname = "VIEW3D_mt_snap_target_pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        pie.operator(SetSnapMode.bl_idname, text="Grid", icon='SNAP_GRID').mode = 'GRID'
        pie.operator(SetSnapMode.bl_idname, text="Face", icon='SNAP_FACE').mode = 'FACE'
        pie.operator(SetSnapMode.bl_idname, text="Vertex", icon='SNAP_VERTEX').mode = 'VERTEX'
        pie.operator(SetSnapMode.bl_idname, text="Edge", icon='SNAP_EDGE').mode = 'EDGE'
        pie.operator(SetSnapMode.bl_idname, text="Increment", icon='SNAP_INCREMENT').mode = 'INCREMENT'
        pie.operator(SetSnapMode.bl_idname, text="Volume", icon='SNAP_VOLUME').mode = 'VOLUME'

class VIEW3D_OT_snap_target_pie(bpy.types.Operator):
    bl_idname = "view3d.snap_target_pie"
    bl_label = "Call Snap Target Pie Menu"

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name=VIEW3D_MT_snap_target_pie_menu.bl_idname)
        return {'FINISHED'}

_addon_keymaps = []

def add_scale_keymap(keymaps, key, scale):
    kmi = keymaps.keymap_items.new(ScaleGrid.bl_idname, key, 'PRESS', shift=False)
    kmi.properties.scale = scale
    return kmi

classes = (
    GridPresetsMenu,
    ScaleGrid,
    SetSnapMode,
    VIEW3D_MT_snap_target_pie_menu,
    VIEW3D_OT_snap_target_pie
)

def enable():
    for cls in classes:
        bpy.utils.register_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    # Only way to make this work is to have two separate keymaps?
    if kc:
        km = kc.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(VIEW3D_OT_snap_target_pie.bl_idname, type='Q', value='PRESS', shift=True)
        _addon_keymaps.append((km, kmi))
        
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

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
