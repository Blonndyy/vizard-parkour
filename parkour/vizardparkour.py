import viz
import vizshape
import vizcam
import vizact
import math
import vizinfo

planesize_x = 30
planesize_y = 30
window_width = 1080
window_height = 960

MOVE_SPEED = 5
START_POSITION = [0, 5, 0]
PLAYER_HEIGHT = 1.82
JUMP_VELOCITY =8.5
GRAVITY = 9.8

y_velocity = 0.0
viz.clearcolor(viz.SKYBLUE)
TURN_SPEED = 60
player = viz.addChild('player.glb')
view = viz.MainView
player.collideMesh()

def get_ground_height():
    pos = viz.MainView.getPosition()
    feet_y = pos[1] - PLAYER_HEIGHT
    info = viz.intersect([pos[0], feet_y + 0.1, pos[2]], [pos[0], feet_y - 0.5, pos[2]])
    return info.point[1] + PLAYER_HEIGHT if info.valid else None


def can_move(local_dir, distance=0.5):
    x, y, z = viz.MainView.getPosition()
    origin = [x, y, z]
    mat = view.getMatrix(viz.HEAD_ORI)
    world_dir = mat.preMultVec(local_dir) 
    info = viz.intersect(origin, world_dir)
    if info.valid:
        dist = math.dist(origin, info.point)
        return dist > distance
    return True 

def updatemovement():
    dt = viz.elapsed()
    if viz.key.isDown('w'):
        if can_move([0,0,1]):
            view.move([0,0,MOVE_SPEED*dt], viz.HEAD_ORI)
        else:
            print("Blocked forward")
    elif viz.key.isDown('s'):
        if can_move([0,0,-1]):
            view.move([0,0,-MOVE_SPEED*dt], viz.HEAD_ORI)
        else:
            print("Blocked backward")

    if viz.key.isDown('a'):
        if can_move([-1,0,0]):
            view.move([-MOVE_SPEED*dt,0,0], viz.HEAD_ORI)
        else:
            print("Blocked left")
    elif viz.key.isDown('d'):
        if can_move([1,0,0]):
            view.move([MOVE_SPEED*dt,0,0], viz.HEAD_ORI)
        else:
            print("Blocked right")
    player.setPosition(view.getPosition())
    player.setEuler(view.getEuler(viz.HEAD_ORI))
    player.setPosition([0.35,-1.2,0.2], viz.REL_LOCAL)

vizact.ontimer(0,updatemovement)

def mousemove(e):
    euler = view.getEuler(viz.HEAD_ORI)
    euler[0] += e.dx * 0.1   # yaw
    euler[1] += -e.dy * 0.1  # pitch
    euler[1] = viz.clamp(euler[1], -85.0, 85.0)
    view.setEuler(euler, viz.HEAD_ORI)

viz.callback(viz.MOUSE_MOVE_EVENT, mousemove)
viz.mouse(viz.OFF)
viz.mouse.setVisible(False)
    
def jump():
    global y_velocity
    ground_height = get_ground_height()
    if ground_height is not None:
        pos = viz.MainView.getPosition()
        if abs(pos[1] - ground_height) < 0.001 and y_velocity == 0.0:
            y_velocity = JUMP_VELOCITY
        else:
            print("Cannot jump")
    else:
        print("Cannot jump")

def update_physics():
    global y_velocity
    pos = viz.MainView.getPosition()
    dt = viz.getFrameElapsed()
    
    y_velocity -= GRAVITY * dt
    new_y = pos[1] + y_velocity * dt

    ground_height = get_ground_height()
    if ground_height is not None and new_y <= ground_height and y_velocity < 0:
        new_y = ground_height
        y_velocity = 0.0
    viz.MainView.setPosition([pos[0], new_y, pos[2]])

def respawn_player():
    viz.MainView.collision(viz.OFF)
    viz.MainView.setPosition(current_checkpoint)
    viz.MainView.setEuler([0,0,0], viz.HEAD_ORI)
    viz.MainView.collision(viz.ON)
    print(f"Respawned at: {current_checkpoint}")
    
current_checkpoint = START_POSITION.copy()
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
        
esc_menu = None

def show_menu():
    global esc_menu
    if esc_menu is None:
        esc_menu = vizinfo.InfoPanel('Paused', align=viz.ALIGN_CENTER, icon=False)

        btn_continue = viz.addButtonLabel('Continue')
        btn_restart  = viz.addButtonLabel('Restart')
        btn_exit     = viz.addButtonLabel('Exit')

        esc_menu.addItem(btn_continue)
        esc_menu.addItem(btn_restart)
        esc_menu.addItem(btn_exit)

        vizact.onbuttondown(btn_continue, continue_game)
        vizact.onbuttondown(btn_restart, restart_game)
        vizact.onbuttondown(btn_exit, exit_game)
    else:
        esc_menu.visible(viz.ON)

    # Release mouse for menu interaction
    viz.mouse.setTrap(False)
    viz.mouse.setVisible(True)
    viz.callback(viz.MOUSE_MOVE_EVENT, None)

    movement_timer.setEnabled(False)
    physics_timer.setEnabled(False)
    fall_timer.setEnabled(False)


def continue_game():
    global esc_menu
    if esc_menu:
        esc_menu.visible(viz.OFF)

    viz.mouse.setTrap(True)
    viz.mouse.setVisible(False)
    viz.callback(viz.MOUSE_MOVE_EVENT, mousemove)

    movement_timer.setEnabled(True)
    physics_timer.setEnabled(True)
    fall_timer.setEnabled(True)


def restart_game():
    global esc_menu
    viz.MainView.setPosition(START_POSITION)
    if esc_menu:
        esc_menu.visible(viz.OFF)

    viz.mouse.setTrap(True)
    viz.mouse.setVisible(False)
    viz.callback(viz.MOUSE_MOVE_EVENT, mousemove)

    movement_timer.setEnabled(True)
    physics_timer.setEnabled(True)
    fall_timer.setEnabled(True)
    print("Game restarted")


def exit_game():
    viz.quit()
    
if __name__ == "__main__":
    viz.MainView.setPosition(START_POSITION)
    viz.mouse.setVisible(False)
    viz.mouse.setTrap(True)

    model = viz.add('parkour_map_13.glb')
    model.setPosition(0, 0, 0.1)
    model.setScale(9, 9, 9)
    model.collideMesh()

    viz.MainView.collision(viz.ON)
    viz.MainView.gravity(0)
    
    movement_timer = vizact.ontimer(0, updatemovement)
    physics_timer  = vizact.ontimer(0, update_physics)
    fall_timer     = vizact.ontimer(0.1, check_fall_trigger)

    vizact.onkeydown(' ', jump)
    vizact.onkeydown('`', show_menu)

    viz.window.setSize(window_width, window_height)
    viz.clearcolor(viz.BLUE)

    sun = viz.addLight()
    sun.position(10, -10, 5)
    sun.color(viz.WHITE)
    sun.intensity(2.5)
    sun.setShadowMode(viz.SHADOW_DEPTH_MAP)
    viz.go()