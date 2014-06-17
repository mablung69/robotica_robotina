import pygame
import os
from enums import Sounds
from enums import Player

class SoundPlayer(object):

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 2048) # setup mixer to avoid sound lag
        pygame.init()                              #initialize pygame

        self.sounds = {}

        self.sounds[Player.eduardo] = pygame.mixer.Sound(os.path.join('data',Sounds.eduardo))
        self.sounds[Player.alexis] = pygame.mixer.Sound(os.path.join('data',Sounds.alexis))
        self.sounds[Player.claudio] = pygame.mixer.Sound(os.path.join('data',Sounds.claudio))
        self.sounds[Player.arturo] = pygame.mixer.Sound(os.path.join('data',Sounds.arturo))
    
    def play_sound(self,player):
        if player in self.sounds.keys():
            self.sounds[player].play()