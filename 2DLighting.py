#!/usr/bin/env python
import pygame,sys,random,math
WIDTH=640	
HEIGHT=480
OBJ_RADIUS=5
OBJ_COLOR=(255,255,255)
DRAW_LIGHT_AS_LINES=True
LIGHT_COLOR=(255,255,0,122)
CLEAR_COLOR=(0,0,0)
FAST_RAYCAST=True

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
			distances=[obj.longest_length(start_point)]
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
	def colliding(self,point):
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
		return dist(self.pos,pos)
	def longest_length(self,pos):
		return dist(self.pos,pos)

class CircleObject(Object):
	def __init__(self,pos=(0,0),radius=OBJ_RADIUS,color=OBJ_COLOR):
		Object.__init__(self,pos,color)
		self.radius=radius
	def colliding(self,point):
		return dist(self.pos,point)<=self.radius
	def draw(self,screen):
		surf=pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
		surf.fill((0,0,0,0))
		pygame.draw.circle(screen,self.color,self.pos,self.radius,0)
		pygame.draw.circle(surf,self.light_color,self.pos,self.radius,0)
		screen.blit(surf,(0,0))	
	def closest_length(self,pos):
		return dist(self.pos,pos)-self.radius
	def longest_length(self,pos):
		return dist(self.pos,pos)+self.radius
class RectObject(Object):
	def __init__(self,pos=[0,0,0,0],color=OBJ_COLOR):
		Object.__init__(self,pos,color)
	def colliding(self,point):
		xvalid=self.pos[0]<point[0]<self.pos[0]+self.pos[2]
		yvalid=self.pos[1]<point[1]<self.pos[1]+self.pos[3]
		return xvalid and yvalid
	def draw(self,screen):
		surf=pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
		surf.fill((0,0,0,0))
		pygame.draw.rect(screen,self.color,self.pos,0)
		pygame.draw.rect(surf,self.light_color,self.pos,0)
		screen.blit(surf,(0,0))
	def change_pos(self,pos):
		self.pos[0],self.pos[1]=pos

class Light:
	def __init__(self,pos,total_strength,color=LIGHT_COLOR):
		self.pos,self.total_strength=pos,total_strength
		self.lines=[]
		self.line_thickness=(self.total_strength/30)
		self.LOD=self.total_strength/50
		if self.LOD<1:
			self.LOD=1
		self.LOD=1
		self.strength=[]
		for i in range(0,360):
			self.lines.append((sin(i),cos(i)))
			self.strength.append(self.total_strength)
		self.recalced_without_objects=True
		self.check_rays([])
		if len(color)==3:
			color.append(61)
		self.color=color

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
			degree_diff=90#int(90*(1.0-(dist(self.pos,obj)/self.total_strength)))
			for i in range(bearing-degree_diff,bearing+degree_diff):
				lines_to_recalc.append(i)
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

	def refine_objs(self,objects):
		toreturn=[]
		for obj in objects:
			print obj.closest_length(self.pos),self.strength
			if obj.closest_length(self.pos)<self.strength:
				toreturn.append(obj)
		return toreturn
	def update(self,objects):
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

class Window:
	def __init__(self):
		pygame.init()
		self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
		self.objects=[CircleObject([250,250],50)]
		self.lights=[Light((200,200),200)]
		self.clock=pygame.time.Clock()		
	def draw(self):
		for obj in self.objects:
			obj.draw(self.screen)
		for light in self.lights:
			light.draw(self.screen)

	def recalc_lights(self):
		for light in self.lights:
			light.check_rays(self.objects)

	def loop(self):
		while True:
			deltaTime=self.clock.tick(30)/1000
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					self.quit()
			self.screen.fill(CLEAR_COLOR)
			for o in self.objects:
				o.update()
			self.objects[0].change_pos(pygame.mouse.get_pos())
			for l in self.lights:
				l.update(self.objects)
			
			self.draw()
			
			pygame.display.update()
	
	def quit(self):
		pygame.quit();sys.exit()

w = Window()
w.loop()

