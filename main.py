from pico2d import (
    SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, clear_canvas, close_canvas,
    delay, get_events, get_time, open_canvas, update_canvas,
)

from grass import Grass
from boy import Boy


def handle_events(boy):
    for event in get_events():
        if event.type == SDL_QUIT:
            return False
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            return False
    return True


def main():
    open_canvas(800, 600)
    try:
        boy = Boy()
        world = [Grass(), boy]
        previous_time = get_time()
        while handle_events(boy):
            current_time = get_time()
            frame_time = max(0.0, current_time - previous_time)
            previous_time = current_time

            for obj in world:
                obj.update(frame_time)

            clear_canvas()
            for obj in world:
                obj.draw()
            update_canvas()
            delay(0.01)
    finally:
        close_canvas()


if __name__ == '__main__':
    main()
