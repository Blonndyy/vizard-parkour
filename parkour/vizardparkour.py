import viz
import vizshape
import vizcam
import time
import random

planesize_x = 30
planesize_y = 30

window_width = 1920
window_height = 1080

if __name__ == "__main__":
    viz.go()
    
    viz.MainView.setPosition([0, 1.6, 0])
    walkNav = vizcam.WalkNavigate(forward = 'w', backward='s', left='a', right='d', moveScale=3.0, turnScale= 1)
    viz.cam.setHandler(walkNav)
    viz.mouse.setVisible(False)
    cam_box_size = [1, 1.6, 1]  
    camera_colbox = vizshape.addBox(size=cam_box_size, color=viz.RED)
    camera_colbox.setParent(viz.MainView)
    camera_colbox.setPosition([0, 0, 0])

    camera_colbox.alpha(1.0)
    viz.MainView.collision(viz.ON)
    
    viz.window.setSize(window_width, window_height)
    viz.clearcolor(viz.SKYBLUE)
    
    floor = vizshape.addPlane(size=(planesize_x, planesize_y))
    floor.setPosition(0, 0, 0)
    floor.color(viz.GREEN)
    


    sun = viz.addLight()
    sun.position(10, 20, 10)
    sun.color(viz.WHITE)
    sun.intensity(1.5)
    sun.setShadowMode(viz.SHADOW_DEPTH_MAP)
