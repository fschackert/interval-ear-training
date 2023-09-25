import datetime
import random
import sys

import pygame

INTERVALS = {
    1: 'k2',
    2: 'g2',
    3: 'k3',
    4: 'g3',
    5: 'r4',
    6: 'u4',
    7: 'r5',
    8: 'k6',
    9: 'g6',
    10: 'k7',
    11: 'g7',
    12: 'r8',
}

OCTAVES = [
    'kontra_',
    'grosses_',
    'kleines_',
    'eingestrichenes_',
    'zweigestrichenes_',
    'dreigestrichenes_',
    'viergestrichenes_',
]

PITCHES = [
    'c',
    'cis',
    'd',
    'dis',
    'e',
    'f',
    'fis',
    'g',
    'gis',
    'a',
    'ais',
    'h',
]

KEYS = ['subkontra_a', 'subkontra_ais', 'subkontra_h']
KEYS += [octave + pitch for octave in OCTAVES for pitch in PITCHES]
KEYS += ['fuenfgestrichenes_c']

WHITE_KEYS = [key for key in KEYS if not key.endswith('is')]
BLACK_KEYS = [key for key in KEYS if key.endswith('is')]


class Keyboard:

    def __init__(
            self,
            width,
            height,
            pos=(0, 0)
    ):
        self.x, self.y = pos
        self.width = width
        self.height = height
        self.white_key_width = self.width/len(WHITE_KEYS)
        self.black_key_width = self.width/len(WHITE_KEYS)/2

    def _get_white_key_positions(self):
        white_key_positions = {}
        for i, key in enumerate(WHITE_KEYS):
            x = self.x + i*self.white_key_width + 1/2*self.white_key_width
            y = self.y + 4/5*self.height
            white_key_positions[key] = (x, y)
        return white_key_positions

    def _get_black_key_positions(self):
        key_index = 0
        black_key_positions = {BLACK_KEYS[key_index]: (self.x + self.white_key_width, self.y + 2/5*self.height)}
        for i in range(2, len(WHITE_KEYS)-1, 7):
            j = i
            for dj in [0, 1, 2, 1, 1]:
                key_index += 1
                j += dj
                x = self.x + j*self.white_key_width + self.white_key_width
                y = self.y + 2/5*self.height
                black_key_positions[BLACK_KEYS[key_index]] = (x, y)
        return black_key_positions

    @property
    def key_positions(self):
        return self._get_white_key_positions() | self._get_black_key_positions()

    def draw(self, surface):
        for i, _ in enumerate(WHITE_KEYS):
            rect = pygame.Rect(
                self.x + i*self.white_key_width,
                self.y,
                10/11*self.white_key_width,
                self.height
            )
            pygame.draw.rect(surface, (225, 225, 225), rect)

        rect = pygame.Rect(
            self.x + 2/3*self.white_key_width,
            self.y,
            2/3*self.white_key_width,
            self.height*2/3
        )
        pygame.draw.rect(surface, (0, 0, 0), rect)

        for i in range(2, len(WHITE_KEYS)-1, 7):
            pos = i
            for increment in [0, 1, 2, 1, 1]:
                pos += increment
                rect = pygame.Rect(
                    self.x + pos*self.white_key_width + 2/3*self.white_key_width,
                    self.y,
                    2/3*self.white_key_width,
                    self.height*2/3
                )
                pygame.draw.rect(surface, (0, 0, 0), rect)


class Marker:

    def __init__(
            self,
            pos,
            radius=10,
            color=(225, 25, 25)
    ):
        self.pos = pos
        self.radius = radius
        self.color = color

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.pos, self.radius)


class Solution:

    def __init__(
            self,
            text,
            pos,
            color=(225, 25, 25)
    ):
        self.text = text
        self.pos = pos
        self.color = color
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 68)

    def draw(self, surface):
        text_render = self.font.render(self.text, True, (225, 25, 25))
        x, y = self.pos
        w = text_render.get_width()
        surface.blit(text_render, (x-w/2, y))


class Timer:

    def __init__(self):
        self.start_time = datetime.datetime.now()

    @property
    def elapsed_time(self):
        return datetime.datetime.now() - self.start_time


def _generate_tasks():
    while True:
        start_key_index = random.randint(0, len(KEYS)-1)
        number_of_steps, interval_name = random.choice(list(INTERVALS.items()))

        if start_key_index - number_of_steps < 0:
            end_key_index = start_key_index + number_of_steps
        else:
            end_key_index = start_key_index - number_of_steps

        start_key = KEYS[start_key_index]
        end_key = KEYS[end_key_index]

        yield start_key, end_key, interval_name


if __name__ == '__main__':
    pygame.init()

    screen_width, screen_height = 1800, 180
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
    canvas = screen.copy()

    task = _generate_tasks()
    key_a, key_b, interval = next(task)
    keyboard = Keyboard(screen_width-screen_height, screen_height)
    marker_a = Marker(keyboard.key_positions[key_a])
    marker_b = Marker(keyboard.key_positions[key_b])
    solution = Solution(interval, (screen_width - screen_height / 2, screen_height * 2 / 5))
    timer = Timer()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print(timer.elapsed_time)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                screen_width, screen_height = event.size
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    try:
                        key_a, key_b, interval = next(task)
                        marker_a.pos = keyboard.key_positions[key_a]
                        marker_b.pos = keyboard.key_positions[key_b]
                        solution.text = interval
                    except StopIteration:
                        pygame.quit()
                        sys.exit()

        canvas.fill((255, 255, 255))
        keyboard.draw(canvas)
        marker_a.draw(canvas)
        marker_b.draw(canvas)
        solution.draw(canvas)

        screen.blit(pygame.transform.scale(canvas, (screen_width, screen_height)), (0, 0))
        pygame.display.update()
