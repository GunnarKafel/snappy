import bpy

class VIEW3D_PT_origin_select(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_origin_select"
    bl_label = "Select Origin"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {"INSTANCED"}

    def draw(self, context):
        self.layout.label(text="Origin Select")

def enable():
    bpy.utils.register_class(VIEW3D_PT_origin_select)

def disable():
    bpy.utils.unregister_class(VIEW3D_PT_origin_select)