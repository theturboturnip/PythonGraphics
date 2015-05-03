#!/usr/bin/env python
WIDTH=640	
HEIGHT=480
OBJ_RADIUS=5
import pygame,sys,random,math


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
def calc_bearing1(pointA, pointB):
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
 
    diffLong = math.radians(pointB[1] - pointA[1])
 
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))
 
    initial_bearing = math.atan2(x, y)
 

    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
 
    return int(compass_bearing)

def calc_bearing(p1,p2):
	xdist=p2[0]-p1[0]
	ydist=p2[1]-p1[1]
	return int(math.degrees(math.atan2(xdist,ydist)))
class Light:
	def __init__(self,pos,strength):
		self.pos,self.strength=pos,strength
		self.lines=[]
		self.line_thickness=(self.strength/30)
		for i in range(0,360):
			self.lines.append((sin(i),cos(i)))
		self.recalced_without_objects=True
		self.check_rays([],True)

	def check_rays(self,objects,creatinglines=False):
		objects=self.refine_objs(objects)
		if len(objects)==0 and not creatinglines and self.recalced_without_objects:
			return 
		lines_to_recalc=[]
		self.rays=[]
		for line in self.lines:
			self.rays.append([self.pos,[int(self.pos[0]+(line[0]*self.strength)),int(self.pos[1]+(line[1]*self.strength))]])
		for obj in objects:
			bearing=calc_bearing(self.pos,obj)
			degree_diff=int(20*(1.0-(dist(self.pos,obj)/self.strength)))
			for i in range(bearing-degree_diff,bearing+degree_diff):
				lines_to_recalc.append(i)
		for degree in lines_to_recalc:
			d=degree-1
			self.rays[d]=[self.pos,cast_ray(self.lines[d],self.pos,self.strength,objects)]
		if len(objects)==0:
			self.recalced_without_objects=True
		else:
			self.recalced_without_objects=False
		#self.rays=lines_to_return

	def refine_objs(self,objects):
		toreturn=[]
		for obj in objects:
			if dist(self.pos,obj)<self.strength:
				toreturn.append(obj)
		return toreturn

class Window:
	def __init__(self):
		pygame.init()
		self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
		#self.bitmask=[]#x,y
		#for i in range(WIDTH):
		#	self.bitmask.append([])
		#	for j in range(HEIGHT):
		#		self.bitmask[i].append(random.randint(0,255))
		self.objects=[(50,50)]
		self.lights=[Light((WIDTH/2,HEIGHT/2),100)]
	def draw(self):
		for light in self.lights:

			for line in light.rays:
				pygame.draw.lines(self.screen,(0,255,0),False,line,light.line_thickness)
				pass
		for obj in self.objects:
			pygame.draw.circle(self.screen,(0,0,0),obj,OBJ_RADIUS,0)
	def recalc_lights(self):
		self.objects[0]=pygame.mouse.get_pos()
		for light in self.lights:
			light.check_rays(self.objects)
	def loop(self):
		while True:
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					self.quit()
				if event.type==pygame.MOUSEMOTION:
					self.recalc_lights()
			self.screen.fill((255,255,255))
			self.draw()
			pygame.display.flip()

	
	def quit(self):
		pygame.quit();sys.exit()



w = Window()
w.loop()

