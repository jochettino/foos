#!/usr/bin/env python
import time
import subprocess
import random
import os


class Plugin:
    # This map scores => sounds
    sounds = {
        'X_0_win': ['Boxing_arena_sound-Samantha_Enrico-246597508', 'Morse Code-SoundBible.com-810471357'],
        '1_goal_left': ['musical105-loud', 'dun_dun_dun-Delsym-719755295-delayed'],
        'goal': ['crowd1', 'crowd2'],
        'reset': ['whistle_2short1long'],
        'competition': ['Air Horn-SoundBible.com-964603082-lower'],
        'sudden_death': ['buzzer2'],
        'timeout_close': ['Woop_Woop-SoundBible.com-198943467'],
        'winner_random_sound': ['street_fighter-you_win', 'dragon_ball-kame_hame_ha']
    }

    def __init__(self, bus):
        self.bus = bus
        self.bus.subscribe(self.process_event, thread=True)
        self.rand = random.Random()
        root = os.path.abspath(os.path.dirname(__file__))
        self.sounds_dir = root + "/../sounds"
        self.running = []
        self.game_mode = None

    def wait_for(self):
        still_running = []
        for p in self.running:
            try:
                p.wait(timeout=0)
            except subprocess.TimeoutExpired:
                still_running.append(p)

        self.running = still_running

    def play(self, s):
        self.wait_for()
        p = subprocess.Popen(['play', '-V0', '-q', s])
        self.running.append(p)

    def choose_sound(self, type):
        return self.rand.choice(self.sounds.get(type, []))

    def process_event(self, ev):
        sounds = []
        if ev.name == 'set_game_mode':
            self.game_mode = ev.data['mode']
        elif ev.name == 'score_goal':
            score = sorted((ev.data['yellow'], ev.data['black']))
            if self.game_mode is not None:
                if score[0] == score[1] and score[0] == self.game_mode - 1:
                    sounds.append('1_goal_left')

                if score[0] == 0 and score[1] == self.game_mode:
                    sounds.append('X_0_win')

            sounds.append('goal')
        elif ev.name == 'score_reset':
            sounds.append('reset')
        elif ev.name == 'sudden_death':
            sounds.append('sudden_death')
        elif ev.name == 'timeout_close':
            sounds.append('timeout_close')
        elif ev.name == 'start_competition':
            sounds.append('competition')
        elif ev.name == 'end_competition':
            sounds.append(self.get_end_competition_sound(ev.data['points']))
        else:
            return

        sounds = [self.sounds_dir + "/{}.wav".format(self.choose_sound(sound)) for sound in sounds]

        for s in sounds:
            self.play(s)

    def get_end_competition_sound(self, points):
        unique_winner = self.get_unique_winner(points)
        if unique_winner:
            time.sleep(2)
            return self.get_winner_custom_sound(unique_winner)
        else:
            return 'competition';

    def get_unique_winner(self, points):
        max_score = 0
        player = None
        for name, ps in points.items():
            if ps > max_score:
                max_score = ps
                player = name
            elif ps == max_score:
                player = None
        return player

    def get_winner_custom_sound(self, winner):
        return 'winner_random_sound';



if __name__ == "__main__":
    sc = SoundController()
    for i in range(6):
        score = (i, 0)
        print(score)
        sc.update(score)
        time.sleep(2)

    for i in range(6):
        score = (0, i)
        print(score)
        sc.update(score)
        time.sleep(2)
    sc.update((4, 4))
    time.sleep(3)
