import bpy
import math
import time
from mathutils import Vector, Quaternion

class VIEW3D_OT_hold_fly(bpy.types.Operator):
    bl_idname = "view3d.hold_fly"
    bl_label = "Hold Fly Navigation"
    bl_options = {'BLOCKING', 'GRAB_CURSOR'}

    _BASE_SPEED        = 18
    _MOUSE_SENSITIVITY = 0.0015
    _SPEED_SCALE       = 1.2
    _BOOST_MULTIPLIER  = 3.0
    _MAX_PITCH         = math.radians(89)
    _SMOOTHING         = 20.0  # higher = snappier, lower = floatier

    # Pixels the mouse must travel before a click is treated as fly, not a context-menu click.
    _DRAG_THRESHOLD = 3

    def _boost_active(self):
        return 'LEFT_SHIFT' in self._keys or 'RIGHT_SHIFT' in self._keys

    def _update_header(self):
        if self._area is None:
            return

        effective = self._speed * (self._BOOST_MULTIPLIER if self._boost_active() else 1.0)
        self._area.header_text_set(
            f"Fly Speed: {self._speed:.2f}"
        )

    def modal(self, context, event):
        rv3d = context.region_data

        # --- Exit on RMB release ---
        if event.type == 'RIGHTMOUSE' and event.value == 'RELEASE':
            self.finish(context)
            if self._total_drag < self._DRAG_THRESHOLD:
                # Didn't really drag — open the context menu instead.
                bpy.ops.wm.call_menu(name='VIEW3D_MT_object_context_menu')
            return {'FINISHED'}

        # --- Track key states ---
        if event.value == 'PRESS':
            self._keys.add(event.type)
        elif event.value == 'RELEASE':
            self._keys.discard(event.type)

        # --- Scroll to adjust fly speed ---
        if event.type == 'WHEELUPMOUSE':
            self._speed *= self._SPEED_SCALE
        elif event.type == 'WHEELDOWNMOUSE':
            self._speed /= self._SPEED_SCALE

        # --- Mouse look — accumulate delta, apply on TIMER ---
        if event.type == 'MOUSEMOVE':
            if self._mouse_prev is not None:
                dx = event.mouse_region_x - self._mouse_prev[0]
                dy = event.mouse_region_y - self._mouse_prev[1]
                self._mouse_delta[0] += dx
                self._mouse_delta[1] += dy
                self._total_drag += abs(dx) + abs(dy)

            self._mouse_prev = (event.mouse_region_x, event.mouse_region_y)

        # --- Apply rotation + movement together so redraws are never partial ---
        if event.type == 'TIMER':
            now = time.perf_counter()
            dt = now - self._last_time
            self._last_time = now

            if self._mouse_delta[0] or self._mouse_delta[1]:
                self.rotate_view(rv3d, self._mouse_delta[0], self._mouse_delta[1])
                self._mouse_delta = [0, 0]
            self.move_view(rv3d, dt)

        self._update_header()
        self._area.tag_redraw()
        return {'RUNNING_MODAL'}

    def rotate_view(self, rv3d: bpy.types.RegionView3D, dx, dy):
        # Compute the camera eye position before rotation — we rotate around
        # the eye, not the pivot, so view_distance never needs to change.
        eye = rv3d.view_location + rv3d.view_rotation @ Vector((0, 0, rv3d.view_distance))

        rot = rv3d.view_rotation.copy()

        # Yaw around world Z
        yaw = Quaternion(Vector((0, 0, 1)), -dx * self._MOUSE_SENSITIVITY)
        rot = yaw @ rot

        # Pitch around the camera's current local right axis.
        # Must use rot @ (1,0,0) — not world X — so pitch stays correct after yaw.
        # Clamp to prevent flipping over.
        forward = rot @ Vector((0, 0, -1))
        current_pitch = math.asin(max(-1.0, min(1.0, forward.z)))
        pitch_delta = max(
            -self._MAX_PITCH - current_pitch,
            min(self._MAX_PITCH - current_pitch, dy * self._MOUSE_SENSITIVITY),
        )
        if abs(pitch_delta) > 1e-7:
            right = rot @ Vector((1, 0, 0))
            pitch = Quaternion(right, pitch_delta)
            rot = pitch @ rot

        rv3d.view_rotation = rot
        # Reposition the pivot so the eye stays in place.
        rv3d.view_location = eye - rot @ Vector((0, 0, rv3d.view_distance))

    def move_view(self, rv3d: bpy.types.RegionView3D, dt: float):
        forward = rv3d.view_rotation @ Vector((0, 0, -1))
        right   = rv3d.view_rotation @ Vector((1, 0, 0))
        up      = Vector((0, 0, 1))

        target = Vector((0, 0, 0))

        if 'W' in self._keys:
            target += forward
        if 'S' in self._keys:
            target -= forward
        if 'A' in self._keys:
            target -= right
        if 'D' in self._keys:
            target += right
        if 'E' in self._keys:
            target += up
        if 'Q' in self._keys:
            target -= up

        if target.length > 0:
            target.normalize()
            if self._boost_active():
                target *= self._BOOST_MULTIPLIER
            target *= self._speed

        # Exponential smoothing: velocity eases toward the target each tick.
        t = min(1.0, self._SMOOTHING * dt)
        self._velocity = self._velocity.lerp(target, t)

        if self._velocity.length > 1e-6:
            rv3d.view_location += self._velocity * dt

    def invoke(self, context, event):
        # Only allow inside 3D viewport
        if context.area is None or context.area.type != 'VIEW_3D':
            return {'PASS_THROUGH'}

        if context.region_data is None:
            return {'CANCELLED'}

        # Initialize per-invocation state (never use class-level mutable defaults)
        self._keys = set()
        self._timer = None
        self._speed = self._BASE_SPEED
        self._mouse_prev = (event.mouse_region_x, event.mouse_region_y)
        self._mouse_delta = [0, 0]
        self._total_drag = 0
        self._velocity = Vector((0, 0, 0))
        self._last_time = time.perf_counter()
        self._area = context.area  # cache: context.area is None during TIMER events

        # Collapse the orbit pivot onto the camera eye so that movement
        # translates the eye directly. view_distance is left unchanged so
        # Blender's zoom remains fully functional after exiting.
        rv3d = context.region_data

        # Capture cursor (prevents UI interaction)
        context.window.cursor_modal_set('NONE')

        wm = context.window_manager
        self._timer = wm.event_timer_add(0, window=context.window)
        wm.modal_handler_add(self)
        self._update_header()

        return {'RUNNING_MODAL'}

    def finish(self, context):
        wm = context.window_manager

        if self._timer:
            wm.event_timer_remove(self._timer)
            self._timer = None

        if self._area is not None:
            self._area.header_text_set(None)

        context.window.cursor_modal_restore()

addon_keymaps = []

def enable():
    bpy.utils.register_class(VIEW3D_OT_hold_fly)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon

    if kc:
        km = kc.keymaps.new(name="Object Mode", space_type='EMPTY')

        kmi = km.keymap_items.new(
            VIEW3D_OT_hold_fly.bl_idname,
            type='RIGHTMOUSE',
            value='PRESS'
        )

        addon_keymaps.append((km, kmi))

def disable():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(VIEW3D_OT_hold_fly)