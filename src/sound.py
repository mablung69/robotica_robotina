import pygame
import os
import time
from enums import PlayerSounds
from enums import Player
from enums import Action
from enums import ActionSounds

class Sound(object):

    def __init__(self):
        pygame.mixer.init()

        self.player_sounds = {}
        self.action_sounds = {}

        self.player_sounds[Player.eduardo] = pygame.mixer.Sound(PlayerSounds.eduardo)
        self.player_sounds[Player.alexis] = pygame.mixer.Sound(PlayerSounds.alexis)
        self.player_sounds[Player.claudio] = pygame.mixer.Sound(PlayerSounds.claudio)
        self.player_sounds[Player.arturo] = pygame.mixer.Sound(PlayerSounds.arturo)

        self.action_sounds[Action.key] = pygame.mixer.Sound(ActionSounds.key)
        self.action_sounds[Action.open_door] = pygame.mixer.Sound(ActionSounds.open_door)
        self.action_sounds[Action.thanks] = pygame.mixer.Sound(ActionSounds.thanks)
    
    def play_player(self,player):
        if player in self.player_sounds.keys():
            self.player_sounds[player].play()
        else:
            raise Exception('Player not valid.')

    def play_action(self, action):
        if action in [Action.key, Action.open_door, Action.thanks]:
            self.action_sounds[action].play()
        else:
            raise Exception('Action not valid.')


if __name__=="__main__":

    s = Sound()
    s.play_player(Player.claudio)


    time.sleep(3)