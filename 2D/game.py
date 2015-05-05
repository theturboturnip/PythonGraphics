#!/usr/bin/env python
import pygame,sys,random,math,os
from objects import *
from character import *
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
		self.objects=[RoomObject(WIDTH,HEIGHT),Character([250,250]),RectObject([250,400],80),CircleObject([500,250],50)]
		self.lights=[]#Light((200,200),200)]
		self.clock=pygame.time.Clock()		
	def draw(self):
		for obj in self.objects:
			obj.draw(self.screen)
		for light in self.lights:
			light.draw(self.screen)
	def loop(self):
		while True:
			deltaTime=self.clock.tick(30)/1000
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					self.quit()
			self.screen.fill(CLEAR_COLOR)
			for o in self.objects:
				o.update(self.objects)
			#self.objects[0].change_pos(list(pygame.mouse.get_pos()))
			for l in self.lights:
				l.update(self.objects)
			self.draw()
			pygame.display.flip()
	
	def quit(self):
		pygame.quit();sys.exit()

w = Window()
w.loop()
