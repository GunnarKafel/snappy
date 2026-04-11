import bpy
import mathutils as math

#Nudge relative to the camera with arrow keys
class VIEW3D_OT_nudge_selected(bpy.types.Operator):
    bl_idname = "view3d.nudge_selected"
    bl_label = "Nudge Selected"
    nudge_options: bpy.props.EnumProperty(
        name="Direction", 
        items=[
            ("LEFT", "Left", "Nudge to camera left"),
            ("RIGHT", "Right", "Nudge to camera right"),
            ("UP", "Up", "Nudge to camera up"),
            ("DOWN", "Down", "Nudge to camera down"),
        ], 
        default="LEFT")
    nudge_extrude: bpy.props.BoolProperty("Extrude")
        
    def execute(self, context):
        #Get our Forward, Up, Right axes with respect to the view camera
        view_matrix = get_view_axes()

        #Pick the axis that best represents our intent
        camera_nudge_direction = math.Vector((0,0,0))
        if (self.nudge_options == "LEFT"):
            camera_nudge_direction = -view_matrix[2]
        elif (self.nudge_options == "RIGHT"):
            camera_nudge_direction = view_matrix[2]
        elif (self.nudge_options == "UP"):
            camera_nudge_direction = view_matrix[1]
        elif (self.nudge_options == "DOWN"):
            camera_nudge_direction = -view_matrix[1]

        #Normalize as a product of my paranoia
        camera_nudge_direction.normalize()

        #Test for all the major axes, potentially naive but also works!
        test_directions = []
        test_directions.append(math.Vector((1, 0, 0)))
        test_directions.append(math.Vector((-1, 0, 0)))
        test_directions.append(math.Vector((0, 1, 0)))
        test_directions.append(math.Vector((0, -1, 0)))
        test_directions.append(math.Vector((0, 0, 1)))
        test_directions.append(math.Vector((0, 0, -1)))

        #Start with the lowest possible dot product result and iterate through them until we find the cloest match
        best_direction = (test_directions[0], -1.0)
        for direction in test_directions:
            dot_result = camera_nudge_direction.dot(direction)

            if dot_result >= best_direction[1]:
                best_direction = (direction, dot_result)

        #Save our offset for later
        translation = math.Vector((best_direction[0] * bpy.context.space_data.overlay.grid_scale))

        if bpy.context.mode == "OBJECT":
            if self.nudge_extrude:
                bpy.ops.object.duplicate_move(TRANSFORM_OT_translate={"value": translation})
                return {'FINISHED'}
            else:
                bpy.ops.transform.translate(value=translation)
            return {'FINISHED'}
        
        if bpy.context.mode == "EDIT_MESH":
            if self.nudge_extrude:
                bpy.ops.mesh.extrude_context_move(TRANSFORM_OT_translate={"value": translation})
                return {'FINISHED'}
            else:
                bpy.ops.transform.translate(value=translation,
                    use_proportional_edit = bpy.context.tool_settings.use_proportional_edit,
                    proportional_edit_falloff = bpy.context.tool_settings.proportional_edit_falloff,
                    proportional_size = bpy.context.tool_settings.proportional_size,
                )
            return {'FINISHED'}
        
        return {'CANCELLED'}

_addon_keymaps = []
def define_nudge_keymap(km, key, option):
        kmi = km.keymap_items.new(VIEW3D_OT_nudge_selected.bl_idname, type=key, value="PRESS")
        kmi.properties.nudge_options = option
        kmi.properties.nudge_extrude = False
        _addon_keymaps.append((km, kmi))

        kmi = km.keymap_items.new(VIEW3D_OT_nudge_selected.bl_idname, type=key, value="PRESS")
        kmi.properties.nudge_options = option
        kmi.properties.nudge_extrude = True
        kmi.shift = True
        _addon_keymaps.append((km, kmi))

def enable():
    bpy.utils.register_class(VIEW3D_OT_nudge_selected)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name='Object Mode', region_type='WINDOW')

        define_nudge_keymap(km, "LEFT_ARROW", "LEFT")
        define_nudge_keymap(km, "RIGHT_ARROW", "RIGHT")
        define_nudge_keymap(km, "UP_ARROW", "UP")
        define_nudge_keymap(km, "DOWN_ARROW", "DOWN")

        km = kc.keymaps.new(name='Mesh', region_type='WINDOW')

        define_nudge_keymap(km, "LEFT_ARROW", "LEFT")
        define_nudge_keymap(km, "RIGHT_ARROW", "RIGHT")
        define_nudge_keymap(km, "UP_ARROW", "UP")
        define_nudge_keymap(km, "DOWN_ARROW", "DOWN")




def disable():
    for km, kmi in _addon_keymaps:
        km.keymap_items.remove(kmi)

    _addon_keymaps.clear()
    bpy.utils.unregister_class(VIEW3D_OT_nudge_selected)

    
def get_view_axes():
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            region = space.region_3d

            #Use the inverse view matrix to get our viewport's axes
            matrix = region.view_matrix.inverted()
            forward = math.Vector((-matrix.col[2].x, -matrix.col[2].y, -matrix.col[2].z))
            up = math.Vector((matrix.col[1].x, matrix.col[1].y, matrix.col[1].z))
            right = math.Vector((matrix.col[0].x, matrix.col[0].y, matrix.col[0].z))
            return (forward, up, right)

    return None    