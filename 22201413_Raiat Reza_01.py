# Task 1 : A House in Rainfall

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

window_width = 500
window_height = 500

raindrops = []
rain_direction = 0.5
bg_brightness = 0.2
bg_step = 0.05

def setup_view():
    glViewport(0, 0, window_width, window_height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def create_house():
    # Ground
    glColor3f(0.57, 0.85, 0.43)
    glBegin(GL_TRIANGLES)
    glVertex2f(0, 200)
    glVertex2f(500, 200)
    glVertex2f(0, 0)

    glVertex2f(0, 0)
    glVertex2f(500, 0)
    glVertex2f(500, 200)
    glEnd()

    glColor3f(0.18 , 0.30, 0.18)
    glBegin(GL_TRIANGLES)
    for i in range(0, 500, 20):
        glVertex2f(0 + i, 195)
        glVertex2f(20 + i, 195)
        glVertex2f(10 + i, 235)
    glEnd()

    # House
    glColor3f(0.62, 0.62, 0.37)
    glBegin(GL_TRIANGLES)
    glVertex2f(180, 250)
    glVertex2f(320, 250)
    glVertex2f(180, 180)

    glVertex2f(180, 180)
    glVertex2f(320, 180)
    glVertex2f(320, 250)
    glEnd()

    # Door
    glColor3f(0.36, 0.25, 0.20)
    glBegin(GL_TRIANGLES)
    glVertex2f(190, 210)
    glVertex2f(220, 210)
    glVertex2f(190, 180)

    glVertex2f(190, 180)
    glVertex2f(220, 180)
    glVertex2f(220, 210)
    glEnd()

    # Window
    glColor3f(0.36, 0.25, 0.20)
    glBegin(GL_TRIANGLES)
    glVertex2f(290, 210)
    glVertex2f(310, 210)
    glVertex2f(290, 195)

    glVertex2f(290, 195)
    glVertex2f(310, 195)
    glVertex2f(310, 210)
    glEnd()

    # Roof
    glColor3f(0.8, 0.49, 0.19)
    glBegin(GL_TRIANGLES)
    glVertex2f(180, 250)
    glVertex2f(320, 250)
    glVertex2f(250, 300)
    glEnd()

def draw_rain():
    glColor3f(0.4, 0.6, 1.0)
    glBegin(GL_LINES)
    for x, y in raindrops:
        glVertex2f(x, y)
        glVertex2f(x + rain_direction, y - 10)
    glEnd()

def initiate_rain():
    for i in range(len(raindrops)):
        x, y = raindrops[i]
        x += rain_direction
        y -= 5
        if x < 0:
            x += window_width
        elif x > window_width:
            x -= window_width
        if y < 0:
            y = window_height
            x = (x + random.randint(-100, 100)) % window_width
        raindrops[i] = (x, y)

def bright_key(key, x, y):
    global bg_brightness
    if key == b'd':
        if bg_brightness < 1.0:
            bg_brightness += bg_step
        elif bg_brightness > 1.0:
            bg_brightness = 1.0
    elif key == b'n':
        if bg_brightness > 0.0:
            bg_brightness -= bg_step
        elif bg_brightness < 0.0:
            bg_brightness = 0.0

def special_key(key, x, y):
    global rain_direction
    if key == GLUT_KEY_LEFT:
        rain_direction -= 0.5
    elif key == GLUT_KEY_RIGHT:
        rain_direction += 0.5

def animate():
    initiate_rain()
    glutPostRedisplay()

def show_screen():
    glClearColor(bg_brightness, bg_brightness, bg_brightness, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_view()
    create_house()
    draw_rain()
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Task 1: A House in Rainfall")
    for i in range(100):
        x = random.randint(0, window_width)
        y = random.randint(0, window_height)
        raindrops.append((x, y))
    glutDisplayFunc(show_screen)
    glutKeyboardFunc(bright_key)
    glutSpecialFunc(special_key)
    glutIdleFunc(animate)
    glutMainLoop()
main()


#Task 2 : The Amazing Box

# from OpenGL.GL import *
# from OpenGL.GLUT import *
# from OpenGL.GLU import *
# import random

# window_width = 500
# window_height = 500

# points = []
# blinking = False
# frozen = False
# blink_state = True
# blink_counter = 0
# blink_interval = 20
# speed_multiplier = 1.0

# class MovingPoint:
#     def __init__(self, x, y):
#         self.x = x
#         self.y = y
#         self.size = random.randint(3, 6)
#         self.color = (random.random(), random.random(), random.random())
#         self.dx = random.choice([-1, 1]) * random.uniform(1, 3)
#         self.dy = random.choice([-1, 1]) * random.uniform(1, 3)

#     def move(self):
#         self.x += self.dx * speed_multiplier
#         self.y += self.dy * speed_multiplier
#         if self.x <= 0 or self.x >= window_width:
#             self.dx *= -1
#         if self.y <= 0 or self.y >= window_height:
#             self.dy *= -1

#     def draw(self):
#         glColor3f(*self.color)
#         glPointSize(self.size)
#         glBegin(GL_POINTS)
#         glVertex2f(self.x, self.y)
#         glEnd()

# def display():
#     glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
#     glLoadIdentity()
#     if not blinking or blink_state:
#         for p in points:
#             p.draw()
#     glutSwapBuffers()

# def keyboard(key, x, y):
#     global blinking, frozen
#     if key == b' ':
#         frozen = not frozen
#         if frozen:
#             print("Frozen")
#         else:
#             print("Unfrozen")

# def special(key, x, y):
#     global speed_multiplier
#     if key == GLUT_KEY_UP:
#         speed_multiplier *= 1.5
#         print("Speed increased:", round(speed_multiplier, 2))
#     elif key == GLUT_KEY_DOWN:
#         if speed_multiplier > 0.1:
#             speed_multiplier /= 1.5
#         if speed_multiplier < 0.1:
#             speed_multiplier = 0.1
#         print("Speed decreased:", round(speed_multiplier, 2))

# def mouse(button, state, x, y):
#     global blinking
#     if state == GLUT_DOWN:
#         if button == GLUT_RIGHT_BUTTON:
#             points.append(MovingPoint(x, y))
#             print(f"Point added at ({x},{y})")
#         elif button == GLUT_LEFT_BUTTON:
#             blinking = not blinking
#             print("Blinking toggled:", blinking)
#     glutPostRedisplay()

# def init():
#     glClearColor(0, 0, 0, 0)
#     glMatrixMode(GL_PROJECTION)
#     glLoadIdentity()
#     glOrtho(0, window_width, window_height, 0, -1, 1)
#     glMatrixMode(GL_MODELVIEW)

# def animate():
#     global blink_state, blink_counter
#     if not frozen:
#         if blinking:
#             blink_counter += 1
#             if blink_counter >= blink_interval:
#                 blink_state = not blink_state
#                 blink_counter = 0
#         for p in points:
#             p.move()
#     glutPostRedisplay()

# def main():
#     glutInit()
#     glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
#     glutInitWindowSize(window_width, window_height)
#     glutInitWindowPosition(100, 100)
#     glutCreateWindow(b"Task 2: The Amazing Box")
#     init()
#     glutDisplayFunc(display)
#     glutIdleFunc(animate)
#     glutKeyboardFunc(keyboard)
#     glutSpecialFunc(special)
#     glutMouseFunc(mouse)
#     glutMainLoop()
# main()