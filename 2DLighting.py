#!/usr/bin/env python
import pygame,sys,random,math
WIDTH=640	
HEIGHT=480
OBJ_RADIUS=5
DRAW_LIGHT_AS_LINES=False

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
	for obj in objects:
		distance=dist(obj,start_point)
		point=[int(start_point[0]+(ray[0]*distance)),int(start_point[1]+(ray[1]*distance))]
		if dist(obj,point)<OBJ_RADIUS:
			if smallest_length>distance:
				smallest_length=distance
	endpoint=[int(start_point[0]+(ray[0]*smallest_length)),int(start_point[1]+(ray[1]*smallest_length))]
	return endpoint
def calc_bearing(p1,p2):
	xdist=p2[0]-p1[0]
	ydist=p2[1]-p1[1]
	return int(math.degrees(math.atan2(xdist,ydist)))


class Light:
	def __init__(self,pos,total_strength):
		self.pos,self.total_strength=pos,total_strength
		self.lines=[]
		self.line_thickness=(self.total_strength/30)
		self.LOD=self.total_strength/50
		if self.LOD<1:
			self.LOD=1
		self.strength=[]
		for i in range(0,360):
			self.lines.append((sin(i),cos(i)))
			self.strength.append(self.total_strength-random.randint(0,20))
		self.recalced_without_objects=True
		self.check_rays([])

	def check_rays(self,objects):
		lines_to_recalc=[]
		self.rays=[]
		self.poly=[]
		for i in range(len(self.lines)):
			line=self.lines[i]
			endpoint=[int(self.pos[0]+(line[0]*self.strength[i])),int(self.pos[1]+(line[1]*self.strength[i]))]
			self.rays.append([self.pos,endpoint])
			self.poly.append(endpoint)
		for obj in objects:
			bearing=calc_bearing(self.pos,obj)
			degree_diff=int(20*(1.0-(dist(self.pos,obj)/self.total_strength)))
			for i in range(bearing-degree_diff,bearing+degree_diff):
				lines_to_recalc.append(i)
		for degree in lines_to_recalc:
			d=degree-1
			self.rays[d]=[self.pos,cast_ray(self.lines[d],self.pos,self.strength[d],objects)]
			self.poly[d]=cast_ray(self.lines[d],self.pos,self.strength[d],objects)
		if len(objects)==0:
			self.recalced_without_objects=True
		else:
			self.recalced_without_objects=False

	def refine_objs(self,objects):
		toreturn=[]
		for obj in objects:
			if dist(self.pos,obj)<self.strength:
				toreturn.append(obj)
		return toreturn
	def update(self,objects):
		objects=self.refine_objs(objects)
		if len(objects)>0 or not self.recalced_without_objects:
			self.check_rays(objects)

class Window:
	def __init__(self):
		pygame.init()
		self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
		self.objects=[(50,50)]
		self.lights=[Light((200,200),200),Light((220,220),100)]
		self.clock=pygame.time.Clock()		
	def draw(self):
		for obj in self.objects:
			pygame.draw.circle(self.screen,(0,0,0),obj,OBJ_RADIUS,0)
		self.draw_lights()
		
	def draw_lights(self):
		deltaTime=self.clock.tick(30)/1000
		surf=pygame.Surface((WIDTH,HEIGHT)).convert_alpha()
		for light in self.lights:
			if DRAW_LIGHT_AS_LINES:
				for line in light.rays:
					pygame.draw.lines(self.screen,(0,255,0),False,line,light.line_thickness)
			else:
				surf.fill((0,0,0,0))
				pygame.draw.polygon(surf,(0,255,0,61),light.poly[::light.LOD],0)
				self.screen.blit(surf, (0,0))

	def recalc_lights(self):
		for light in self.lights:
			light.check_rays(self.objects)

	def loop(self):
		while True:
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					self.quit()
			self.screen.fill((255,255,255))
			self.objects[0]=pygame.mouse.get_pos()
			for l in self.lights:
				l.update(self.objects)
			self.draw()
			
			pygame.display.update()
	
	def quit(self):
		pygame.quit();sys.exit()

w = Window()
w.loop()

