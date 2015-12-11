function sign(p1, p2, p3)
	return (p1[1] - p3[1]) * (p2[2] - p3[2]) - (p2[1] - p3[1]) * (p1[2] - p3[2])
end


function pointInTriangle(p, verts)
	local b1 = sign(p, verts[1], verts[2]) < 0
	local b2 = sign(p, verts[2], verts[3]) < 0
	local b3 = sign(p, verts[3], verts[1]) < 0

	return (b1 == b2) and (b2 == b3)
end


function love.load()
  cm = love.filesystem.load('test_collision.lua')()
	ob = love.filesystem.load('test_objects.lua')()

  t = 0
  depi = love.image.newImageData("test_depth.png")
  col = love.graphics.newImage("test_color.png")
  dep = love.graphics.newImage(depi)
  bal = love.graphics.newImage("ball.png")

  colc = love.graphics.newCanvas()
  depc = love.graphics.newCanvas()

  bgshader = love.graphics.newShader [[
    uniform Image depthMap;
    void effects(vec4 color, Image texture, vec2 texture_coords, vec2 screen_coords) {
      love_Canvases[0] = Texel(texture, texture_coords);
      love_Canvases[1] = Texel(depthMap, texture_coords);
    }
  ]]

  fgshader = love.graphics.newShader [[
    uniform Image depthMap;
    uniform float depth;
    vec4 effect(vec4 color, Image texture, vec2 texture_coords, vec2 screen_coords) {
      vec4 dm = Texel(depthMap, vec2(screen_coords.x / 800, 1.0 - screen_coords.y / 600));
      float d = dm.r * 256.0 + dm.g * 256.0*256.0;
      if(depth > d) {
        discard;
      } else {
        return Texel(texture, texture_coords);
      }
    }
  ]]

  fgshader:send('depthMap', depc)
  bgshader:send('depthMap', dep)
  f = 0
  bz = 600
  bx = 400
end


function projectPoint(p)
	return p[1], 600 - p[2] / 2 - math.sin(60 * 3.14159 / 180.0) * p[3], 600 - (1200 - p[2]) * 0.5 - p[3] * math.sin(30 / 180 *3.14159)
end


function projectVerts(verts)
  local t = {}
  for i, v in ipairs(verts) do
		t[#t+1], t[#t+2] = projectPoint(v)
  end

  return t
end





function len(v1, v2)
	local x = v1[1] - v2[1]
	local y = v1[2] - v2[2]
	return math.sqrt(x*x+y*y)
end


function triangleArea(v1, v2, v3)
	local a = len(v1, v2)
	local b = len(v2, v3)
	local c = len(v3, v1)
	local s = (a+b+c)/2
	return math.sqrt(s*(s-a)*(s-b)*(s-c))
end


print(triangleArea({0,0}, {10,5}, {3,8}))


function heightOnTriangle(p, verts)
	local at = triangleArea(verts[1], verts[2], verts[3])
	local a1 = triangleArea(p, verts[2], verts[3])
	local a2 = triangleArea(p, verts[1], verts[3])
	local a3 = triangleArea(p, verts[1], verts[2])

  --print("H: " .. at .. ", " .. a1 .. " + " .. a2 .. " + " .. a3 .. " = " .. (a1+a2+a3))

	return (verts[1][3] * a1 + verts[2][3] * a2 + verts[3][3] * a3) / at
end


function love.draw()
  love.graphics.setLineStyle("rough")
  love.graphics.setShader(bgshader)
  love.graphics.setCanvas(colc, depc)
  love.graphics.draw(col)

  love.graphics.setShader()
  love.graphics.setCanvas()
  love.graphics.draw(colc)

  love.graphics.setShader(fgshader)
	local gx, gy, gz = projectPoint({bx, bz, h})
  fgshader:send("depth", gz)

  love.graphics.draw(bal, gx, gy, 0, 1, 1, 32, 58)

  love.graphics.setShader()

  love.graphics.setColor(0,0,0)
  love.graphics.print(love.timer.getFPS(), 10, 10)
  local dir, dig = depi:getPixel(bx, bz / 2)
  local dd = dig * 256 + dir
  love.graphics.print("H=" .. h, 300, 10)
  love.graphics.setColor(255,0,0)

  if intri then
    local t = projectVerts(intri.verts)
    love.graphics.polygon('line', t)
  end
  

	local a, b = projectPoint(ob.Empty.pos)
	love.graphics.rectangle('fill', bx-5, 600-bz/2-5, 10, 10)

  love.graphics.setColor(255, 255, 255)

end


function depth(y, z)
  local e = 600 - (1200-y-z) / 2
  return e
end


function love.update(dt)
  f = f + 1
  t = t + dt
  --bx = 400 -- 400+200*math.sin(t)
  --bz = 600+200*math.cos(t)

  --bz = 512
  d  = depth(bz, 0)

  local dd = 200

  if love.keyboard.isDown('up') then
    bz = bz + dd * dt
  end

  if love.keyboard.isDown('down') then
    bz = bz - dd * dt
  end

  if love.keyboard.isDown('left') then
    bx = bx - dd * dt
  end

  if love.keyboard.isDown('right') then
    bx = bx + dd * dt
  end

  for i, t in ipairs(cm) do
		local inside = pointInTriangle({bx, bz}, t.verts)
		if inside then
      intri = t
			h = heightOnTriangle({bx, bz}, t.verts)
		end
  end
end

