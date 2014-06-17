import pygame
import os
from enums import Sounds
from enums import Player

class SoundPlayer(object):

    def __init__(self):
        pygame.init()                              #initialize pygame
        pygame.mixer.init()

        self.sounds = {}

        if not os.path.isfile(Sounds.eduardo):
            print "No file for eduardo"

        self.sounds[Player.eduardo] = pygame.mixer.Sound(os.path.join('data',Sounds.eduardo))
        self.sounds[Player.alexis] = pygame.mixer.Sound(os.path.join('data',Sounds.alexis))
        self.sounds[Player.claudio] = pygame.mixer.Sound(os.path.join('data',Sounds.claudio))
        self.sounds[Player.arturo] = pygame.mixer.Sound(os.path.join('data',Sounds.arturo))
    
    def play_sound(self,player):
        if player in self.sounds.keys():
            self.sounds[player].play()

if __name__=="__main__":

    s = SoundPlayer()
    s.play_sound(Player.alexis)