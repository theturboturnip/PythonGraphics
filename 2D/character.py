#!/usr/bin/env python
from objects import *

class Controller:
	xmod=0
	ymod=0
	gravity=[0,90]
	def update(self):
		pass

class PlayerController(Controller):
	momentum=[0,0]	
	def update(self):	
		keys=pygame.key.get_pressed()
		self.xmod=((keys[pygame.K_LEFT]*-1)+(keys[pygame.K_RIGHT]))
		self.ymod=((keys[pygame.K_UP]*-1)+(keys[pygame.K_DOWN]))


class Character(SpriteObject):
	def __init__(self,pos,move_speed,controller):
		SpriteObject.__init__(self,pos,"sonic",sub_objects=[CircleObject([50,50])])
		self.base_move_speed=move_speed
		self.controller=controller
	def move(self,difference):
		previous=self.pos[0]
		for i in floatrange(self.pos[0],self.pos[0]+difference[0]):
			self.pos[0]=i
			self.set_corners()
			if self.check_collisions():
				self.pos[0]=previous
				break
			previous=i
		previous=self.pos[1]
		for i in floatrange(self.pos[1],self.pos[1]+difference[1]):
			self.pos[1]=i
			self.set_corners()
			if self.check_collisions():
				self.pos[1]=previous
				break
			previous=i

	def update(self,objects,deltaTime):
		Object.update(self,objects,deltaTime)
		move_speed=int(self.base_move_speed*deltaTime)
		self.controller.update()
		self.move([self.controller.xmod*move_speed,(self.controller.ymod*move_speed)+self.controller.gravity[1]*deltaTime])
		self.update_sub_objs()
