import pygame
import sys
import typing

# --- Settings ---
WIDTH, HEIGHT = 1800, 1000
FPS = 360
PLAYER_SPEED = 10
GRAVITY = 9.8

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# set background color
pygame.display.set_caption("Starter Pygame Project")
clock = pygame.time.Clock()
vec2 = pygame.math.Vector2

class Object:
    def __init__(self, x, y, player_color = (0, 200, 255), player_size = 50, mass=1, cr=1.0):
        self.prev_pos = vec2(x, y)
        self.pos = vec2(x, y)
        self.prev_vel = vec2(0, 0)
        self.vel = vec2(0, 0)
        self.color = player_color
        self.player_size = player_size
        self.mass = mass
        self.cr = cr

    def draw(self):
        pygame.draw.circle(screen, (0,255,0), self.pos, self.player_size)

    def update(self, delta):
        self.prev_pos = self.pos
        self.prev_vel = self.vel
        self.vel.y += GRAVITY * delta
        self.pos += self.vel * delta

    def update_keys(self, keys):
        if keys[pygame.K_a]:
            self.vel.x = +PLAYER_SPEED
        elif keys[pygame.K_d]:
            self.vel.x = -PLAYER_SPEED
        if keys[pygame.K_w]:
            self.vel.y = +PLAYER_SPEED
        elif keys[pygame.K_d]:
            self.vel.y = -PLAYER_SPEED

    def is_colliding(self, other):
        return (self.pos.x - other.pos.x)**2 + (self.pos.y - other.pos.y)**2 < (self.player_size + other.player_size)**2

    def collideWall(self):
        width, height = pygame.display.get_window_size()
        if self.pos.x > width - self.player_size:
            self.pos.x = width - self.player_size
            self.vel.x = self.vel.x - (1 + self.cr) * self.vel.x
        if self.pos.x < self.player_size:
            self.pos.x = self.player_size
            self.vel.x = self.vel.x - (1 + self.cr) * self.vel.x
        if self.pos.y > height - self.player_size:
            self.pos.y = height - self.player_size
            self.vel.y = self.vel.y - (1 + self.cr) * self.vel.y
        if self.pos.y < self.player_size:
            self.pos.y = self.player_size
            self.vel.y = self.vel.y - (1 + self.cr) * self.vel.y

    def collide(self, other) -> typing.Tuple[vec2,vec2]:
        mRatio = (self.cr + 1) * other.mass / ( self.mass + other.mass)
        mvDiff:vec2 = self.vel - other.vel
        mpDiff:vec2 = self.pos - other.pos
        ret_obj_vel = self.vel
        if mpDiff.length() > 0.00001 and mvDiff.length() > 0.00001:
            proj:vec2 = mvDiff.project(mpDiff)
            ret_obj_vel = self.vel - proj * mRatio

        mRatio = (self.cr + 1) * self.mass / ( self.mass + other.mass)
        mvDiff:vec2 = other.vel - self.vel
        mpDiff:vec2 = other.pos - self.pos
        other_obj_vel = self.vel
        if mpDiff.length() > 0.00001 and mvDiff.length() > 0.00001:
            proj:vec2 = mvDiff.project(mpDiff)
            other_obj_vel = other.vel - proj * mRatio

        return (ret_obj_vel, other_obj_vel)


    def resolve_collision(self, other) -> typing.Tuple[vec2, vec2]:
        dir = (self.pos - other.pos).normalize()
        overlap = 2 * (self.pos - other.pos).length() - (self.player_size + other.player_size)
        if (overlap < 0):
            overlap = 0
        return (self.pos + dir * (overlap / 2), other.pos - dir * (overlap / 2))


class quadTree:
    def __init__(self, boundary:pygame.Rect, capacity:int):
        self.boundary = boundary
        self.capacity = capacity
        self.points: list[Object] = []
        self.divided = False
        self.northwest: quadTree = None
        self.northeast: quadTree = None
        self.southwest: quadTree = None
        self.southeast: quadTree = None

    def subdivide(self):
        x, y, w, h = self.boundary
        nw = pygame.Rect(x, y, w / 2, h / 2)
        ne = pygame.Rect(x + w / 2, y, w / 2, h / 2)
        sw = pygame.Rect(x, y + h / 2, w / 2, h / 2)
        se = pygame.Rect(x + w / 2, y + h / 2, w / 2, h / 2)
        self.northwest = quadTree(nw, self.capacity)
        self.northeast = quadTree(ne, self.capacity)
        self.southwest = quadTree(sw, self.capacity)
        self.southeast = quadTree(se, self.capacity)
        self.divided = True

    def insert(self, point:Object) -> bool:
        if not self.boundary.collidepoint(point.pos.x, point.pos.y):
            return False
        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if not self.divided:
                self.subdivide()
            if (self.northwest.insert(point) or
                self.northeast.insert(point) or
                self.southwest.insert(point) or
                self.southeast.insert(point)):
                return True
        return False

    def query(self, range:pygame.Rect, found:typing.List[Object]) -> typing.List[Object]:
        if not self.boundary.colliderect(range):
            return found
        else:
            for p in self.points:
                if range.collidepoint(p.pos.x, p.pos.y):
                    found.append(p)
            if self.divided:
                self.northwest.query(range, found)
                self.northeast.query(range, found)
                self.southwest.query(range, found)
                self.southeast.query(range, found)
        return found

# --- Game Loop ---
objs: list[Object] = []
for i in range(0,10):
    for j in range(0,10):
        objs.append(Object(i * 20 + j, j * 20 + i, (100, 100, 0), player_size=5, mass=5))
running = True
ACCEPT_COLOR = (0,50,0)
NORMAL_COLOR = (30,30,30)
was_colliding = False
old_time = pygame.time.get_ticks()
while running:
    new_time = pygame.time.get_ticks()
    delta = new_time - old_time
    old_time = new_time

    # 1. Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE);

    # initialze an alpha value color, and fill the screen
    screen.fill((0, 0, 0, 1))

    # 2. Input handling
    # keys = pygame.key.get_pressed()
    # player.update_keys(keys)

    # 4. Draw
    for i in range(len(objs)):
        for j in range(i + 1, len(objs)):
            obj1 = objs[i]
            obj2 = objs[j]
            if obj1.is_colliding(obj2):
                obj1.pos, obj2.pos = obj1.resolve_collision(obj2)
                obj1.vel, obj2.vel = obj1.collide(obj2)

    for i in range(len(objs)):
        objs[i].collideWall()
        objs[i].update(delta / 100)
        objs[i].draw()

    # 5. Refresh display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
