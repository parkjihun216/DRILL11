from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_a, load_image
from transitions import Machine

FRAME_COUNT = 8
ANIMATION_FPS = 8.0
SPRITE_SIZE = 100
CANVAS_WIDTH = 800
RUN_SPEED = 200.0  # pixels per second
AUTO_RUN_SPEED = RUN_SPEED * 2
AUTO_RUN_SCALE = 1.5
AUTO_RUN_DURATION = 5.0
KEY_DIRECTIONS = {SDLK_LEFT: -1, SDLK_RIGHT: 1}


class Idle:
    @staticmethod
    def enter(boy):
        boy.frame = 0.0

    @staticmethod
    def update(boy, frame_time):
        boy.animate(frame_time)

    @staticmethod
    def draw(boy):
        boy.draw_sprite(300 if boy.direction > 0 else 200)


class Run:
    @staticmethod
    def enter(boy):
        boy.frame = 0.0

    @staticmethod
    def update(boy, frame_time):
        boy.animate(frame_time)
        boy.x += boy.direction * RUN_SPEED * frame_time
        half_size = SPRITE_SIZE / 2
        boy.x = max(half_size, min(CANVAS_WIDTH - half_size, boy.x))

    @staticmethod
    def draw(boy):
        boy.draw_sprite(100 if boy.direction > 0 else 0)


class AutoRun:
    @staticmethod
    def enter(boy):
        boy.frame = 0.0
        boy.held_keys.clear()
        boy.auto_run_elapsed = 0.0
        left, right = AutoRun.bounds()
        boy.x = max(left, min(right, boy.x))

    @staticmethod
    def bounds():
        half_size = SPRITE_SIZE * AUTO_RUN_SCALE / 2
        return half_size, CANVAS_WIDTH - half_size

    @staticmethod
    def update(boy, frame_time):
        remaining = AUTO_RUN_DURATION - boy.auto_run_elapsed
        active_time = min(frame_time, remaining)
        boy.auto_run_elapsed = min(AUTO_RUN_DURATION, boy.auto_run_elapsed + frame_time)
        boy.animate(active_time)
        left, right = AutoRun.bounds()
        span = right - left
        # Fold travel along a round trip, retaining distance even after multiple bounces.
        phase = boy.x - left if boy.direction > 0 else 2 * span - (boy.x - left)
        phase = (phase + AUTO_RUN_SPEED * active_time) % (2 * span)
        if phase < span:
            boy.x, boy.direction = left + phase, 1
        else:
            boy.x, boy.direction = right - (phase - span), -1
        if boy.auto_run_elapsed >= AUTO_RUN_DURATION:
            boy.finish_auto_run()

    @staticmethod
    def draw(boy):
        boy.draw_sprite(100 if boy.direction > 0 else 0, AUTO_RUN_SCALE)


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.direction = 1
        self.held_keys = []
        self.image = load_image(str(Path(__file__).with_name('animation_sheet.png')))
        self.state_classes = {'IDLE': Idle, 'RUN': Run, 'AUTO_RUN': AutoRun}
        self.machine = Machine(
            model=self,
            states=list(self.state_classes),
            transitions=[
                {'trigger': 'start_run', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'stop_run', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'start_auto_run', 'source': 'IDLE', 'dest': 'AUTO_RUN'},
                {'trigger': 'finish_auto_run', 'source': 'AUTO_RUN', 'dest': 'IDLE'},
                {'trigger': 'cancel_auto_run', 'source': 'AUTO_RUN', 'dest': 'RUN'},
            ],
            initial='IDLE',
            auto_transitions=False,
            after_state_change=self.enter_state,
        )
        self.enter_state()

    def enter_state(self):
        self.state_classes[self.state].enter(self)

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key == SDLK_a:
            if event.type == SDL_KEYDOWN and not getattr(event, 'repeat', False):
                if self.state == 'IDLE':
                    self.start_auto_run()
            return
        if event.key not in KEY_DIRECTIONS:
            return
        if event.type == SDL_KEYDOWN:
            if event.key in self.held_keys:
                return  # Ignore keyboard auto-repeat.
            self.held_keys.append(event.key)
        elif event.key in self.held_keys:
            self.held_keys.remove(event.key)

        if self.held_keys:
            self.direction = KEY_DIRECTIONS[self.held_keys[-1]]
            if self.state == 'IDLE':
                self.start_run()
            elif self.state == 'AUTO_RUN':
                self.cancel_auto_run()
        elif self.state == 'RUN':
            self.stop_run()

    def animate(self, frame_time):
        self.frame = (self.frame + ANIMATION_FPS * frame_time) % FRAME_COUNT

    def draw_sprite(self, row, scale=1.0):
        size = SPRITE_SIZE * scale
        # Keep the feet at the same height when the sprite grows.
        draw_y = self.y + (size - SPRITE_SIZE) / 2
        self.image.clip_draw(
            int(self.frame) * SPRITE_SIZE, row, SPRITE_SIZE, SPRITE_SIZE,
            self.x, draw_y, size, size,
        )

    def update(self, frame_time):
        self.state_classes[self.state].update(self, max(0.0, frame_time))

    def draw(self):
        self.state_classes[self.state].draw(self)
from pathlib import Path

