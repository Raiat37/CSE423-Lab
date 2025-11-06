import random
import time
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

Screen_Width = 1000
Screen_Height = 600
Left, Right = -Screen_Width // 2, Screen_Width // 2
Bottom, Top = -Screen_Height // 2, Screen_Height // 2

Score = 0
Game_Over = False
Paused = False
Restart = False
Diamonds = []
Diamond_Speed = 150
L_width = 1
catcher_move = 25
end_time = time.time()
Reload_Speed = 30

def Draw_Line(x1, y1, x2, y2):
    zone = Find_Zone(x1, y1, x2, y2)
    m, n = Zone_to_Zone0(x1, y1, zone)
    p, q = Zone_to_Zone0(x2, y2, zone)

    dx = p - m
    dy = q - n
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)

    x, y = m, n
    while x <= p:
        s, t = Zone0_to_Zone(x, y, zone)
        glVertex2f(float(s), float(t))
        if d < 0:
            d += dE
        else:
            d += dNE
            y += 1
        x += 1

def Find_Zone(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx >= 0 and dy < 0:
            return 7
        elif dx < 0 and dy >= 0:
            return 3
        else:
            return 4
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx < 0 and dy >= 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else:
            return 6

def Zone_to_Zone0(x, y, zone):
    return {0: (x, y), 1: (y, x), 2: (y, -x), 3: (-x, y), 4: (-x, -y), 5: (-y, -x), 6: (-y, x), 7: (x, -y)}[zone]

def Zone0_to_Zone(x, y, Zone):
    return {0: (x, y), 1: (y, x), 2: (-y, x), 3: (-x, y), 4: (-x, -y), 5: (-y, -x), 6: (y, -x), 7: (x, -y)}[Zone]

class Box:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

class Diamond:
    def __init__(self):
        self.x = random.randint(Left + 20, Right - 20)
        self.y = Top - 50
        self.color = []
        for i in range(3):
            self.color.append(random.randint(155, 255))
    def draw(self):
        R, G, B = self.color
        glColor3f(R / 255, G / 255, B / 255)
        glPointSize(L_width)
        glBegin(GL_POINTS)
        Draw_Line(self.x - 10, self.y - 10, self.x, self.y)
        Draw_Line(self.x, self.y, self.x + 10, self.y - 10)
        Draw_Line(self.x, self.y - 20, self.x - 10, self.y - 10)
        Draw_Line(self.x + 10, self.y - 10, self.x, self.y - 20)
        glEnd()
    def move(self, dt):
        if not Paused:
            self.y -= Diamond_Speed * dt

Catcher = Box(-80, Bottom + 10, 200, 20)
Pause_Box = Box(0, Top - 20, 40, 50)
Restart_Box = Box(Left + 10, Top - 40, 40, 40)
Exit_Box = Box(Right - 10, Top - 20, 40, 40)

def Initiate_Catcher():
    glColor3f(1, 1, 1)
    if Game_Over:
        glColor3f(1, 0, 0)
    glBegin(GL_POINTS)
    Draw_Line(Catcher.x, Catcher.y + Catcher.height, Catcher.x + Catcher.width, Catcher.y + Catcher.height)
    Draw_Line(Catcher.x, Catcher.y + Catcher.height, Catcher.x + 20, Catcher.y)
    Draw_Line(Catcher.x + 20, Catcher.y, Catcher.x + Catcher.width - 20, Catcher.y)
    Draw_Line(Catcher.x + Catcher.width, Catcher.y + Catcher.height, Catcher.x + Catcher.width - 20, Catcher.y)
    glEnd()

def draw_pause_button():
    glColor3f(1, 0.75, 0)
    glBegin(GL_POINTS)
    Draw_Line(Pause_Box.x + 10, Pause_Box.y, Pause_Box.x + 10, Pause_Box.y - 40)
    Draw_Line(Pause_Box.x - 10, Pause_Box.y, Pause_Box.x - 10, Pause_Box.y - 40)
    glEnd()

def draw_resume_button():
    glColor3f(1, 0.75, 0)
    glBegin(GL_POINTS)
    Draw_Line(Pause_Box.x + 10, Pause_Box.y - 20, Pause_Box.x - 10, Pause_Box.y - 40)
    Draw_Line(Pause_Box.x - 10, Pause_Box.y, Pause_Box.x + 10, Pause_Box.y - 20)
    Draw_Line(Pause_Box.x - 10, Pause_Box.y , Pause_Box.x - 10, Pause_Box.y - 40)
    glEnd()

def draw_restart_button():
    glColor3f(0, 1, 1)
    glBegin(GL_POINTS)
    Draw_Line(Restart_Box.x, Restart_Box.y, Restart_Box.x + 25, Restart_Box.y + 25)
    Draw_Line(Restart_Box.x, Restart_Box.y, Restart_Box.x + 50, Restart_Box.y)
    Draw_Line(Restart_Box.x, Restart_Box.y, Restart_Box.x + 25, Restart_Box.y - 25)
    glEnd()

def draw_exit_button():
    glColor3f(1, 0, 0)
    glBegin(GL_POINTS)
    Draw_Line(Exit_Box.x, Exit_Box.y, Exit_Box.x - 40, Exit_Box.y - 40)
    Draw_Line(Exit_Box.x, Exit_Box.y - 40, Exit_Box.x - 40, Exit_Box.y)
    glEnd()

def check_collision(diamond, catcher):
    diamond_box = Box(diamond.x - 10, diamond.y - 20, 20, 20)
    catcher_box = catcher
    return (diamond_box.x < catcher_box.x + catcher_box.width and diamond_box.x + diamond_box.width > catcher_box.x and diamond_box.y < catcher_box.y + catcher_box.height and diamond_box.y + diamond_box.height > catcher_box.y)

def update_game():
    global Diamond_Speed, catcher_move, Score, Game_Over, end_time, Paused
    current_time = time.time()
    dt = current_time - end_time
    end_time = current_time
    if not Paused and not Game_Over:
        for d in list(Diamonds):
            d.move(dt)
            if d.y < Bottom:
                Game_Over = True
                print(f"Game Over! Your Final Score is : {Score}")
            elif check_collision(d, Catcher):
                Diamonds.remove(d)
                Diamonds.append(Diamond())
                Score += 1
                print(f"Score: {Score}")
                if Score % 2 == 0:
                    Diamond_Speed += 25
                    
def restart_game():
    global Diamonds, Diamond_Speed, catcher_move, Score, Game_Over, Paused
    Diamonds.clear()
    Diamonds.append(Diamond())
    Game_Over = False
    Score = 0
    Paused = False
    Diamond_Speed = 150
    catcher_move = 25
    Catcher.x = -80
    Catcher.width = 200
    print("Game Restarted")

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    Initiate_Catcher()
    if Paused:
        draw_resume_button()
    else:
        draw_pause_button()
    draw_restart_button()
    draw_exit_button()
    for d in Diamonds:
        d.draw()
    glutSwapBuffers()

def idle():
    update_game()
    glutPostRedisplay()

def mouse(button, state, x, y):
    global Paused
    x, y = x - Screen_Width // 2, Screen_Height // 2 - y
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if Pause_Box.x - 20 < x < Pause_Box.x + 20 and Pause_Box.y - 40 < y < Pause_Box.y:
            Paused = not Paused
            if Paused:
                print("Game Paused")
            else:
                print("Game Resumed")
        elif Restart_Box.x < x < Restart_Box.x + Restart_Box.width and Restart_Box.y - 25 < y < Restart_Box.y + 25:
            restart_game()
        elif Exit_Box.x - 50 < x < Exit_Box.x and Exit_Box.y - 50 < y < Exit_Box.y:
            print("Game Exited")
            glutLeaveMainLoop()

def special_keys(key, x, y):
    if not Paused and not Game_Over:
        if key == GLUT_KEY_RIGHT:
            if Catcher.x + Catcher.width + catcher_move <= Right:
                Catcher.x += catcher_move
            else:
                Catcher.x = Right - Catcher.width
        elif key == GLUT_KEY_LEFT:
            if Catcher.x - catcher_move >= Left:
                Catcher.x -= catcher_move
            else:
                Catcher.x = Left

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(Screen_Width, Screen_Height)
glutInitWindowPosition(550, 250)
glutCreateWindow(b"Diamond Catcher")
glClearColor(0, 0, 0, 1)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(Left, Right, Bottom, Top, 0, 1)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()
Diamonds.append(Diamond())
glutDisplayFunc(display)
glutIdleFunc(idle) 
glutSpecialFunc(special_keys)
glutMouseFunc(mouse)
glutMainLoop()
