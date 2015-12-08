import bpy
from math import cos, sin, tan

def make_outname(suffix):
    f = bpy.data.scenes["Scene"].render.filepath
    x = f.rfind('.')
    return f[0:x] + suffix + f[x:]


def set_image_settings(mode):
    bpy.data.scenes["Scene"].render.image_settings.file_format = "PNG"
    bpy.data.scenes["Scene"].render.image_settings.color_depth = '8'
    bpy.data.scenes["Scene"].render.image_settings.color_mode = mode

class MakeGameFiles(bpy.types.Operator):
    bl_idname = "scene.make_game_files"
    bl_label = "Make Game Files"

    def invoke(self, context, event):
        bpy.ops.scene.make_depth_map('INVOKE_DEFAULT')

        set_image_settings('RGB')
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(make_outname('_color'))
        
        

        return {"FINISHED"}

class MakeDepthMap(bpy.types.Operator):
    bl_idname = "scene.make_depth_map"
    bl_label = "Make Depth Map"

    def invoke(self, context, event):
        engine = bpy.data.scenes["Scene"].render.engine
        use_aa = bpy.data.scenes["Scene"].render.use_antialiasing
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
        print(scale)
        renderMat.node_tree.nodes['Scale'].inputs[1].default_value = scale
                
        orig_materials = {}
    

        
        for (k, m) in bpy.data.meshes.items():
            if k != 'RenderDummy':
                orig_materials[k] = []
                for i in range(len(m.materials)):
                    print(i)
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
#        row.scale_y = 3.0
        row.operator("scene.make_depth_map")




def register():
    bpy.utils.register_class(DepthMapRenderPanel)
    bpy.utils.register_class(MakeDepthMap)
    bpy.utils.register_class(MakeGameFiles)    


def unregister():
    bpy.utils.unregister_class(DepthMapRenderPanel)
    bpy.utils.unregister_class(MakeDepthMap)
    bpy.utils.unregister_class(MakeGameFiles)

if __name__ == "__main__":
    register()
