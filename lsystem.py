import pygame
import random
import math
import sys

from pygame.threads import MAX_WORKERS_TO_TEST

# TODO
# Add a gui with sliders to change the settings in real time and regenerate
# Make a git project

# --- Settings ---
WIDTH, HEIGHT = 1800, 1000
FPS = 120
MAX_CHILDREN = 3
THETA_RANGE = math.pi / 12
BRANCH_SWING = 3
MAX_STEP = 100
MAX_DIST = 30
R_CHANGE_MAX = 20
G_CHANGE_MAX = 20
B_CHANGE_MAX = 20
MIN_COLOR = 20
MAX_COLOR = 255
STARTING_WIDTH = 10

STARTING_COLOR = (128, 128, 128)
BACKGROUND_COLOR = (0, 0, 0)

def step_to_dist(step: int):
    # return MAX_DIST * (1.1 - math.sqrt(step / MAX_STEP))
    return random.uniform(0.02, MAX_DIST)

def step_to_number_children(step: int):
    if step < 65:
        options = [1, 2, 3, 4, 5]
        weights = [0.97, 0.02, 0.017, 0.002, 0.001]
        return random.choices(options, weights)[0]
    else:
        options = [0, 1, 2, 3, 4, 5]
        weights = [0.2, 0.3, 0.15, 0.03, 0.005, 0.002]
        return random.choices(options, weights)[0]
    # return int(random.uniform(1, math.pow(step / 100, 5) + 2))
    # return random.randint(1 if step < MAX_CHILDREN / 3 else 0, MAX_CHILDREN)

# --- Initialize ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# set background color
pygame.display.set_caption("Starter Pygame Project")
clock = pygame.time.Clock()
vec2 = pygame.math.Vector2

global_theta = 0

class Node:
    parent: 'Node | None'
    children: list['Node']
    pos: vec2
    theta: float
    step: int
    length: float
    max_length: float
    color: tuple[int, int, int]

    def __init__(self, parent: 'Node | None' = None, multiple_children: bool = False):
        self.parent = parent
        self.children = []
        if parent is None:
            self.step = 0
            self.theta = -math.pi / 2
            self.color = self._clamp_color(STARTING_COLOR)
            self.max_length = MAX_DIST
            self.length = 0.0
            self.pos = vec2(WIDTH / 2, HEIGHT)
            self.width = STARTING_WIDTH
        else:
            parent.children.append(self)
            self.step = parent.step + 1
            self.theta = self._gen_theta(parent.theta, multiple_children)
            self.color = self._gen_color(parent.color)
            self.max_length = step_to_dist(parent.step)
            self.length = self.gen_length(parent.max_length)
            self.pos = self._calc_pos(parent.pos, self.theta, self.length)
            self.width = self._calc_width(parent.width, multiple_children)

    def get_theta(self):
        return self.theta + global_theta

    @staticmethod
    def _calc_pos(parent_pos: vec2, theta: float, length: float) -> vec2:
        return vec2(
            parent_pos.x + math.cos(theta) * length,
            parent_pos.y + math.sin(theta) * length,
        )


    @staticmethod
    def _clamp_color(color: tuple[int, int, int]) -> tuple[int, int, int]:
        r, g, b = color
        r = max(MIN_COLOR, min(MAX_COLOR, r))
        g = max(MIN_COLOR, min(MAX_COLOR, g))
        b = max(MIN_COLOR, min(MAX_COLOR, b))
        return (r, g, b)

    @staticmethod
    def _gen_theta(parent_theta: float, multiple_children: bool) -> float:
        new_theta = parent_theta + random.uniform(-THETA_RANGE * BRANCH_SWING if multiple_children else -THETA_RANGE, THETA_RANGE * BRANCH_SWING if multiple_children else THETA_RANGE)
        if new_theta > math.pi / 8:
            new_theta = math.pi / 8
        if new_theta < -9 * math.pi / 8:
            new_theta = -9 * math.pi / 8
        return new_theta

    @staticmethod
    def _calc_width(parent_width: int, multiple_children: bool) -> int:
        if multiple_children:
            return max(1, parent_width - 1)
        else:
            return parent_width

    @staticmethod
    def _gen_color(parent_color: tuple[int, int, int]) -> tuple[int, int, int]:
        color = (
            parent_color[0] + random.randrange(-R_CHANGE_MAX, R_CHANGE_MAX),
            parent_color[1] + random.randrange(-G_CHANGE_MAX, G_CHANGE_MAX),
            parent_color[2] + random.randrange(-B_CHANGE_MAX, B_CHANGE_MAX),
        )
        return Node._clamp_color(color)

    def gen_length(self, max_len: float):
        return random.uniform(0.02, max_len)

    def draw(self):
        if self.parent:
            self.pos = self._calc_pos(self.parent.pos, self.get_theta(), self.length)
            pygame.draw.line(
                screen,
                self.color,
                self.parent.pos,
                self.pos,
                self.width
            )
        for child in self.children:
            child.draw()

# --- Game Loop ---
running = True
root = Node()
list_of_nodes = [root]
completed_nodes = []
last_time = pygame.time.get_ticks()
while running:
    new_time = pygame.time.get_ticks()

    # 1. Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE);

    new_nodes = []

    # 2. Update
    global_theta = math.sin(pygame.time.get_ticks() / 1000) * math.pi / 50
    if new_time - last_time > 100 and len(list_of_nodes) < 30000:
        last_time = new_time
        for node in list_of_nodes:
            if node.step < MAX_STEP:
                num_children = step_to_number_children(node.step)
                for i in range(num_children):
                    new_nodes.append(Node(node, num_children > 1))
            completed_nodes.append(node)

        list_of_nodes = new_nodes

    screen.fill(BACKGROUND_COLOR)

    # 4. Draw
    root.draw()

    # 5. Refresh display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
