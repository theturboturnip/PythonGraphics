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

class Object:
	def __init__(self,pos=(0,0),color=OBJ_COLOR):
		self.pos=pos
		self.color=color
		self.light_color=(0,0,0,0)
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
	def update(self):
		self.light_color=(0,0,0,0)
	def closest_length(self,pos):
		return int(dist(self.pos,pos))
	def longest_length(self,pos):
		return self.closest_length(pos)

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


class Window:
	def __init__(self):
		pygame.init()
		self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
		self.objects=[CircleObject([250,250],20)]
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
				o.update()
			self.objects[0].change_pos(list(pygame.mouse.get_pos()))
			for l in self.lights:
				l.update(self.objects)
			self.draw()
			pygame.display.flip()
	
	def quit(self):
		pygame.quit();sys.exit()

w = Window()
w.loop()
