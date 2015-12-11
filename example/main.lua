


function love.load()
  cm = love.filesystem.load('test_collision.lua')()

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
  bz = 300
  bx = 400
end


function projectVerts(verts)
  local t = {}
  for i, v in ipairs(verts) do
    t[#t+1] = v[1]
    t[#t+1] = 600 - v[2] / 2 - math.sin(60 * 3.14159 / 180.0) * v[3]
  end

  return t
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
  fgshader:send("depth", d)
  love.graphics.draw(bal, bx, bz / 2, 0, 1, 1, 32, 58)

  love.graphics.setShader()

  love.graphics.setColor(0,0,0)
  love.graphics.print(love.timer.getFPS(), 10, 10)
--  local dir, dig = depi:getPixel(bx, bz / 2)
--  print(dir, dig)
--  local dd = dig * 256 + dir
--  love.graphics.print("" .. bx .. ", " .. bz .. ": " .. d .. "/" .. dd, 10, 24)
  love.graphics.setColor(255,0,0)
  
  for i, t in ipairs(cm) do
    love.graphics.polygon("line", projectVerts(t.verts))
  end


  love.graphics.setColor(255, 255, 255)

end


function depth(y)
  local e = 600 - y / 2
  return e
end


function love.update(dt)
  f = f + 1
  t = t + dt
  --bx = 400 -- 400+200*math.sin(t)
  --bz = 600+200*math.cos(t)

  --bz = 512
  d  = depth(bz)

  local dd = 200

  if love.keyboard.isDown('up') then
    bz = bz - dd * dt
  end

  if love.keyboard.isDown('down') then
    bz = bz + dd * dt
  end

  if love.keyboard.isDown('left') then
    bx = bx - dd * dt
  end

  if love.keyboard.isDown('right') then
    bx = bx + dd * dt
  end
end

