"""Behavior checks without opening a window or waiting for real time."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pico2d import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_a, SDLK_SPACE

import boy as game
import main as application


def key_event(key, event_type=SDL_KEYDOWN, repeat=False):
    return SimpleNamespace(type=event_type, key=key, repeat=repeat)


class CharacterTests(unittest.TestCase):
    def setUp(self):
        self.image = Mock()
        loader = patch.object(game, 'load_image', return_value=self.image)
        loader.start()
        self.addCleanup(loader.stop)
        self.boy = game.Boy()

    def start_auto(self):
        self.boy.handle_event(key_event(SDLK_a))
        self.assertEqual(self.boy.state, 'AUTO_RUN')

    def test_idle_stays_idle_without_input(self):
        self.boy.update(10.0)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.x, 400)

    def test_run_moves_and_release_stops(self):
        self.boy.handle_event(key_event(SDLK_RIGHT))
        self.boy.update(0.5)
        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.x, 500)
        self.boy.handle_event(key_event(SDLK_RIGHT, SDL_KEYUP))
        self.boy.update(1.0)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.x, 500)

    def test_last_pressed_arrow_wins_and_release_restores_other(self):
        for key in (SDLK_LEFT, SDLK_RIGHT, SDLK_RIGHT):
            self.boy.handle_event(key_event(key))
        self.assertEqual(self.boy.direction, 1)
        self.boy.handle_event(key_event(SDLK_RIGHT, SDL_KEYUP))
        self.assertEqual(self.boy.state, 'RUN')
        self.assertEqual(self.boy.direction, -1)
        self.boy.handle_event(key_event(SDLK_LEFT, SDL_KEYUP))
        self.assertEqual(self.boy.state, 'IDLE')

    def test_a_only_starts_from_idle(self):
        self.boy.handle_event(key_event(SDLK_LEFT))
        self.boy.handle_event(key_event(SDLK_a))
        self.assertEqual(self.boy.state, 'RUN')
        self.boy.handle_event(key_event(SDLK_LEFT, SDL_KEYUP))
        self.start_auto()
        self.assertEqual(self.boy.direction, -1)

    def test_auto_moves_without_held_keys_at_double_speed_and_larger_size(self):
        self.start_auto()
        self.boy.handle_event(key_event(SDLK_a, SDL_KEYUP))
        self.boy.update(0.1)
        self.assertEqual(self.boy.x, 440)
        self.assertEqual(self.boy.held_keys, [])
        self.boy.draw()
        self.assertEqual(self.image.clip_draw.call_args.args[-2:], (150.0, 150.0))

    def test_both_edges_reflect_and_keep_sprite_inside(self):
        self.start_auto()
        for x, direction, expected_x, expected_direction in (
            (724, 1, 722, -1), (76, -1, 78, 1),
        ):
            with self.subTest(direction=direction):
                self.boy.x, self.boy.direction = x, direction
                self.boy.update(0.01)
                self.assertAlmostEqual(self.boy.x, expected_x)
                self.assertEqual(self.boy.direction, expected_direction)
                self.assertTrue(75 <= self.boy.x <= 725)

    def test_enlarging_at_normal_run_edges_stays_inside(self):
        for x, expected in ((50, 75), (750, 725)):
            with self.subTest(x=x):
                boy = game.Boy()
                boy.x = x
                boy.handle_event(key_event(SDLK_a))
                self.assertEqual(boy.x, expected)

    def test_large_frame_matches_small_frames_across_multiple_bounces(self):
        self.start_auto()
        other = game.Boy()
        other.handle_event(key_event(SDLK_a))
        self.boy.update(4.0)
        for _ in range(40):
            other.update(0.1)
        self.assertAlmostEqual(self.boy.x, other.x)
        self.assertEqual(self.boy.direction, other.direction)

    def test_five_second_timeout_restores_idle_size_and_stops(self):
        self.start_auto()
        self.boy.update(4.999)
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.boy.update(0.001)
        self.assertEqual(self.boy.state, 'IDLE')
        position = self.boy.x
        self.boy.update(2.0)
        self.assertEqual(self.boy.x, position)
        self.boy.draw()
        self.assertEqual(self.image.clip_draw.call_args.args[-2:], (100.0, 100.0))

    def test_long_frame_does_not_move_beyond_five_second_duration(self):
        self.start_auto()
        self.boy.update(20.0)
        self.assertEqual(self.boy.state, 'IDLE')
        self.assertEqual(self.boy.x, 350)

    def test_repressing_a_does_not_restart_active_timer(self):
        self.start_auto()
        self.boy.update(4.0)
        self.boy.handle_event(key_event(SDLK_a))
        self.boy.update(1.0)
        self.assertEqual(self.boy.state, 'IDLE')
        self.boy.handle_event(key_event(SDLK_a, repeat=True))
        self.assertEqual(self.boy.state, 'IDLE')
        self.start_auto()
        self.boy.update(4.0)
        self.assertEqual(self.boy.state, 'AUTO_RUN')

    def test_either_arrow_cancels_to_normal_run_then_release_stops(self):
        for key, direction in ((SDLK_LEFT, -1), (SDLK_RIGHT, 1)):
            with self.subTest(key=key):
                boy = game.Boy()
                boy.handle_event(key_event(SDLK_a))
                boy.update(0.1)
                boy.handle_event(key_event(key))
                self.assertEqual(boy.state, 'RUN')
                position = boy.x
                boy.update(0.1)
                self.assertAlmostEqual(boy.x - position, direction * 20)
                boy.draw()
                self.assertEqual(self.image.clip_draw.call_args.args[-2:], (100.0, 100.0))
                boy.handle_event(key_event(key, SDL_KEYUP))
                self.assertEqual(boy.state, 'IDLE')

    def test_unrelated_input_and_stray_release_do_not_cancel_auto(self):
        self.start_auto()
        self.boy.handle_event(key_event(SDLK_SPACE))
        self.boy.handle_event(key_event(SDLK_LEFT, SDL_KEYUP))
        self.assertEqual(self.boy.state, 'AUTO_RUN')
        self.assertEqual(self.boy.direction, 1)

    def test_main_forwards_keyboard_events(self):
        with patch.object(application, 'get_events', return_value=[key_event(SDLK_a)]):
            self.assertTrue(application.handle_events(self.boy))
        self.assertEqual(self.boy.state, 'AUTO_RUN')


if __name__ == '__main__':
    unittest.main()
