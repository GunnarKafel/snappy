"""Holds the UI that exists in the viewport"""
import bpy
from . import snapping, pivot, utility

def draw_VIEW3D_HT_header(self, context):
    layout: bpy.types.UILayout = self.layout
    layout = layout.box()

    row = layout.row(align=True)
    # row.popover(panel=pivot.OriginSelectPanel.bl_idname, text="", icon="OBJECT_ORIGIN")

    formatted_scale = f"{context.space_data.overlay.grid_scale:.3f}"
    formatted_scale = formatted_scale.rstrip('0').rstrip('.')
    grid_text = f"{formatted_scale}{utility.unit()}"

    row.ui_units_x = 5
    row.menu(menu=snapping.GridPresetsMenu.bl_idname, text=grid_text, translate=False, icon='NONE')

    decrement = row.operator(operator=snapping.ScaleGrid.bl_idname, text="", icon='REMOVE')
    decrement.scale = 0.5

    increment = row.operator(operator=snapping.ScaleGrid.bl_idname, text="", icon='ADD')
    increment.scale = 2

def enable():
    bpy.types.VIEW3D_HT_header.append(draw_VIEW3D_HT_header)

def disable():
    bpy.types.VIEW3D_HT_header.remove(draw_VIEW3D_HT_header)