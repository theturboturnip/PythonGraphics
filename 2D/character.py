#!/usr/bin/env python
from objects import *

class Controller:
	xmod=0
	ymod=0
	def update(self):
		pass

class PlayerController(Controller):	
	def update(self):	
		keys=pygame.key.get_pressed()
		self.xmod=((keys[pygame.K_LEFT]*-1)+(keys[pygame.K_RIGHT]))
		self.ymod=((keys[pygame.K_UP]*-1)+(keys[pygame.K_DOWN]))

class Character(SpriteObject):
	def __init__(self,pos,move_speed,controller):
		SpriteObject.__init__(self,pos,"sonic")
		self.base_move_speed=move_speed
		self.controller=controller
	def update(self,objects,deltaTime):
		Object.update(self,objects,deltaTime)
		move_speed=int(self.base_move_speed*deltaTime)
		self.controller.update()
		self.change_pos([self.pos[0]+self.controller.xmod*move_speed,self.pos[1]+self.controller.ymod*move_speed])
		self.check_collisions()

