import viz
import vizshape
import vizcam
import vizact
import math

planesize_x = 30
planesize_y = 30
window_width = 1080
window_height = 960

walk_speed = 3.5
player_height = 1.8
start_position = [0, 5, 0]

gravity = -9.8         
jump_speed = 8         
vertical_velocity = 0.0
grounded = True

walk_speed = 10
player_height = 1.8

viz.mouse.setVisible(False)
viz.mouse.setTrap(True)

def move_player():
    step = walk_speed * viz.getFrameElapsed()
    m = viz.MainView.getMatrix()
    pos = viz.MainView.getPosition()
    x, y, z = pos

    forward = [m[8], m[9], m[10]]
    right = [m[0], m[1], m[2]]

    new_x, new_y, new_z = x, y, z

    if viz.key.isDown('w'):
        target_x = x + forward[0] * step
        target_y = y + forward[1] * step
        target_z = z + forward[2] * step
        hit = viz.intersect([x, y, z], forward)
        if not hit.valid or math.dist([x,y,z], hit.point) > step:
            new_x, new_y, new_z = target_x, target_y, target_z


    if viz.key.isDown('s'):
        target_x = x - forward[0] * step
        target_y = y - forward[1] * step
        target_z = z - forward[2] * step
        hit = viz.intersect([x, y, z], [-forward[0], -forward[1], -forward[2]])
        if not hit.valid or math.dist([x,y,z], hit.point) > step:
            new_x, new_y, new_z = target_x, target_y, target_z


    if viz.key.isDown('a'):
        target_x = x - right[0] * step
        target_y = y - right[1] * step
        target_z = z - right[2] * step
        hit = viz.intersect([x, y, z], [-right[0], -right[1], -right[2]])
        if not hit.valid or math.dist([x,y,z], hit.point) > step:
            new_x, new_y, new_z = target_x, target_y, target_z


    if viz.key.isDown('d'):
        target_x = x + right[0] * step
        target_y = y + right[1] * step
        target_z = z + right[2] * step
        hit = viz.intersect([x, y, z], right)
        if not hit.valid or math.dist([x,y,z], hit.point) > step:
            new_x, new_y, new_z = target_x, target_y, target_z

    viz.MainView.setPosition([new_x, new_y, new_z])

vizact.ontimer(0, move_player)

def check_ceiling():
    x, y, z = viz.MainView.getPosition()


    origin = [x, y, z]
    direction = [0, 1, 0]

    info = viz.intersect(origin, direction)
    if info.valid:
        hit_x, hit_y, hit_z = info.point
        dist = math.dist(origin, info.point)
        print(f"Ceiling detected at {dist:.2f} units above head at {info.point}")
        return dist
    else:
        print("No ceiling detected above head")
        return None
def jump():
    global grounded, vertical_velocity
    if grounded:
        dist = check_ceiling()
        if dist is None or dist > player_height:
            vertical_velocity = jump_speed
            grounded = False
            print("Jump initiated")
        else:
            print("Jump blocked: ceiling too close")




def update_physics():
    global grounded, vertical_velocity
    x, y, z = viz.MainView.getPosition()
    vertical_velocity += gravity * viz.getFrameElapsed()
    y += vertical_velocity * viz.getFrameElapsed()
    info = viz.intersect([x, y - player_height + 0.1, z], [0, -1, 0])
    if info.valid:
        ground_y = info.point[1]
        if y <= ground_y + player_height:
            y = ground_y + player_height
            vertical_velocity = 0.0
            grounded = True
        else:
            grounded = False
    else:
        grounded = False
    viz.MainView.setPosition([x, y, z])
    
    
def respawn_player():
    viz.MainView.collision(viz.OFF)
    viz.MainView.setPosition(current_checkpoint)
    viz.MainView.collision(viz.ON)
    print(f"Respawned at: {current_checkpoint}")
    
current_checkpoint = start_position.copy()
checkpoints = [
    {
        'respawn_position': [-4, 30, 58], 
        'trigger_min_x': -10, 'trigger_max_x': -3,  
        'trigger_min_z': 55, 'trigger_max_z': 62,   
        'trigger_min_y': 30, 'trigger_max_y': 40,   
        'name': 'Checkpoint 1',
        'reached': False
    },
]

def check_fall_trigger():
    global current_checkpoint 

    player_pos = viz.MainView.getPosition()
    player_x, player_y, player_z = player_pos
    
    for checkpoint in checkpoints:
        if (checkpoint['trigger_min_x'] <= player_x <= checkpoint['trigger_max_x'] and
            checkpoint['trigger_min_z'] <= player_z <= checkpoint['trigger_max_z'] and
            checkpoint['trigger_min_y'] <= player_y <= checkpoint['trigger_max_y']):
            if not checkpoint['reached']:
                checkpoint['reached'] = True
                current_checkpoint = checkpoint['respawn_position'].copy()
                print(f"Checkpoint reached: {checkpoint['name']}")
                print(f"Respawn set to: {current_checkpoint}")
                
    if player_y <= 0:
        respawn_player()


if __name__ == "__main__":
    viz.MainView.setPosition(start_position)

    navigator = vizcam.WalkNavigate( 
    )
    viz.cam.setHandler(navigator)
    
    viz.mouse.setVisible(False)
    viz.mouse.setTrap(True)

    model = viz.add('parkour_map_13.glb')
    model.setPosition(0, 0, 0.1)
    model.setScale(9, 9, 9)
    model.collideMesh()

    viz.MainView.collision(viz.ON)
  

    
    vizact.ontimer(0, update_physics)
    vizact.onkeydown(' ', jump)
    vizact.ontimer(0.1, check_fall_trigger)

    viz.window.setSize(window_width, window_height)
    viz.clearcolor(viz.BLUE)

    sun = viz.addLight()
    sun.position(10, -10, 5)
    sun.color(viz.WHITE)
    sun.intensity(2.5)
    sun.setShadowMode(viz.SHADOW_DEPTH_MAP)
    viz.go()
    #okey then cast an ray in each y  x x- z z- direction and check the same thi