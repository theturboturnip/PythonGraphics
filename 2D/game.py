#!/usr/bin/env python
import pygame,sys,random,math,os
from objects import *
from character import *
from lighting import *
#character.test()
PATH=os.path.dirname(os.path.realpath(__file__))
RESOURCES_PATH=PATH+"/Resources/"
WIDTH=640	
HEIGHT=480
OBJ_RADIUS=5
OBJ_COLOR=(255,255,255)
LIGHT_COLOR=(255,255,0,122)
CLEAR_COLOR=(0,0,0)
FAST_RAYCAST=True
CIRCLE_COLLIDER=0
RECTANGLE_COLLIDER=1

class Window:
	def __init__(self):
		pygame.init()
		self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
		self.objects=[RoomObject(WIDTH,HEIGHT),RectObject([50,90],80),CircleObject([500,250],50),Character([250,250],200,PlayerController())]
		self.objects.append(BakeableLight([50,50],200,baked=True,objects=self.objects))
		self.clock=pygame.time.Clock()		
	def draw_objs(self):
		for obj in self.objects:
			obj.draw(self.screen)
	def update_objs(self):
		for obj in self.objects:
			obj.update(self.objects,self.deltaTime)
	def loop(self):
		while True:
			self.deltaTime=self.clock.tick(60)/1000.0
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					self.quit()
			self.screen.fill(CLEAR_COLOR)
			self.update_objs()
			self.draw_objs()
			pygame.display.flip()
	
	def quit(self):
		pygame.quit();sys.exit()

w = Window()
w.loop()
