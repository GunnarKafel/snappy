"""Holds the UI that exists in the viewport"""
import bpy
from . import snapping, pivot, utility

def draw_grid_ui(layout, context):
    formatted_scale = f"{context.space_data.overlay.grid_scale:.3f}"
    formatted_scale = formatted_scale.rstrip('0').rstrip('.')
    grid_text = f"{formatted_scale}{utility.unit()}"

    row = layout.row(align=True)
    row.ui_units_x = 5
    row.menu(menu=snapping.VIEW3D_MT_grid_presets_menu.bl_idname, text=grid_text, translate=False, icon='NONE')

    decrement = row.operator(operator=snapping.VIEW3D_OT_scale_grid.bl_idname, text="", icon='REMOVE')
    decrement.scale = 0.5

    increment = row.operator(operator=snapping.VIEW3D_OT_scale_grid.bl_idname, text="", icon='ADD')
    increment.scale = 2


def draw_after_VIEW3D_HT_header(self, context):
    """Rendered on the right side of the View3D header"""
    layout: bpy.types.UILayout = self.layout

    layout = layout.box()
    draw_grid_ui(layout, context)

def draw_before_VIEW3D_HT_header(self, context):
    """Rendered on the left side of the View3D header"""
    pass

def enable():
    bpy.types.VIEW3D_HT_header.append(draw_after_VIEW3D_HT_header)
    bpy.types.VIEW3D_HT_header.prepend(draw_before_VIEW3D_HT_header)

def disable():
    bpy.types.VIEW3D_HT_header.remove(draw_after_VIEW3D_HT_header)
    bpy.types.VIEW3D_HT_header.remove(draw_before_VIEW3D_HT_header)