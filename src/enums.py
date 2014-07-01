class Orientation(object):
	up    = 0
	left  = 1
	down  = 2
	right = 3

class Action(object):
	move       	= 0
	turn_left  	= 1
	turn_right 	= 2
	recognize 	= 3
	open_door		= 4
	nothing 		= 5

class RobotState(object):
	searching = 0
	returning = 1

	@staticmethod
	def to_string(n):
		if n==RobotState.searching:
			return 'Searching'
		if n==RobotState.returning:
			return 'Returning'

class Sign(object):
	turn_left 		= 1
	turn_right 		= 2
	dont_turn_left 	= 3
	dont_turn_right = 4

	@staticmethod
	def to_string(n):
		if n==Sign.turn_left:
			return 'Turn Left'
		if n==Sign.turn_right:
			return 'Turn right'
		if n==Sign.dont_turn_left:
			return 'Dont turn Left'
		if n == Sign.dont_turn_right:
			return 'Dont turn right'

class Player(object):
	eduardo = 0
	alexis 	= 1
	claudio = 2
	arturo	= 3

	@staticmethod
	def to_string(n):
		if n == Player.eduardo:
			return 'Eduardo Vargas'
		if n == Player.alexis:
			return 'Alexis Sanchez'
		if n == Player.claudio:
			return 'Claudio Bravo'
		if n == Player.arturo:
			return 'Arturo Vidal'

class Sounds(object):
	SOUND_PATH="src/sonidos_chile/"
	eduardo = SOUND_PATH + "vargas_01.wav"
	alexis 	= SOUND_PATH + "sanchez_02.wav"
	claudio = SOUND_PATH + "bravo_04.wav"
	arturo	= SOUND_PATH + "vidal_01.wav"


if __name__ == '__main__':
	print Player.to_string(Player.eduardo)
