import pygame
import os
import time
from enums import Sounds
from enums import Player

class SoundPlayer(object):

    def __init__(self):
        pygame.mixer.init()

        self.sounds = {}

        self.sounds[Player.eduardo] = pygame.mixer.Sound(Sounds.eduardo)
        self.sounds[Player.alexis] = pygame.mixer.Sound(Sounds.alexis)
        self.sounds[Player.claudio] = pygame.mixer.Sound(Sounds.claudio)
        self.sounds[Player.arturo] = pygame.mixer.Sound(Sounds.arturo)
    
    def play_sound(self,player):
        if player in self.sounds.keys():
            self.sounds[player].play()

if __name__=="__main__":

    s = SoundPlayer()
    s.play_sound(Player.claudio)

    time.sleep(3)