import time
import math
import random

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class GameLayout:
    def __init__(self):
        self._init_display_settings()
        self._init_player_settings()
        self._init_enemy_settings()
        self._init_weapon_settings()
        self._init_game_state()

    def _init_display_settings(self):
        # Display settings
        self.screen_width = 1000
        self.screen_height = 800
        self.arena_size = 600
        self.camera_fov = 120

        # Camera settings
        self.camera_pos = [0, 500, 500]
        self.camera_dist = 500
        self.camera_elev = 500
        self.camera_rot = 0

    def _init_player_settings(self):
        self.player_pos = [0, 0, 0]
        self.player_speed = 12
        self.turn_speed = 12
        self.player_rot = 0
        self.health = 5
        self.score = 0

    def _init_weapon_settings(self):
        self.bullets = []
        self.missed_shots = 0
        self.max_misses = 10
        self.bullet_size = 7.5
        self.bullet_speed = 4

    def _init_enemy_settings(self):
        self.enemies = []
        self.enemy_scale = 1.0
        self.enemy_timer = 0
        self.enemy_speed = 0.025
        self.max_enemies = 5
        self.enemy_hitbox = 60

    def _init_game_state(self):
        self.game_over = False
        self.first_person = False
        self.auto_shoot = False
        self.auto_follow = False
        self._prev_in_sight = False     
        self.cheat_fire_cooldown = 0.15 
        self._last_shot_ts = 0.0
        self.cheat_turn_speed = 6       

class GameRender:
    def __init__(self, config):
        self.cfg = config
        self.weapon_offset = [30, 20, 80]
        self.head_center_z = 130   
        self.head_radius   = 20   
        self.fp_clearance  = 8    
        self.fp_forward    = 12    

    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
        """Displays text on screen at specified position"""
        self._setup_2d_rendering()
        self._render_text(x, y, text, font)
        self._restore_3d_rendering()

    def _setup_2d_rendering(self):
        """Switch to 2D orthographic projection for text rendering"""
        glColor3f(1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.cfg.screen_width, 0, self.cfg.screen_height)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

    def _render_text(self, x, y, text, font):
        """Render text at the specified position"""
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    def _restore_3d_rendering(self):
        """Restore previous 3D rendering state"""
        glPopMatrix()  
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()  
        glMatrixMode(GL_MODELVIEW)  

    def setup_view(self):
        """Set up the camera view based on current configuration"""
        self._setup_projection()

        if self.cfg.first_person:
            self._setup_first_person_view()
        else:
            self._setup_third_person_view()

    def _setup_projection(self):
        """Set up perspective projection"""
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()  
        gluPerspective(self.cfg.camera_fov,float(self.cfg.screen_width)/self.cfg.screen_height,0.1, 1500)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity() 

    def _setup_first_person_view(self):
        """First-person camera that never starts inside the head."""
        safe_eye_z = (self.cfg.player_pos[2] + self.head_center_z + self.head_radius + self.fp_clearance)
        angle = math.radians(self.cfg.player_rot)

        nudge_x = math.sin(angle) * self.fp_forward
        nudge_y = math.cos(angle) * self.fp_forward

        eye_x = self.cfg.player_pos[0] + nudge_x
        eye_y = self.cfg.player_pos[1] + nudge_y
        eye_z = safe_eye_z

        if self.cfg.auto_shoot and not getattr(self.cfg, "auto_follow", False):
            look_x = eye_x
            look_y = eye_y + 100
            look_z = eye_z
            gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)
            return
        look_x = eye_x - math.sin(-angle) * 100
        look_y = eye_y - math.cos(-angle) * 100
        look_z = eye_z
        gluLookAt(eye_x, eye_y, eye_z, look_x, look_y, look_z, 0, 0, 1)

    def _setup_third_person_view(self):
        """Set up camera for third-person view"""
        angle = math.radians(self.cfg.camera_rot)
        cam_x = self.cfg.camera_dist * math.sin(angle)
        cam_y = self.cfg.camera_dist * math.cos(angle)
        gluLookAt(cam_x, cam_y, self.cfg.camera_elev, 0, 0, 0, 0, 0, 1)

    def draw_arena(self):
        """Draw the game arena floor and walls"""
        self._draw_floor_tiles()
        self._draw_boundary_walls()

    def _draw_floor_tiles(self):
        """Draw the checkerboard pattern floor"""
        glBegin(GL_QUADS)
        for i in range(-self.cfg.arena_size, self.cfg.arena_size + 1, 100):
            for j in range(-self.cfg.arena_size, self.cfg.arena_size + 1, 100):
                # Alternate colors for checkerboard pattern
                if (i + j) % 200 == 0:
                    glColor3f(1, 1, 1)
                else :
                    glColor3f(0.7, 0.5, 0.95)
                glVertex3f(i, j, 0)
                glVertex3f(i + 100, j, 0)
                glVertex3f(i + 100, j + 100, 0)
                glVertex3f(i, j + 100, 0)
        glEnd()

    def _draw_boundary_walls(self):
        """Draw the arena boundary walls"""
        colors = [(0,0,1),(0,1,0),(0,1,1) , (1,1,1)]  # Different colors for each wall
        walls = [[(-self.cfg.arena_size, -self.cfg.arena_size), (-self.cfg.arena_size, self.cfg.arena_size+100)],
            [(self.cfg.arena_size+100, -self.cfg.arena_size), (self.cfg.arena_size+100, self.cfg.arena_size+100)],
            [(-self.cfg.arena_size, self.cfg.arena_size+100), (self.cfg.arena_size+100, self.cfg.arena_size+100)],
            [(-self.cfg.arena_size, -self.cfg.arena_size), (self.cfg.arena_size+100, -self.cfg.arena_size)]]

        glBegin(GL_QUADS)
        for idx, wall in enumerate(walls):
            glColor3f(*colors[idx])
            glVertex3f(wall[0][0], wall[0][1], 0)
            glVertex3f(wall[1][0], wall[1][1], 0)
            glVertex3f(wall[1][0], wall[1][1], 150)
            glVertex3f(wall[0][0], wall[0][1], 150)
        glEnd()

    def draw_player(self):
        """Draw player"""
        glPushMatrix()
        glTranslatef(*self.cfg.player_pos)
        glRotatef(self.cfg.player_rot, 0, 0, 1)

        if self.cfg.game_over:
            glRotatef(-90, 1, 0, 0)

        # leg
        leg_base = 15     
        leg_tip = 9       
        leg_len = 60      

        for leg_x in [-20, 20]:
            glPushMatrix()
            glTranslatef(leg_x, 0, 0)  
            glColor3f(0, 0, 1)  # Blue
            gluCylinder(gluNewQuadric(), leg_tip, leg_base, leg_len, 10, 10)
            glPopMatrix()

        # Body (olive cuboid)
        glPushMatrix()
        glTranslatef(0, 0, 70)
        glColor3f(85/255, 108/255, 47/255)  
        glScalef(1.5, 1, 2)
        glutSolidCube(35)
        glPopMatrix()

        # Head 
        glPushMatrix()
        glTranslatef(0, 0, 130)
        glColor3f(0, 0, 0)
        gluSphere(gluNewQuadric(), 20, 20, 20)
        glPopMatrix()

        # Arms 
        arm_z = 110
        arm_offset = 20   
        arm_len = 70      
        arm_base = 12     
        arm_tip = 6       

        for side in [-1, 1]:
            glPushMatrix()
            glTranslatef(side * arm_offset, 0, arm_z)
            glRotatef(90, 1, 0, 0)
            glColor3f(254/255, 223/255, 188/255)  # Skin tone
            gluCylinder(gluNewQuadric(), arm_base, arm_tip, arm_len, 10, 10)
            glPopMatrix()

        # Gun 
        glPushMatrix()
        glTranslatef(0, 0, arm_z)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.7, 0.7, 0.7)  
        gluCylinder(gluNewQuadric(), 7, 3, 80, 10, 10)  
        glPopMatrix()

        glPopMatrix()

    def draw_projectile(self, x, y, z):
        """Draw a bullet projectile at specified position"""
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-90, 1, 0, 0)
        glColor3f(1, 0, 0)  # Red color
        glutSolidCube(self.cfg.bullet_size)
        glPopMatrix()

    def draw_enemy(self, x, y, z):
        """Draw an enemy at specified position"""
        glPushMatrix()
        glTranslatef(x, y, z + 35)
        glScalef(self.cfg.enemy_scale, self.cfg.enemy_scale, self.cfg.enemy_scale)

        # Enemy body
        glColor3f(1, 0, 0)  # Red color for body
        gluSphere(gluNewQuadric(), 35, 10, 10)

        # Enemy head
        glTranslatef(0, 0, 50)
        glColor3f(0, 0, 0)  # Black color for head
        gluSphere(gluNewQuadric(), 15, 10, 10)
        glPopMatrix()

class GameLogic:
    """Handles game mechanics and state updates"""
    def __init__(self, config, renderer):
        self.cfg = config
        self.renderer = renderer

    def fire_weapon(self):
        bullet_pos = self._calculate_bullet_starting_position()
        self.cfg.bullets.append([*bullet_pos, self.cfg.player_rot])

    def _calculate_bullet_starting_position(self):
        if self.cfg.first_person:
            angle = math.radians(self.cfg.player_rot + 45)
            x = self.cfg.player_pos[0] + self.renderer.weapon_offset[0] * math.sin(angle) - self.renderer.weapon_offset[1] * math.cos(angle)
            y = self.cfg.player_pos[1] - self.renderer.weapon_offset[0] * math.cos(angle) - self.renderer.weapon_offset[1] * math.sin(angle)
            z = self.cfg.player_pos[2] + self.renderer.weapon_offset[2]
        else:
            angle_rad = math.radians(self.cfg.player_rot)
            z = self.cfg.player_pos[2] + 110
            x = self.cfg.player_pos[0] + math.sin(angle_rad) * 80
            y = self.cfg.player_pos[1] + math.cos(angle_rad) * -80
        return x, y, z

    def auto_aim(self):
        """Cheat scan and auto-shoot at enemies in sight"""
        if not self.cfg.auto_shoot:
            return

        spin = getattr(self.cfg, "cheat_turn_speed", self.cfg.turn_speed)
        self.cfg.player_rot = (self.cfg.player_rot + spin) % 360

        if not self.cfg.enemies:
            self.cfg._prev_in_sight = False
            return

        in_sight = any(self._has_clear_shot(e) for e in self.cfg.enemies)

        if in_sight and not self.cfg._prev_in_sight:
            now = time.time()
            if now - self.cfg._last_shot_ts >= self.cfg.cheat_fire_cooldown:
                self.fire_weapon()
                self.cfg._last_shot_ts = now

        self.cfg._prev_in_sight = in_sight

    def _has_clear_shot(self, enemy):
        """Check if there is a clear shot to the enemy"""
        x, y, _= self._calculate_bullet_starting_position()

        theta = math.radians(self.cfg.player_rot - 90)
        dir_x, dir_y = math.cos(theta), math.sin(theta)

        ex, ey = enemy[0] - x, enemy[1] - y

        t = ex * dir_x + ey * dir_y
        if t < 0:
            return False 

        closest_x = t * dir_x
        closest_y = t * dir_y
        dx = ex - closest_x
        dy = ey - closest_y
        dist_to_ray = math.hypot(dx, dy)

        return dist_to_ray <= self.cfg.enemy_hitbox

    def update_projectiles(self):
        """Update positions of all projectiles and remove those out of bounds"""
        bullets_to_remove = []

        for bullet in self.cfg.bullets:
            self._move_bullet(bullet)

            if self._is_bullet_out_of_bounds(bullet):
                bullets_to_remove.append(bullet)
                self.cfg.missed_shots += 1

                if self.cfg.missed_shots >= self.cfg.max_misses:
                    self.cfg.game_over = True

        for bullet in bullets_to_remove:
            self.cfg.bullets.remove(bullet)

    def _move_bullet(self, bullet):
        """Update a bullet's position based on its direction"""
        angle = math.radians(bullet[3] - 90)
        bullet[0] += self.cfg.bullet_speed * math.cos(angle)
        bullet[1] += self.cfg.bullet_speed * math.sin(angle)

    def _is_bullet_out_of_bounds(self, bullet):
        """Check if a bullet is outside the arena bounds"""
        return (bullet[0] > self.cfg.arena_size + 100 or
                bullet[0] < -self.cfg.arena_size or
                bullet[1] > self.cfg.arena_size + 100 or
                bullet[1] < -self.cfg.arena_size)

    def spawn_enemies(self, count=1):
        """Spawn new enemies at random positions away from the player"""
        for i in range(count):
            while True:
                x = random.uniform(-self.cfg.arena_size + 100, self.cfg.arena_size - 100)
                y = random.uniform(-self.cfg.arena_size + 100, self.cfg.arena_size - 100)

                if (abs(x - self.cfg.player_pos[0]) > 200 and
                    abs(y - self.cfg.player_pos[1]) > 200):
                    self.cfg.enemies.append([x, y, 0])
                    break

    def update_enemies(self):
        """Move all enemies toward the player"""
        for enemy in self.cfg.enemies:
            dx = self.cfg.player_pos[0] - enemy[0]
            dy = self.cfg.player_pos[1] - enemy[1]
            angle = math.atan2(dy, dx)

            enemy[0] += self.cfg.enemy_speed * math.cos(angle)
            enemy[1] += self.cfg.enemy_speed * math.sin(angle)

    def animate_enemies(self):
        """Animate enemy size using a sine wave effect"""
        self.cfg.enemy_timer += 0.01
        self.cfg.enemy_scale = max( 0.8, 1.0 + 0.5 * math.sin(self.cfg.enemy_timer))

    def check_collisions(self):
        """Handle all game collisions"""
        self._handle_bullet_enemy_collisions()
        self._handle_player_enemy_collisions()

    def _handle_bullet_enemy_collisions(self):
        """Check and handle bullet–enemy hits without double-removal errors."""
        hit_enemy_ids = set()
        hit_bullet_ids = set()

        for bullet in self.cfg.bullets:
            bx, by = bullet[0], bullet[1]
            for enemy in self.cfg.enemies:
                dx = bx - enemy[0]
                dy = by - enemy[1]
                if (dx*dx + dy*dy) ** 0.5 <= self.cfg.enemy_hitbox:
                    e_id = id(enemy)
                    b_id = id(bullet)

                    if e_id not in hit_enemy_ids:
                        self.cfg.score += 1
                    hit_enemy_ids.add(e_id)
                    hit_bullet_ids.add(b_id)
                    break 
        if not hit_enemy_ids and not hit_bullet_ids:
            return

        self.cfg.enemies = [e for e in self.cfg.enemies if id(e) not in hit_enemy_ids]
        self.cfg.bullets = [b for b in self.cfg.bullets if id(b) not in hit_bullet_ids]
        self.spawn_enemies(len(hit_enemy_ids))

    def _handle_player_enemy_collisions(self):
        """Player–enemy collisions using the same identity-safe filtering approach."""
        collided_enemy_ids = set()

        for enemy in self.cfg.enemies:
            dx = self.cfg.player_pos[0] - enemy[0]
            dy = self.cfg.player_pos[1] - enemy[1]
            if (dx*dx + dy*dy) ** 0.5 < 50:
                collided_enemy_ids.add(id(enemy))
                self.cfg.health -= 1
                if self.cfg.health <= 0:
                    self.cfg.game_over = True
                    break
        if not collided_enemy_ids:
            return
        
        self.cfg.enemies = [e for e in self.cfg.enemies if id(e) not in collided_enemy_ids]

        self.spawn_enemies(len(collided_enemy_ids))

class Controls :
    def __init__(self):
        self.config = GameLayout()
        self.renderer = GameRender(self.config)
        self.logic = GameLogic(self.config, self.renderer)

    def reset_game(self):
        self.config.__init__()
        self.logic.spawn_enemies(self.config.max_enemies)
        self.config._prev_in_sight = False

    def game_loop(self):
        if not self.config.game_over:
            self._update_game_state()
        glutPostRedisplay()
    def _update_game_state(self):
        self.logic.update_enemies()
        self.logic.animate_enemies()
        self.logic.update_projectiles()
        self.logic.check_collisions()

    def keyboard_handler(self, key, *args):
        """Handle keyboard input for player movement and game controls"""
        if not self.config.game_over:
            self._process_movement_keys(key)
            self._process_game_control_keys(key)

        if key == b'r':  # Reset game regardless of game state
            self.reset_game()
        self._constrain_player_position()

    def _process_movement_keys(self, key):
        x, y = self.config.player_pos[0], self.config.player_pos[1]
        angle = math.radians(-self.config.player_rot)

        if key == b'w':  # Move forward
            x -= self.config.player_speed * math.sin(angle)
            y -= self.config.player_speed * math.cos(angle)
        elif key == b's':  # Move backward
            x += self.config.player_speed * math.sin(angle)
            y += self.config.player_speed * math.cos(angle)
        elif key == b'a':  # Turn left
            self.config.player_rot += self.config.turn_speed
        elif key == b'd':  # Turn right
            self.config.player_rot -= self.config.turn_speed

        self.config.player_pos[0], self.config.player_pos[1] = x, y

    def _process_game_control_keys(self, key):
        if key in (b'c', b'C'):  # Toggle cheat mode
            self.config.auto_shoot = not self.config.auto_shoot
            self.config.enemy_hitbox = 40 if self.config.auto_shoot else 60
            if not self.config.auto_shoot:
                self.config.auto_follow = False

        elif key in (b'v', b'V'):
            if self.config.auto_shoot:
                self.config.auto_follow = not self.config.auto_follow
                if self.config.auto_follow:
                    self.config.first_person = True

    def _constrain_player_position(self):
        """Keep player within the arena bounds"""
        self.config.player_pos[0] = max(-self.config.arena_size,min(self.config.arena_size + 100, self.config.player_pos[0]))
        self.config.player_pos[1] = max(-self.config.arena_size,min(self.config.arena_size + 100, self.config.player_pos[1]))

    def specialKeyListener(self, key, *args):
        """Handle special keys (arrow keys) for camera control"""
        if key == GLUT_KEY_UP:  # Move camera closer
            self.config.camera_elev -= 10
            self.config.camera_dist -= 10
        elif key == GLUT_KEY_DOWN:  # Move camera farther
            self.config.camera_elev += 10
            self.config.camera_dist += 10
        elif key == GLUT_KEY_LEFT:  # Rotate camera left
            self.config.camera_rot -= 5
        elif key == GLUT_KEY_RIGHT:  # Rotate camera right
            self.config.camera_rot += 5

    def mouseListener(self, button, state, x, y):
        """Handle mouse clicks for weapon firing and view toggling"""
        if self.config.game_over:
            return

        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            # Left click to fire weapon
            self.logic.fire_weapon()
        elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
            # Right click to toggle first-person view
            self._toggle_first_person()

    def _toggle_first_person(self):
        """Toggle between first-person and third-person views"""
        self.config.first_person = not self.config.first_person
        self.config.turn_speed = 2.5 if self.config.first_person else 5

    def render_scene(self):
        """Render the complete game scene"""
        self._setup_rendering()
        self._render_game_elements()
        self._display_game_info()
        glutSwapBuffers()

    def _setup_rendering(self):
        """Initialize rendering for the current frame"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glViewport(0, 0, self.config.screen_width, self.config.screen_height)
        self.renderer.setup_view()

    def _render_game_elements(self):
        """Render all visible game elements"""
        # Draw static elements
        self.renderer.draw_arena()
        self.renderer.draw_player()

        if not self.config.game_over:
            if self.config.auto_shoot:
                self.logic.auto_aim()

            # Draw dynamic elements
            self._render_enemies()
            self._render_projectiles()

    def _render_enemies(self):
        """Render all enemies"""
        for enemy in self.config.enemies:
            self.renderer.draw_enemy(*enemy)

    def _render_projectiles(self):
        """Render all projectiles"""
        for bullet in self.config.bullets:
            self.renderer.draw_projectile(*bullet[:3])

    def _display_game_info(self):
        """Display game status information"""
        if not self.config.game_over:
            self.renderer.draw_text(10, 770, f"Player Life: {self.config.health}")
            self.renderer.draw_text(10, 740, f"Score: {self.config.score}")
            self.renderer.draw_text(10, 710, f"Misses: {self.config.missed_shots}")
        else:
            self.renderer.draw_text(10, 770, f"Game Over! Score: {self.config.score}")
            self.renderer.draw_text(10, 740, 'Press "R" to restart')

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(1000, 800)
glutCreateWindow(b"3D Bullet Frenzy")
glEnable(GL_DEPTH_TEST)

game = Controls ()
game.logic.spawn_enemies(game.config.max_enemies)

glutDisplayFunc(game.render_scene)
glutIdleFunc(game.game_loop)
glutKeyboardFunc(game.keyboard_handler)
glutSpecialFunc(game.specialKeyListener)
glutMouseFunc(game.mouseListener)

# Increase enemy speed for challenge
game.config.enemy_speed += .06
glutMainLoop()
