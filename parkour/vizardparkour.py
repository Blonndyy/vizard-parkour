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
player_height = 1.8
start_position = [0, 2, 0]

isJumping = False
jumpHeight = 20.0
jumpDuration = 2
jumpStartY = 0.0
jumpStartTime = 0.0
jumpTimer = None


trigger_box = {
    'min_x': -25,
    'max_x': 15,
    'min_z': 20,
    'max_z': 75,
    'fall_threshold': 5  
}

current_checkpoint = start_position.copy()
checkpoints = [
    {
        'respawn_position': [-6, 32, 60],  # Where player spawns when they fall
        'trigger_min_x': -10, 'trigger_max_x': -3,  # Checkpoint trigger zone X
        'trigger_min_z': 55, 'trigger_max_z': 62,   # Checkpoint trigger zone Z
        'trigger_min_y': 30, 'trigger_max_y': 40,   # Checkpoint trigger zone Y
        'name': 'Checkpoint 1',
        'reached': False
    },
]




def respawn_player():
    viz.MainView.setPosition(current_checkpoint)

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


def check_fall_trigger():
    player_pos = viz.MainView.getPosition()
    player_x = player_pos[0]
    player_y = player_pos[1]
    player_z = player_pos[2]
    
    if (trigger_box['min_x'] <= player_x <= trigger_box['max_x'] and
        trigger_box['min_z'] <= player_z <= trigger_box['max_z']):
        if player_y <= trigger_box['fall_threshold']:
            respawn_player()   
            
    for checkpoint in checkpoints:
        if (checkpoint['trigger_min_x'] <= player_x <= checkpoint['trigger_max_x'] and
            checkpoint['trigger_min_z'] <= player_z <= checkpoint['trigger_max_z'] and
            checkpoint['trigger_min_y'] <= player_y <= checkpoint['trigger_max_y']): 
            if not checkpoint['reached']:  
                checkpoint['reached'] = True
                global current_checkpoint
                current_checkpoint = checkpoint['respawn_position'].copy()
                print(f"Checkpoint reached: {checkpoint['name']}")
    


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

    model = viz.add('Parkor_map_13.glb')
    model.setPosition(0, 0, 0.1)
    model.setScale(9, 9, 9)
    viz.MainView.collision(viz.ON)


    viz.MainView.setPosition(start_position)
    vizact.onkeydown(' ', jump)
    vizact.ontimer(0.1, check_fall_trigger)

    viz.window.setSize(window_width, window_height)
    viz.clearcolor(viz.SKYBLUE)

    sun = viz.addLight()
    sun.position(10, -10, 5)
    sun.color(viz.WHITE)
    sun.intensity(2.5)
    sun.setShadowMode(viz.SHADOW_DEPTH_MAP)
    viz.go()