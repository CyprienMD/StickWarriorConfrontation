# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 16:23:03 2016

@author: test
"""
import math
import pygame
from copy import copy

class Animation :
    pasued = False
    def __init__(self,subject,phases,unit,new=False) :
        self.subject=subject
        self.anim_phases=phases
        self.anim_num=0
        subject.game.all_animations.append(self)
        if new :
            subject.game.temporary_sprites.add(subject)
        self.init_phase()
        self.unit = unit
        self.pause_factor = None
        self.derivatives = []
        #print(self," - Phases are ",phases
    def animate(self):
        if not(self.paused):
            pos=self.subject.getPosition()
            self.subject.setPosition((pos[0]+self.increase_pos[0],pos[1]+self.increase_pos[1]))
            self.subject.size = (int(self.subject.size[0] + self.increase_size[0]), int(self.subject.size[1] + self.increase_size[1]))
            if hasattr(self.subject,"all_effects"): #weird
                assert 1==0
                for effect in self.subject.all_effects:
                    self.subject.all_effects[effect].update()
            if any([s<0 for s in self.subject.size] ) :
                #print("self.subject.size ",self.subject.size
                try :
                    print("ERROR with ",self.subject.name)
                except :
                    print("ERROR with unnamed sprite")
            #print("appel a rotate to ",self.subject.angle,self.increase_rotation
            if self.increase_rotation:
                self.subject.rotate_to(self.subject.angle+self.increase_rotation)
            self.phase_time += 1
            if self.phase_time == self.phase_end_time:
                destination,delay,endsize,effect,endrotation=self.anim_phases[self.anim_num]
                self.subject.setPosition(destination)
                #print("destination:",destination)
                self.anim_num += 1
                #self.subject.posUpdate()
                if self.effect:
                    #print(self, " execute functiun ",self.effect
                    self.effect()
                self.init_phase()

            #self.subject.imageUpdate()
    def init_phase(self):
        if self.anim_num < len(self.anim_phases):
            self.phase_time = 0
            #print("phase ",self.anim_num
            #print("angle:",self.subject.angle
            phase = self.anim_phases[self.anim_num]
            destination,delay,endsize,self.effect,endrotation=phase
            if endsize :
                self.increase_size = ((endsize[0]-self.subject.size[0])/delay,(endsize[1]-self.subject.size[1])/delay)
            else :
                self.increase_size = (0,0)
            if endrotation != None:
                #print("increase_rotation ",endrotation,self.subject.angle,delay
                if (endrotation-self.subject.angle)%360 > 180:
                    self.increase_rotation = ((endrotation-self.subject.angle)%360-360)/delay
                else:
                    self.increase_rotation = (float((endrotation-self.subject.angle)%360))/delay
            else:
                self.increase_rotation = 0
            self.increase_pos = ((destination[0]-self.subject.center_x)/delay,(destination[1]-self.subject.center_y)/delay)
            self.phase_end_time=delay
            #print("angle:",self.subject.angle
        else:
            self.stop()
    
    def pause(self,pause_factor):
        self.paused = True
        self.pause_factor = pause_factor
    
    def run(self):
        self.paused =False
        self.pause_factor = None
            
    def stop(self):
        #print(self, " is stopped "
        while self in self.subject.game.all_animations:
            self.subject.game.all_animations.remove(self)

    def add_derivative(self,anim):
        self.derivatives.append(anim)

class Fade(Animation):
    def __init__(self,subject,phases,unit):
        self.anim_phases=phases
        self.anim_num=0        
        self.unit = unit
        self.subject = subject
        self.time = 0
        subject.game.all_animations.append(self)
        self.init_phase()
        self.pause_factor = None
        self.paused = False
    def animate(self):
        self.subject.alpha += self.alpha_increase
        self.time += 1
        if self.time > self.delay-1:
            self.subject.alpha = self.endfade
            if self.end:
                self.end()
            self.anim_num += 1
            self.init_phase()
        #self.subject.imageUpdate()
    
    def init_phase(self):
        if self.anim_num < len(self.anim_phases):
            self.time = 0
            phase = self.anim_phases[self.anim_num]
            delay,endfade,self.effect=phase
        
            self.alpha_increase = (endfade - self.subject.alpha)/delay
            self.end = self.effect
            self.delay = delay
            self.endfade = endfade
        else:            
            self.stop()

class Size(Animation):
    def __init__(self,subject,phases,unit):
        self.anim_phases=phases
        self.anim_num=0        
        self.unit = unit
        self.subject = subject
        self.time = 0
        subject.game.all_animations.append(self)
        self.init_phase()
        self.pause_factor = None
        
    def animate(self):
        self.subject.size = (int(self.subject.size[0]+self.x_increase), int(self.subject.size[1]+self.y_increase))
        self.time += 1
        if self.time > self.delay-1:
            self.subject.size = self.endsize
            if self.end:
                self.end()
            self.anim_num += 1
            self.init_phase()
        self.subject.imageUpdate()    
    def init_phase(self):
        if self.anim_num < len(self.anim_phases):
            self.time = 0
            phase = self.anim_phases[self.anim_num]
            delay,endsize,self.effect=phase        
            self.x_increase = (endsize[0] - self.subject.size[0])/delay
            self.y_increase = (endsize[1] - self.subject.size[1])/delay
            self.end = self.effect
            self.delay = delay
            self.endsize = endsize
        else:            
            self.stop()

class Rotation(Animation):
    def __init__(self,subject,phases,unit):
        self.anim_phases=phases
        self.anim_num=0        
        self.unit = unit
        self.subject = subject
        self.time = 0
        subject.game.all_animations.append(self)
        self.init_phase()
        self.pause_factor = None
        
    def animate(self):
        self.subject.angle = int(self.subject.angle+self.increase)
        self.time += 1
        if self.time > self.delay-1:
            self.subject.angle = self.endangle
            if self.end:
                self.end()
            self.anim_num += 1
            self.init_phase()
        #self.subject.imageUpdate()

    def init_phase(self):
        if self.anim_num < len(self.anim_phases):
            self.time = 0
            phase = self.anim_phases[self.anim_num]
            delay,endangle,self.effect=phase        
            self.increase = (endangle - self.subject.angle)/delay
            self.end = self.effect
            self.delay = delay
            self.endangle = endangle
        else:            
            self.stop()

class OscilationY(Animation):
    def __init__(self,subject,amplitude,end,unit):
        self.amplitude=amplitude
        self.unit = unit
        self.end = end
        self.subject = subject
        self.base_pos = self.subject.bottom_y
        self.time = 0
        subject.game.all_animations.append(self)
        self.init_oscilation()
        self.pause_factor = None
        self.should_stop = False
        self.added_y = 0
        
    def animate(self):
        self.subject.bottom_y += self.increase_y
        self.added_y  += self.increase_y
        self.increase_y += self.inc_y_evolution
        if self.increase_y>self.base_n or self.increase_y<-self.base_n:
            self.inc_y_evolution *= -1
        if self.should_stop and int(0-self.added_y)<5:
            self.subject.bottom_y -= self.added_y
            self.subject.posUpdate()
            self.end()
            self.stop()
            
        #self.subject.imageUpdate()

    def init_oscilation(self):
        self.base_n = 0
        while True:
            self.base_n += 1
            total = sum([i for i in range(self.base_n)])
            if total>self.amplitude:
                break
        self.increase_y = self.base_n
        self.inc_y_evolution = -1
    
    def shouldStop(self):
        self.should_stop = True
        

class ProjectileAnimation(Animation):
            directional = False
            def __init__(self,unit,end_pos,delay,y_move_up,functiun):
                self.base_pos  =  [unit.center_x,unit.center_y]
                self.end_pos  =  end_pos
                self.paused = True
                self.delay   =  delay
                self.unit = unit
                self.y_move_up  =  y_move_up
                self.distance_y = -(self.base_pos[1]-self.end_pos[1])
                print("distance y is ",self.distance_y)
                self.time = 0
                self.enemy_hit = []
                self.game = self.unit.game
                self.game.all_animations.append(self)
                self.functiun = functiun                
                if self.y_move_up:         
                    self.distance_done = 0#(float(end_pos[0])-self.base_pos[0])/delay * float(delay)/4
                    self.distance_increase = (float(end_pos[0]-self.distance_done*2)-self.base_pos[0])/delay
                    self.distance_x = (end_pos[0]-self.base_pos[0])
                    self.base_movement = (  math.sin(  math.radians(  (self.distance_done*180)  /self.distance_x-90)  )  *self.distance_x)/2
                    self.base_y =  -math.cos(math.radians((self.distance_done*180)  /self.distance_x-90))*self.y_move_up
                    self.add_x = (self.base_movement)/delay
                else:
                    self.distance_done = 0
                    self.distance_x = (end_pos[0]-self.base_pos[0])
                    self.distance_increase = float(self.distance_x)/self.delay
                
                if not(self.distance_x):
                    self.distance_x = 1           
                self.animate()    
                self.pause_factor = None 
                
            def stop(self):
                self.unit.game.all_animations.remove(self)
                if self.unit in self.game.temporary_sprites :
                    self.game.temporary_sprites.remove(self.unit)
                if hasattr(self.unit,"animations") and self in self.unit.animations:
                    self.unit.animations.remove(self)
                    print("\n errUnit has an attribute animations, so anylisis of it to find animation I paused:")
                    b = False
                    for a in self.unit.animations:
                        if a.paused and a.pause_factor == self:
                            a.run()
                            print("Animation ",a," is replaying")
                            b = True
                        elif a.paused:
                            print(a, " is paused but I am not responsible for that")
                            b = True
                        elif a.pause_factor == self:
                            print("error, ",a," is not paused but i am it's pause factor")
                            b = True
                    if not(b):
                        print("-nothing special")
                    
            def animate(self):
                    self.time += 1
                    if self.time> self.delay:
                        self.functiun()
                        self.stop()
                    else:
                        if self.y_move_up:
                            self.distance_done += self.distance_increase
                            angle =   (self.distance_done*180)  /self.distance_x-90       
                            center_x = int(  math.sin(math.radians(angle))*self.distance_x/2  -  self.time*self.add_x + self.base_pos[0]-self.base_movement)
                            center_y = int( -math.cos(math.radians(angle))*self.y_move_up + self.base_pos[1]-self.base_y)+(self.distance_done*self.distance_y)/self.distance_x
                            self.unit.setPosition([center_x,center_y])
                            if self.time == self.delay:
                                print("distance done / x:",self.distance_done,self.distance_x)
                                print("new center y ", center_y)
                                print(angle,int( -math.cos(math.radians(angle))*self.y_move_up),self.base_pos[1],self.base_y,self.distance_y)
                            if self.directional:
                                if self.unit.direction == -1:
                                    self.image = pygame.transform.rotate(self.graphism,angle)
                                else:
                                    self.image = pygame.transform.rotate(self.graphism,360-angle)
                        else:
                            self.distance_done += self.distance_increase
                            center_x = int(self.base_pos[0] + self.distance_done)
                            center_y = self.base_pos[1]+(self.distance_done*self.distance_y)/self.distance_x
                            self.unit.setPosition([center_x,center_y])
                    #self.unit.imageUpdate()
            
                    

class ImageEffect(pygame.sprite.Sprite):
    def __init__(self,pos,image,delay,game,unit=None):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.alpha = 255
        self.image = pygame.image.load(image)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.center_x,self.center_y = pos
        self.size = self.image.get_size()
        self.pos = pos
        self.game = game
        self.delay = delay
        self.unit = unit
        self.phase_time = 0
        self.animations = []
        self.update()
        
    def update(self):
        if self.delay:
            self.phase_time += 1
            if self.phase_time > self.delay-1:
                for a in self.animations:
                    a.stop()
                self.die()
        self.imageUpdate()
        self.posUpdate()
    
    def posUpdate(self):        
        if self.unit:
            self.rect.x = self.center_x -self.size[0]/2
        else:
            self.rect.x = self.center_x + self.game.size[0]/2 - self.game.screen_center_x -self.size[0]/2
        self.rect.y = self.center_y -self.size[1]/2
    
    def die(self):
        if self.unit:
            print(self.unit.image_effects)
            if self in self.unit.image_effects:
                self.unit.image_effects.remove(self)
                print(" i am removed from list")
        if self in self.game.obstacles:
            self.game.obstacles.remove(self)
        print("died")
        self.kill()
        

    def imageUpdate(self):
        if self.alpha != 255:
            self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
        #print("alpha ",self.alpha

class SpriteCopy(pygame.sprite.Sprite):
    def __init__(self,sprite,rect_x_modify,rect_y_modify):
        pygame.sprite.Sprite.__init__(self)
        self.sprite = sprite
        self.image = copy(sprite.image)
        self.rect = self.image.get_rect()
        self.rect.x = self.sprite.rect.x + rect_y_modify
        self.rect.y = self.sprite.rect.y + rect_y_modify
        
class UnitCopy(SpriteCopy):
    def __init__(self,sprite,rect_x_modify,rect_y_modify):
        SpriteCopy.__init__(self,sprite,rect_x_modify,rect_y_modify)
        self.center_x = self.sprite.center_x + rect_x_modify
        self.center_y = self.sprite.center_y + rect_y_modify

class ImageEffectCopy(SpriteCopy):
    pass

class BaseCopy():
    def __init__(self,base,rect_x_modify,rect_y_modify):
        self.base = base
        self.image = copy(base.image)        
        self.pos = [self.base.pos[0]+rect_x_modify,self.base.pos[1]+rect_y_modify]
        self.swift = self.base.swift