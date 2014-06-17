class Orientation(object):
	up    = 0
	left  = 1
	down  = 2
	right = 3

class Action(object):
	move       = 0
	turn_left  = 1
	turn_right = 2
	recognize = 3

class Sign(object):
	turn_left 		= 1
	turn_right 		= 2
	dont_turn_left 	= 3
	dont_turn_right = 4

class Player(object):
	eduardo = 0
	alexis 	= 1
	claudio = 2
	arturo	= 3

class Sounds(object):
	SOUND_PATH="src/sonidos_chile/"
	eduardo = SOUND_PATH + "vargas_01.wav"
	alexis 	= SOUND_PATH + "sanchez_02.wav"
	claudio = SOUND_PATH + "bravo_03.wav"
	arturo	= SOUND_PATH + "vidal_01.wav"

	
