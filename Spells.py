# -*- coding: utf-8 -*-
"""
Created on Sat Mar 12 19:10:22 2016

@author: test
"""
import pygame
import random
from Animation import ImageEffect,Fade

class Spell():
    attack_range = -1
    damage_type = "physical"
    def __init__(self,player):
        self.player = player
        self.game = player.game
        self.cooldown = 0
        self.initialise()
    
    def effect(self):
        pass
    
    def initialise(self):
        pass
    
    def update(self):
        if self.cooldown>0:
            self.cooldown-=1

class MassHealing(Spell):
    reloading = 70
    level = 70
    manacost = 35
    icon = "spellcreator_heal.png"
    def effect(self):
        print(self.__class__.__name__,"Spell effect ")
        for u in self.player.army:
            if u.hp>0:
                u.hp = min([u.hp + u.max_hp*(self.level)/100,u.max_hp])
                ie = ImageEffect([u.img_center_x,u.size[1]/2 - u.head.size[1]/2 + u.head.center_y - u.get_basic_size()[1]/2],"Img/healing_blue.png",30,self.game,unit=u)
                #u.animations.append(Fade(ie,[[30,10,None]],u))
                u.image_effects.append(ie)
                print(u.image_effects)
                print(u.image_effects[0].center_x,u.image_effects[0].center_y)
        self.cooldown = self.reloading

class Destruction(Spell):
    reloading = 160
    damages = 30
    manacost = 90
    damage_type = "force"
    icon = "spellcreator_eruption.png"
    def effect(self):
        print(self.__class__.__name__,"Spell effect ")
        for u in self.player.adv.army:
            if u.hp>0:
                u.receive(self.damages//3,self.damages*2//3,self)
        self.cooldown = self.reloading

class MassWeakness(Spell):
    reloading = 100
    manacost = 75    
    icon = "spellcreator_weakness.png"
    def initialise(self):
        from Powers import WeaknessHex
        self.weakness = WeaknessHex
    def effect(self):
        print(self.__class__.__name__,"Spell effect ")
        for u in self.player.adv.army:
            if u.hp>0:
                u.new_effect(self.weakness,self)
                ie = ImageEffect([u.size[0]/2,u.size[1]/2 - u.head.size[1]/2 + u.head.center_y - u.get_basic_size()[1]/2-30],"Img/hex.png",self.game.fps*8,self.game,unit=u)
                u.animations.append(Fade(ie,[[30,10,None]],u))
                u.image_effects.append(ie)
        self.cooldown = self.reloading

class GhostCharge(Spell):
    reloading = 100
    manacost = 55
    icon = "spellcreator_ghostcharger.png"
    def initialise(self):
        from SWC_Units import GhostSpearman
        self.spear_man = GhostSpearman
    def effect(self):
        print(self.__class__.__name__,"Spell effect ")
        unit = self.spear_man(self.game,self.player)
        self.game.all_battlefield_sprites.add(unit)
        self.player.army.remove(unit)
        self.cooldown = self.reloading

class MeteorRain(Spell):
    damages = 30
    reloading = 100
    attack_range =  -1
    damage_type = "rock"
    icon = "spellcreator_meteorrain.png"
    manacost = 150
    def initialise(self):
        self.active_time = 0
        self.meteors = pygame.sprite.Group()
        
    def effect(self):
        if self.active_time == 0:
            print(self.__class__.__name__,"Spell effect ")
            self.active_time = 90
    
    def update(self):
        if self.cooldown>0:
            self.cooldown-=1
        
        if self.active_time > 0:
            if self.active_time%2 == 0:
                self.meteors.add(Meteor(self.game,self.player,random.randrange(200,self.game.length-200),random.randrange(-30,30)))
            self.active_time -= 1
            if self.active_time == 0:
                self.cooldown = self.reloading
        
        for u in pygame.sprite.groupcollide(self.player.adv.army,self.meteors,False,True):
            u.receive(self.damages//3,(self.damages*2)//3,self)
                

class Meteor(pygame.sprite.Sprite):
    def __init__(self,game,player,base_x,angle):
        pygame.sprite.Sprite.__init__(self)
        
        self.game = game
        self.game.all_battlefield_sprites.add(self)
        self.player = player
        self.pos_x = base_x
        self.pos_y = -500
        
        i = random.choice(["Img/meteor_yellow.png","Img/meteor_rock.png","Img/meteor_red.png"])
        self.image = pygame.image.load(i)
        self.image = pygame.transform.rotate(self.image,angle)
        
        self.x_increase = angle/6
        self.y_increase = random.randint(15,30)
        
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = self.pos_x - self.size[0]/2 - self.game.screen_center_x + self.game.size[0]/2
        self.rect.y = self.pos_y - self.size[1]/2
        
        self.enemies = self.player.adv.army
        
    def update(self):
        self.pos_x += self.x_increase
        self.pos_y += self.y_increase
        
        if self.pos_y > 1500:
            self.kill()
            print(self," is destroyed as it touched the ground")
        
        self.posUpdate()
            
    def posUpdate(self):
        self.rect.x = self.pos_x - self.size[0]/2 - self.game.screen_center_x + self.game.size[0]/2
        self.rect.y = self.pos_y - self.size[1]/2


all_spells = [MassHealing,Destruction,MassWeakness,MeteorRain,GhostCharge]


def getAllSpells():
    return all_spells
        