#!/usr/bin/env python2.7
import math,pygame,sys
SCREEN_DATA=[640,480,90,45]
AXES=['x','y','z']

from PIL import Image
import numpy

def find_coeffs(pb, pa):
	matrix = []
	for p1, p2 in zip(pa, pb):
		matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
    		matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])

	A = numpy.matrix(matrix, dtype=numpy.float)
	B = numpy.array(pb).reshape(8)

    	res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)

	return numpy.array(res).reshape(8)

def deform_img(img,perspective_rect,dimensions,full_dimensions):
	pygame_img=img
	try:
		w,h=dimensions
		pygame_img=pygame.transform.scale(pygame_img,(w,h))
		
		img=Image.fromstring("RGBA",(w,h),pygame.image.tostring(pygame_img,"RGBA"))
		coeffs=find_coeffs([(0,0),(w,0),(w,h),(0,h)],perspective_rect)
		img=img.transform(full_dimensions, Image.PERSPECTIVE, coeffs)
		return pygame.image.fromstring(img.tostring(),full_dimensions,"RGBA")
	except:
		return pygame.Surface((0,0))
def RelativeToTransform(WorldPoint,transform):
	TransPos=transform.get_pos()
	RelPos=WorldPoint-TransPos
	for axis in AXES:
		RelPos=RelPos.rotate(TransPos,-transform.get_rot(axis),axis)
	return RelPos

def RotatedAround(RelPos,transform):
	TransPos=transform.get_pos()
	for axis in AXES:
		RelPos=RelPos.rotate(TransPos,-transform.get_rot(axis),axis)
	return RelPos

def PointListSum(l):
	total=Point(0,0,0)
	for p in l:
		total+=p
	return total

class Transform:
	def __init__(self,pos,rot,parent=None):
		self.position,self.rotation,self.parent=Point(pos),rot,parent
	def get_pos(self):
		if self.parent!=None:
			return self.position+self.parent.get_pos()
		return self.position
	def get_rot(self,axis):
		index=AXES.index(axis)
		if self.parent!=None:
			return self.rotation[index]+self.parent.get_rot(axis)
		return self.rotation[index]

class Point:
	def __init__(self,x,y=None,z=None):
		if y==None:
			y=x[1]
			z=x[2]
			x=x[0]
		self.x,self.y,self.z=x*1.0,y*1.0,z*1.0
		self.world_pos=[self.x,self.y,self.z]
	def __add__(self,p):
		return Point(self.x+p.x,self.y+p.y,self.z+p.z)
	def __sub__(self,p):
		return Point(self.x-p.x,self.y-p.y,self.z-p.z)
	def __mul__(self,n):
		return Point(self.x*n,self.y*n,self.z*n)
	def __div__(self,n):
		return self.__mul__(1.0/n)
	def __ne__(self,p):
		return not self.__eq__(p)
	def __eq__(self,p):
		return (p.x==self.x) and (p.y==self.y) and (p.z==self.z)
	def __getitem__(self,index):
		return self.world_pos[index]
	def rotate(self,center,angle=0,axis='x'):
		p=Point(self.x,self.y,self.z)-center
		s = math.sin(math.radians(angle))
  		c = math.cos(math.radians(angle))
		if axis=='x':
			p.y=(p.y*c)-(p.z*s)
			p.z=(p.y*s)+(p.z*c)
		elif axis=='y':
			p.x=(p.x*c)+(p.z*s)
			p.z=(-p.x*s)+(p.z*c)
		elif axis=='z':
			p.x=(p.x*c)-(p.y*s)
			p.y=(p.x*s)+(p.y*c)
		p+=center
		return p
	def __repr__(self):
		return "Point"+str(self.world_pos)

class Camera(Transform):
	def __init__(self,position=Point(0,0,0),rotation=[0,0,0],screen_data=SCREEN_DATA):
		Transform.__init__(self,position,rotation)
		screen_data[3]=((1.0*screen_data[1]*screen_data[2])/screen_data[0])
		self.screen_data=screen_data
		self.screen=pygame.display.set_mode((SCREEN_DATA[0],SCREEN_DATA[1]))
	def Rasterize(self,WorldPoint):
		RelPoint=RelativeToTransform(WorldPoint,self)
		ScrWidth,ScrHeight,FOV,VERT_FOV=self.screen_data
		ScreenX=int((((math.degrees(math.atan2(RelPoint.x,RelPoint.z)))/(FOV/2))+1)*(ScrWidth/2))
		ScreenY=int((((math.degrees(math.atan2(RelPoint.y,RelPoint.z)))/(VERT_FOV/2))+1)*(ScrHeight/2))
		return [ScreenX,ScreenY],RelPoint
	def rotate_around(self,amount,axis):
		self.rotation[AXES.index(axis)]+=amount
	def clear_screen(self):
		self.screen.fill((255,255,255))
	def draw_point(self,p):
		rel_pos,rel_world=self.Rasterize(p.world_pos)
		if rel_world.z>0:
			pygame.draw.circle(self.screen,(0,0,0),rel_pos, 2, 0)
	def draw_poly(self,p):
		points=p.rasterize(self.Rasterize)
		pygame.draw.polygon(self.screen,(0,0,0),points)
	def draw_textured_poly(self,p):
		start,points,scale_pts=p.rasterize(self.Rasterize)
		img=deform_img(img=p.img,perspective_rect=scale_pts,dimensions=scale_pts[2],full_dimensions=start[1])
		self.screen.blit(img,start[0])
	def update(self):
		pygame.display.flip()
	def translate(self,direction):
		rel_direc=Point(direction.x*math.cos(math.radians(self.rotation[1])),direction.y*1.0,direction.z*math.cos(math.radians(self.rotation[1])))
		self.position+=rel_direc

class DrawablePoint(Point):
	def __init__(self,x,y,z):
		Point.__init__(self,x,y,z)
		self.world_pos=Point(x,y,z)
	def CalcScreenPos(self,cam):
		self.screen_pos=cam.Rasterize(self.world_pos)

class DrawablePolygon(Transform):
	def __init__(self,position,rotation,pointlist,parent=None):
		Transform.__init__(self,position,rotation,parent)
		self.pointlist=pointlist

	def __getitem__(self,index):
		return self.pointlist[index]
	def rasterize(self,callback):
		center_point=PointListSum(self.pointlist)/4.0
		points=[]
		for p in self.pointlist:
			rel=(RotatedAround(p,Transform(center_point,self.rotation))+self.get_pos())
			par=self.parent
			while par!=None:
				rel=RotatedAround(rel,par)
				par=par.parent
			points.append(callback(rel)[0])
		return points

class TexturedPolygon(DrawablePolygon):
	def __init__(self,position,rotation,w,h,img_path,parent=None):
		pointlist=[Point(-w/2,-h/2,0),Point(w/2,-h/2,0),Point(w/2,h/2,0),Point(-w/2,h/2,0)]
		self.img=pygame.image.load(img_path)
		DrawablePolygon.__init__(self,position,rotation,pointlist,parent)
		
		self.equivalent=DrawablePolygon(position,rotation,pointlist,parent)
	def __getitem__(self,index):
		return self.pointlist[index]
	def rasterize(self,callback):
		points=DrawablePolygon.rasterize(self,callback)
		rev_points=[0,0,0,0]
		left=points[0][0]
		top=points[0][1]
		bottom=points[0][0]
		right=points[0][1]
		for p in points:
			if left>p[0]:
				left=p[0]
			if top>p[1]:
				top=p[1]
			if right<p[0]:
				right=p[0]
			if bottom<p[1]:
				bottom=p[1]
		width=right-left
		height=bottom-top
		for i in reversed(range(0,4)):
			rev_points[i]=[points[i][0]-left,points[i][1]-top]
		return [(left,top),(width,height)],points,rev_points

class Mouse:
	pos=[0,0]
	buttons=[0,0,0]
	def update(self):
		self.pos=pygame.mouse.get_pos()
		self.buttons=pygame.mouse.get_pressed()

class Player:
	def __init__(self):
		pygame.init()
		self.clock = pygame.time.Clock()
		self.camera=Camera([0,0,0],[0,0,0],SCREEN_DATA)
		self.POLYS=[]
		self.TEX_POLYS=[TexturedPolygon([0,0,10],[0,0,0],5,5,'/home/theturboturnip/Desktop/wall.jpg',parent=Transform([0,0,5],[0,0,0]))]
		self.mouse=Mouse()
	def loop(self):
		while True:
			msElapsed = self.clock.tick(60) 
			deltaTime=msElapsed/1000.0
			self.camera.clear_screen()
			self.keys=pygame.key.get_pressed()
			self.mouse.update()
			self.update()#This is to allow subclasses of the player to affect the world in real time
			for event in pygame.event.get():
				if event.type==pygame.QUIT:
					pygame.quit();sys.exit();
			for p in self.POLYS:
				self.camera.draw_poly(p)
			for p in self.TEX_POLYS:
				self.camera.draw_poly(p.equivalent)
				self.camera.draw_textured_poly(p)
			self.camera.update()
	def update(self):
		pass #This is for subclasses to modify

#p=Player()
#p.loop()




