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

After running the script, a new panel is available in the Scene tab of the Properties editor. This panel contains two buttons: One to only render the depth map, one for rendering the depth map and one to conveniently render the depth map and normal image.

The render path (Properties Editor -> Render -> Output) has to be set up for both buttons to function correctly. It must be the full path to a a PNG file, including the .png suffix. No file of that name will be generated though, instead, two files are written: The normal render will get the part _color inserted between filename and file ending, the depth map's filename gets _depth inserted.

# What now?

In order to use the files, you first write the color file to the color buffer and the depth file to the depth buffer. In LÖVE (which I planned to use this with), no depth buffer is available, so it needs to be written to a canvas.

After that, objects must be rendered with depth testing (or an equivalent shader comparing the object's and the depth maps values).

To convert object coordinates from the the original XYZ coords to on-screen X'Y' and depth coords, the following formulas should work:

- X' = X
- Y' = Y * cos(alpha) + Z
- depth = RenderHeight - (Y - Z) * cos(alpha)

alpha is the Euler angle around the X axis that was used when rendering the images, RenderHeight is the height of the images that were rendered.

I hope those formulas check out for all cases, I only tried them with the "isometric" 60° downfacing angle.
