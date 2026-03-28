import bpy

def unit():
    return {
        'KILOMETERS': "km",
        'METERS': 'm',
        'CENTIMETERS': 'cm',
        'MILLIMETERS': 'mm',
        'MICROMETERS': '?',
        'FEET': 'ft',
        'INCHES': 'in',
        'MILES': 'mi',
        'ADAPTIVE': ""
    }[bpy.context.scene.unit_settings.length_unit]