from pico2d import load_image
from transitions import Machine

class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.image = load_image('animation_sheet.png')
        # 현재 캐릭터는 IDLE 상태 하나만 갖는다.
        self.machine = Machine( 
            model=self,
            states=['IDLE'],
            initial='IDLE',
            auto_transitions=False,
        )
    def update(self, frame_time):
        if self.state == 'IDLE':
            self.frame = (self.frame + 8.0 * frame_time) % 8
    def draw(self):
        if self.state == 'IDLE':
            self.image.clip_draw(int(self.frame) * 100, 300, 100, 100,self.x, self.y)
