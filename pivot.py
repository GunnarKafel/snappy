import bpy

def draw_header(self, context):
    layout: bpy.types.UILayout = self.layout
    layout.popover("VIEW3D_PT_snapping", text="Origin")

def enable():
    bpy.types.VIEW3D_HT_tool_header.append(draw_header)

def disable():
    bpy.types.VIEW3D_HT_tool_header.remove(draw_header)