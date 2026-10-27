from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, load_image
from transitions import Machine

FRAME_COUNT = 8
ANIMATION_FPS = 8.0
SPRITE_SIZE = 100
CANVAS_WIDTH = 800
RUN_SPEED = 200.0  # pixels per second
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


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.direction = 1
        self.held_keys = []
        self.image = load_image('animation_sheet.png')
        self.state_classes = {'IDLE': Idle, 'RUN': Run}
        self.machine = Machine( 
            model=self,
            states=list(self.state_classes),
            transitions=[
                {'trigger': 'start_run', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'stop_run', 'source': 'RUN', 'dest': 'IDLE'},
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
        elif self.state == 'RUN':
            self.stop_run()

    def animate(self, frame_time):
        self.frame = (self.frame + ANIMATION_FPS * frame_time) % FRAME_COUNT

    def draw_sprite(self, row, scale=1.0):
        size = SPRITE_SIZE * scale
        self.image.clip_draw(
            int(self.frame) * SPRITE_SIZE, row, SPRITE_SIZE, SPRITE_SIZE,
            self.x, self.y, size, size,
        )

    def update(self, frame_time):
        self.state_classes[self.state].update(self, frame_time)

    def draw(self):
        self.state_classes[self.state].draw(self)
