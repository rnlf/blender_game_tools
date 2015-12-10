import bpy
from mathutils import Vector
import math

def make_outname(suffix):
    f = bpy.data.scenes["Scene"].render.filepath
    x = f.rfind('.')
    return f[0:x] + suffix

def worldToGameLoc(v):
    # Render resolution, required for orthographic image size
    rx = bpy.data.scenes[0].render.resolution_x
    ry = bpy.data.scenes[0].render.resolution_y
            
    # Find intersection between lower bound of ortho camera and zero-plane
    # It will be the nearest visible y coord in the depth map
    sy = 0
    sx = 0
    os = bpy.data.scenes[0].camera.data.ortho_scale
    if rx > ry:
        sy = ry / rx * os
        sx = os            
    else:
        sy = os
        sx = rx / ry * os  
         
    rp = bpy.data.scenes[0].render.resolution_percentage
    w = v + Vector([sx/2,sy/(2*math.cos(bpy.data.scenes[0].camera.rotation_euler.x)),0])
    w.x *= rx * rp / (100.0 * os)
    w.y *= ry * rp / (100.0 * os)
    w.z *= ry * rp / (100.0 * os)
    
    w.x = round(w.x, 2)
    w.y = round(w.y, 2)
    w.z = round(w.z, 2)
    
    return w
    

class MakeGameFiles(bpy.types.Operator):
    bl_idname = "scene.export_game_objects"
    bl_label = "Export Game Objects"

    def invoke(self, context, event):

        layernum = bpy.data.scenes[0].namedlayers.layers.find("Objects")
        s = bpy.data.scenes[0].camera.data.ortho_scale
        with open(make_outname("_objects.lua"), "w") as f:
            f.write("return {\n")
            for o in filter(lambda x: x.layers[layernum], bpy.data.objects):
                f.write("  [\"" + o.name + "\"] = {\n")
                f.write("    pos = { " + (", ".join(map(str, worldToGameLoc(o.location)))) + " },\n")
                for p in o.game.properties:
                    v = ""
                    if p.type == "STRING":
                        v = "\"" + p.value + "\""
                    elif p.type in ["FLOAT", "INT", "TIMER"]:
                        v = str(p.value)
                    elif p.type == "BOOL":
                        v = "true" if p.value else "false"
                    pass
                    f.write("    " + p.name + " = " + v + ",\n")
                f.write("  },\n")
            f.write("}")

        return {"FINISHED"}


class ExportObjectsPanel(bpy.types.Panel):
    """Exports Game Objects"""
    bl_label = "Export Game Objects"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
        
        row.operator("scene.export_game_objects")


def register():
    bpy.utils.register_class(MakeGameFiles)
    bpy.utils.register_class(ExportObjectsPanel)


def unregister():
    bpy.utils.unregister_class(ExportObjectsPanel)
    bpy.utils.unregister_class(MakeGameFiles)    


if __name__ == "__main__":
    register()
