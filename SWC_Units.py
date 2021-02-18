# -*- coding: utf-8 -*-
"""
Created on Fri Feb 05 18:48:55 2016

@author: test
"""
"""
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

import pygame
import random
import math
from copy import copy
from types import MethodType
from Animation import Size,Rotation,Animation
#from Animation import ImageEffect,Size,Rotation,OscilationY,Animation
#from CreatureGenerator import dress


from Powers import Charge,NatureSpirit,MagicShield,FireAura,Teleport,PriorityPass,Stun,HeavySword,CourageAura,Heal,ThorianSpeed,Fade,Critical,ArmorDestruction,ManaRegeneration,Heroism,HealingSword,CrowAura,PainDevouration,ManaBloodshed,ManaRageImmunity,MummyInvocation,Dodge,Lightning,SealedKilled,Regeneration,EffectImmunity,OneTry,Slow,Poison,RenegadeSpawn,FireImmunity,PriorityPassZombies #pouvoirs uniquement
from Powers import Seal,SkullBuff,Plague

#class SkullBuff(SkullBuff): pass

RED = (255,0,0)
GREEN = (0,255,0)


    
def is_around(i,ii,length):
    if ii < i -length or ii > i +length:
        return False
    else:
        return True

cost_lvl1 = 150
cost_lvl2 = 260
cost_lvl3 = 500
cost_lvl4 = 630
cost_lvl5 = 1500

all_costs = [0,cost_lvl1,cost_lvl2,cost_lvl3,cost_lvl4,cost_lvl5]

all_cooldowns = [0,30,30,45,80,150]

class Attack():
    damages_on_base = 1.0
    def __init__(self,source,physical_damage,magical_damage,attack_range,at_the_animation_end,attack_type="physical"):
        self.physical_damage,self.magical_damage,self.source,self.attack_range = physical_damage,magical_damage,source,attack_range
        self.animation = source.hitAnimation
        self.projectile = None
        self.projectileMaker = source.makeProjectile
        self.effects = []
        self.functiunEffects = []
        self.damage_type = attack_type
        self.at_the_animation_end = at_the_animation_end
    
    def inflict(self, target=None):
        if target==None: #attaques aux corps à corps
            targeted = self.last_target
        else:
            targeted = target
        if not(self.source.is_dead):
            print("inflict of ",self.source," toward ",targeted)
            print("animation is ",self.animation.__name__)
            targeted.receive(int(self.physical_damage*[1,self.damages_on_base][targeted.__class__.__name__=="Base"]),int(self.magical_damage*[1,self.damages_on_base][targeted.__class__.__name__=="Base"]),self)
            if self.at_the_animation_end and target==None:
                self.source.attacking = False
            for e in self.effects:
                if targeted.hp>0:
                    targeted.new_effect(e,self)
            for e in reversed(self.functiunEffects):
                if True:
                    e(self,targeted)
        #print("Inflict"
    """
    def inflict(self,target):
        target.receive(int(self.physical_damage*[1,self.damages_on_base][target.__class__.__name__=="Base"]),int(self.magical_damage*[1,self.damages_on_base][target.__class__.__name__=="Base"]),self) 
        for e in self.effects:
            if target.hp > 0:
                target.new_effect(e,self)
        for e in reversed(self.functiunEffects):
            if True:
                e(self,target)"""
        
    def shoot(self):
        enemy = self.last_target
        projectile = self.projectileMaker(enemy,self)
        self.source.game.all_battlefield_sprites.add(projectile)
        if self.at_the_animation_end:
            self.source.attacking = False
    
    def end_when_canceled(self):        
        self.source.attacking = False

    def interrupt(self):
        for anim in self.source.animations:
            if hasattr(anim,"anim_phases"):
                def f(anim,tochange=False):
                    changed = False
                    for phase in anim.anim_phases:
                        if phase[-2] in (self.inflict,self.shoot):
                            phase[-2] = self.end_when_canceled
                            changed = True
                    if changed or tochange:
                        anim.anim_num = len(anim.anim_phases)-1
                        anim.init_phase()
                        for a in anim.derivatives:
                            f(a,True)
                f(anim)
        self.source.cooldown = (self.source.game.fps*60/self.source.att_speed) #formule copiée à l'initialisation d'une unité
            


class Unit(pygame.sprite.Sprite):
    upgrades = ["Vitality","Attack","Defence"]
    instance_type = "unit"
    is_a_zombie = False
    targetable = True
    
    def getBonus(fake,enemies,allies,game):
        if any([a.projectile!=None for a in fake.attacks]):
            if len(allies)>0:
                shield = sum([u.hp for u in allies])
                return min([5+ shield/10,30])
            else:
                return -10
        else:
            return 0
        
    def __init__(self,game,player):
        pygame.sprite.Sprite.__init__(self)
        
        self.game = game
        self.player = player
        self.enemies= player.adv.army
        self.allies = player.army
        self.player.army.add(self)
        self.powers = []
        self.attacks = []
        self.effects = []
        self.active_powers = []
        self.image_effects = []
        self.stealth = self.played_this_turn = False
        self.origin = "Recruit"
        self.max_mana = self.mana = 0
        
        self.is_dead = False
        
        self.b3 = 0 #a supprimer
        
        
        if self.player.side=="right":
            self.direction = -1
        else:
            self.direction = 1
        
        self.magic_resistance = 0
        self.magic_power_bonus = 0
        self.alpha = 255
        self.set_parameters()        
        self.max_hp = self.hp
        self.max_range = max([att.attack_range for att in self.attacks])
        self.set_skin()
        self.hit_box = self.get_hit_box() 
        self.big_image = self.get_image()
        #self.graphism = copy(self.big_image)
        
        if self.__class__ in self.player.upgrades.keys():
            for u in self.player.upgrades[self.__class__]:
                u.modify(self)
            
        self.cooldown = self.game.fps*60/self.att_speed # mid way refreshed 
        
        for p in self.powers:
            try:
                p.initialise(self)
            except:
                print("i'm a ",self.__class__.__name__," of ",self.player.side," player ")
                print("My powers are ",self.powers, "and I crashed ")
                p.initialise(self)
        
        self.step_stopped = self.blocked =  self.attacking = False
        self.animations =  []

        self.center_x = self.player.base.pos[0]
        self.bottom_y = 750        
        self.center_y = self.bottom_y - (self.left_leg.size[1]/2) #self.left_leg.center_y-self.size[1]/2-
        
        self.angle = 0
        
        self.imageUpdate()
        #tuple : (width, height, rect.x (from the top left corner of unit), rect.y)
        
        
        self.rect = self.image.get_rect()
        self.posUpdate()
        
        self.initStepAnimation()
    
    def get_hit_box(self):
        width = int(max([self.head.size[0],self.torso.size[0]]))
        height = int(self.torso.rect[1]+self.torso.size[1]*1.5-self.head.rect[1])
    
        return (width,height,int(self.torso.center_x)-width//2,int(self.head.rect[1]))
    
    def set_skin(self):
        
        self.size = self.get_basic_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2
        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_base.png"),(center_x,center_y-30),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_base.png"),(center_x,center_y-80),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_base.png"),(center_x-6,center_y-45),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_base.png"),(center_x+10,center_y-45),20,self)
        self.left_leg = Rib(pygame.image.load("Img/Ribs/leftleg_base.png"),(center_x-5,center_y+5),-15,self)
        self.right_leg = Rib(pygame.image.load("Img/Ribs/rightleg_base.png"),(center_x,center_y+5),25,self)
        
        """
        dress(self)
        #self.head.setSize((60,59))
        self.torso.setSize((60,80))
        self.right_leg.setSize((40,135))
        self.left_leg.setSize((40,135))
        """
        
    def get_image(self):
        
        #center_x,center_y = self.size[0]/2,self.size[1]/2
        image = pygame.Surface(self.size) # pygame.Surface(self.get_basic_size())
        image.fill((255,255,255))
        image.set_colorkey((255,255,255))
        for rib in self.getRibsOrder(): #(self.direction-1)/-2
             image.blit(rib.image,rib.rect)
        for i in self.image_effects:
             image.blit(i.image,i.rect)
        image.convert_alpha()
        if self.direction == -1:
            image = pygame.transform.flip(image,1,0)
        
        self.graphism = image
        return image
    
    def get_basic_image_size(self):
        return self.get_basic_size()
    
    def setSize(self,new_size):
        first_size = self.get_basic_image_size()
        r0,r1 = (new_size[0]/first_size[0],new_size[1]/first_size[1])
        g0,g1 = (new_size[0]/self.size[0],new_size[1]/self.size[1])
        for rib in self.getRibsOrder():
            x,y = rib.getPosition()
            print((x,y),(r0,r1))
            rib.setPosition( ( x*g0 , y*g1) )
            rib.base_center_x = rib.base_center_x*g0
            rib.base_center_y = rib.base_center_y*g1
            wi, hi = rib.big_image.get_size()
            rib.setSize( (int(wi*r0) , int(hi * r1)) )
        self.size = new_size
        self.hit_box = self.get_hit_box() 
        #self.posUpdate() 
        
    
    def blit_on_surface(self,surface):
        d = self.direction
        e = (1-d)//2  #0 if d=1, 1 if d=(-1)
        [w,h] = self.size
        for rib in self.getRibsOrder(): #(self.direction-1)/-2
            image = rib.image
            if d == -1:
                image = pygame.transform.flip(image,1,0)
            surface.blit(image,[[rib.rect[0],w-rib.rect[0]-rib.image.get_size()[0]][e]+self.rect.x,rib.rect[1]+self.rect.y])
        for i in self.image_effects:
            image = rib.image
            if d == -1:
                image = pygame.transform.flip(image,1,0)
            surface.blit(i.image,[[i.rect[0],w-i.rect[0]-i.image.get_size()[0]][e]+self.rect.x,i.rect[0]+self.rect.y])
        
        
    def getAttackChoice(self):
        return self.attacks[0]
    
    def getRibsOrder(self):
        return (self.right_arm,self.right_leg,self.left_leg,self.torso,self.head,self.left_arm)
        
    def hitInitiation(self,enemy):
        pass
    
    def makeProjectile(self):
        pass
    
    def new_effect(self,effect,cause):
        if not(any([eff.__class__ == effect for eff in self.effects]) and effect.cummulable == False) and [eff.__class__ == effect for eff in self.effects].count(True)<effect.max_cummulation:
            self.effects.append(effect(self,cause))
    
    def hit_animation_end(self):
        self.attacking = False
    
    def get_distance(self,sprite):
        return self.direction*(sprite.center_x-self.center_x)-(self.torso.size[0]/2)-(sprite.torso.size[0]/2)
        
    def update(self):
        
        if self.cooldown < (self.game.fps*60/self.att_speed):#formule recopiée dans attack interupt et plus loin 2 fois
            self.cooldown += 1
        
        self.actual_speed = self.speed
        blocked_before = self.blocked
        if not(self.attacking):
            self.blocked = False
            self.attack = self.getAttackChoice()
            for enemy in self.enemies:
                if  self.get_distance(enemy)< self.attack.attack_range and self.center_x*self.direction<enemy.center_x*self.direction:
                    if self.cooldown >= self.game.fps*60/self.att_speed:
                        self.attack.last_target = enemy
                        self.attack.animation(enemy)
                        self.blocked = True
                        print("launched an attack toward ",enemy,", part of my enemies ",self.enemies)
                    else:
                        #condition enlievée: self.get_distance(enemy)< 5
                        if self.center_x*self.direction<enemy.center_x*self.direction and not(self.center_x*self.direction < self.player.base.center_x*self.direction):
                            self.blocked = True
            if not(self.stealth):
                for obstacle in self.game.obstacles:
                    if  self.get_distance(obstacle)< 5  and self.center_x*self.direction<obstacle.center_x*self.direction:
                        self.blocked = True
        else:
            self.blocked = True
         
        if not(self.stealth):          
            for ally in self.allies:
                if ally != self:
                    if not(ally.stealth) and self.get_distance(ally) < 5 and self.center_x*self.direction<ally.center_x*self.direction:
                            self.blocked = True
                    elif not(ally.stealth) and (self.get_distance(ally)+(ally.speed * (1-ally.played_this_turn)))<self.speed*2 and self.center_x*self.direction<ally.center_x*self.direction:
                        if ally.speed<self.speed:
                            self.actual_speed = ally.speed
        
        for p in self.powers+self.image_effects:
            p.update()
        for e in self.effects:
            e.update()


        if not(self.attacking):
            if -(self.center_x*self.direction-self.player.adv.base.pos[0]*self.direction) < self.attack.attack_range+40 and not(any([c.center_x*self.direction>self.center_x*self.direction for c in self.enemies])):
                if self.cooldown >= self.game.fps*60/self.att_speed-1:
                    #print("launched animation agaisnt baase"
                    print("launched an attack toward base")
                    print("animation is ",self.attack.animation.__name__)
                    self.attack.last_target = self.player.adv.base
                    self.attack.animation(self.player.adv.base)
                    self.blocked = True
                
            if self.center_x*self.direction < (self.player.adv.base.pos[0])*self.direction-50:
                if not(self.blocked):
                    self.center_x += self.actual_speed*self.direction
            else:
                self.blocked = True

        if blocked_before == True and self.blocked == False and self.step_stopped:
            #print("Reinitialise step"
            print("new step animation because the previous was interupt")
            self.initStepAnimation()

        #self.imageUpdate()
        self.posUpdate()
        
        self.played_this_turn = True
        
        self.b3 += 1 #a supprimer

    def hitAnimation(self,enemy):
        for member in self.left_arm,self.right_arm:
            member.resetPosition()
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*60)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.7*mod),0,None,angle+170]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
        #print("Animation created"
    
    def initStepAnimation(self):
        
        
        #print("Init a new step animation of ", self
        for member in self.left_leg,self.right_leg:
            member.resetPosition() 
            
        if not(self.blocked) and self.speed > 0:
            semi_delay = int(15*9*self.size[0]/(220 * self.speed))
            pos_x,pos_y = self.left_leg.getPosition()
            angle = self.left_leg.angle
            phase1 = [(pos_x,pos_y),semi_delay,0,None,angle+50]
            phase2 = [(pos_x,pos_y),semi_delay,0,None,angle]
            self.animations.append(Animation(self.left_leg,[phase1,phase2],self))
            
            pos_x,pos_y = self.right_leg.getPosition()
            angle = self.right_leg.angle
            phase1 = [(pos_x,pos_y),semi_delay,0,None,angle-50]
            phase2 = [(pos_x,pos_y),semi_delay,0,self.initStepAnimation,angle]
            self.animations.append(Animation(self.right_leg,[phase1,phase2],self))
            
            self.step_stopped = False
        else:
            self.step_stopped = True
        
    
    def hit(self): #is not used?
        raise "should not be used"
        self.last_target.receive(self.damage,self.magic_damage)
        self.attacking = False
    
    def inflict_damage(self,target):#is not used?
        raise "should not be used"
        target.receive(self.damage,self.magic_damage)
        
    def setPosition(self,pos):
        x,y = pos
        self.center_x = x
        self.center_y = y
        self.bottom_y = y + (self.left_leg.size[1]*0.4+self.left_leg.center_y-self.size[1]/2)
    
    def posUpdate(self):
        self.rect.x = self.center_x - self.size[0]/2 -self.game.screen_center_x + self.game.size[0]/2
        self.center_y = self.bottom_y - (self.left_leg.size[1]*0.4+self.left_leg.center_y-self.size[1]/2)
        #self.center_y = self.bottom_y - ((self.left_leg.size[1]*0.4+self.left_leg.center_y-self.get_basic_size()[1]/2)*self.size[1]/(self.get_basic_size()[1]))
        self.rect.y = self.center_y - self.size[1]/2
        
    def getPosition(self):
        return [self.center_x, self.center_y]
        
    def set_parameters(self):
        self.speed = 9
        self.range = 300
        self.damage = 12
        self.att_speed = 30 #in per minutes
        self.hp = 30
        self.armor = 50# in %
        self.magic_damage = 0
    
    def get_basic_size(self):
        return [220,360]
        
    
    def receive(self,damage,magic_damage,attack):
        assert type(damage)==type(1)
        damage = int(max([((damage)*(100-self.armor))/100+((magic_damage)*(100-self.magic_resistance))/100,1]) )
        self.hp -= damage
        if self.hp<0:
            self.die(attack)
        else:
            self.game.damageEffect(self," -"+str(damage))
            
    def die(self,source,animation=True):
        #print("im fucking dead"
        self.kill()
        self.is_dead = True
        for unit in self.player.adv.army:
            if unit.attacking and unit.last_target == self:
                for attack in unit.attacks:
                    attack.interrupt() #en espèrant sque l'attaque séléctionnée est toujours la bonne
        for a in reversed(self.animations):
                a.stop()
        if self.animations:
            print("Error: ",self.animations)
        for p in self.powers:
            p.death(source)
        self.blocked = True
        if animation:
            self.game.temporary_sprites.add(self)
            self.deathAnimation()
        #self.player.adv.fund += self.game.all_costs[self.level]/2
    
    def rotate_to(self,angle):
        if not( angle-self.angle<15 or angle+360-self.angle<15 or angle-360-self.angle<15):
            print("gros changement d'angle pour ",self.__class__.__name__)
        self.angle = angle%360
        """
        if self.player.side == "left":
            print("appel a rotate to ",angle,self.player.side
        """
        #self.imageUpdate()
        #self.posUpdate()
        
    
    def deathAnimation(self):
        pos_x,pos_y = self.getPosition()
        angle = self.angle
        phase1 = [(pos_x-(self.size[1]/8*self.direction),self.bottom_y+self.size[0]/2),30,0,None,angle+(90*self.direction)]
        phase2 = [(pos_x-(self.size[1]/8*self.direction),self.bottom_y+self.size[0]/2),30,0,self.fadeAway,None]
        self.animations.append(Animation(self,[phase1,phase2],self))
        
        pos_x,pos_y = self.head.getPosition()
        angle = self.head.angle
        phase1 = [(pos_x,pos_y),30,0,None,angle]
        phase2 = [(pos_x,pos_y-40),30,0,None,angle+120]
        self.animations.append(Animation(self.head,[phase1,phase2],self))
    
    
    
    def throwAnimation(self,unit,function):
        self.attacking = True
        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.right_arm.angle
        phase1 = [(pos_x,pos_y),15,0,None,angle+130]
        phase2 = [(pos_x,pos_y),10,0,function,angle]
        phase3 = [(pos_x,pos_y),20,0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.right_arm,[phase1,phase2,phase3],self))
    
    def fadeAway(self):
        #print(self.center_y)
        self.game.all_animations.append(Fade(self,[[50,0,self.get_obliterated]],self))
        #self.game.temporary_sprites.add(self)
    
    def get_obliterated(self):
        self.kill()
        for a in self.animations:
            a.stop()
        
    def imageUpdate(self): #n'est pas vraiment utilisé normalement
        self.image = pygame.transform.scale(self.get_image(),self.size)
        self.image = pygame.transform.rotate(self.image,int(self.angle))
        self.image.set_alpha(self.alpha)
        
        #self.posUpdate() Peut être nécessaire!
    
"""
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""        

class Rib(pygame.sprite.Sprite):
    def __init__(self,image,pos,angle,owner):
        pygame.sprite.Sprite.__init__(self)
        image.convert_alpha()
        self.graphism = image #-> the graphism's size might change, but not its angle
        self.big_image = image #-> the big image can't change
        self.owner = owner
        self.game = owner.game
        self.alpha = 2555
        self.image = copy(image)
        self.img_center_x = self.image.get_size()[0]/2
        self.img_center_y = self.image.get_size()[1]/2
        self.base_angle = self.angle = angle
        self.potential_images = []
        self.base_center_x,self.base_center_y = self.center_x,self.center_y = pos
        self.size = image.get_size()
        self.setSize( ((self.image.get_size()[0]*self.owner.get_basic_size()[0])//self.owner.get_basic_image_size()[0] , (self.image.get_size()[1]*self.owner.get_basic_size()[1])//self.owner.get_basic_image_size()[1] ))

    
    def imageUpdate(self):
        #print("update",self.angle,self.owner.player.side,self.center_y,self.img_center_y,self.image.get_size()
        #self.image = pygame.transform.scale(self.graphism,self.size)
        self.image = pygame.transform.rotate(self.graphism,int(self.angle))
        self.img_center_x = self.image.get_size()[0]/2
        self.img_center_y = self.image.get_size()[1]/2
        self.rect = (self.center_x-self.img_center_x,self.center_y-self.img_center_y)
        if self.alpha!=255:
            self.image.set_alpha(self.alpha)

    def setImage(self,image):
        if type(image) == type("image"):
            self.graphism = pygame.image.load(image)
        else:
            self.graphism = image
        self.graphism.convert_alpha()
        #self.size = self.graphism.get_size()
        self.imageUpdate()
        
    def setPosition(self,pos):
        self.center_x,self.center_y = pos
        #self.rect = (self.center_x -self.size[0]//2,self.center_y -self.size[1]//2)
        self.posUpdate()
        
    def posUpdate(self):
        self.rect = (self.center_x-self.img_center_x,self.center_y-self.img_center_y)
    
    def getPosition(self):
        return (self.center_x,self.center_y)
    
    def resetPosition(self):
        self.rotate_to(self.base_angle)
        self.center_x,self.center_y = self.base_center_x,self.base_center_y
        self.imageUpdate()
    
    def move(self,x,y):
        self.base_center_x,self.base_center_y = self.center_x,self.center_y = self.base_center_x+x,self.base_center_y+y
        self.imageUpdate()
        
    def rotate_to(self,angle):
        self.angle = angle%360
        #print("rotate to angle: ",self.angle
        self.imageUpdate()
    
    def setAngle(self,angle):
        self.base_angle = self.angle = angle%360
        self.imageUpdate()
    
    def setSize(self,size,swift = False):
        if swift:
             raise "error" #should not be used in fact
        if swift:
            self.center_x = int(size[0]*self.center_x/self.size[0])
            self.center_y = int(size[1]*self.center_y/self.size[1])
            self.base_center_x = int(size[0]*self.center_x/self.size[0])
            self.base_center_y = int(size[1]*self.center_y/self.size[1])
        self.img_center_x = (self.img_center_x*size[0])/self.size[0]
        self.img_center_y = (self.img_center_x*size[1])/self.size[1]
        self.size = size
        print("appel de SetSize")
        self.graphism = pygame.transform.scale(self.big_image,size)
        self.imageUpdate()

"""
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""

class Boxman(Unit):
    level = 1
    creator_image = "creator_boxman.png"
    upgrades = ["Vitality","Attack","Defence"]
    description = "A basic unit with no armor and little damage."
    def set_parameters(self):
        self.speed = 9
        #self.range = 80
        #self.damage = 8
        self.att_speed = 30 #in per minutes
        self.hp = 30
        self.armor = 0# in %
        #self.magic_damage = 0
        self.attacks.append(Attack(self,8,0,22,True))
        
    def get_basic_size(self):
        return [220,360]

class Skeleton(Unit):
    level = 1
    creator_image = "creator_skeleton.png"
    upgrades = ["Vitality","Attack","Defence"]
    description = "About the most rubbish unit, the only good point is his great magic resistance."
    def set_parameters(self):
        self.speed = 6
        self.att_speed = 25 #in per minutes
        self.hp = 34
        self.armor = 0# in %
        self.magic_resistance = 70
        
        self.attacks.append(Attack(self,6,0,30,True))

    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_skeleton.png")
        self.left_arm.setImage("Img/Ribs/leftarm_skeleton.png")
        self.torso.setImage("Img/Ribs/torso_skeleton.png")
        self.right_arm.setImage("Img/Ribs/rightarm_skeleton.png")
        self.right_leg.setImage("Img/Ribs/rightleg_skeleton.png")
        self.left_leg.setImage("Img/Ribs/leftleg_skeleton.png")
        self.left_leg.setPosition((self.left_leg.center_x,self.left_leg.center_y))
        self.right_leg.setPosition((self.right_leg.center_x,self.right_leg.center_y))
        self.right_arm.setAngle(30)


class Spearman(Unit):
    level = 1
    creator_image = "creator_spearman.png"
    upgrades = ["Vitality","Attack","Power"]
    description = "A light and quick unit, which charges when created and inflicts more damage on the first strike."
    def getBonus(fake,enemies,allies,game):
        if len(allies)==0:
            return 5
        else:
            return -15
            
    def set_parameters(self):
        self.speed = 9
        #self.range = 80
        #self.damage = 5
        self.att_speed = 20 #in per minutes
        self.hp = 20
        self.armor = 0# in %
        #self.magic_damage = 0
        self.hitAnimation = self.hitChargeAnimation
        self.attacks.append(Attack(self,4,0,150,False))
        
        self.powers.append(Charge(self))

    
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_spearman.png")
        self.left_arm.setImage("Img/Ribs/leftarm_spearman.png")
    
    def initChargeAnimation(self):
        for member in self.left_leg,self.right_leg:
            member.resetPosition()
        print("initialisaztion of a charge movement")
        if not(self.blocked):
            self.left_arm.setAngle(30)
            
            pos_x,pos_y = self.left_leg.getPosition()
            angle = self.left_leg.angle
            phase1 = [(pos_x,pos_y),20,0,None,angle+70]
            phase2 = [(pos_x,pos_y),20,0,None,angle-20]
            self.animations.append(Animation(self.left_leg,[phase1,phase2],self))
            
            pos_x,pos_y = self.right_leg.getPosition()
            angle = self.right_leg.angle
            phase1 = [(pos_x,pos_y),20,0,None,angle-70]
            phase2 = [(pos_x,pos_y),20,0,self.initStepAnimation,angle+20]
            self.animations.append(Animation(self.right_leg,[phase1,phase2],self))
            
            self.step_stopped = False
        else:
            self.step_stopped = True
    
    def hitChargeAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),1,0,self.attack.inflict,None]
        phase2 = [(pos_x,pos_y),int(0.2*mod),0,None,angle+30]
        phase3 = [(pos_x,pos_y),int(0.3*mod),0,self.hit_animation_end,angle]
        animation1 = Animation(self.left_arm,[phase1,phase2,phase3],self)
        self.animations.append(animation1)
        
        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.right_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase2 = [(pos_x,pos_y),int(0.2*mod),0,None,angle+45]
        phase3 = [(pos_x,pos_y),int(0.3*mod),0,None,angle]
        animation2 = Animation(self.right_arm,[phase2,phase3],self)
        self.animations.append(animation2)
        animation1.add_derivative(animation2)
        
    def get_basic_size(self):
        return [350,420]

class Slinger(Unit):
    level = 1
    creator_image = "creator_slinder.png"
    upgrades = ["Vitality","Attack","Range"]
    description = "A fragile archer that has a lot of range but inflicts little damage."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 30 #in per minutes
        self.hp = 15
        self.armor = 0# in %
        self.projectile = Projectile
        
        attack = Attack(self,4,0,450,False)
        attack.projectile = Projectile
        self.attacks.append(attack)
        self.projectile_image = "Img/stone.png"
    def set_skin(self):
        Unit.set_skin(self)
        
        self.right_arm.setImage("Img/Ribs/leftarm_slinger.png")    
     
    def makeProjectile(self,enemy,attack):
        heigth = 0
        for e in self.enemies:
            if e!= enemy and e.center_x*self.direction<enemy.center_x*self.direction and e.center_x*self.direction > self.center_x*self.direction:
                if heigth <  e.size[1]-self.size[1]/2:
                    heigth =  e.size[1]-self.size[1]/2
        for a in self.allies:
            if a!= self and a.center_x*self.direction<enemy.center_x*self.direction and a.center_x*self.direction > self.center_x*self.direction:
                if heigth < a.size[1]-self.size[1]/2:
                    heigth =  a.size[1]-self.size[1]/2
        return self.projectile(self,[self.center_x+20,self.center_y-55],[enemy.center_x,enemy.center_y-30],max([abs(self.center_x-enemy.center_x)//35,1]),heigth,1,attack.inflict,self.projectile_image)
  
    def hitAnimation(self,enemy):
        for member in self.left_arm,self.right_arm:
            member.resetPosition()
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.25*mod),0,None,angle+90]
        phase2 = [(pos_x-40,pos_y),int(0.3*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase4 = [(pos_x,pos_y),int(0.25*mod),0,None,angle]
        a1 = Animation(self.left_arm,[phase1,phase2,phase3,phase4],self)
        self.animations.append(a1)

        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.right_arm.angle
        phase1 = [(pos_x,pos_y),int(0.25*mod),0,None,angle+70]
        phase2 = [(pos_x,pos_y),int(0.4*mod),0,self.attack.shoot,None]
        phase3 = [(pos_x,pos_y),int(0.25*mod),0,self.hit_animation_end,angle]
        a2 = Animation(self.right_arm,[phase1,phase2,phase3],self)
        self.animations.append(a2)
        a2.add_derivative(a1)
        #print("Animation created"

class Dryad(Unit):
    level = 1
    creator_image = "creator_dryad.png"
    upgrades = ["Vitality","Swiftness","Power"]
    description = "One of the nature spirits, with magic attacks. If any one dares killing the dryad, ivy plants will take revenge on the murderer."
    def set_parameters(self):
        self.speed = 12
        self.att_speed = 40 #in per minutes
        self.hp = 12
        self.armor = 0# in %
        self.magic_resistance = 0
        
        self.attacks.append(Attack(self,2,5,30,True))
        self.powers.append(NatureSpirit(self))

    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_dryad.png")
        self.left_arm.setImage("Img/Ribs/leftarm_dryad.png")
        self.torso.setImage("Img/Ribs/torso_dryad.png")
        self.right_arm.setImage("Img/Ribs/rightarm_dryad.png")
        self.right_leg.setImage("Img/Ribs/rightleg_dryad.png")
        self.left_leg.setImage("Img/Ribs/leftleg_dryad.png")
        self.right_leg.setAngle(5)
        self.left_leg.setAngle(-25)

    def initStepAnimation(self):
        #print("Init a new step animation of ", self
        for member in self.left_leg,self.right_leg:
            member.resetPosition()
        if not(self.blocked) and self.speed > 0:
            pos_x,pos_y = self.left_leg.getPosition()
            angle = self.left_leg.angle
            phase1 = [(pos_x,pos_y),20,0,None,angle+30]
            phase2 = [(pos_x,pos_y),20,0,None,angle]
            self.animations.append(Animation(self.left_leg,[phase1,phase2],self))
            
            pos_x,pos_y = self.right_leg.getPosition()
            angle = self.right_leg.angle
            phase1 = [(pos_x,pos_y),20,0,None,angle-30]
            phase2 = [(pos_x,pos_y),20,0,self.initStepAnimation,angle]
            self.animations.append(Animation(self.right_leg,[phase1,phase2],self))
            
            self.step_stopped = False
        else:
            self.step_stopped = True

class Wisp(Unit):
    level = 2
    creator_image = "creator_wisp.png"
    upgrades = ["Vitality","Attack","Power"]
    description = "A magic origin creature, that suffers less magic damage and inflicts magic damage. A significant part of the damage he receives are magicly sent back on the source of the damage."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 40 #in per minutes
        self.hp = 35
        self.armor = 0# in %
        self.magic_resistance = 50
        
        self.attacks.append(Attack(self,2,7,30,True))
        
        self.powers.append(MagicShield(self))
    
    def initStepAnimation(self):
        pass

    def get_hit_box(self):
        h = Unit.get_hit_box(self)
        h= (h[0],h[1]-30,h[2],h[3])
        return h
        
    def set_skin(self):
        self.size = self.get_basic_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_magicfire.png"),(center_x,center_y-20),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_magicfire.png"),(center_x,center_y-70),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_magicfire.png"),(center_x-13,center_y-50),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_magicfire.png"),(center_x+13,center_y-45),20,self)
        self.left_leg = Rib(pygame.image.load("img/empty.png"),(center_x,center_y+20),0,self)
        self.right_leg = Rib(pygame.image.load("img/empty.png"),(center_x,center_y+20),0,self)
    
    def deathAnimation(self):
        self.fadeAway()

class Swordman(Unit):
    level = 2
    creator_image = "creator_swordman.png"
    description = "A warrior with a heavy sword that hits all enemies under it. Nice damage and correct health."
    def getBonus(fake,enemies,allies,game):
        if len(enemies)>1:
            return 5
        else:
            return -3
    def set_parameters(self):
        self.speed = 12
        self.att_speed = 35 #in per minutes
        self.hp = 34
        self.armor = 0# in %
        self.powers.append(HeavySword(self))
        
        self.attacks.append(Attack(self,9,0,30,True))
    def get_basic_size(self):
        return [300,500]
        
    def set_skin(self):
        Unit.set_skin(self)
        
        #self.head.setImage("Img/Ribs/head_goliath.png")
        self.left_arm.setImage("Img/Ribs/leftarm_Swordman.png")

class Bowman(Slinger):
    level = 2
    creator_image = "creator_archer.png"
    upgrades = ["Vitality","Attack","Range"]
    description = "A basic archer, with high range and few health."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 35 #in per minutes
        self.hp = 20
        self.armor = 0# in %
        self.projectile = Projectile
        
        attack = Attack(self,9,0,500,False)
        attack.projectile = Projectile
        self.attacks.append(attack)
        self.projectile_image = "Img/arrow.png"
        
    def set_skin(self):
        Unit.set_skin(self)
        
        self.right_arm.setImage("Img/Ribs/rightarm_archer.png")
        self.torso.setImage("Img/Ribs/torso_archer.png")
        
class ScourgeMan(Unit):
    level = 2
    creator_image = "creator_scourgeman.png"
    upgrades = ["Vitality","Attack","Defence"]
    description = "This soldier has a medium armor and a significant health, and stuns the enemy each 3 attacks."

    def set_parameters(self):
        self.speed = 9
        self.att_speed = 20  #in per minutes
        self.hp = 44
        self.armor = 40# in %
        for i in range(3):
            self.attacks.append(Attack(self,9,0,30,True))
        self.attacks[2].effects.append(Stun)
        self.attack_num = 0
    
    def getAttackChoice(self):        
        return self.attacks[self.attack_num]
    
    def hitAnimation(self,enemy):
        Unit.hitAnimation(self,enemy)
        self.attack_num = (self.attack_num+1)%3
        
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_scourgeman.png")
        self.torso.setImage("Img/Ribs/torso_scourgeman.png")
        self.left_arm.setImage("Img/Ribs/leftarm_scourgeman.png")

class FlagBearer(Unit):
    level = 2
    creator_image = "creator_flagbearer.png"
    upgrades = ["Vitality","Defence","Power"]
    description = "A weak unit which gives important attack bonus to nearby allies."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 30 #in per minutes
        self.hp = 39
        self.armor = 0# in %
        self.attacks.append(Attack(self,6,0,30,True))
        
        self.powers.append(CourageAura(self))
    
    def getBonus(self,ennemies,allies,game):
        allie_power = sum([game.all_costs[u.level]/2. for u in allies])
        return -15+allie_power/20.
    
    def get_basic_size(self):
        return [240,600]
        
    def set_skin(self):
        Unit.set_skin(self)
        self.left_arm.setImage("Img/Ribs/leftarm_flagbearer.png")
        self.right_arm.setImage("Img/Ribs/rightarm_flagbearer.png")
        self.right_arm.setAngle(15)   

class Clerk(Unit):
    level = 2
    creator_image = "creator_healer.png"
    upgrades = ["Defence","Range","Power"]
    description = "A flimsy troup, that heals allies from the distance."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 20 #in per minutes
        self.hp = 25
        self.armor = 0# in %
        self.attacks.append(Attack(self,5,0,30,True))
        
        h = Heal(self)
        self.powers.append(h)
        self.active_powers.append(h)
        
    def set_skin(self):
        Unit.set_skin(self)
        self.left_arm.setImage("Img/Ribs/leftarm_healer.png")
        self.right_arm.setImage("Img/Ribs/rightarm_healer.png")
        self.torso.setImage("Img/Ribs/torso_healer.png")
        self.head.setImage("Img/Ribs/head_healer.png")
    
    
    def makeProjectile(self,allie,power):
        p = power.projectile(self,[self.center_x,self.center_y-120],[allie.center_x,allie.center_y-100],max([abs(self.center_x-allie.center_x)/20,1]),0,1,power.heal,"Img/heal_ball.png",allie) 
        return p
    
    def getBonus(fake,enemies,allies,game):
        if len(allies)==0:
            return -30
        else:
            if len(allies)>1:
                return 5+len(allies)*2
            elif len(allies)==1:
                if allies[0].hp/float(allies[0].max_hp)*100 > 80:
                    return (abs(allies[0].player.base.center_x-allies[0].center_x)<allies[0].hp*10)
                else:
                    return -20

class Mercenary(Unit):
    level = 3
    creator_image = "creator_mercenary.png"
    upgrades = ["Vitality","Attack","Defence"]
    description = "A warrior with heavy damage which dodge the projectiles he receives."
    def getBonus(fake,enemies,allies,game):
        b = 0
        for u in enemies:
            if any([a.projectile!=None for a in u.attacks]):
                b+=5
        b = min([b,15])
        return b
    def set_parameters(self):
        self.speed = 9
        #self.range = 80
        #self.damage = 8
        self.att_speed = 50 #in per minutes
        self.hp = 43
        self.armor = 0# in %
        #self.magic_damage = 0
        attack1 = Attack(self,11,0,30,True)
        attack1.animation =  self.hitAnimation1
        attack2 = Attack(self,11,0,30,True)
        attack2.animation =  self.hitAnimation2
        attack3 = Attack(self,11,0,30,True)
        attack3.animation =  self.hitAnimation3
        self.attacks = [attack1,attack2,attack3]
        self.attack_num = 0
        
        self.powers.append(ThorianSpeed(self))
        self.set_skin = self.set_skin_special        
    def getAttackChoice(self):        
        return self.attacks[self.attack_num]

    def set_skin_special(self):
        Unit.set_skin(self)
        
        self.right_arm.setImage("Img/Ribs/rightarm_mercenary.png")
        self.left_arm.setImage("Img/Ribs/leftarm_mercenary.png")
        self.head.setImage("Img/Ribs/head_mercenary.png")

    def set_skin(self):
        Unit.set_skin(self)        
        self.right_arm.setImage("Img/Ribs/Skins/rightarm_mercenary.png")
        self.left_arm.setImage("Img/Ribs/Skins/leftarm_mercenary.png")
        self.head.setImage("Img/Ribs/Skins/head_mercenary.png")
        self.torso.setImage("Img/Ribs/Skins/torso_mercenary.png")
        self.left_leg.setImage("Img/Ribs/Skins/leftleg_mercenary.png")
        self.right_leg.setImage("Img/Ribs/Skins/rightleg_mercenary.png")
    
    def hitInitiation(self,enemy):
        #print("initiation of attack toward ",enemy
        self.attacking = True
        self.last_target = enemy
        self.cooldown = 0
        self.attack_num += 1
        if self.attack_num > 2:
            self.attack_num = 0        
    
    def hitAnimation1(self,enemy):
        self.hitInitiation(enemy)
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.7*mod),0,None,angle+170]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
    
    def hitAnimation2(self,enemy):
        self.hitInitiation(enemy)
        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.7*mod),0,None,angle+150]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.right_arm,[phase1,phase2,phase3],self))
        
    def hitAnimation3(self,enemy):
        self.hitInitiation(enemy)
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.5*mod),0,None,angle+120]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
        
        print("double attack of attack of animation ",self.attack.animation.__name__)
        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.left_arm.angle
        phase1 = [(pos_x,pos_y),int(0.7*mod),0,None,angle+150]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.right_arm,[phase1,phase2,phase3],self))       
   
    
    
    

class Ghost(Unit):
    level = 3
    creator_image = "creator_ghost.png"
    upgrades = ["Vitality","Attack","Power"]
    description = "A quick and fragile unit with high armor and which dodges most of the attacks he receives."
    def set_parameters(self):
        self.speed = 12
        self.att_speed = 30 #in per minutes
        self.hp = 16
        self.armor = 70# in %
        self.attacks.append(Attack(self,12,0,30,True))
        
        self.powers.append(Dodge(self))
    
    def get_basic_size(self):
        return [240,400]

    def get_hit_box(self):
        h = Unit.get_hit_box(self)
        h= (h[0],h[1]-50,h[2],h[3])
        return h
        
    def set_skin(self):
        self.size = self.get_basic_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_ghost.png"),(center_x,center_y-20),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_ghost.png"),(center_x,center_y-90),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_ghost.png"),(center_x-13,center_y-50),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_ghost.png"),(center_x+13,center_y-45),20,self)
        self.left_leg = Rib(pygame.image.load("img/empty.png"),(center_x,center_y+50),0,self)
        self.right_leg = Rib(pygame.image.load("img/empty.png"),(center_x,center_y+50),0,self)
    
    def deathAnimation(self):
        self.fadeAway()
    
    def initStepAnimation(self):        
        if not(self.blocked):  
            phase1 = [40,100,None]
            phase2 = [40,255,self.initStepAnimation]
            self.animations.append(Fade(self,[phase1,phase2],self))
            self.step_stopped = False
        else:
            self.step_stopped = True
  
class AxeThrower(Slinger):
    level = 3
    creator_image = "creator_axethrower.png"
    description = "This axe thrower will inflicts a big amount of damage at every hit, and may inflicts critical hits on his target, killing it directly if it is low level or inflicting 3 times as much damage."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 20 #in per minutes
        self.hp = 32
        self.armor = 0# in %
        
        self.powers.append(Critical(self))

        att = Attack(self,13,0,600,False)
        self.attacks.append(att)
        self.projectile_image = "Img/axe.png"
        self.projectile = Projectile
    
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_axethrower.png")
        self.torso.setImage("Img/Ribs/torso_axethrower2.png")
        self.left_arm.setImage("Img/Ribs/leftarm_axethrower.png")
        self.left_leg.setImage("Img/Ribs/leftleg_axethrower.png")
        self.right_leg.setImage("Img/Ribs/rightleg_axethrower.png")
        
        self.left_arm.image1 = pygame.image.load("Img/Ribs/leftarm_axethrower.png")
        self.left_arm.image2 = pygame.image.load("Img/Ribs/leftarm_base.png")
        self.left_arm.potential_images = [self.left_arm.image1,self.left_arm.image2]
        
    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        self.cooldown = 0
        self.left_arm.setImage(self.left_arm.image1)
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.5*mod),0,None,angle+170]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,self.throw_axe,angle+100]
        phase3 = [(pos_x,pos_y),int(0.3*mod),0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
    
    def throw_axe(self):
        self.attack.shoot()
        self.left_arm.setImage(self.left_arm.image2)
        #self.imageUpdate()
        
    def makeProjectile(self,enemy,attack):
        heigth = 0
        for e in self.enemies:
            if e!= enemy and e.center_x*self.direction<enemy.center_x*self.direction and e.center_x*self.direction > self.center_x*self.direction:
                if heigth <  e.size[1]-self.size[1]/2:
                    heigth =  e.size[1]-self.size[1]/2
        for a in self.allies:
            if a!= self and a.center_x*self.direction<enemy.center_x*self.direction and a.center_x*self.direction > self.center_x*self.direction:
                if heigth < a.size[1]-self.size[1]/2:
                    heigth =  a.size[1]-self.size[1]/2
        heigth += 80
        p = self.projectile(self,[self.center_x+48,self.center_y-80],[enemy.center_x,enemy.center_y-30],max([abs(self.center_x-enemy.center_x)/15,1]),heigth,1,attack.inflict,self.projectile_image)
        p.directional = False
        def ir(projectile_self):
            p.angle = p.angle%360# + 60
            phase1 = [10,-60,None]
            phase2 = [10,-180,None]
            phase3 = [10,-300,p.initRotation]
            r = Rotation(p,[phase1,phase2,phase3],self)
            self.animations.append(r)
        p.initRotation = MethodType(ir,p)
        p.initRotation()
        return p

class BattleMage(Unit):
    level = 3
    creator_image = "creator_battlemage.png"
    upgrades = ["Defence","Range","Power"]
    description = "A healthy and powerful mage, that can send a magic orb with heavy magical damage and which destroys partly the target's armor."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 20 #in per minutes
        self.hp = 49
        self.armor = 25# in %
        
        attack = Attack(self,0,9,400,False)
        attack.projectile = Projectile        
        self.attacks.append(attack)
        attack.mana_cost = 0
        
        attack = Attack(self,0,18,550,False)
        attack.projectile = Projectile  
        attack.projectileMaker = self.makeProjectile1
        attack.mana_cost = 20
        attack.effects.append(ArmorDestruction)
        self.attacks.append(attack)
        
        self.max_mana = self.mana = 25
        
        self.powers.append(ManaRegeneration(self))
    
    
    def getAttackChoice(self):
        if self.mana >= self.attacks[1].mana_cost:
            return self.attacks[1]
        else:
            return self.attacks[0]
        
    def set_skin(self):
        Unit.set_skin(self)
        
        self.right_arm.setImage("Img/Ribs/rightarm_battlemage.png")
        self.left_arm.setImage("Img/Ribs/leftarm_battlemage.png")
        self.head.setImage("Img/Ribs/head_battlemage.png")
    
    def makeProjectile(self,enemy,attack):
        return attack.projectile(self,[self.center_x,self.center_y-120],[enemy.center_x,enemy.center_y-50],max([abs(self.center_x-enemy.center_x)/20,1]),0,1,attack.inflict,"Img/magic_ball.png") 
    
    def makeProjectile1(self,enemy,attack):
        self.mana -= attack.mana_cost
        projectile = attack.projectile(self,[self.center_x,self.center_y-120],[enemy.center_x,enemy.center_y-50],max([abs(self.center_x-enemy.center_x)/5,1]),0,1,attack.inflict,"Img/magic_ball1.png",size=[10,10]) 
        phase1 = [max([abs(self.center_x-enemy.center_x)/5,1]),[100,100],None]
        self.animations.append(Size(projectile,[phase1],self))
        return projectile

    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        mod = float(self.game.fps*90)/self.att_speed
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        phase1 = [(pos_x,pos_y),int(0.3*mod),0,None,angle+170]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,angle+190]
        phase2_1 = [(pos_x,pos_y),int(0.1*mod),0,None,angle+150]
        phase2_2 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.shoot,angle+170]
        phase3 = [(pos_x,pos_y),int(0.3*mod),0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase2_1,phase2_2,phase3],self))

class HighMage(Unit):
    level = 3
    creator_image = "creator_highmage.png"
    upgrades = ["Vitality","Range","Power"]
    description = "This flimsy but destructive mage, that can create a projectile which will go through enemies and harm multiple targets."

    def set_parameters(self):
        self.speed = 9
        self.damage = 0
        self.att_speed = 45 #in per minutes
        self.hp = 29
        self.armor = 0# in %
        
        attack = Attack(self,0,6,400,False)
        attack.projectile = Projectile        
        attack.mana_cost = 0
        self.attacks.append(attack)
        
        attack = Attack(self,0,13,300,False)
        attack.projectile = Projectile
        attack.projectileMaker = self.makeProjectile2
        attack.mana_cost = 30
        attack.damages_on_base = 0.25
        self.attacks.append(attack)
        
        self.powers.append(ManaRegeneration(self))
        
        self.max_mana = self.mana = 60
    
    def get_basic_size(self):
        return [280,390]
    
    def getAttackChoice(self):
        if self.mana >= self.attacks[1].mana_cost:
            return self.attacks[1]
        else:
            return self.attacks[0]

    def set_skin(self):
        Unit.set_skin(self)
        
        self.right_arm.setImage("Img/Ribs/rightarm_highmage.png")
        self.left_arm.setImage("Img/Ribs/leftarm_highmage.png")
        self.head.setImage("Img/Ribs/head_highmage.png")
    
    def makeProjectile(self,enemy,attack):
        return attack.projectile(self,[self.center_x-50,self.center_y-200],[enemy.center_x,enemy.center_y-70],max([abs(self.center_x-enemy.center_x)/20,1]),0,1,attack.inflict,"Img/magic_shot.png") 
    
    def makeProjectile2(self,enemy,attack):
        self.mana -= self.attacks[1].mana_cost
        return attack.projectile(self,[self.center_x-50,self.center_y-200],[enemy.center_x+50*self.direction,enemy.center_y-120],max([abs(self.center_x-enemy.center_x)/20,1]),0,2,attack.inflict,"Img/magic_shot2.png") 

    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.35*mod),0,None,angle+170]
        phase2 = [(pos_x,pos_y),int(0.2*mod),0,self.attack.shoot,angle+170]
        phase3 = [(pos_x,pos_y),int(0.35*mod),0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
        

class Ranger(Slinger):
    level = 4
    creator_image = "creator_ranger.png"
    upgrades = ["Vitality","Attack","Range"]
    description = "A powerful archer, with poisonned arrows that will slow the enemy then poison him, and he will then finish them with his dangerous knife."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 30 #in per minutes
        self.hp = 40
        self.armor = 0# in %
        self.projectile = Projectile
        
        attack = Attack(self,7,0,600,False)
        attack.projectile = Projectile
        attack1 = Attack(self,7,0,600,False)
        attack1.projectile = Projectile
        attack2 = Attack(self,13,0,30,True)
        attack2.projectile = Projectile
        self.attacks.append(attack)
        attack.effects.append(Slow)
        self.attacks.append(attack1)
        attack1.effects.append(Poison)
        self.attacks.append(attack2)    
        attack2.animation = MethodType(Unit.hitAnimation,self)
        
        self.projectile_image = "Img/arrow.png"
    
    def getAttackChoice(self):
        slowed = False
        poisoned = False
        enemy = None
        for enemy in self.enemies:
                if abs(self.center_x+(self.size[0]/8)*self.direction-enemy.center_x-(enemy.size[0]/8)*enemy.direction) < self.attacks[0].attack_range:
                    for p in enemy.effects:
                        if p.__class__ == Slow:
                            slowed = True
                        if p.__class__ == Poison:
                            poisoned = True
                    break
        if enemy:
            if not(slowed) and abs(enemy.center_x-self.center_x)>200 and not(any([a.attack_range>150 for a in enemy.attacks])):
                return self.attacks[0]
            elif not(poisoned):
                return self.attacks[1]
        else:
            if  -(self.center_x*self.direction-self.player.adv.base.pos[0]*self.direction) < self.attacks[2].attack_range+40:
                return self.attacks[2]
            elif -(self.center_x*self.direction-self.player.adv.base.pos[0]*self.direction) < self.attacks[0].attack_range+40:
                return self.attacks[0]
            
                    
        return self.attacks[2]
        """  
    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),10,0,None,angle+90]
        phase2 = [(pos_x-40,pos_y),10,0,None,None]
        phase3 = [(pos_x,pos_y),3,0,None,None]
        phase4 = [(pos_x,pos_y),10,0,None,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3,phase4],self))

        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.right_arm.angle
        phase1 = [(pos_x,pos_y),10,0,None,angle+70]
        phase2 = [(pos_x,pos_y),13,0,self.attack.shoot,None]
        phase3 = [(pos_x,pos_y),10,0,None,angle]
        self.animations.append(Animation(self.right_arm,[phase1,phase2,phase3],self))
        #print("Animation created"
    """

    def set_skin(self):
        Unit.set_skin(self)
        
        self.right_arm.setImage("Img/Ribs/rightarm_ranger.png")
        self.left_arm.setImage("Img/Ribs/leftarm_assassin.png")
        self.torso.setImage("Img/Ribs/torso_assassin.png")

class Goliath(Unit):
    level = 4
    creator_image = "creator_goliath.png"
    upgrades = ["Vitality","Attack","Defence"]
    description = "A high armored tank, with a slow and powerful physical attack."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 20 #in per minutes
        self.hp = 50
        self.armor = 65# in %
        
        self.attacks.append(Attack(self,22,0,30,True))
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_goliath.png")
        self.torso.setImage("Img/Ribs/torso_goliath.png")
        self.left_arm.setImage("Img/Ribs/leftarm_goliath.png")
        self.right_arm.setImage("Img/Ribs/rightarm_goliath.png")
        self.left_leg.setImage("Img/Ribs/leftleg_goliath.png")
        self.right_leg.setImage("Img/Ribs/rightleg_goliath.png")  

class FireElementary(Unit):
    level = 4
    creator_image = "creator_elementary.png"
    upgrades = ["Vitality","Defence","Power"]
    description = "This imposant fire golem (thus with magic resistance) frequently inflicts magical damage to anyone around him, enemy or ally. Cool. The bad point is that the golem is unstable so its hit points are continuously consumed."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 15 #in per minutes
        self.hp = 75
        self.armor = 25# in %
        self.magic_resistance = 25
        
        self.attacks.append(Attack(self,0,18,30,False))
        
        self.powers.append(FireAura(self))
        self.powers.append(FireImmunity(self))
    
    def get_basic_size(self):
        return [300,600]
    
    def get_hit_box(self):
        h = Unit.get_hit_box(self)
        return (h[0],h[1]-100,h[2],h[3]-50)
    
    def set_skin(self):
        self.size = self.get_basic_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2        
        self.torso = Rib(pygame.image.load("Img/SpecialRibs/torso_elementary.png"),(center_x,center_y-80),0,self)
        self.head = Rib(pygame.image.load("img/empty.png"),(center_x,center_y-140),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_elementary.png"),(center_x-40,center_y-140),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_elementary.png"),(center_x+30,center_y-130),20,self)
        self.left_leg = Rib(pygame.image.load("img/empty.png"),(center_x,center_y+50),0,self)
        self.right_leg = Rib(pygame.image.load("img/empty.png"),(center_x,center_y+50),0,self)
    
    def initStepAnimation(self):
        pass
    
    def deathAnimation(self):
        angle = self.angle
        phase1 = ((self.center_x,self.center_y +600),100,0,self.get_obliterated,angle)
        self.animations.append(Animation(self,[phase1],self))
        
    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle+100]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.2*mod),0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
    
    def getBonus(fake,enemies,allies,game):
        return (len(enemies)>3)*20 - (len(allies))*10 - (enemies[0].center_x - enemies[0].player.base.center_x < 600)*5

class Assassin(Unit):
    level = 4
    creator_image = "creator_assassin.png"
    upgrades = ["Vitality","Attack","Power"]
    description = "A unit which doesn't seem really scary until it teleports on the weakest enemy to slay it with one strike. Ouch..."
    def getBonus(fake,enemies,allies,game):
        if enemies:
            bonus = 0
            power = fake.powers[0]
            if power.__class__.__name__ != "Teleport":
                print("ERROR: expected teleport power and got ",power.__class__.__name__," instead")
                return 0
            else:
                bonus = [u.hp<=fake.attacks[0].physical_damage*power.multiplicator+power.aditional for u in enemies].count(True)
                print(bonus," targets can be oneshot")
                bonus *= 5
                
                direct = enemies[0].direction
                closest = [None,-200000000*direct]
                for u in enemies:
                    if u.center_x*direct > closest[1]*direct:
                        closest = [u,u.center_x]
                print("the closest is ",closest[0],"(",closest[1],"), and he have ",closest[0].hp," hp"   )             
                if closest[0].hp > 80 and bonus >9:
                    print("bonus is even higher because of a big fat guy protecting his minions")
                    bonus += 8
                return bonus
        else:
            return 0
            
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 50 #in per minutes
        self.hp = 35
        self.armor = 0# in %
        self.magic_damage = 0
        self.powers.append(Teleport(self))
        self.powers.append(ThorianSpeed(self))
        
        self.attacks.append(Attack(self,10,0,30,True))
        
    def set_skin(self):
        Unit.set_skin(self)
        
        self.left_arm.setImage("Img/Ribs/leftarm_assassin.png")
        self.torso.setImage("Img/Ribs/torso_assassin.png")
        self.head.setImage("Img/Ribs/head_assassin.png")
        """
    
    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),15,0,None,angle+170]
        phase2 = [(pos_x,pos_y),3,0,None,None]
        phase3 = [(pos_x,pos_y),3,0,self.attack.inflict,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
        """
        
    def hitChargeAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        self.cooldown = 0
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        phase1 = [(pos_x,pos_y),1,0,self.attack.inflict,None]
        self.animations.append(Animation(self.left_arm,[phase1],self))
    

class Troll(Unit):
    level = 4
    creator_image = "creator_troll.png"
    upgrades = ["Defence","Vitality","Attack"]
    description = "A really big unit with that much lifes added to a powerful regeneration? The perfect tank. But quite harmless, except followed by archers..."
    def set_parameters(self):
        self.speed = 6
        self.att_speed = 15 #in per minutes
        self.hp = 110
        self.armor = 0# in %
        self.powers.append(Regeneration(self))
        
        self.attacks.append(Attack(self,9,0,30,True))
    
    
    def get_basic_size(self):
        return [330,520]
    
    def set_skin(self):
        self.size = self.get_basic_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_troll.png"),(center_x,center_y-30),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_troll.png"),(center_x,center_y-100),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_troll.png"),(center_x-20,center_y-70),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_troll.png"),(center_x+20,center_y-65),20,self)
        self.left_leg = Rib(pygame.image.load("Img/Ribs/leftleg_troll.png"),(center_x-10,center_y+10),-20,self)
        self.right_leg = Rib(pygame.image.load("Img/Ribs/rightleg_troll.png"),(center_x+10,center_y+10),20,self)

class Valkyrie(Unit):
    level = 4
    creator_image = "creator_valkyrie.png"
    upgrades = ["Vitality","Attack","Power"]
    description = "A winged warrior, fast, armored, both magic and physical damage, heals itself with it's sword and becomes extremely resistant when it is close to death. Better in your army than his..."
    def set_parameters(self):
        self.speed = 12
        self.range = 80
        self.damage = 8
        self.att_speed = 20 #in per minutes
        self.hp = 45
        self.armor = 40# in %
        self.magic_damage = 5
        
        self.attacks.append(Attack(self,10,6,30,True))
        
        self.powers.append(Heroism(self))
        self.powers.append(HealingSword(self))
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_valkyrie.png")
        self.torso.setImage("Img/Ribs/torso_valkyrie.png")
        self.left_arm.setImage("Img/Ribs/leftarm_valkyrie.png")
        self.left_arm.move(8,0)

class Titan(Unit):
    level = 5
    creator_image = "creator_titan.png"
    upgrades = ["Defence","Attack","Power"]
    description = "A colossal but slow soldier, with heavy armor which send lightning when hitting, which inflicts enormous zone damage, both physical and magic."
    def set_parameters(self):
        self.speed = 3
        self.att_speed = 15 #in per minutes
        self.hp = 140
        self.armor = 50# in %
        self.attacks.append(Attack(self,13,25,50,True))
        
        self.powers.append(Lightning(self))
    
    def get_basic_size(self):
        return [350,550]
    
    def set_skin(self):       
        self.size = self.get_basic_size()      
        center_x,center_y = self.size[0]/2,self.size[1]/2        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_titan.png"),(center_x,center_y-60),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_titan.png"),(center_x,center_y-160),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_titan.png"),(center_x-15,center_y-95),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_titan.png"),(center_x+20,center_y-95),20,self)
        self.left_leg = Rib(pygame.image.load("Img/Ribs/leftleg_titan.png"),(center_x-10,center_y+10),-15,self)
        self.right_leg = Rib(pygame.image.load("Img/Ribs/rightleg_titan.png"),(center_x,center_y+10),25,self)
    
    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.left_arm.getPosition()
        size_x,size_y = self.left_arm.size
        angle = self.left_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.6*mod),0,None,angle+170]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.left_arm,[phase1,phase2,phase3],self))
        #print("Animation created"

class Butcher(Unit):
    level = 5
    creator_image = "creator_butcher.png"
    upgrades = ["Vitality","Attack","Power"]
    description = "A terrifying killing machine, with a quick attack and damage that increases when hitting the same target more than once, until it burns it. When burning, they have no chances to survive."
    def getBonus(fake,enemies,allies,game):
        if enemies:
            hp_mean = sum([u.hp for u in enemies])/len(enemies)
            direct = enemies[0].direction
            closest = [None,-200000000*direct]
            for u in enemies:
                if u.center_x*direct > closest[1]*direct:
                    closest = [u,u.center_x]
            print("the closest is ",closest[0],"(",closest[1],"), and he have ",closest[0].hp," hp")
            print("the hp mean is ",hp_mean)
            if closest[0].hp > 80 or hp_mean > 50:
                return 10
            else:
                return 0
        else:
            return 0
                    
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 60 #in per minutes
        self.hp = 96
        self.armor = 20# in %
        self.magic_resistance = 20
        
        attack = Attack(self,15,0,30,True)
        attack.effects.append(Seal)        
        self.attacks.append(attack)
        self.animation_num = 0
        
        self.powers.append(SealedKilled(self))
        self.powers.append(PriorityPass(self))
    
    def get_basic_size(self):
        return [400,500]
    
    def get_hit_box(self):
        h = Unit.get_hit_box(self)
        h= (70,h[1]-100,h[2],h[3]+80)
        return h
        
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_butcher.png")
        self.left_arm.setImage("Img/Ribs/leftarm_butcher.png")
        self.right_arm.setImage("Img/Ribs/rightarm_butcher.png")
        self.left_leg.setImage("Img/Ribs/leftleg_butcher.png")
        self.right_leg.setImage("Img/Ribs/rightleg_butcher.png")
        self.torso.setImage("Img/Ribs/torso_butcher.png")
        
        self.action_arm = self.left_arm
        
    
    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        self.cooldown = 0
        self.animation_num = (self.animation_num+1)%3
        self.action_arm = {self.left_arm:self.right_arm,self.right_arm:self.left_arm}[self.action_arm]
        [self.hitAnimation1,self.hitAnimation2,self.hitAnimation3][self.animation_num](enemy)
    
    def hitAnimation1(self,enemy):
        pos_x,pos_y = self.action_arm.getPosition()
        size_x,size_y = self.action_arm.size
        angle = self.action_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.3*mod),0,None,angle-130]
        phase2 = [(pos_x,pos_y),int(mod*0.3),0,None,angle-240]
        phase3 = [(pos_x,pos_y),int(0.3*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.action_arm,[phase1,phase2,phase3],self))
    
    def hitAnimation2(self,enemy):
        pos_x,pos_y = self.action_arm.getPosition()
        size_x,size_y = self.action_arm.size
        angle = self.action_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle+100]
        phase3 = [(pos_x,pos_y),int(0.8*mod),0,None,angle]
        self.animations.append(Animation(self.action_arm,[phase1,phase3],self))
    
    def hitAnimation3(self,enemy):
        pos_x,pos_y = self.action_arm.getPosition()
        size_x,size_y = self.action_arm.size
        angle = self.action_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.7*mod),0,None,angle+170]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.inflict,angle]
        self.animations.append(Animation(self.action_arm,[phase1,phase2,phase3],self))


class SkeletonLord(Unit):
    level = 5
    creator_image = "creator_skeletonlord.png"
    upgrades = ["Power","Attack","Defence"]
    description = "A great skeleton warrior resistant to magic and immune to most effects. His victims will come back from the dead and serve the skeleton lord as lifeless zombies."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 35 #in per minutes
        self.hp = 85
        self.armor = 50# in %
        self.magic_resistance = 70
        self.attacks.append(Attack(self,17,0,30,True))
        
        self.powers.append(RenegadeSpawn(self))
        self.powers.append(EffectImmunity(self))
        self.powers.append(PriorityPassZombies(self))
        
    def get_basic_size(self):
        return [400,600]
    
    def set_skin(self):        
        self.size = self.get_basic_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2
        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_skeletonlord.png"),(center_x,center_y-40),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_skeletonlord.png"),(center_x,center_y-105),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_skeletonlord.png"),(center_x-16,center_y-60),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_skeletonlord.png"),(center_x+12,center_y-60),20,self)
        self.left_leg = Rib(pygame.image.load("Img/Ribs/leftleg_skeletonlord.png"),(center_x-7,center_y+7),-15,self)
        self.right_leg = Rib(pygame.image.load("Img/Ribs/rightleg_skeletonlord.png"),(center_x,center_y+7),25,self)
        
class CrowLord(Unit):
    level = 5
    creator_image = "creator_crowlord.png"
    upgrades = ["Defence","Attack","Power"]
    description = "This dark melee warrior feeds himself of the others pain. When anyone on the map receives damage, he grows even more and earns health and attack. When he finally comes to fights, his crow aura will slow and weaken the nearbie enemies. Creepy..."
    def set_parameters(self):
        self.speed = 9
        self.att_speed = 30 #in per minutes
        self.hp = 58
        self.armor = 0# in %
        
        self.powers.append(PainDevouration(self))
        self.powers.append(CrowAura(self))
        
        self.attacks.append(Attack(self,7,0,30,True))

    def get_basic_size(self): #taille que doit faire l'unité
        #return [2080,2800]
        return [600,856]

    def get_basic_image_size(self): # doit renvoyer la taille obtenue sans redimensionnement des Ribs
        return [2080,2800]
        #return [600,856]
    
    def getRibsOrder(self):
        return (self.mantle,self.right_arm,self.right_leg,self.left_leg,self.torso,self.head,self.left_arm)
        
    def set_skin(self):
        
        self.size = self.get_basic_image_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2
        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_crowlord.png"),(center_x,center_y-26),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_crowlord.png"),(center_x,center_y-190),0,self)
        self.mantle = Rib(pygame.image.load("Img/Ribs/mantle_crowlord.png"),(center_x,center_y+25),0,self)
        #self.top = Rib(pygame.image.load("Img/Ribs/top_crowlord.png"),(center_x,center_y-35),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm1_crowlord.png"),(center_x-45,center_y-80),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_crowlord.png"),(center_x+35,center_y-90),20,self)
        self.left_leg = Rib(pygame.image.load("Img/Ribs/leftleg_crowlord.png"),(center_x-15,center_y+146),-15,self)
        self.right_leg = Rib(pygame.image.load("Img/Ribs/rightleg_crowlord.png"),(center_x,center_y+146),25,self)
    
        self.setSize([600,865])
        for i in range(120):
            self.setSize([600+i,865+i])
    
    def getBonus(fake,enemies,allies,game):
        return (len(allies)-4)*8


class Purifier(Slinger):
    level = 5    
    creator_image = "creator_purifier.png"
    upgrades = ["Vitality","Range","Power"]
    description = "A magic controlling destroyer, which can slow it enemies with spells making mummies, until it's mana reaches maximum. He will then enter in a fury mode and destroys everything in front of him. Truly everything."
    def set_parameters(self):
        self.speed = 9
        self.damage = 0
        self.att_speed = 25 #in per minutes
        self.hp = 59
        self.armor = 0# in %
        
        attack = Attack(self,0,17,700,False)
        attack.projectile = Projectile        
        attack.projectile_image = "Img/magic_shot.png"
        attack.hitAnimationManaRage = self.hitAnimationManaRage
        self.attacks.append(attack)        
        
        attack = Attack(self,0,12,700,False)
        attack.projectile = Projectile
        attack.projectileMaker = self.makeProjectileSummon
        attack.projectile_image = "Img/sun_disk.png"
        attack.animation = self.summonAnimation
        attack.effects.append(Slow)
        self.attacks.append(attack)
        
        self.powers.append(ManaBloodshed(self))
        self.powers.append(ManaRageImmunity(self))
        self.powers.append(MummyInvocation(self,attack))
        
        self.max_mana = 60
        self.mana = 0
        self.mummy_number = 0
        
    def getAttackChoice(self):
        if self.attacks[1].projectile == UnalterableProjectile or self.mummy_number>1:
            return self.attacks[0]
        else:
            enemy_unit = None
            for enemy in self.enemies:
                    if abs(self.center_x+(self.size[0]/8)*self.direction-enemy.center_x-(enemy.size[0]/8)*enemy.direction) < self.attacks[0].attack_range:
                        if not(enemy_unit) or abs(enemy.center_x-self.center_x)<abs(enemy_unit.center_x-self.center_x):
                            enemy_unit = enemy
            if enemy_unit:
                if abs(enemy_unit.center_x-self.center_x)>200:
                    return self.attacks[1]
                else:
                    return self.attacks[0]
            return self.attacks[1]
        
    def hitAnimation(self,enemy):
        for member in self.left_arm,self.right_arm:
            member.resetPosition()
        self.attacking = True
        self.last_target = enemy
        self.cooldown = 0
        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.right_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.5*mod),0,None,angle+80]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.shoot,None]
        phase3 = [(pos_x,pos_y),int(0.3*mod),0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.right_arm,[phase1,phase2,phase3],self))
        
    def summonAnimation(self,enemy):
        for member in self.left_arm,self.right_arm:
            member.resetPosition()
        self.attacking = True
        self.last_target = enemy
        self.cooldown = 0
        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.right_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.3*mod),0,None,angle+40]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
        phase3 = [(pos_x,pos_y),int(0.3*mod),0,self.attack.shoot,angle-30]        
        phase4 = [(pos_x,pos_y),int(0.15*mod),0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.right_arm,[phase1,phase2,phase3,phase4],self))
    
    
    def hitAnimationManaRage(self,enemy):
        for member in self.left_arm,self.right_arm:
            member.resetPosition()
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.right_arm.getPosition()
        size_x,size_y = self.right_arm.size
        angle = self.right_arm.angle
        mod = float(self.game.fps*90)/self.att_speed
        phase1 = [(pos_x,pos_y),int(0.3*mod),0,None,angle+40]
        phase2 = [(pos_x,pos_y),int(0.1*mod),0,self.attack.shoot,None]
        phase3 = [(pos_x,pos_y),int(0.2*mod),0,self.hit_animation_end,angle]
        self.animations.append(Animation(self.right_arm,[phase1,phase2,phase3],self))
    
    def getRibsOrder(self):
        return (self.right_arm,self.wand,self.right_leg,self.left_leg,self.torso,self.left_arm,self.head)
    
    def get_basic_size(self):
        return [280,550]
    
    def update(self):
        Unit.update(self)
        self.wand.setPosition([self.right_arm.center_x+math.sin(math.radians(self.right_arm.angle))*92,self.right_arm.center_y+math.cos(math.radians(self.right_arm.angle))*92-10])
        self.wand.imageUpdate()
    
    def set_skin(self):
        
        self.size = self.get_basic_size()
        
        center_x,center_y = self.size[0]/2,self.size[1]/2
        
        self.torso = Rib(pygame.image.load("Img/Ribs/torso_purifier.png"),(center_x,center_y-30),0,self)
        self.head = Rib(pygame.image.load("Img/Ribs/head_purifier.png"),(center_x,center_y-80),0,self)
        self.left_arm = Rib(pygame.image.load("Img/Ribs/leftarm_purifier.png"),(center_x-12,center_y-45),0,self)
        self.right_arm = Rib(pygame.image.load("Img/Ribs/rightarm_purifier.png"),(center_x+10,center_y-45),80,self)
        self.left_leg = Rib(pygame.image.load("Img/Ribs/leftleg_purifier.png"),(center_x-5,center_y+5),-15,self)
        self.right_leg = Rib(pygame.image.load("Img/Ribs/rightleg_purifier.png"),(center_x,center_y+5),25,self)
        self.wand = Rib(pygame.image.load("Img/Ribs/wand_purifier_blue.png"),(center_x+10+86,center_y-45+31+70),0,self)

    def beginManaRageMode(self):
        self.wand.setImage("Img/Ribs/wand_purifier_red.png")
    
    def endManaRageMode(self):
        self.wand.setImage("Img/Ribs/wand_purifier_blue.png")
        
    def makeProjectile(self,enemy,attack):
        return attack.projectile(self,[self.center_x-50*self.direction,self.center_y-250],[enemy.center_x,enemy.center_y-70],max([abs(self.center_x-enemy.center_x)/20,1]),0,1,attack.inflict,attack.projectile_image) 
    
    def makeProjectileSummon(self,enemy,attack):
        return attack.projectile(self,[self.center_x-50*self.direction,self.center_y-250],[enemy.center_x,enemy.center_y-70],10,0,1,attack.inflict,attack.projectile_image) 

class Mummy(Unit):
    level = 1 # normally unused
    creator_image = "creator_skeleton.png" # normally unused
    upgrades = ["Vitality","Attack","Defence"] # normally unused
    description = "Basic and weak soldier created by a purifier."
    def set_parameters(self):
        self.speed = 6
        self.att_speed = 20 #in per minutes
        self.hp = 18
        self.armor = 0# in %
        self.magic_resistance = 0
        
        self.attacks.append(Attack(self,6,0,30,True))
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_mummy.png")
        self.left_arm.setImage("Img/Ribs/leftarm_mummy.png")
        self.torso.setImage("Img/Ribs/torso_mummy.png")
        self.right_arm.setImage("Img/Ribs/rightarm_mummy.png")
        self.right_leg.setImage("Img/Ribs/rightleg_mummy.png")
        self.left_leg.setImage("Img/Ribs/leftleg_mummy.png")   
    


class GhostSpearman(Spearman):
    def set_parameters(self):
        self.speed = 16
        self.att_speed = 40
        self.hp = 1
        self.armor = 0# in %
        self.stealth = True
        self.alpha = 50
        self.hitAnimation = self.hitChargeAnimation
        self.attacks.append(Attack(self,0,70,30,False))
        
        self.powers.append(OneTry(self))
        
    def set_skin(self):
        Unit.set_skin(self)
        
        self.head.setImage("Img/Ribs/head_ghostcharger.png")
        self.torso.setImage("Img/Ribs/torso_ghostcharger.png")
        self.left_arm.setImage("Img/Ribs/leftarm_ghostcharger.png")
        self.right_arm.setImage("Img/Ribs/rightarm_ghostcharger.png")
        self.left_leg.setImage("Img/Ribs/leftleg_ghostcharger.png")
        self.right_leg.setImage("Img/Ribs/rightleg_ghostcharger.png")
    
    def deathAnimation(self):
        self.game.all_animations.append(Fade(self,[[10,0,self.get_obliterated]],self))
        self.game.temporary_sprites.add(self)


class Ninja(Butcher):
    level = 1
    creator_image = "creator_assassin.png"
    upgrades = ["Vitality","Attack","Power"]
    description = "What could I say about it, except that it is SO OP."
    def set_skin(self):
        Unit.set_skin(self)        
        self.action_arm = self.left_arm  
        self.head.setImage("Img/Ribs/head_ninja.png")
                    
    def set_parameters(self):
        self.speed = 12
        self.att_speed = 80 #in per minutes
        self.hp = 15
        self.armor = 0# in %
        self.magic_resistance = 0
        
        attack = Attack(self,7,0,30,True)
        attack.effects.append(Seal)
        attack.effects.append(Stun)   
        self.attacks.append(attack)
        self.animation_num = 0
        
        self.powers.append(SealedKilled(self))
        self.powers.append(Teleport(self))
        self.powers.append(ThorianSpeed(self))
        self.powers.append(FireAura(self))
        self.powers.append(Regeneration(self))
        self.powers.append(HealingSword(self))
        self.powers.append(CrowAura(self))
        self.powers.append(MagicShield(self))
        #self.powers.append(PainDevouration(self))
        #self.powers.append(RenegadeSpawn(self))
        self.powers.append(Dodge(self))
        self.powers.append(Heroism(self))
        self.powers.append(Critical(self))
        self.powers.append(Lightning(self))
        self.powers.append(EffectImmunity(self))
    
    def get_basic_size(self):
        return [150,350]

"""
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
"""
    
 

class Projectile(pygame.sprite.Sprite):
    directional = True
    possible_targets = "self.source.enemies"
    def __init__(self,source,base_pos,end_pos,delay,y_move_up,lifes,functiun,image_name,size=None,rotate=False):   
        
        pygame.sprite.Sprite.__init__(self)        
        self.base_pos  =  base_pos
        self.end_pos  =  end_pos
        self.delay   =  delay
        self.y_move_up  =  y_move_up
        self.distance_y = -(self.base_pos[1]-self.end_pos[1])
        self.time = 0
        self.lifes = lifes
        self.dead = False
        self.enemy_hit = []
        self.source = source
        self.game = self.source.game
        self.angle = 0
        self.functiun = functiun 
        #self.angle = 90-math.degrees(math.atan((base_pos[0]-end_pos[0])/math.sqrt((base_pos[0]-end_pos[0])**2+(base_pos[1]-end_pos[1])**2)))
        self.image = pygame.image.load(image_name)
        if source.direction == -1:
            self.image = pygame.transform.flip(self.image,1,0)  
        self.image.convert_alpha()
        self.graphism = self.image
        if size:
            self.size = size
        else:            
            self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        
        if self.y_move_up:            
            self.distance_done = (float(end_pos[0])-base_pos[0])/delay * float(delay)/4
            self.distance_increase = (float(end_pos[0]-self.distance_done*2)-base_pos[0])/delay
            self.distance_x = end_pos[0]-base_pos[0]
            if self.distance_x == 0:
                self.distance_x = source.direction
            self.base_movement = (  math.sin(  math.radians(  (self.distance_done*180)  /self.distance_x-90)  )  *self.distance_x)/2
            self.base_y =  -math.cos(math.radians((self.distance_done*180)  /self.distance_x-90))*self.y_move_up
            #print(self.base_y,"\n"
            self.add_x = (self.base_movement)/delay
        else:
            self.distance_done = 0
            self.distance_x = (end_pos[0]-base_pos[0])
            self.distance_increase = float(self.distance_x)/self.delay
            self.rotate = rotate
            if rotate:
                self.angle = -math.degrees(math.atan((base_pos[1] - end_pos[1])/float(base_pos[0]-end_pos[0])))
        
        if not(self.distance_x):
            self.distance_x = 1
        
        
        self.center_x = self.base_pos[1] -self.image.get_size()[1]/2
        print("Initialisation of ",self)
        print("base pos 1 =",self.base_pos[1],", center_x = ",self.center_x)
        
        
        self.update()
        self.imageUpdate()
    
    def imageUpdate(self):
        self.image = pygame.transform.scale(self.graphism,self.size)
        self.image = pygame.transform.rotate(self.image,self.angle)
        self.posUpdate()
    
    def posUpdate(self):
        size = self.image.get_size()
        self.rect.y = self.center_y - size[1]/2
        self.rect.x = self.center_x - size[0]/2        
    
    def update(self):
        if self.dead:
            self.kill()
        if self.rect.y>900:# self.delay:
            #print("Projectile is killed"
            self.kill()            
        else:
            self.time += 1
            
            if self.y_move_up:
                
                angle =   (self.distance_done*180)  /self.distance_x-90            
                self.distance_done += self.distance_increase
                self.center_x = int(  math.sin(math.radians(  angle))*self.distance_x/2  -  self.time*self.add_x + self.base_pos[0]-self.base_movement)-self.game.screen_center_x + self.game.size[0]/2# -self.image.get_size()[0]/2
                self.center_y = int( -math.cos(math.radians(  angle))*self.y_move_up + self.base_pos[1]-self.base_y)# -self.image.get_size()[1]/2
                
                if self.directional:
                    if self.source.direction == -1:
                        self.angle = angle
                        #self.image = pygame.transform.flip(self.image,1,0)
                    else:
                        self.angle = 360-angle
            
            else:
                self.distance_done += self.distance_increase
                self.center_x = int(self.base_pos[0] + self.distance_done)-self.game.screen_center_x + self.game.size[0]/2# -self.image.get_size()[0]/2
                self.center_y = self.base_pos[1]+(self.distance_done*self.distance_y)/self.distance_x
        
        
        if self.rect.x + self.game.screen_center_x - self.game.size[0]/2 > self.game.length or self.rect.y > self.game.size[1] or self.rect.x+ self.game.screen_center_x - self.game.size[0]/2<-100 :
            self.kill()
        
        for c in eval(self.possible_targets):
            (w,h,x,y) = c.hit_box
            if not((self.rect.x>c.rect.x+x+w) or (self.rect.y>c.rect.y+y+h) or (self.rect.x+self.size[0]<x+c.rect.x) or (self.rect.y+self.size[1]<y+c.rect.y)):
                if not(c == self.source) and not(c in self.enemy_hit) and self.lifes>0:
                    self.functiun(c)
                    self.enemy_hit.append(c)
                    self.lifes -= 1
                    if self.lifes < 1:
                        self.kill()
                        self.dead = True
        
        
        b =  self.source.player.adv.base  
        if is_around(self.rect.x+self.game.screen_center_x-self.game.size[0]/2,b.pos[0]-b.swift+350,100) and is_around(self.rect.y,500,250):
            self.functiun(b)
            self.kill()
        
        self.imageUpdate()

class AllieProjectile(Projectile):
    possible_targets = "[self.target]"
    def __init__(self,source,base_pos,end_pos,delay,y_move_up,lifes,functiun,image_name,target,size=None):
        self.target = target
        Projectile.__init__(self,source,base_pos,end_pos,delay,y_move_up,lifes,functiun,image_name,size)

class UnalterableProjectile(Projectile):
    possible_targets = "self.source.enemies.sprites()+self.source.allies.sprites()"
    def __init__(self,source,base_pos,end_pos,delay,y_move_up,lifes,functiun,image_name,size=None,rotate=False):
        Projectile.__init__(self,source,base_pos,end_pos,delay,y_move_up,1000,functiun,image_name,size,rotate)
        
class Turret(pygame.sprite.Sprite):
    instance_type = "turret"
    is_dead=False
    def __init__(self,game,player,position):
        pygame.sprite.Sprite.__init__(self)        
        self.game = game
        self.player = player
        self.enemies= player.adv.army
        self.allies = player.army
        self.player.turrets.append(self)
        self.attacks = []
        self.effects = []        
        if self.player.side=="right":
            self.direction = -1
        else:
            self.direction = 1            
        self.set_parameters()
        self.graphism =  pygame.image.load(self.image_name)
        self.image = self.get_image()
        self.graphism = copy(self.image)
        self.size = self.image.get_size()            
        self.cooldown = 0
        self.attacking = False
        self.animations = []        
        self.rect = self.image.get_rect()
        self.center_x = position[0]
        self.center_y = position[1]
        self.angle = 0
        self.alpha = 255
        
        self.img_center_x = self.image.get_size()[0]/2
        self.img_center_y = self.image.get_size()[1]/2
        
        self.posUpdate()
        
    def get_image(self):
        image = copy(self.graphism)
        if self.direction == -1:
            image = pygame.transform.flip(image,1,0)
        return image
    
    def getAttackChoice(self):
        return self.attacks[0]
    
    def makeProjectile(self,enemy,attack):
        return attack.projectile(self,[self.center_x,self.center_y-50],[enemy.center_x,enemy.center_y-50],max([abs(self.center_x-enemy.center_x)/20,1]),0,1,attack.inflict,self.bullet_image_name,rotate=True)
    
    def new_effect(self,effect,source):
        pass
        
    def update(self):        
        if self.cooldown < (self.game.fps*90/self.att_speed):
            self.cooldown += 1        
        if not(self.attacking):
            self.attack = self.getAttackChoice()
            any_enemy = False
            for enemy in self.enemies:
                if abs(self.center_x+(self.size[0]/8)*self.direction-enemy.center_x-(enemy.size[0]/8)*enemy.direction) < self.attack.attack_range:
                    any_enemy = True
                    if self.cooldown >= self.game.fps*90/self.att_speed: 
                        self.attack.last_target = enemy                       
                        self.attack.animation(enemy)
        
            if not(any_enemy) and self.angle != 0 and self.need_to_return:
                self.returnAnimation()
        self.posUpdate()
    
    def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.getPosition()
        size_x,size_y = self.size
        angle = self.angle
        a = -math.degrees(math.atan(abs(enemy.center_y-pos_y)/abs(float(enemy.center_x-pos_x))))
        if self.direction == -1:
            a = -a
        print("Turret angle : ",a)
        phase1 = [(pos_x,pos_y),30,0,None,a]
        phase2 = [(pos_x,pos_y),5,0,self.attack.shoot,None]
        phase3 = [(pos_x,pos_y),30,0,self.hit_animation_end,angle]
        self.animations.append(Animation(self,[phase1,phase2,phase3],self))
    
    def hit_animation_end(self):
        self.attacking = False   
    
    def rotate_to(self,angle):
        self.angle = angle%360
        self.imageUpdate()
        
    def setPosition(self,pos):
        x,y = pos
        self.center_x = x
        self.center_y = y
        self.bottom_y = y + self.size[1]/2
    
    def getPosition(self):
        return [self.center_x, self.center_y]
        
    def destroy(self):
        self.kill()
    
    def receive(*args):
        pass
        
    def imageUpdate(self):
        self.image = pygame.transform.scale(self.get_image(),self.size)
        self.image = pygame.transform.rotate(self.image,int(self.angle))
        self.image.set_alpha(self.alpha)
        self.img_center_x = self.image.get_size()[0]/2
        self.img_center_y = self.image.get_size()[1]/2
        self.posUpdate()
    
    def posUpdate(self):
        self.rect.x = self.center_x - self.img_center_x - self.game.screen_center_x + self.game.size[0]/2
        self.rect.y = self.center_y - self.img_center_y

class Canon(Turret):
    def set_parameters(self):
        self.att_speed = 30 #in per minutes
        
        attack0 = Attack(self,11,0,600,False)
        attack0.projectile = Projectile
        self.attacks.append(attack0)
        
        
        self.need_to_return = False
        
        
        self.image_name = "Img/turret_canon.png"
        self.bullet_image_name = "Img/bullet_base.png"

class CrossBow(Turret):
   def set_parameters(self):
        self.att_speed = 45 #in per minutes
        
        attack0 = Attack(self,6,0,700,True)
        attack0.projectile = Projectile
        self.attacks.append(attack0)
        
        self.need_to_return = True
        
        self.image_name = "Img/turret_crossbow.png"
        self.bullet_image_name = "Img/arrow.png"
    
    
   def hitAnimation(self,enemy):
        self.attacking = True
        self.last_target = enemy
        #print("hit"
        self.cooldown = 0
        
        #destination,delay,endsize,self.effect,endrotation
        pos_x,pos_y = self.getPosition()
        size_x,size_y = self.size
        a = -math.degrees(math.atan(abs(enemy.center_y-pos_y)/abs(float(enemy.center_x-pos_x))))
        if self.direction == -1:
            a = -a
        phase1 = [(pos_x,pos_y),max([int(abs(self.angle%360-a%360)/10),1]),0,None,a]
        phase2 = [(pos_x,pos_y),5,0,self.attack.shoot,None]
        self.animations.append(Animation(self,[phase1,phase2],self))
    
   def returnAnimation(self):
        self.attacking = True
        pos_x,pos_y = self.getPosition()
        phase1 = [(pos_x,pos_y),20,0,self.finishedAnimation,0]
        self.animations.append(Animation(self,[phase1],self))
    
   def finishedAnimation(self):
        self.attacking = False

class Upgrade():
    level = 1
    costs = [150,200,300]

class PowerUpgrade(Upgrade):
    icon_names = ["upgrade_power_I.png","upgrade_power_II.png","upgrade_power_III.png","upgrade_power_end.png"]
    def __init__(self):
        #self.costs = [100,150,250]
        self.power_bonus = 0
    def levelUp(self):
        self.level = min([self.level+1,4])
        if self.level == 2:
            self.power_bonus = 15
        elif self.level == 3:
            self.power_bonus = 35
        elif self.level == 4:
            self.power_bonus = 60        
        elif self.level==1:
            self.power_bonus = 0
    def modify(self,unit):
        unit.magic_power_bonus = self.power_bonus
        for a in unit.attacks:
            a.magical_damage = int(a.magical_damage*(100+self.power_bonus)/100)
        

class AttackUpgrade(Upgrade):
    icon_names = ["upgrade_attack_I.png","upgrade_attack_II.png","upgrade_attack_III.png","upgrade_attack_end.png"]
    def __init__(self):
        #self.costs = [100,150,250]
        self.attack_bonus = 0
        self.att_speed_bonus = 0
    def levelUp(self):
        self.level = min([self.level+1,4])
        if self.level == 2:
            self.attack_bonus = 10
            self.att_speed_bonus = 4
        elif self.level == 3:
            self.attack_bonus = 25
            self.att_speed_bonus = 9
        elif self.level == 4:
            self.attack_bonus = 50
            self.att_speed_bonus = 16
        elif self.level==1:
            self.attack_bonus = 0
            self.att_speed_bonus = 0
    def modify(self,unit):
        unit.att_speed += self.att_speed_bonus
        for a in unit.attacks:
            a.physical_damage =int( a.physical_damage*(100+self.attack_bonus)/100)

class Swiftness(Upgrade):
    icon_names = ["upgrade_swiftness_I.png","upgrade_swiftness_II.png","upgrade_swiftness_III.png","upgrade_swiftness_end.png"]
    def __init__(self):
        #self.costs = [150,200,300]
        self.speed_bonus = 0
        self.att_speed_bonus = 0
    def levelUp(self):
        self.level = min([self.level+1,4])
        if self.level == 2:
            self.speed_bonus = 10
            self.att_speed_bonus = 20
        elif self.level == 3:
            self.speed_bonus = 20
            self.att_speed_bonus = 40
        elif self.level == 4:
            self.speed_bonus = 100
            self.att_speed_bonus = 30
        elif self.level==1:
            self.speed_bonus = 0
            self.att_speed_bonus = 0
    def modify(self,unit):
        unit.att_speed = int(unit.att_speed*(100+self.att_speed_bonus)/100)
        unit.base_speed = unit.speed = int(unit.speed*(100+self.speed_bonus)/100)

class VitalityUpgrade(Upgrade):
    icon_names = ["upgrade_vitality_I.png","upgrade_vitality_II.png","upgrade_vitality_III.png","upgrade_vitality_end.png"]
    def __init__(self):
        #self.costs = [150,200,300]
        self.vitality_bonus = 0
    def levelUp(self):
        self.level = min([self.level+1,4])
        if self.level == 2:
            self.vitality_bonus = 15
        elif self.level == 3:
            self.vitality_bonus = 35
        elif self.level == 4:
            self.vitality_bonus = 60
        elif self.level==1:
            self.vitality_bonus = 0
    def modify(self,unit):
        unit.max_hp = unit.hp = int(unit.hp*(100+self.vitality_bonus)/100)
   
class DefenceUpgrade(Upgrade):
    icon_names = ["upgrade_defence_I.png","upgrade_defence_II.png","upgrade_defence_III.png","upgrade_defence_end.png"]
    def __init__(self):
        #self.costs = [150,200,300]
        self.defence_bonus = 0
    def levelUp(self):
        self.level = min([self.level+1,4])
        if self.level == 2:
            self.defence_bonus = 10
        elif self.level == 3:
            self.defence_bonus = 25
        elif self.level == 4:
            self.defence_bonus = 45
        elif self.level==1:
            self.defence_bonus = 0
    def modify(self,unit):
        unit.armor += int((100-unit.armor)*(self.defence_bonus)/100)
        unit.magic_resistance += int((100-unit.armor)*(self.defence_bonus)/100)

class RangeUpgrade(Upgrade):
    icon_names = ["upgrade_range_I.png","upgrade_range_II.png","upgrade_range_III.png","upgrade_range_end.png"]
    def __init__(self):
        #self.costs = [100,150,250]
        self.range_bonus = 0
    def levelUp(self):
        self.level = min([self.level+1,4])
        if self.level == 2:
            self.range_bonus = 20
        elif self.level == 3:
            self.range_bonus = 45
        elif self.level == 4:
            self.range_bonus = 75
        elif self.level==1:
            self.range_bonus = 0
    def modify(self,unit):
        for a in unit.attacks:
            if a.attack_range>30:
                a.attack_range = int(a.attack_range*(100+self.range_bonus)/100)
        for p in unit.active_powers:
            if hasattr(p,"power_range"):
                p.power_range = int(p.power_range*(100+self.range_bonus)/100)



level1 = [Boxman,Skeleton,Spearman,Slinger,Dryad]
level2 = [Wisp,Bowman,Swordman,ScourgeMan,FlagBearer,Clerk]
level3 = [Mercenary,HighMage,BattleMage,Ghost,AxeThrower]
level4 = [Goliath,Troll,Assassin,Valkyrie,FireElementary,Ranger]
level5 = [Titan,Butcher,CrowLord,SkeletonLord,Purifier]

units_by_level = [level1,level2,level3,level4,level5]

all_units = level1+level2+level3+level4+level5
#print(len(all_units)

player1_units = [Skeleton,Wisp,BattleMage,Assassin,Butcher,ScourgeMan,Slinger]
player2_units = [Spearman,Skeleton,BattleMage,Mercenary,CrowLord,SkeletonLord,Titan]
player1_units = [random.choice(units_by_level[i]) for i in range(5)]+[random.choice(all_units),random.choice(all_units)]
player2_units = [random.choice(units_by_level[i]) for i in range(5)]+[random.choice(all_units),random.choice(all_units)]



non_used_unit = copy(all_units)
for u in reversed(non_used_unit):
    if u in player1_units:
        non_used_unit.remove(u)
non_used_unit = non_used_unit[:10]



def getCooldowns():
    return all_cooldowns

def getUpgrades():
    return {"Power":PowerUpgrade,"Attack":AttackUpgrade,"Vitality":VitalityUpgrade,"Defence":DefenceUpgrade,"Range":RangeUpgrade,"Swiftness":Swiftness}

def getUnits():
    return all_units

def getUnits2():
    return non_used_unit

def getUnitsOfPlayer(player):
    if player.__class__.__name__ == "ComputerPlayer" or player.__class__.__name__ == "ComputerPlayer2":
        units = []
        for l in range(5):
            selected = []
            for u in all_units:
                if  u.level == l+1 and not(u in [Clerk]):
                    selected.append(u)
            units.append(random.choice(selected))
        for y in range(2):
            unit = units[0]
            while unit in units or unit in [Clerk]:
                unit = random.choice(all_units)            
            units.append(unit)
        print(units)
        return units
    elif player.__class__.__name__ == "HumanPlayer":
        return player1_units
    else:
        return player2_units

def getCosts():
    return all_costs
    
