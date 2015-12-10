# What's This?

![screenshot](https://raw.githubusercontent.com/rnlf/blender_game_tools/master/example.gif)

A script for blender that allows rendering orthographics depth maps in screen space. The rendered depth map will be a 8BPP RGB PNG with the 16 bit depth map encoded in the red and green channels.

The red channel gets the lower 8 bit, the green channel the upper 8. Depth value 0 will be the depth value of a Z (vertical) distance of 0 from the lowest point visable in the rendered image.

An increase of 1 represents a depth increase equal to the increase from the lowest to the second to lowest row in the rendered image at Z position 0.

At the moment the script only works for orthographics cameras with a Euler rotations of 0 around Y and Z and (hopefully) arbitrary rotations around X. I have only tested it with 60° rotated cameras though.

This is what the rendered files look like that were used to create the example above:

![screenshot](https://raw.githubusercontent.com/rnlf/blender_game_tools/master/example_color.png)
![screenshot](https://raw.githubusercontent.com/rnlf/blender_game_tools/master/example_depth.png)


# Installation

Append the RenderDummy Object from the .blend file to your Blender project (File->Append).

Load the .py file into a text editor node in Blender and execute it (Alt+P).

# Usage

After running the script, a new panel is available in the Scene tab of the Properties editor. This panel contains several buttons: One to only render the depth map, one for rendering the depth map and one to conveniently render the depth map and normal image.

The render path (Properties Editor -> Render -> Output) has to be set up for both buttons to function correctly. It must be the full path to a a PNG file, including the .png suffix. No file of that name will be generated though, instead, two files are written: The normal render will get the part _color inserted between filename and file ending, the depth map's filename gets _depth inserted.

There are also two more buttons: One exports a mesh with the name "Collision" into a lua file called <Output>_collision.lua.
This Lua file contains all triangles of the exported mesh. As a bonus, each triangle has a list of its neighboring triangles (with which it shares an edge). This is useful for room based collisions (where each edge between two triangles is a portal). Other uses for this graph are navigation, line-of-sight and elevations. The format of each triangle is:

```
{ verts = {{x1, y1, z1}, {x2, y2, z2}, {x3, y3, z3}},
  neighbors = {N1, N2, N3}}
```

Here, N1, N2 and N3 are the indices (1-based, as usual for Lua) that are connected to the current triangle through edges 1-2, 2-3 and 3-1 (in that order). An index of -1 indicates "no neighbor".

The vertex locations are in final world coordinates, see below!

The other additional module allows exporting game objects. If a named layer (Addons->3D View->Layer Management) with name "Objects" exists, then the game properties (Settable via Blender's Logic Editor) of each object in the "Objects" layer are written to a file <Output>_objects.lua. The format for each object is:

```
["Name"] = {
   pos = {x, y, z},
   prop1 = ...,
   ...,
   propN = ...
}
```

Here, "Name" is Blender's name for this objects, pos is the position (in final world coordinates, see below). prop1, ..., propN are the properties as defined in the Logic Editor.

# What now?

In order to use the files, you first write the color file to the color buffer and the depth file to the depth buffer. In LÖVE (which I planned to use this with), no depth buffer is available, so it needs to be written to a canvas.

After that, objects must be rendered with depth testing (or an equivalent shader comparing the object's and the depth maps values).

The coordinate system of all outputs is like this:

X = 0 is on the left edge of the visible area and expands to the right. The far right edge is X = <Render Width> * <Render Percentage>.
Y = 0 is on the bottom of the visible area (such that Y=0, Z=0 is the first visible row of pixels). The top row of pixels has the Y coordinate as scaled by the same factor as the X axis. That means, at the "isometric" angle of 60° and a square render area, Y(top) = 2 * X(right).

Z is scaled with the same factor as well. Z=0 is the same as in blender.

To convert object coordinates from the the original XYZ coords to on-screen X'Y' and depth coords, the following formulas should work:

- X' = X
- Y' = Y * cos(alpha) + Z * sin(alpha)
- depth = RenderHeight - (Y - Z) * cos(alpha)

alpha is the Euler angle around the X axis that was used when rendering the images, RenderHeight is the height of the images that were rendered.
 
I hope those formulas check out for all cases, I only tried them with the "isometric" 60° downfacing angle.
