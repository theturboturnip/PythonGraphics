#!/usr/bin/env python
import pygame,sys,random,math,os
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


def rect_intersect(r1,r2):
	if r1[0]>r2[0]+r2[2]:
		return False
	if r2[0]>r1[0]+r1[2]:
		return False
	if r1[1]>r2[1]+r2[3]:
		return False
	if r2[1]>r1[1]+r1[3]:
		return False
	return True
def refine_objs(objects,pos):
	toreturn=[]
	for obj in objects:
		if obj.closest_length(pos)<self.strength:
			toreturn.append(obj)
	return toreturn
def load_image(name):
	return pygame.image.load(RESOURCES_PATH+name+".png")
def floatrange(start,end,interval):
	toreturn=[]
	i=start
	while i<=end:
		i+=interval
		toreturn.append(i)
	return toreturn		
def sin(degrees):
	return math.sin(math.radians(degrees))
def cos(degrees):
	return math.cos(math.radians(degrees))
def dist(p1,p2):
	xdist=p1[0]-p2[0]
	ydist=p1[1]-p2[1]
	return math.sqrt((xdist**2)+(ydist**2))
def cast_ray(ray,start_point,length,objects):
	smallest_length=length
	closest_object=None
	for obj in objects:
		if FAST_RAYCAST:
			distances=range(obj.closest_length(start_point),obj.longest_length(start_point))
		else:
			distances=range(length)
		for distance in distances:
			point=[int(start_point[0]+(ray[0]*distance)),int(start_point[1]+(ray[1]*distance))]
			if obj.colliding(point):
				if smallest_length>distance:
					smallest_length=distance
					closest_object=obj
				break
	
	endpoint=[int(start_point[0]+(ray[0]*smallest_length)),int(start_point[1]+(ray[1]*smallest_length))]
	return endpoint,closest_object
def calc_bearing(p1,p2):
	xdist=p2[0]-p1[0]
	ydist=p2[1]-p1[1]
	return int(math.degrees(math.atan2(xdist,ydist)))
def clamp(toclamp,min_,max_):
	if toclamp<min_:
		return min_
	if toclamp>max_:
		return max_
	return toclamp

class Object(object):
	def __init__(self,pos=(0,0),color=OBJ_COLOR):
		self.pos=pos
		self.color=color
		self.light_color=(0,0,0,0)
		self.cached_state=[]
	def __getitem__(self,index):
		return self.pos[index]
	def point_intersecting(self,point):
		return False
	def change_pos(self,pos):
		self.pos=pos
	def add_light_color(self,color,amount=1.0):
		self.light_color=[clamp(int(self.light_color[i]+(color[i]*amount)),0,255) for i in range(0,4)]
	def draw(self,screen):
		pass
	def update(self,objects):
		self.light_color=(0,0,0,0)
		self.chached_state=objects[:]
		self.chached_state.remove(self)
		for obj in self.chached_state:
			if self.colliding(obj):
				self.collided_with(obj)
	def collided_with(self,obj):
		print self,obj.pos
	def closest_length(self,pos):
		return int(dist(self.pos,pos))
	def longest_length(self,pos):
		return self.closest_length(pos)
	def colliding(self,obj):
		return False

class CircleObject(Object):
	def __init__(self,pos=(0,0),radius=OBJ_RADIUS,color=OBJ_COLOR):
		Object.__init__(self,pos,color)
		self.radius=radius
		
	def point_intersecting(self,point):
		return dist(self.pos,point)<=self.radius
	def draw(self,screen):
		surf=pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
		surf.fill((0,0,0,0))
		pygame.draw.circle(screen,self.color,self.pos,self.radius,0)
		pygame.draw.circle(surf,self.light_color,self.pos,self.radius,0)
		screen.blit(surf,(0,0))	
	def closest_length(self,pos):
		return int(dist(self.pos,pos)-self.radius)
	def longest_length(self,pos):
		return int(dist(self.pos,pos)+(self.radius*0.75))
	def colliding(self,obj):
		if type(obj)==CircleObject:
			return dist(self,obj)<=(self.radius+obj.radius)
		else:
			return obj.closest_length(self)<self.radius
class RectObject(Object):
	def __init__(self,pos=[0,0],w=20,h=0,color=OBJ_COLOR):
		if h==0:
			h=w
		pos+=[h,w]
		Object.__init__(self,pos,color)
		self.corners=[[self.pos[0],self.pos[1]],
			     [self.pos[0]+self.pos[2],self.pos[1]],
			     [self.pos[0]+self.pos[2],self.pos[1]+self.pos[3]],
			     [self.pos[0],self.pos[1]+self.pos[3]]]
	def point_intersecting(self,point):
		xvalid=self.pos[0]<=point[0]<=self.pos[0]+self.pos[2]
		yvalid=self.pos[1]<=point[1]<=self.pos[1]+self.pos[3]
		return xvalid and yvalid
	def draw(self,screen):
		surf=pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
		surf.fill((0,0,0,0))
		pygame.draw.rect(screen,self.color,self.pos,0)
		pygame.draw.rect(surf,self.light_color,self.pos,0)
		screen.blit(surf,(0,0))
	def change_pos(self,pos):
		self.pos[0],self.pos[1]=pos
		self.corners=[[self.pos[0],self.pos[1]],
			     [self.pos[0]+self.pos[2],self.pos[1]],
			     [self.pos[0]+self.pos[2],self.pos[1]+self.pos[3]],
			     [self.pos[0],self.pos[1]+self.pos[3]]]
	def closest_length(self,pos):
		smallest=-1
		for p in self.corners:
			d=dist(p,pos)
			if d<smallest or smallest==-1:
				smallest=d
		return int(smallest*0.95)
	def longest_length(self,pos):
		longest=-1
		for p in self.corners:
			d=dist(p,pos)
			if d>longest or longest==-1:
				longest=d
		return int(longest*1.05)
	def colliding(self,obj):
		if type(obj)==CircleObject:
			return self.closest_length(obj)<obj.radius
		elif type(obj) in [RectObject,SpriteObject]:
			return rect_intersect(self,obj)
		else:
			return False

class SpriteObject(RectObject):
	def __init__(self,pos=[0,0],img_path="favicon"):
		self.image=load_image(img_path).convert_alpha()
		self.w,self.h=self.image.get_width(),self.image.get_height()
		RectObject.__init__(self,pos,self.w,self.h)
	def draw(self,screen):
		screen.blit(self.image,self.pos[:2])
	def point_intersecting(self,point):
		relpoint=[point[i]-self.pos[i] for i in range(2)]
		if relpoint[0]>=self.w or 0>relpoint[0]:	
			return False
		if relpoint[1]>=self.h or 0>relpoint[1]:
			return False
		return self.image.get_at(relpoint).a>0

class RoomObject(Object):
	def __init__(self,w,h):
		self.w,self.h=w,h
		self.pos=[0,0,w,h]
	def colliding(self,obj):
		if type(obj)==CircleObject:
			x,y=obj.pos
			if x<obj.radius or x>self.w-obj.radius:
				return True
			if y<obj.radius or y>self.h-obj.radius:
				return True
		else:

			return (not rect_intersect(self,obj))

