import viz
import vizshape
import vizcam
import vizact
import math


planesize_x = 30
planesize_y = 30
window_width = 1920
window_height = 1080

walk_speed = 3.5
player_height = 1.6

isJumping = False
jumpHeight = 3.0
jumpDuration = 0.8
jumpStartY = 0.0
jumpStartTime = 0.0
jumpTimer = None

def jump():
    global isJumping, jumpStartTime, jumpStartY, jumpTimer
    if not isJumping:
        isJumping = True
        jumpStartTime = viz.tick()
        jumpStartY = viz.MainView.getPosition()[1]
        jumpTimer = vizact.ontimer(0, updateJump)

def updateJump():
    global isJumping, jumpStartTime, jumpStartY, jumpTimer
    if not isJumping:
        return
    elapsed = viz.tick() - jumpStartTime
    progress = elapsed / jumpDuration
    if progress >= 1.0:
        currentPos = viz.MainView.getPosition()
        viz.MainView.setPosition([currentPos[0], jumpStartY, currentPos[2]])
        isJumping = False
        if jumpTimer:
            try:
                jumpTimer.remove()
            except Exception:
                pass
            jumpTimer = None
        return
    if progress <= 0.5:
        t = progress * 2
        height = jumpStartY + jumpHeight * (1 - (1 - t) ** 2)
    else:
        t = (progress - 0.5) * 2
        height = jumpStartY + jumpHeight * (1 - t ** 2)
    currentPos = viz.MainView.getPosition()
    viz.MainView.setPosition([currentPos[0], height, currentPos[2]])

if __name__ == "__main__":
    
    navigator = vizcam.WalkNavigate(
        forward='w',
        backward='s',
        left='a',
        right='d',
        moveScale=walk_speed,
        turnScale=1.0
    )
    viz.cam.setHandler(navigator)
    viz.mouse.setVisible(False)
    viz.mouse.setTrap(True)

    model = viz.add('parkour_mape10.glb')
    model.setPosition(0, 0, 0.1)
    model.setScale(9, 9, 9)
    viz.MainView.collision(viz.ON)

    vizact.onkeydown(' ', jump)

    viz.window.setSize(window_width, window_height)
    viz.clearcolor(viz.SKYBLUE)

    sun = viz.addLight()
    sun.position(10, -10, 5)
    sun.color(viz.WHITE)
    sun.intensity(2.5)
    sun.setShadowMode(viz.SHADOW_DEPTH_MAP)
    # Start the Vizard main loop after initialization
    viz.go()