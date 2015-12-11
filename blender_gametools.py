import bpy
import bmesh
from math import cos, sin, tan
from mathutils import Vector

def make_outname(suffix, removeEnding=False):
    f = bpy.data.scenes["Scene"].render.filepath
    x = f.rfind('.')
    return f[0:x] + suffix + (f[x:] if not removeEnding else "")


def set_image_settings(mode):
    bpy.data.scenes["Scene"].render.image_settings.file_format = "PNG"
    bpy.data.scenes["Scene"].render.image_settings.color_depth = '8'
    bpy.data.scenes["Scene"].render.image_settings.color_mode = mode


def worldToGameLoc(v):
    print(v)
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
    c = bpy.data.scenes[0].camera.rotation_euler.x
    print(c)
    w = v + Vector([sx/2,sy/(2*cos(c)),0])


    
 
    w.x *= rx * rp / (100.0 *  sx) # os * (rx / ry))
    w.y *= ry * rp / (100.0 *  sy) # os)
    w.z *= rx * rp / (100.0 *  sx)
    
    w.x = round(w.x, 2)
    w.y = round(w.y, 2)
    w.z = round(w.z, 2)
    
    return w
    
class MakeTriggerFile(bpy.types.Operator):
    bl_idname = "scene.export_triggers"
    bl_label = "Export Triggers"

    def invoke(self, context, event):  
        layernum = bpy.data.scenes[0].namedlayers.layers.find("Triggers")          
        with open(make_outname("_triggers.lua", True), "w") as f:
            f.write("return {\n")
            for o in filter(lambda x: x.layers[layernum], bpy.data.objects):
                s = o.scale * o.empty_draw_size
                
                f.write("  [\"" + o.name + "\"] = {\n")
                f.write("    min = {" + ", ".join(map(str, worldToGameLoc(o.location - s / 2))) + "},\n")
                f.write("    max = {" + ", ".join(map(str, worldToGameLoc(o.location + s / 2))) + "}\n")                
                f.write("  }\n")
            f.write("}\n")
        return {"FINISHED"}

class MakeObjectFile(bpy.types.Operator):
    bl_idname = "scene.export_game_objects"
    bl_label = "Export Game Objects"

    def invoke(self, context, event):

        layernum = bpy.data.scenes[0].namedlayers.layers.find("Objects")

        with open(make_outname("_objects.lua", True), "w") as f:
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

class MakeCollisionFile(bpy.types.Operator):
    bl_idname = "scene.make_game_collision_file"
    bl_label = "Make Game Collision Mesh Files"

    def invoke(self, context, event):
        obj = bpy.data.objects["Collision"]
        mat = obj.matrix_world
        #collision = bpy.data.meshes["Collision"]
        collision = obj.data
        cc = bmesh.new()
        cc.from_mesh(collision)

        bmesh.ops.triangulate(cc, faces=cc.faces)

        

        with open(make_outname("_collision.lua", True), "w") as of:
                

            of.write("return {\n")
            for f in cc.faces:
                of.write("  { verts = {\n")
                vs = sorted(f.verts, key=lambda x: x.index)
                for v in vs:
                    of.write("      {" + ", ".join(map(str, worldToGameLoc(mat * v.co))) + "},\n")
            
                of.write("    },\n    neighbors = { ")
                
                for i in range(3):
                    for e in f.edges:
                        if vs[i] in e.verts and vs[(i-1)%3] in e.verts:
                            if len(e.link_faces) == 2:
                                if e.link_faces[0] == f:
                                    of.write(str(e.link_faces[1].index + 1) + ", ")
                                else:
                                    of.write(str(e.link_faces[0].index + 1) + ", ")
                            else:
                                of.write("-1, ")
                                
                
                of.write("}\n  }, \n")
                
            of.write("}\n")
            cc.free()

        return {"FINISHED"}


class MakeGameFiles(bpy.types.Operator):
    bl_idname = "scene.make_game_files"
    bl_label = "Make Game Files"

    def invoke(self, context, event):
        bpy.ops.scene.make_depth_map('INVOKE_DEFAULT')

        set_image_settings('RGB')
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(make_outname('_color'))
        
        bpy.ops.scene.make_game_collision_file('INVOKE_DEFAULT')
        bpy.ops.scene.export_game_objects('INVOKE_DEFAULT')
        bpy.ops.scene.export_triggers('INVOKE_DEFAULT')

        return {"FINISHED"}

class MakeDepthMap(bpy.types.Operator):
    bl_idname = "scene.make_depth_map"
    bl_label = "Make Depth Map"

    def invoke(self, context, event):
        engine = bpy.data.scenes["Scene"].render.engine
        use_aa = bpy.data.scenes["Scene"].render.use_antialiasing
        colspace = bpy.data.scenes[0].display_settings.display_device
        bpy.data.scenes[0].display_settings.display_device = "None"
        bpy.data.scenes["Scene"].render.use_antialiasing = False
        
        bpy.data.scenes["Scene"].render.engine = "BLENDER_RENDER"
        set_image_settings('RGB')
        
        use_compositor = bpy.data.scenes["Scene"].use_nodes
        bpy.data.scenes["Scene"].use_nodes = False
        
        # Render resolution, required for orthographic image size
        rx = bpy.data.scenes[0].render.resolution_x
        ry = bpy.data.scenes[0].render.resolution_y
                
        # Find intersection between lower bound of ortho camera and zero-plane
        # It will be the nearest visible y coord in the depth map
        sy = 0
        if rx > ry:
            sy = ry / rx * bpy.data.scenes[0].camera.data.ortho_scale
        else:
            sy = bpy.data.scenes[0].camera.data.ortho_scale
            
        
    
        cy = bpy.data.scenes[0].camera.location.y
        cz = bpy.data.scenes[0].camera.location.z
        a = bpy.data.scenes[0].camera.rotation_euler.x
    
        # Position of the lower edge of the viewport    
        py = cy - (sy / 2)*cos(a)
        pz = cz - (sy / 2)*sin(a)
        
        # Distance in y-direction from the lower edge of the viewport to the
        # intersection of viewport and zero plane
        r = tan(a) * pz
    
        # Final position in y-direction    
        iy = py + r

        renderMat = bpy.data.materials['RenderDummy']        

        # Set nearest visible y coord as 0 output distance
        renderMat.node_tree.nodes['LowerEdge'].inputs[1].default_value = -iy
        
        renderMat.node_tree.nodes['ZScale'].inputs[1].default_value = cos(a)
        
        scale = (ry / 256) * cos(a) / sy
        renderMat.node_tree.nodes['Scale'].inputs[1].default_value = scale
                
        orig_materials = {}
    

        
        for (k, m) in bpy.data.meshes.items():
            if k != 'RenderDummy':
                orig_materials[k] = []
                for i in range(len(m.materials)):
                    orig_materials[k].append(m.materials[i])
                    m.materials[i] = renderMat

        bpy.ops.render.render()
        
                
        for (k, m) in bpy.data.meshes.items():
            if k != 'RenderDummy':
                for i in range(len(m.materials)):
                    m.materials[i] = orig_materials[k][i]

        bpy.data.images['Render Result'].save_render(make_outname('_depth'))                

        bpy.data.scenes["Scene"].use_nodes = use_compositor
        bpy.data.scenes["Scene"].render.engine = engine
        bpy.data.scenes["Scene"].render.use_antialiasing = use_aa
        
        bpy.data.scenes[0].display_settings.display_device = colspace
        
        return {"FINISHED"}


class DepthMapRenderPanel(bpy.types.Panel):
    """Panel containing tools for 2D game"""
    bl_label = "2D Game Tools"
    bl_idname = "SCENE_PT_gametool"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        
        row = layout.row()
        row.scale_y = 3.0
        row.operator("scene.make_game_files")        

        row = layout.row()
        row.operator("scene.make_depth_map")
        row = layout.row()
        row.operator("scene.make_game_collision_file")
        row = layout.row()
        row.operator("scene.export_game_objects")
        row = layout.row()
        row.operator("scene.export_triggers")

def register():
    bpy.utils.register_class(MakeDepthMap)
    bpy.utils.register_class(MakeGameFiles)    
    bpy.utils.register_class(MakeCollisionFile)
    bpy.utils.register_class(MakeObjectFile)
    bpy.utils.register_class(MakeTriggerFile)
    bpy.utils.register_class(DepthMapRenderPanel)
    


def unregister():
    bpy.utils.unregister_class(DepthMapRenderPanel)
    bpy.utils.register_class(MakeObjectFile)
    bpy.utils.unregister_class(MakeDepthMap)
    bpy.utils.unregister_class(MakeGameFiles)
    bpy.utils.unregister_class(MakeCollisionFile)
    bpy.utils.unregister_class(MakeTriggerFile)

if __name__ == "__main__":
    register()
