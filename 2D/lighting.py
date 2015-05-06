#!/usr/bin/env python
import pygame,sys,random,math,os
from objects import *
from character import *
PATH=os.path.dirname(os.path.realpath(__file__))
RESOURCES_PATH=PATH+"/Resources/"
WIDTH=640	
HEIGHT=480
OBJ_RADIUS=5
OBJ_COLOR=(255,255,255)
LIGHT_COLOR=(255,255,0,122)
CLEAR_COLOR=(0,0,0)
FAST_RAYCAST=True

class Light(Object):
	def __init__(self,pos,total_strength,color=LIGHT_COLOR):
		if len(color)==3:
			color.append(61)
		Object.__init__(self,pos,color)
		self.can_collide=False
		self.total_strength=total_strength
		self.lines=[]
		self.line_thickness=(self.total_strength/30)
		self.LOD=1
		self.strength=[]
		for i in range(0,360):
			self.lines.append((sin(i),cos(i)))
			self.strength.append(self.total_strength)
		self.recalced_without_objects=True
		self.check_rays([])
		
	def refine_objs(self,objects):
		toreturn=[]
		for obj in objects:
			if obj.closest_length(self.pos)<self.strength:
				toreturn.append(obj)
		return toreturn
	def check_rays(self,objects):
		lines_to_recalc=[]
		self.poly=[]
		objs_hit=[]
		for i in range(len(self.lines)):
			line=self.lines[i]
			endpoint=[int(self.pos[0]+(line[0]*self.strength[i])),int(self.pos[1]+(line[1]*self.strength[i]))]
			self.poly.append(endpoint)
		for obj in objects:
			bearing=calc_bearing(self.pos,obj)
			degree_diff=int(90*(1.0-(dist(self.pos,obj)/self.total_strength)))
			for i in range(bearing-degree_diff,bearing+degree_diff):
				lines_to_recalc.append(i)
			if obj.colliding(self):
				self.poly=[(0,0),(0,0),(0,0)]
				return
		for degree in lines_to_recalc:
			d=degree-1
			rayData=cast_ray(self.lines[d],self.pos,self.strength[d],objects)
			self.poly[d]=rayData[0]
			if rayData[1] not in objs_hit and rayData[1]!=None:
				objs_hit.append(rayData[1])	
		for obj in objs_hit:
			obj.add_light_color(self.color,1.0-(dist(self.pos,obj)/self.total_strength))		
		if len(objects)==0:
			self.recalced_without_objects=True
		else:
			self.recalced_without_objects=False
	
	def update(self,objects,deltaTime):
		objects=self.refine_objs(objects)
		if len(objects)>0 or not self.recalced_without_objects:
			self.check_rays(objects)
	def change_pos(self,pos):
		self.pos=pos
		self.check_rays([])
	def draw(self,screen):
		surf=pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
		surf.fill((0,0,0,0))
		pygame.draw.polygon(surf,self.color,self.poly[::self.LOD],0)
		screen.blit(surf, (0,0))


