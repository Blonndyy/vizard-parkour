import viz
import vizshape
import vizcam
import time
import random
import vizact

gameDuration = 5
planesize_x = 30
planesize_y = 30

gameStarted = False
gameOver = False
currentPlayer = 1
player1_name = ""
player2_name = ""
player1_score = 0
player2_score = 0
score = 0
startTime = 0

balls = []
colors = [viz.RED, viz.GREEN, viz.BLUE]
sizes = [0.2, 0.3, 0.4]

if __name__ == "__main__":
    viz.go()
    
    collectSound = viz.addAudio('point_collect.mp3')
    collectSound.setTime(4)
    collectSound.setRate(2)

    window_width = 1920
    window_height = 1080
    viz.window.setSize(window_width, window_height)
    
    viz.clearcolor(viz.SKYBLUE)
    
    
    model = viz.add('objekts4.glb')  
    model.setPosition(0, 0, 0.1)
    model.setScale(0.3, 0.3, 0.3)
 
   

    
    startPrompt = viz.addText('', parent=viz.SCREEN)
    startPrompt.setPosition(0.5, 0.5, 0)
    startPrompt.fontSize(30)
    startPrompt.alignment(viz.ALIGN_CENTER)
    
    scoreText = viz.addText('Score: 0', parent=viz.SCREEN)
    scoreText.setPosition(0.1, 0.95, 0)
    scoreText.fontSize(30)
    
    timerText = viz.addText(f'Time: {gameDuration}', parent=viz.SCREEN)
    timerText.setPosition(0.8, 0.95, 0)
    timerText.fontSize(30)
    timerText.alignment(viz.CENTER)
    
    playerText = viz.addText('', parent=viz.SCREEN)
    playerText.setPosition(0.5, 0.95, 0)
    playerText.fontSize(30)
    playerText.alignment(viz.CENTER)
    
    def setupPlayers():
        global player1_name, player2_name
        player1_name = viz.input('Enter Player 1 name:')
        player2_name = viz.input('Enter Player 2 name:')
        startPrompt.message(f'Press ENTER for {player1_name} to start')
    
    def startPlayerTurn():
        global gameStarted, startTime, score, currentPlayer, gameOver, balls

        if gameOver:
            gameOver = False
            currentPlayer = 1
            player1_score = 0
            player2_score = 0
            score = 0
            for ball in balls:
                ball.remove()
            balls.clear()
            spawnBalls()
            startPrompt.message(f'Press ENTER for {player1_name} to start')
            return

        if not gameStarted:
            viz.MainView.setPosition([0, 1.6, 0]) 
            viz.MainView.setEuler([0, 0, 0])
            gameStarted = True
            startTime = time.time()
            score = 0
            scoreText.message('Score: 0')
            playerText.message(f'Current Player: {player1_name if currentPlayer == 1 else player2_name}')
            startPrompt.visible(False)

            
    def spawnBalls():
        global balls
        margin = 0.5
        while len(balls) < 10:
            radius = random.choice(sizes)
            color = random.choice(colors)
            x = random.uniform(-planesize_x/2 + margin, planesize_x/2 - margin)
            z = random.uniform(-planesize_y/2 + margin, planesize_y/2 - margin)
            ball = vizshape.addSphere(radius=radius, color=color)
            ball.setPosition(x, radius, z)
            balls.append(ball)
    
    def endPlayerTurn():
        global gameStarted, currentPlayer, player1_score, player2_score, gameOver, spawnBalls

        if currentPlayer == 1:
            player1_score = score
            currentPlayer = 2
            startPrompt.message(f'Time\'s up! {player1_name}: {score} points\nPress ENTER for {player2_name} to start')
            startPrompt.visible(True)
            gameStarted = False
        else:
            player2_score = score
            if player1_score == player2_score:
                result = "It's a tie!"
            else:
                winner = player1_name if player1_score > player2_score else player2_name
                result = f'{winner} wins! ({player1_score} vs {player2_score} points)'
            startPrompt.message(result + "\nPress ENTER to play again")
            startPrompt.visible(True)
            gameStarted = False
            gameOver = True  
    
    setupPlayers()
    spawnBalls()
    
    vizact.onkeydown(viz.KEY_RETURN, startPlayerTurn)

floor = vizshape.addPlane(size=(planesize_x, planesize_y))
floor.setPosition(0, 0, 0)
floor.color(viz.GREEN)

viz.MainView.setPosition([0, 1.6, 0])
walkNav = vizcam.WalkNavigate(forward = 'w', backward='s', left='a', right='d', moveScale=3.0, turnScale= 1)
viz.cam.setHandler(walkNav)
viz.mouse.setVisible(False)

try:
    viz.mouse.setTrap(True)
except Exception:
    pass

cam_box_size = [1, 1.6, 1]  
camera_colbox = vizshape.addBox(size=cam_box_size, color=viz.RED)
camera_colbox.setParent(viz.MainView)
camera_colbox.setPosition([0, 0, 0])

camera_colbox.alpha(1.0)
viz.MainView.collision(viz.ON)
 
head_light = viz.MainView.getHeadLight()
head_light.intensity(1)

dir_light = viz.addDirectionalLight()
dir_light.direction(0, -1, 0) 
dir_light.intensity(0.5)
dir_light.enable()

viz.setOption('viz.SHADOW_ENABLE', True)
viz.setOption('viz.SHADOW_MAP_SIZE', 2048)  # Try 4096 for higher quality
viz.setOption('viz.SHADOW_BIAS', 0.001)     # Reduce shadow acne
viz.MainView.getHeadLight().disable()

dir_light.setShadowMode(viz.SHADOW_DEPTH_MAP)

sun = viz.addLight()
sun.position(10, 20, 10)
sun.color(viz.WHITE)
sun.intensity(1.5)
sun.setShadowMode(viz.SHADOW_DEPTH_MAP)


def checkCollision():
    global score, gameStarted
    if not gameStarted:
        return
    cx, cy, cz = viz.MainView.getPosition()
    half_x = cam_box_size[0] / 2.0
    half_y = cam_box_size[1] / 2.0
    half_z = cam_box_size[2] / 2.0

    for ball in list(balls):
        bx, by, bz = ball.getPosition()
        scale = ball.getScale()
        br = scale[0] 

        if (abs(cx - bx) <= half_x + br) and (abs(cy - by) <= half_y + br) and (abs(cz - bz) <= half_z + br):
            pts = getPoints(ball)
            score += pts
            scoreText.message('Score: {}'.format(score))
            
            collectSound.play()
            ball.remove()
            balls.remove(ball)

startTime = time.time()

def checkTime():
    global gameStarted
    if gameStarted:
        timeLeft = gameDuration - int(time.time() - startTime)
        if timeLeft <= 0:
            endPlayerTurn()
        else:
            timerText.message(f'Time: {timeLeft}')

vizact.ontimer(0.1, checkTime)
vizact.ontimer(0.05, checkCollision)

def getPoints(ball):
    if hasattr(ball, 'isBonus') and ball.isBonus:
        return 5  # Bonus cube
    radius = ball.getBoundingBox().size[0]
    if radius < 0.25:
        return 1
    elif radius < 0.35:
        return 2
    else:
        return 3
       
def spawnBonus():
    margin = 0.5

    bonus = vizshape.addCube(size=0.5, color=viz.YELLOW)
    bonus.setPosition(0, 1.5, 0)
    bonus.isBonus = True  
    balls.append(bonus)

vizact.ontimer(2.5, spawnBonus)
vizact.ontimer(0.5, spawnBalls)