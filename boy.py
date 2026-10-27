from pico2d import load_image
from transitions import Machine

FRAME_COUNT = 8
ANIMATION_FPS = 8.0
SPRITE_SIZE = 100


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


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.direction = 1
        self.image = load_image('animation_sheet.png')
        self.state_classes = {'IDLE': Idle}
        self.machine = Machine( 
            model=self,
            states=['IDLE'],
            initial='IDLE',
            auto_transitions=False,
            after_state_change=self.enter_state,
        )
        self.enter_state()

    def enter_state(self):
        self.state_classes[self.state].enter(self)

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
