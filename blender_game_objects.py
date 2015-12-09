import bpy
import bmesh

def make_outname(suffix):
    f = bpy.data.scenes["Scene"].render.filepath
    x = f.rfind('.')
    return f[0:x] + suffix

class MakeGameObjectFiles(bpy.types.Operator):
    bl_idname = "scene.make_game_object_files"
    bl_label = "Make Game Object Files"

    def invoke(self, context, event):

        collision = bpy.data.meshes["Collision"]
        cc = bmesh.new()
        cc.from_mesh(collision)

        bmesh.ops.triangulate(cc, faces=cc.faces)

        
        with open(make_outname("_collision.lua"), "w") as of:
                

            of.write("return {\n")
            for f in cc.faces:
                of.write("  { verts = {\n")
                vs = sorted(f.verts, key=lambda x: x.index)
                for v in vs:
                    of.write("      {" + ", ".join(map(str, v.co)) + "},\n")
            
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



class GameObjectPanel(bpy.types.Panel):
    """Bla"""
    bl_label = "Game Objects"
    bl_idname = "OBJECT_PT_hello"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        
        row.operator("scene.make_game_object_files")
  
        


def register():
    bpy.utils.register_class(MakeGameObjectFiles)
    bpy.utils.register_class(GameObjectPanel)


def unregister():
    bpy.utils.unregister_class(GameObjectPanel)
    bpy.utils.unregister_class(MakeGameObjectFiles)

if __name__ == "__main__":
    register()
