#!/usr/bin/env python
import math,pygame,sys,ThreeDMath,os

PATH=os.path.dirname(os.path.realpath(__file__))
RESOURCES_PATH=PATH+"/Resources/"

class Wall(ThreeDMath.TexturedPolygon):
	def __init__(self,position,rotation,w,h,img_name="wall.jpg"):
		ThreeDMath.TexturedPolygon.__init__(self,position,rotation,w,h,RESOURCES_PATH+img_name)
		self.corners=[]
		for p in self.pointlist:
			self.corners.append(ThreeDMath.RotatedAround(p,self))

class Doom(ThreeDMath.World):
	def __init__(self):
		ThreeDMath.World.__init__(self)
		self.FPS=30
		self.TEX_POLYS.append(Wall([0,0,5],[0,0,0],2,1))
		print self.TEX_POLYS
	#def update(self):
	

d=Doom()
d.loop()	
