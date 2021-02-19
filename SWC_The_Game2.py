# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 12:10:52 2016

@author: test
"""

# Most recent version


import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print(os.path.dirname(os.path.abspath(__file__)))
import pygame

import random
import SWC_Units
from copy import copy
import time
import Spells
from Animation import BaseCopy,UnitCopy

BLACK = (0,0,0)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
GREY=(40,40,40)
BLUEGREY=(40,40,120)

size = (1285, 800)
screen_size = (1285, 1000)
length = 2800

pygame.init()

def is_around(i,ii,length):
    if ii < i -length or ii > i +length:
        return False
    else:
        return True

class CreatorButton(pygame.sprite.Sprite):
    def __init__(self,x_center,y_center,image,unit,game,player,index):
        
        self.game = game
        pygame.sprite.Sprite.__init__(self)        
        self.image = image.convert_alpha()
        #self.image.set_colorkey((255,255,255))
        self.base_image = copy(self.image)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = x_center - self.size[0]/2
        self.rect.y = y_center - self.size[1]/2
        self.player = player
        self.unit = unit
        self.cost = game.all_costs[unit.level]
        self.index = index
        
        self.refresh_image()
    
    def setUpgradeButton(self,upgrade_button):
        self.upgrade_button = upgrade_button
        self.game.all_foreground_sprites.add(upgrade_button)
         
    def update(self):
        if is_around(self.rect.x+self.size[0]/2,pygame.mouse.get_pos()[0],self.size[0]/2) and is_around(self.rect.y+self.size[1]/2,pygame.mouse.get_pos()[1],self.size[1]/2):
            #print("selected"
            if self.game.click == True and not(self.upgrade_button.is_clicked()):
                #print("clicked "
                if self.cost < self.player.fund and len(self.player.training)<self.player.max_training:
                    self.player.train(self.unit)
                    
    def refresh_image(self):
        self.image = copy(self.base_image)
        
        font = pygame.font.SysFont("Verdana",18)
        text = font.render(str(self.cost),True,(0,160,0))
        self.image.blit(text,(30,10))
        
        font = pygame.font.SysFont("Verdana",26)
        text = font.render(str(self.index),True,(0,0,120))
        self.image.blit(text,(20,60))

class SpellButton(CreatorButton):
    def __init__(self,x_center,y_center,image,spell,game,player):
        
        self.game = game
        pygame.sprite.Sprite.__init__(self)        
        self.image = image
        self.image.set_colorkey((255,255,255))
        self.base_image = copy(image)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = x_center - self.size[0]/2
        self.rect.y = y_center - self.size[1]/2
        self.player = player
        self.spell = spell
        self.mana_cost = spell.manacost
         
    def update(self):
        if is_around(self.rect.x+self.size[0]/2,pygame.mouse.get_pos()[0],self.size[0]/2) and is_around(self.rect.y+self.size[1]/2,pygame.mouse.get_pos()[1],self.size[1]/2):
            if self.game.click == True:
                if self.mana_cost < self.player.mana and self.spell.cooldown == 0:
                    self.spell.effect()
                    self.player.mana -= self.mana_cost

class SelectForUpgradeButton(pygame.sprite.Sprite):
    def __init__(self,center,image,button):
        (x_center,y_center) = center
        pygame.sprite.Sprite.__init__(self)        
        self.image = image
        self.image.set_colorkey(BLACK)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = x_center - self.size[0]/2
        self.rect.y = y_center - self.size[1]/2
        self.player = button.player
        self.unit = button.unit
        self.game = button.game
        self.button = button
        
    def update(self):
        if self.is_clicked():
            if self.game.click == True:
                if self.player == self.game.player_left:
                    self.game.upgrade_selection.goTo(self.button)
                else:
                    self.game.upgrade_selection2.goTo(self.button)
    
    def is_clicked(self):
        #print(bool(is_around(self.rect.x+self.size[0]/2,pygame.mouse.get_pos()[0],self.size[0]/2) and is_around(self.rect.y+self.size[1]/2,pygame.mouse.get_pos()[1],self.size[1]/2))
        return bool(is_around(self.rect.x+self.size[0]/2,pygame.mouse.get_pos()[0],self.size[0]/2) and is_around(self.rect.y+self.size[1]/2,pygame.mouse.get_pos()[1],self.size[1]/2))

class UpgradeSelection(pygame.sprite.Sprite):
    def __init__(self,image,button):
        pygame.sprite.Sprite.__init__(self)        
        self.image = image
        self.image.set_colorkey(BLACK)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.player = button.player
        self.unit = button.unit
        self.game = button.game
        self.button = button
        
        self.button.image.blit(self.image,self.rect)
    
    def goTo(self,button):
        self.button.refresh_image()
        
        self.button = button
        self.rect.x = 0
        self.rect.y = 0
        self.button.image.blit(self.image,self.rect)
        
        self.game.refreshUpgrades(button.unit,button.player)
    
    def update(self):
        pass

class Upgrader(pygame.sprite.Sprite):
    def __init__(self,center,upgrade,game,player,level):     
        x_center,y_center = center
        self.game = game
        pygame.sprite.Sprite.__init__(self)
        self.level = level
        self.player = player
        self.upgrade = upgrade
        self.upgrade.level = self.level
        if self.level < 4:
            self.cost = self.upgrade.costs[self.level-1]
        else:
            self.cost = 0
        self.image = pygame.image.load("Img/Upgrades/"+self.upgrade.icon_names[self.level-1]).convert_alpha()
        #self.image.set_colorkey((0,0,0))
        #self.image = self.image.convert()
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = x_center - self.size[0]/2
        self.rect.y = y_center - self.size[1]/2
         
    def update(self):
        if is_around(self.rect.x+self.size[0]/2,pygame.mouse.get_pos()[0],self.size[0]/2) and is_around(self.rect.y+self.size[1]/2,pygame.mouse.get_pos()[1],self.size[1]/2):
            if self.game.click == True:
                if self.cost < self.player.fund and self.level!=4:
                    self.upgrade.levelUp()
                    print( "upgrade to ",self.upgrade.level)
                    self.level = self.upgrade.level
                    self.player.fund -= self.cost
                    if self.level != 4:
                        self.cost = self.upgrade.costs[self.level-1]
                    self.image = pygame.image.load("Img/Upgrades/"+self.upgrade.icon_names[self.level-1]).convert_alpha()
                    
                    global allFakes
                    for i in allFakes.keys():
                        if i in self.player.upgrades.keys():
                            allFakes[i].refresh(self.player.upgrades[i])
                            print( i.__name__," 's fake is upgrade refreshed")
    
    def refresh(self):
        self.level = self.upgrade.level
        if self.level != 4:
            self.cost = self.upgrade.costs[self.level-1]
        self.image = pygame.image.load("Img/Upgrades/"+self.upgrade.icon_names[self.level-1])
        self.image.set_colorkey(BLACK)

class QueueIcon(pygame.sprite.Sprite):
    def __init__(self,image,index,queue_icon_group,front_pos,direction):
        pygame.sprite.Sprite.__init__(self)
        
        self.queue_icon_group = queue_icon_group
        queue_icon_group.add(self)
        self.index = index
        self.direction = direction
        self.front_pos = front_pos
        
        
        self.size = (40,40)
        self.image = pygame.transform.scale(pygame.image.load("Img/Creators/"+image),self.size)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = (self.index*(self.size[0]+5))*direction+front_pos[0]
        self.rect.y = self.front_pos[1]
        
        #print("im a new queue icon and i want to say hello, my inputs are: ",image,index,queue_icon_group,front_pos,direction
        #print("(image,index,queue_icon_group,front_pos,direction)"
        
    
    def swift(self):
        self.index -= 1
        self.rect.x = (self.index*(self.size[0]+5))*self.direction+self.front_pos[0]
        self.rect.y = self.front_pos[1]
    
    def die(self):
        self.kill()
        for u in self.queue_icon_group:
            u.swift()
        


class Player():
    upgrade_mode = False #Only used for Computer 1
    def __init__(self,game,side,base_pos,base_images,swift,turret_pos):
        self.game = game
        self.side = side
        self.army = pygame.sprite.Group()
        self.base = Base(self)
        
        self.fund = game.GOLDATTHEBEGINING
        self.time = 0
        self.seconds = 0
        self.queue_icon_group = pygame.sprite.Group()
        
        self.base.images = [pygame.image.load(i) for i in base_images]
        for e in self.base.images:
            e.convert_alpha()

        self.base.image = self.base.images[0]
        self.base.pos[0] = base_pos
        self.base.center_x = base_pos+400-(side=="right")*100-swift#+self.base.image.get_size()[0]/2
        self.base.bottom_y = 750
        self.base.center_y = 450
        self.base.swift = swift
        self.base.size = self.base.image.get_size()
        self.base_open_time = 0
        self.base.turret_pos = turret_pos

        self.effects = []
        self.turrets = []
        self.creators = []
        
        self.base.max_hp = self.base.hp = 100
        self.training = []
        self.max_training = 4
        self.cooldown = 0
        self.max_mana = self.mana = 184
        self.mana_increase = 0.5
            
    def open_base(self):
        self.base_open_time = 15
    
    def defeat(self):
        self.game.end(self)
    
    def Power(self,level):
        print( "Power upgraded to level ",level)
        
        
    def recruit(self,monster_class):
        monster = monster_class(self.game,self)
        #self.game.all_battlefield_sprites.add(monster)
        
        if self.game.last_creature_time == 100:
            r = SWC_Units.SkullBuff(monster)
            monster.powers.append(r)
            r.initialise(monster)
            
        self.game.last_creature_time = 0
        if self.game.COOLDOWNS:
            q = None
            for queue in self.queue_icon_group:
                    if queue.index == 0:
                            q = queue
            try:
                q.die()
            except:
                print( "error in recruit")
        if monster_class.level==5:
            son_cor.play()
            self.game.dramatic_entrance_effect=self.game.fps*2
    
    def train(self,unit):
        if self.game.COOLDOWNS:            
            if len(self.training)<=self.max_training and self.game.all_costs[unit.level]:
                if not(self.training):
                    self.cooldown = self.game.all_cooldowns[unit.level]
                self.training.append(unit)
                self.fund -= self.game.all_costs[unit.level]
                self.game.all_foreground_sprites.add(QueueIcon(unit.creator_image,len(self.queue_icon_group),self.queue_icon_group,[[60,size[0]-60][["left","right"].index(self.side)],60],(1-2*["left","right"].index(self.side))))
        else:
            self.recruit(unit)
        
    def update(self):
        """
        for e,c in enumerate(self.cooldowns):
            if c:
                self.cooldowns[e]-=1
        """
        self.time += 1
        if (self.time+1)%self.game.fps == 0:
            self.seconds += 1
            self.time = 0
        
        if self.money_per_second <= self.game.fps:
            if self.time%(self.game.fps/(self.money_per_second/5))==0:
                self.fund += 5
        else:
            if self.time%(self.game.fps/5)==0:
                self.fund += int( (self.money_per_second*5)/self.game.fps )
            

        self.action_update()        
        
        for s in self.spells:
            s.update()
            
        if self.mana+1 > -1 and self.mana+1 < self.max_mana+1 and self.time%int((self.game.fps*self.mana_increase))==0: 
            self.mana += 5
        
        if self.base_open_time:
            self.base_open_time -= 1
            self.base.image = self.base.images[1]
            if self.base_open_time == 0:
                self.base.image = self.base.images[0]
        
        if self.training:
            self.cooldown -= 1
            if self.cooldown < 1:
                self.recruit(self.training[0])
                del self.training[0]
                if self.training:
                    self.cooldown = self.game.all_cooldowns[self.training[0].level]
            elif self.cooldown < 6:
                self.open_base()

    def initialise(self):
        self.creatures = self.game.getUnitsOfPlayer(self)
        self.spells = [s(self) for s in Spells.getAllSpells()]        
        self.upgrades = {}
        for m in self.creatures:
            self.upgrades[m] = [self.game.all_upgrades[u]() for u in m.upgrades]         
        self.properInitialise()
    
    def action_update(self):
            pass
    
    def upgrade_level_up(self,upgrade):
        self.fund -= upgrade.costs[upgrade.level-1]  
        upgrade.levelUp()
        global allFakes
        for i in allFakes.keys():
            if i in self.upgrades.keys():
                allFakes[i].refresh(self.upgrades[i])
                print( i.__name__," 's fake is upgrade refreshed")
        self.game.upgraders_refresh()

class Base():
    def __init__(self,player):
        self.player = player
        self.game = self.player.game 
        self.pos = [None,self.game.size[1]-550] # x pos is defined after
        self.effects = []
    
    def receive(self,damage,magic_damage,attack):
        self.hp -= max([damage/3,1])+max([magic_damage/3,1])
        if self.hp < 1:
            self.player.defeat()
            self.hp = 0
    
    def new_effect(self,eff,source):
        pass

class Magister():
    def __init__(self,game):
        self.game = game
        self.allStickmen_list = SWC_Units.getUnits()[:5]
        self.clash_tested = {}
        self.armies_to_test = [(c,) for c in self.allStickmen_list]
        for c in self.allStickmen_list:
            self.armies_to_test += [(c,c1) for c1 in self.allStickmen_list]
            for c1 in self.allStickmen_list:
                self.armies_to_test += [(c,c1,c2) for c2 in self.allStickmen_list]
        self.clash_to_test = []
        for army in self.armies_to_test:
            for army2 in self.armies_to_test:
                if army != army2 and not((army2,army) in self.clash_to_test):
                    self.clash_to_test.append((army,army2))
        self.clash = None
        self.timer = 0
    
    def initialise(self):
        for player in (self.game.player_left,self.game.player_right):
            for m in self.allStickmen_list:
                player.upgrades[m] = [self.game.all_upgrades[u]() for u in m.upgrades]   
    
    def update(self): 
        if len(self.game.player_left.army)==0 or len(self.game.player_right.army)==0:
            self.timer += 1
            if self.clash and self.timer > self.game.fps*4:
                self.clash_tested[str(([c.__name__ for c in self.clash[0]],[c.__name__ for c in self.clash[1]]))] = ([c.__class__.__name__+str(c.hp)+"/"+str(c.max_hp) for c in self.game.player_left.army],[c.__class__.__name__+str(c.hp)+"/"+str(c.max_hp) for c in self.game.player_right.army])
                self.clash = None
                self.game.player_left.base.hp = self.game.player_left.base.max_hp
                self.game.player_right.base.hp = self.game.player_right.base.max_hp
                
                for spr in self.game.all_battlefield_sprites:
                    spr.kill()
                    if hasattr(spr,"animations"):
                        for a in spr.animations:
                            a.stop()
            elif self.timer >= self.game.fps*6:
                self.timer = 0
                self.sendWave()
    
    def sendWave(self):
        self.clash = self.clash_to_test[0]
        for creature in self.clash[0]:
            self.game.player_left.train(creature)
        for creature in self.clash[1]:
            self.game.player_right.train(creature)
        del self.clash_to_test[0]        
        




class HumanPlayer(Player):
    def properInitialise(self):
        self.money_per_second = 30
        for n,s in enumerate(self.spells):
            print( "pygame.K_"+["q","w","e","r","t","y","u","i"][n],": ",s.__class__.__name__)
    def key_pressed(self,event,shift):
        if not(shift):
            for e,creature in enumerate(self.creatures):
                if event.key == eval("pygame.K_"+str(e)):
                    if len(self.training)<self.max_training and self.fund>=self.game.all_costs[creature.level]:
                        self.train(creature)
        else:
            for e,creature in enumerate(self.creatures):
                if event.key == eval("pygame.K_"+str(e)):
                    self.game.upgrade_selection.goTo(self.creators[e])
        for [key,n] in [[pygame.K_q,0],[pygame.K_w,1],[pygame.K_e,2]]:
            if event.key == key:
                upgrade = self.upgrades[self.game.upgrade_selection.button.unit][n]
                if upgrade.level<4 and self.fund > upgrade.costs[upgrade.level-1]:
                    self.upgrade_level_up(upgrade)
        """
        for n,s in enumerate(self.spells):
            if event.key == eval("pygame.K_"+["q","w","e","r","t","y","u","i"][n]):
                print("key of spell ",s.__class__.__name__
                if s.cooldown == 0 and self.mana > s.manacost:
                    s.effect()
                    self.mana -= s.manacost
        """

class HumanPlayer2(HumanPlayer):
    def properInitialise(self):
        self.money_per_second = 30
    def key_pressed(self,event,shift):
        if not(shift):
            for e,creature in enumerate(self.creatures):
                if len(self.training)<self.max_training  and self.fund>=self.game.all_costs[creature.level]:
                    if event.key == eval("pygame.K_KP"+str(e)):
                        self.train(creature)
        else:
            for e,creature in enumerate(self.creatures):
                if event.key == eval("pygame.K_KP"+str(e)):
                    self.game.upgrade_selection2.goTo(self.creators[e])

        for [key,n] in [[pygame.K_KP_MULTIPLY,0],[pygame.K_KP_MINUS,1],[pygame.K_KP_PLUS,2]]:
            if event.key == key:
                upgrade = self.upgrades[self.game.upgrade_selection2.button.unit][n]
                if upgrade.level<4 and self.fund > upgrade.costs[upgrade.level-1]:
                    self.upgrade_level_up(upgrade)
        

class ComputerPlayer(Player):
    def properInitialise(self):
        costs = []
        self.money_per_second = 50
        ordered_waves = []
        waves= {}
        treshholds = []

        for e,cost in enumerate(self.game.all_costs[1:]):
            costs.append(cost)
            waves[cost] = [e+1]
            for i,cost2 in enumerate(self.game.all_costs[1:]):
                costs.append(cost+cost2)
                waves[cost+cost2] = [e+1,i+1]
                for a,cost3 in enumerate(self.game.all_costs[1:]):
                    costs.append(cost+cost2+cost3)
                    waves[cost+cost2+cost3] = [e+1,i+1,a+1]
        costs.sort()
        for c in costs[:10]:
            ordered_waves.append([c,waves[c]])
        
        upgrades_time_intervals = [(30*i,30*i+6) for i in range(1,40)] #must be sorted
        
        i = 0
        j = 0
        while i<len(upgrades_time_intervals) and j<len(ordered_waves):
            (d,f) = upgrades_time_intervals[i]
            
            t = int((ordered_waves[j][0]/(self.game.fps))**1.8 *0.5) #attention : formule recopiée en dessous
            if t < d:
                treshholds.append((t,ordered_waves[j]))
                j += 1
            else:
                if treshholds[-1][1] == "upgrade":
                    treshholds.append([upgrades_time_intervals[i-1][1],random.choice(ordered_waves[-20:])])
                treshholds.append((d,"upgrade"))
                while t<f and j<len(ordered_waves)-1: #on ignore les vagues qui auraient lieu pendant la phase d'upgrade
                    j += 1
                    t = int((ordered_waves[j][0]/(self.game.fps))**1.8*0.5)
                i += 1
        print(len(treshholds))
        while i<len(upgrades_time_intervals):
            (d,f) = upgrades_time_intervals[i]            
            if treshholds[-1][1] == "upgrade":
                treshholds.append([upgrades_time_intervals[i-1][1],random.choice(ordered_waves[-20:])])
            treshholds.append((d,"upgrade"))
            i += 1
        
        self.selection = 0
        self.treshholds = treshholds    
        print( "treshholds = ",treshholds)
        self.next_upgrade = (0,0) # [unit , index]
            
    def key_pressed(self,event,shift):
        pass
    
    def action_update(self):
            #print("seconds ",self.seconds
        for s in self.spells:
            s.update()

        if self.seconds >= self.treshholds[self.selection+1][0]:
            self.selection += 1
            if self.treshholds[self.selection][1] == "upgrade":
                self.upgrade_mode = True
                print("Entered upgrade mode")
            else:
                self.upgrade_mode = False
                print( "Changed selection to ",self.treshholds[self.selection][1][1]," that costs ",self.treshholds[self.selection][1][0])
        if self.upgrade_mode:
            i,j = self.next_upgrade
            upgrade = self.upgrades[self.creatures[i]][j]
            if self.fund >= upgrade.costs[upgrade.level]:
                self.fund = self.fund - upgrade.costs[upgrade.level]
                upgrade.levelUp()
                self.next_upgrade = ((i+1)%7, (j+1)%3) # atteint toutes les upgrades car 7 et 3 sont premiers entre eux!
        else:
            if self.fund >= self.treshholds[self.selection][1][0]:
                to_train = []
                print( "Building levels ",self.treshholds[self.selection][1][1]," that costs ",self.treshholds[self.selection][1][0])
                for u in self.treshholds[self.selection][1][1]:
                    selected = []
                    for unit in self.creatures:
                        if unit.level == u:
                            selected.append(unit)
                    if selected:
                        to_train.append(random.choice(selected))
                while to_train:
                    attack_range = 100000000
                    unit = None
                    for t in to_train:
                        if any([isinstance(p,SWC_Units.Charge) for p in allFakes[t].powers]):
                            attack_range = allFakes[t].attacks[0].attack_range
                            unit = t
                            break
                        elif allFakes[t].attacks[0].attack_range < attack_range:
                            attack_range = allFakes[t].attacks[0].attack_range
                            unit = t
                    to_train.remove(unit)
                    self.train(unit)
        
        for unit in self.adv.army:
            if self.side == "right" and (max([attack.attack_range for attack in unit.attacks]) + unit.center_x - (self.base.center_x-self.base.size[0]/2))>0 or (self.side == "left" and (max([attack.attack_range for attack in unit.attacks]) + unit.center_x - (self.base.center_x+self.base.size[0]/2))<0):
                if len(self.army.sprites())<1:
                    biggest  = None
                    for g in self.creatures:
                        if self.game.all_costs[g.level] < self.fund and (not(biggest) or biggest.level<g.level):# or (  biggest.level==g.level and min([a.attack_range for a in biggest.attacks])<min([a.attack_range for a in b.attacks])  )):
                            biggest = g
                    if biggest:
                        self.train(biggest)

class StaticPlayer(Player):
    def properInitialise(self):
        self.money_per_second = 100

class ComputerPlayer2(ComputerPlayer):   
    def __init__(self,*args):
        ComputerPlayer.__init__(self,*args)
    
    def properInitialise(self):
        
        self.unit_to_build = self.creatures[0]
        self.money_per_second = 30   
        self.internal_timing = 0
        self.planned_unit = self.creatures[4]
        self.asleep = False

#        for g in self.game.creatures:
#            print(g.__name__,allFakes[g].attacks
#            g.magic_level = sum([(100*a.magical_damage)/(a.magical_damage+a.physical_damage) for a in allFakes[g].attacks])/len(allFakes[g].attacks) #a %
#            print(g.__name__,".magic_level is ",g.magic_level
    
    
    def get_score(self,unit_class,enemy): # unit class
        
        unit = allFakes[unit_class]
        
        enemy_add_magic_dps = sum([power.get_add_magic_dps(unit) for power in enemy.powers])
        enemy_magic_att_add = sum([power.get_magic_att_add(unit) for power in enemy.powers])
        enemy_physic_att_add = sum([power.get_physic_att_add(unit) for power in enemy.powers])
        enemy_magical_dps = float(enemy.att_speed)*(enemy.attacks[0].magical_damage+enemy_magic_att_add)/60+enemy_add_magic_dps
        enemy_physical_dps = float(enemy.att_speed)*(enemy.attacks[0].physical_damage+enemy_physic_att_add)/60
        unit_taken_dps = enemy_magical_dps*(100-unit.magic_resistance)/100+enemy_physical_dps*(100-unit.armor)/100
        for power in unit.powers:
            unit_taken_dps = power.modify_taken_dps(unit_taken_dps,enemy)
        
        unit_add_magic_dps = sum([power.get_add_magic_dps(enemy) for power in unit.powers])
        unit_magic_att_add = sum([power.get_magic_att_add(enemy) for power in unit.powers])
        unit_physic_att_add = sum([power.get_physic_att_add(enemy) for power in unit.powers])
        unit_magical_dps = float(unit.att_speed)*(unit.attacks[0].magical_damage+unit_magic_att_add)/60+unit_add_magic_dps
        unit_physical_dps = float(unit.att_speed)*(unit.attacks[0].physical_damage+unit_physic_att_add)/60
        enemy_taken_dps = unit_magical_dps*(100-enemy.magic_resistance)/100+unit_physical_dps*(100-enemy.armor)/100
        for power in enemy.powers:
            enemy_taken_dps = power.modify_taken_dps(enemy_taken_dps,unit)
        #enemy taken dps?

        enemy_damage_before = max([0,(enemy.max_range-unit.max_range)*unit_taken_dps/(30*unit.speed)]) + sum([power.damage_before(unit) for power in enemy.powers])
        unit_damage_before = max([0,(unit.max_range-enemy.max_range)*enemy_taken_dps/(30*enemy.speed)])  + sum([power.damage_before(unit) for power in enemy.powers])
        
        duel_duration = max([0,min([(unit.hp-enemy_damage_before)/unit_taken_dps,(enemy.hp-unit_damage_before)/enemy_taken_dps])])
        
        hp_lost_by_unit = -int(max([enemy_damage_before+duel_duration*unit_taken_dps,unit.hp-unit.max_hp]))
        hp_lost_by_enemy = -int(max([unit_damage_before+duel_duration*enemy_taken_dps,enemy.hp-enemy.max_hp]))
        
        score = self.game.all_costs[enemy.level]*hp_lost_by_enemy/(enemy.max_hp) - self.game.all_costs[unit.level]*hp_lost_by_unit/(unit.max_hp)
        
        print( unit_class.__name__," is rated ",score)
        return int(score)
    
    def getDamageTaken(self,time_to_build):
        damage_taken = 0
        ordered_units = {}
        for u in self.adv.army:
            index = u.center_x
            while index in ordered_units.keys():
                index -= 1
            ordered_units[index]=u
        order = copy(ordered_units.keys())
        order.sort()
        ordered = [ordered_units[i] for i in order ]
        if len(ordered) != len(self.adv.army):
            print( "ERROR DIFFERENT SIZE WHEN ORDERED")
            raise( "error")
        for u in ordered:
            max_range = max([a.attack_range for a in u.attacks])
            print( "maxrange is ",max_range)
            if u.speed > 0 and time_to_build>abs(u.center_x-self.base.center_x)/(u.speed*self.game.fps):
                hit_time = time_to_build-abs(u.center_x-self.base.center_x)/(u.speed*self.game.fps)
                print( "hit time = ",time_to_build,"-abs(",u.center_x,"-",self.base.center_x,")/(",u.speed,"*",self.game.fps,")")
                print(hit_time)
                damage_taken += hit_time*[0,6,8,10,12,14][u.level]
                print("add ",hit_time*[0,6,8,10,12,14][u.level],' damages')
        print( "damage taken", damage_taken)
        return int(damage_taken)

    def getAdvPower(self):
        return sum([self.game.all_costs(unit.level)*float(unit.hp)/unit.max_hp for unnit in self.adv.army])
    
    def getArmyPower(self,player):
        return sum([self.game.all_costs(unit.level)*float(unit.hp)/unit.max_hp for unnit in self.army])
        
    def getBestUnit(self):
            print( "getAdvPower of ComputerPlayer2 -------------------------------------------------------------------------------------")
            #self.getAdvPower()
            utility = {}
            for u in self.creatures:
                p = self.get_score(u,self.adv.army.sprites()[0])
                while True:
                    if not(p in utility.keys()):
                        utility[p] = u
                        break
                    else:
                        p+=0.1
            keys = utility.keys()
            keys.sort()
            best = utility[keys[-1]]
            print( utility)
            print( "Best is build ",best.__name__)
            
            #print("Own army Power is :", self.army_power
            if len(self.army)>1: #the 30 comes from the turret
                print( "There's enough, I can rest")
                self.asleep = True
            else:
                self.asleep = False
            return best
        

    def key_pressed(self,event,shift):
        if event.key == pygame.K_k:
            self.getBestUnit()
    
    def recruit(self,*args):
        Player.recruit(self,*args)
        self.asleep = False
        self.planned_unit = self.getBestUnit()
        
        
    def action_update(self):
        self.internal_timing = self.internal_timing+1%1000
        if self.internal_timing%100 == 0 and len(self.adv.army)>0:
            self.planned_unit = self.getBestUnit()
        
        if self.fund>=game.all_costs[self.planned_unit.level] and not(self.asleep):
            self.train(self.planned_unit)
            self.asleep = True
        
        """
            #print("seconds ",self.seconds)
        for s in self.spells:
            s.update()
        
        if self.time == 0:
            self.unit_to_build = self.getBestUnit()

        if self.seconds >= self.treshholds[self.selection+1][0]:
            self.selection += 1
            print("Changed selection to ",self.treshholds[self.selection][1][1]," that costs ",self.treshholds[self.selection][1][0])

        if self.fund >= self.game.all_costs[self.unit_to_build.level]:
            self.train(self.unit_to_build)
            """
        for s in self.spells:
            s.update()

allFakes = {}
for unit_class in SWC_Units.getUnits():        
    class UnitFake(unit_class):
        def __init__(self,*args):
            self.powers = []
            self.attacks = []
            self.effects = []
            self.active_powers = []
            self.max_mana = self.mana = 0            
            self.magic_resistance = 0
            self.set_parameters()
            # sets hp, armor, magic_resistance, attack speed, powers
            self.max_hp = self.hp
            
            self.max_range = max([att.attack_range for att in self.attacks])
            
        def refresh(self,upgrades):
            self.__init__()
            for up in upgrades:
                up.modify(self)
            
    allFakes[unit_class] = UnitFake()
            
    

class damageEffect():
    def __init__(self,unit,txt,game,color):
        self.txt = txt
        self.alpha = 250 #n'est plus pris en compte
        self.game = game
        self.color = color
        self.makeImage()
        self.unit = unit
        self.center_x,self.center_y = unit.center_x,unit.bottom_y-unit.size[1]*3/4
        self.rect = [self.center_x -self.game.screen_center_x + size[0]/2,self.center_y]
        print("damage Effect rect:",self.rect)
    def update(self):
        self.center_y -= 1
        self.alpha -= 5
        if self.alpha < 0:
            game.all_effects.remove(self)
        self.rect = [self.center_x -self.game.screen_center_x + size[0]/2,self.center_y]
        self.makeImage()
    def makeImage(self):
        self.text = self.txt
        self.image = pygame.Surface([len(self.text)*20,40])
        font = pygame.font.SysFont("Calibri",18)
        text = font.render(self.text,True,self.color)
        self.image.blit(text,(0,0))
        self.image.set_colorkey(BLACK)
        self.image.set_alpha(self.alpha)

class HealthBar(pygame.sprite.Sprite):
    def __init__(self,sprite):
        pygame.sprite.Sprite.__init__(self)
        monster = sprite
        self.monster = monster
        self.game = monster.game
        if not(self.monster.__class__ == Base) and self.monster.max_mana:
            self.mana = True
        else:
            self.mana = False
        
        if self.monster.__class__ == Base:
            self.tkness = 8
        else:
            self.tkness = 4
            
        self.imageUpdate()
        self.rect = self.image.get_rect()
        self.posUpdate()        
    
    def imageUpdate(self):
        if not(self.mana):
            self.image = pygame.Surface([self.monster.max_hp,self.tkness])
        else:
            self.image = pygame.Surface([max([self.monster.max_hp,self.monster.max_mana]),int(self.tkness*2.5)])
        self.image.fill(GREY)
        red_part = pygame.Surface([max([self.monster.max_hp,0]),self.tkness])
        red_part.fill(RED)
        self.image.blit(red_part,[0,0])
        green_part = pygame.Surface([max([self.monster.hp,0]),self.tkness])
        green_part.fill(GREEN)
        self.image.blit(green_part,[0,0])
        if self.mana:
            green_part = pygame.Surface([max([self.monster.max_mana,0]),self.tkness])
            green_part.fill(BLUEGREY)
            self.image.blit(green_part,[0,6])
            blue_part = pygame.Surface([max([self.monster.mana,0]),self.tkness])
            blue_part.fill(BLUE)
            self.image.blit(blue_part,[0,6])            
    
    def update(self):
        self.imageUpdate()
        self.posUpdate()        
    
    def posUpdate(self):
        self.rect.x = self.monster.center_x - self.monster.max_hp/2 - self.game.screen_center_x + size[0]/2
        if self.monster.__class__ != Base:
            r = 1 #self.monster.size[1]/self.monster.get_basic_size()[1]
            self.rect.y = int(self.monster.head.rect[1]*r)+self.monster.rect.y# - 20
        else:
            self.rect.y = self.monster.bottom_y - self.monster.size[1]*3/4                   
        
class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)        
        self.image = pygame.Surface((6,6))
        pygame.draw.circle(self.image,(155,0,0),(3,3),3)
        self.image.set_colorkey((0,0,0))        
        self.mode = "normal"        
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
    def update(self):
        if self.mode == "normal":
            self.image = pygame.Surface((3,3))
            pygame.draw.circle(self.image,(155,0,0),(3,3),3)
            self.image.set_colorkey((0,0,0))
        else:
            self.image = pygame.Surface([4,4])
            self.image.set_colorkey((0,0,0))
        self.rect.x = pygame.mouse.get_pos()[0]
        self.rect.y = pygame.mouse.get_pos()[1]      

class MiniMap(pygame.sprite.Sprite):
    def __init__(self,game):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([400,110])
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.rect.x = size[0]/2-self.size[0]/2
        self.bg = pygame.image.load("Img/minimap.png")
        self.bg.convert_alpha()
        self.rect.y = 10
        self.game = game
        self.resized_game_bg = pygame.transform.scale(self.game.img_bg1,[self.size[0]-20,self.size[1]-20])
    def update(self):
        self.image = pygame.Surface([400,110])
        self.image.set_colorkey(BLACK)
        self.image.blit(self.bg,[0,0])
        self.image.blit( self.resized_game_bg ,[10,10])
        for u in game.player_left.army:
            pygame.draw.circle(self.image,(255,0,0),[10+int(u.center_x*(self.size[0]-20)/length),80],u.level*2)
        for u in game.player_right.army:
            pygame.draw.circle(self.image,(0,0,255),[10+int(u.center_x*(self.size[0]-20)/length),80],u.level*2)

class ManaBar(pygame.sprite.Sprite):
    def __init__(self,game,player):  
        pygame.sprite.Sprite.__init__(self)
        self.bg = self.image = pygame.image.load("Img/ManaBar.png")
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.rect.x = size[0]/2-self.size[0]/2
        self.end_img = pygame.image.load("Img/ManaBarLastPart.png")
        self.part = pygame.image.load("Img/ManaBarLittlePart.png")
        self.bg.convert_alpha()
        self.rect.y = 140
        self.game = game
        self.player = player
        self.mana = self.player.mana
    def update(self):
        self.image = copy(self.bg)
        mana = self.mana
        if self.mana > self.player.mana:
            if self.mana-5 < self.player.mana:
                self.mana = self.player.mana
            else:
                self.mana -= 5
        elif self.mana < self.player.mana:
            if self.mana+5 > self.player.mana:
                self.mana = self.player.mana
            else:
                self.mana += 5    
        if mana>0:
            for i in range(0,mana,8)[:-1]:
                self.image.blit(self.part,[i+8,2])            
            self.image.blit(self.part,[mana+8-8,2])
            if mana == self.player.max_mana:
                self.image.blit(self.end_img,[192,2])
        self.image.convert_alpha()
        

class Hint(pygame.sprite.Sprite):
    def __init__(self,game):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([120,120])
        self.rect = self.image.get_rect()
        self.size = self.image.get_size()
        self.rect.x = 10
        self.rect.y = screen_size[1] - 130
        self.game = game
        self.font = pygame.font.SysFont("Calibri",14)
        self.image.set_colorkey(BLACK)
        for i,m in enumerate(game.player_left.creatures):
            text = self.font.render(str(i)+": "+m.__name__,False,BLUE)
            self.image.blit(text,[5,i*10])
    def update(self):
        pass

class CameraMan():
    def __init__(self,game):
        self.game = game
        self.camera_speed = 15
        
    def update_camera(self):
        if len(self.game.player_left.army)+len(self.game.player_right.army) == 0:
            self.final_position = self.game.length/2
            self.camera_speed = 15
        elif len(self.game.player_left.army)== 0:
            farest = [-100,None]
            for u in self.game.player_right.army:
                if u.direction*(u.center_x-u.player.base.pos[0]) > farest[0]:
                    farest = [u.direction*(u.center_x-u.player.base.pos[0]),u]
            self.final_position = max([self.game.size[0]/2,min([self.game.length-self.game.size[0]/2,farest[1].center_x])])
        else:
            farest = [-1,None]
            for u in self.game.player_left.army:
                if u.direction*(u.center_x-u.player.base.pos[0]) > farest[0]:
                    farest = [u.direction*(u.center_x-u.player.base.pos[0]),u]
            self.final_position = max([self.game.size[0]/2,min([self.game.length-self.game.size[0]/2,farest[1].center_x])])  
        self.update_position()
    
    def update_position(self):
        if self.final_position == self.game.screen_center_x:
            pass
        elif abs(self.final_position-self.game.screen_center_x) < self.camera_speed:
            self.game.screen_center_x = self.final_position
        elif self.game.screen_center_x < self.final_position:
            self.game.screen_center_x += self.camera_speed
        elif self.game.screen_center_x > self.final_position:
            self.game.screen_center_x -= self.camera_speed
            
class Game():
    def __init__(self):
        self.all_battlefield_sprites = pygame.sprite.Group()
        self.obstacles = []
        self.all_foreground_sprites = pygame.sprite.Group()
        self.screen_center_x = size[0]/2
        self.length = length
        self.fps = fps
        self.size = size
        self.creatures = SWC_Units.getUnits()
        self.all_costs = SWC_Units.getCosts()
        self.all_upgrades = SWC_Units.getUpgrades()
        self.all_cooldowns = SWC_Units.getCooldowns()
        self.all_effects = []
        self.paused = False
        self.temporary_sprites = pygame.sprite.Group()
        self.all_animations = []
        self.health_bars = []
        self.mouse = Mouse()
        self.all_foreground_sprites.add(self.mouse)
        
        self.img_bg1 = pygame.transform.scale(pygame.image.load(random.choice(["Img/bg_snow.jpg","Img/bg_desert.jpg"])),(length,size[1])).convert()

        self.minimap = MiniMap(self)        
        self.all_foreground_sprites.add(self.minimap)
        #self.hint = Hint(self)
        #self.all_foreground_sprites.add(self.hint)
        self.battlescreen = pygame.Surface(self.size)
        self.creators_bar = pygame.image.load("Img/BarreDesTaches.png")
        self.creators_bar.convert_alpha()
        self.creators_bar_size = self.creators_bar.get_size()
        self.alpha = 255
        self.alpha_change = -1
        self.active_upgraders = []
        self.active_upgraders2 = []
        self.last_creature_time = 100
        self.skull_image = pygame.image.load("Img/dark_skull.png")
        self.goldscore_image = pygame.image.load("Img/gold_score.png")
        self.goldscore_image.convert_alpha()
        self.defeated = None
        self.dramatic_entrance_effect = 0
#        
        self.default_font = pygame.font.SysFont("Verdana",18)
        
        self.magister = None
            
    def initialize(self):
        self.player_left.adv = self.player_right
        self.player_right.adv = self.player_left
        
        for player in [self.player_left,self.player_right]:
            player.initialise()
        
        if self.magister:
            self.magister.initialise()
        
        
        if 0 and self.MODE == "pvp":
            self.display = self.splitDisplay
            self.bgImg = pygame.Surface((length,self.size[1]/2))
            self.bgImg.blit(img_bg1,[0,-self.size[1]/2])
            self.player_right.base_copy = BaseCopy(self.player_right.base,0,-size[1]/2)
            self.player_left.base_copy = BaseCopy(self.player_left.base,0,-size[1]/2)
            self.buttons_bar_mid = pygame.transform.scale(pygame.image.load("Img/bottom_bar.png"),[screen_size[0],(screen_size[1]-size[1])/2]).convert() 
            self.buttons_bar = pygame.transform.scale(pygame.image.load("Img/bottom_bar.png"),[screen_size[0],screen_size[1]-size[1]]).convert() 
        elif self.MODE == "pvp" or self.MODE == "battle":
            self.display = self.normalDisplay
            self.bgImg = self.img_bg1
            self.buttons_bar = pygame.transform.scale(pygame.image.load("Img/bottom_bar.png"),[screen_size[0],screen_size[1]-size[1]]).convert()       
            self.camera_man = CameraMan(self)
        else:
            self.display = self.normalDisplay
            self.bgImg = self.img_bg1
            self.buttons_bar = pygame.transform.scale(pygame.image.load("Img/bottom_bar.png"),[screen_size[0],screen_size[1]-size[1]]).convert()

        for player in self.player_left,self.player_right:
            for i,m in enumerate(self.TURRETS):
                a = i+(len(self.TURRETS)<2)
                self.all_battlefield_sprites.add(m(self,player,[player.base.turret_pos[a][0]+player.base.center_x-player.base.size[0]/2,player.base.turret_pos[a][1]+size[1]-550]))
                
        self.time = 0
        
        for n,unit in enumerate(self.player_left.creatures):
            cr_b = CreatorButton(size[0]/2-3*110+109*n,size[1]+17,pygame.image.load("Img/Creators/"+unit.creator_image),unit,self,self.player_left,n)
            self.all_foreground_sprites.add(cr_b)
            self.player_left.creators.append(cr_b)
            cr_b.setUpgradeButton(SelectForUpgradeButton((cr_b.rect.x+45+30,cr_b.rect.y+45+30),pygame.image.load("Img/upgrade_button.png"),cr_b))        
        self.upgrade_selection = UpgradeSelection(pygame.image.load("Img/creator_selection.png"),cr_b)
        self.refreshUpgrades(self.player_left.creatures[0],self.player_left)
        self.upgrade_selection.goTo(cr_b)
        
        if self.DOUBLE_CREATURE_BAR:
            for n,unit in enumerate(self.player_right.creatures):
                cr_b2 = CreatorButton(size[0]/2-3*110+109*n,size[1]+100,pygame.image.load("Img/Creators/"+unit.creator_image),unit,self,self.player_right,n)
                self.all_foreground_sprites.add(cr_b2)
                self.player_right.creators.append(cr_b2)
                cr_b2.setUpgradeButton(SelectForUpgradeButton((cr_b2.rect.x+45+30,cr_b2.rect.y+45+30),pygame.image.load("Img/upgrade_button.png"),cr_b2))
            self.upgrade_selection2 = UpgradeSelection(pygame.image.load("Img/creator_selection.png"),cr_b2)
            self.upgrade_selection2.goTo(cr_b2)
            self.refreshUpgrades(self.player_right.creatures[0],self.player_right)
        """
        for n,spell in enumerate(self.player_right.spells):
            spl = SpellButton(size[0]/2+450-2*60+60*n,110,pygame.transform.scale(pygame.image.load("Img/Creators/"+spell.icon),(50,50)),spell,self,self.player_right)
            self.all_foreground_sprites.add(spl) """       
        self.mana_bar = ManaBar(self,self.player_left)
        """self.all_foreground_sprites.add(self.mana_bar)"""
        
    def refreshUpgrades(self,unit,player):
        upgraders_list = [self.active_upgraders,self.active_upgraders2][player==self.player_right]
        for u in copy(upgraders_list):
            del upgraders_list[0]
            u.kill()
        for e,u in enumerate(player.upgrades[unit]):
            upgr = Upgrader(self.getUpgradePos(e,player),u,self,player,u.level)
            upgraders_list.append(upgr)
            self.all_foreground_sprites.add(upgr)
            if u.level != 1:
                print("error")
    
    def defaultUpgradeButtonPosition(self,e,player):
        return [size[0]/2-250+250*e,size[1]+110]
        
    def pvpUpgradeButtonPosition(self,e,player):
        return [[120,size[0]-120][player==self.player_right],size[1]+40+50*e]

    def resetUpgrades(self):
        for player in [self.player_left,self.player_right]:            
            for p in player.upgrades.values():
                for u in p:
                    u.level = 0
                    u.levelUp()        
        self.refreshUpgrades(self.upgrade_selection.button.unit,self.player_left)
        if self.DOUBLE_UPGRADES:
            self.refreshUpgrades(self.upgrade_selection2.button.unit,self.player_right)
    
    def upgraders_refresh(self):
        for u in self.active_upgraders:
            u.refresh()
        for u in self.active_upgraders2:
            u.refresh()

    def update(self):
        self.time += 1
        """
        if random.randrange(150) == 99:
            self.all_battlefield_sprites.add(Unit(self,self.player_right))
            self.all_battlefield_sprites.add(Unit(self,self.player_left))
        """   
        prev_time = time.time()
        
        self.mouse_pos = pygame.mouse.get_pos()
        self.click = False
        self.l_shift = pygame.key.get_pressed()[pygame.K_LSHIFT]
        self.r_shift = pygame.key.get_pressed()[pygame.K_RSHIFT]
        
        self.alpha += self.alpha_change
        if self.alpha<150:
            self.alpha_change = 1
        elif self.alpha>255:
            self.alpha_change = -1      
        
        all_events = pygame.event.get()
        for event in all_events:
            if event.type == pygame.QUIT:
                self.done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click = True
            
            if event.type == pygame.KEYDOWN:
                """
                for e,creature in enumerate(self.creatures):
                    if event.key == eval("pygame.K_KP"+str(e)):
                        self.all_battlefield_sprites.add(creature(self,self.player_right))
                        self.player_right.open_base()
                    if event.key == eval("pygame.K_"+str(e)):
                        self.all_battlefield_sprites.add(creature(self,self.player_left))
                        self.player_left.open_base()
                """
                if event.key == pygame.K_p:
                    for e in self.player_right.army:
                        e.effects.append(SWC_Units.Plague(e,self))
                    for e in self.player_left.army:
                        e.effects.append(SWC_Units.Plague(e,self))
                if event.key == pygame.K_SPACE:
                    self.resetUpgrades()
                if event.key == pygame.K_ESCAPE:
                    self.paused = not(self.paused)
                if event.key == pygame.K_RSHIFT:
                    self.r_shift = True
                if event.key == pygame.K_LSHIFT:
                    self.l_shift = True
                if event.key == pygame.K_z:
                    for unit in self.player_left.army.sprites()+self.player_right.army.sprites():
                        print(unit.__class__.__name__,unit.center_x,unit.attacking,unit.blocked)
                        print(unit.center_y)
                self.click = True #weird
                self.player_left.key_pressed(event,self.l_shift)
                self.player_right.key_pressed(event,self.r_shift)
        if not(self.paused):
            if self.time%15==0:  print("time spent on part 1: ",round((time.time()-prev_time)*1000,3)," ns")
            prev_time = time.time()
            
        if self.MODE == "pvp" or self.MODE=="battle":
            self.camera_man.update_camera()
        else:
            if self.mouse_pos[0] < 100:
                self.screen_center_x = max([size[0]/2,self.screen_center_x-40])
            elif self.mouse_pos[0] > (size[0]-100):
                self.screen_center_x = min([length-size[0]/2,self.screen_center_x+40])
        
        if self.magister:
            self.magister.update()
         
        if not(self.paused):
            if self.last_creature_time < 100:
                if len(self.player_left.army)+len(self.player_right.army)==0:
                    self.last_creature_time += 1
            
            for a in self.all_animations:
                a.animate()
            for e in self.all_effects:
                e.update()
            for unit in self.player_left.army.sprites()+self.player_right.army.sprites():
                unit.played_this_turn = False
            
            if self.time%15==0: print("time spent on part 2-3: ",round((time.time()-prev_time)*1000,3)," ns");prev_time = time.time()
            self.all_battlefield_sprites.update()
            if self.time%15==0: print("time spent on part 4: ",round((time.time()-prev_time)*1000,3)," ns");prev_time = time.time()
            self.all_foreground_sprites.update()
            if self.time%15==0: print("time spent on part 5: ",round((time.time()-prev_time)*1000,3)," ns");prev_time = time.time()
            self.player_left.update()
            self.player_right.update()
            if self.time%15==0: print("time spent on part 6: ",round((time.time()-prev_time)*1000,3)," ns");prev_time = time.time()
                
            for army in [self.player_right.army,self.player_left.army]:
                for crea in army:
                    crea.update()
            if self.time%15==0: print("time spent on part 7: ",round((time.time()-prev_time)*1000,3)," ns");prev_time = time.time()
            
            for s in self.temporary_sprites:
                s.imageUpdate()
                s.posUpdate()
        else:
            for u in self.all_battlefield_sprites.sprites()+self.player_left.army.sprites()+self.player_right.army.sprites():
                u.posUpdate()
        
        self.mouse.update()
        for b in self.health_bars:
            self.health_bars.remove(b)
            b.kill()
        """
        if self.HB_MODE == "manual":
            for c in pygame.sprite.spritecollide(self.mouse,self.player_left.army,False)+pygame.sprite.spritecollide(self.mouse,self.player_right.army,False):
                hp_bar = HealthBar(c)
                self.all_foreground_sprites.add(hp_bar)
                self.health_bars.append(hp_bar)                
            for b in [self.player_left.base,self.player_right.base]:#,self.player_left.base_copy,self.player_right.base_copy]:
                if is_around(self.mouse.rect.x+self.screen_center_x-size[0]/2,b.pos[0]-b.swift+350,100) and is_around(self.mouse.rect.y,b.pos[1],250):
                    hp_bar = HealthBar(b)
                    self.all_foreground_sprites.add(hp_bar)
                    self.health_bars.append(hp_bar)"""
        if 1: #self.HB_MODE == "automatic" -> always:
            for c in self.player_left.army:
                hp_bar = HealthBar(c)
                self.all_foreground_sprites.add(hp_bar)
                self.health_bars.append(hp_bar)
            for c  in self.player_right.army:
                hp_bar = HealthBar(c)
                self.all_foreground_sprites.add(hp_bar)
                self.health_bars.append(hp_bar)
            for b in [self.player_left.base,self.player_right.base]:
                hp_bar = HealthBar(b)
                self.all_foreground_sprites.add(hp_bar)
                self.health_bars.append(hp_bar)
        
        if self.dramatic_entrance_effect!=0:
            self.dramatic_entrance_effect-=1
    
    def last_phase(self):
        print("Initialise Last Phase")
        done = False
        images = []
        if SOUND:
            pygame.mixer.music.fadeout(1000)
        time.sleep(1)
        if self.defeated==self.player_right:
            images.append("Img/Victory.png")
        elif self.defeated==self.player_left:
            images.append("Img/Defeat.png")
        if AUKTAV:
            images.append("Img/itisnotall.png")
            images.append("Img/youwontescape.png")
            images.append("Img/withoutussaying.png")
            images.append("Img/gateau-d-anniversaire.png")
        if SOUND:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("Sounds/Deceptive.mp3")
            pygame.mixer.music.play(-1)
        for i in images:
            if i == "Img/gateau-d-anniversaire.png" and SOUND:
                pygame.mixer.music.stop()
                pygame.mixer.music.load("Sounds/HP.mp3")
                pygame.mixer.music.play(-1)
            for a in range(10):
                if done:
                    break
                for event in pygame.event.get():
                     if event.type == pygame.QUIT:
                        done = True
                if a == 8 and i == images[-1] and SOUND:
                    pygame.mixer.music.fadeout(1000)
                elif a == 8 and i == "Img/withoutussaying.png" and SOUND:
                    pygame.mixer.music.fadeout(1000)
                screen.fill(BLACK)
                img = pygame.image.load(i)
                screen.blit(img,[screen_size[0]/2-img.get_size()[0]/2,screen_size[1]/2-img.get_size()[1]/2])
                pygame.display.flip()
                if i == "Img/withoutussaying.png":
                    clock.tick(0.75)
                elif i == "Img/gateau-d-anniversaire.png":
                    clock.tick(0.5)
                else:
                    clock.tick(1)
            
                
    def end(self,player):
        self.done = True
        self.defeated = player
    
    def damageEffect(self,unit,damage,color=RED):
        effect = damageEffect(unit,damage,self,color)
        self.all_effects.append(effect)
    
    def defaultUnitsOfPlayer(self,player):
        return SWC_Units.getUnitsOfPlayer(player)
    
    def testUnitsOfPlayer(self,player):
        return SWC_Units.getUnitsOfPlayer(player)
    
    def customUnitsOfPlayer(self,player):
        if player==self.player_left:
            return self.units_of_player["1"]
        else:
            return self.units_of_player["2"]
        
    def splitDisplay(self,screen):
        zone_1 = pygame.Surface([self.size[0],self.size[1]/2])
        
        zone_1.blit(self.bgImg,(0-game.screen_center_x + size[0]/2,-self.size[1]/2))
        zone_1.blit(self.player_left.base_copy.image,[self.player_left.base_copy.pos[0]-self.player_left.base_copy.swift+size[0]/2-self.screen_center_x,self.player_left.base_copy.pos[1]])
        zone_1.blit(self.player_right.base_copy.image,[self.player_right.base_copy.pos[0]-self.player_right.base_copy.swift+size[0]/2-self.screen_center_x,self.player_right.base_copy.pos[1]])
        
        for s in self.all_battlefield_sprites.sprites()+self.temporary_sprites.sprites():
            zone_1.blit(s.image,[s.rect.x,0])
        for e in self.all_effects:
            zone_1.blit(e.image,[e.rect[0],e.rect[1]])
        
        """"""
        
        zone_2 = pygame.Surface([self.size[0],self.size[1]/2])
        
        zone_2.blit(self.bgImg,(0-game.screen_center_x + size[0]/2,-self.size[1]/2))
        zone_2.blit(self.player_left.base.image,[self.player_left.base.pos[0]-self.player_left.base.swift+size[0]/2-self.screen_center_x,self.player_left.base.pos[1]-screen_size[1]/2])
        zone_2.blit(self.player_right.base.image,[self.player_right.base.pos[0]-self.player_right.base.swift+size[0]/2-self.screen_center_x,self.player_right.base.pos[1]-screen_size[1]/2])
        
        for s in self.all_battlefield_sprites.sprites()+self.temporary_sprites.sprites():
            zone_2.blit(s.image,[s.rect.x,s.rect.y-screen_size[1]/2])
        for e in self.all_effects:
            zone_2.blit(e.image,[e.rect[0],e.rect[1]-screen_size[1]/2])
        
        self.battlescreen.blit(zone_1,[0,0])
        self.battlescreen.blit(zone_2,[0,screen_size[1]/2])
        self.battlescreen.set_alpha(self.alpha)
        
        screen.blit(self.battlescreen,[0,0])
        screen.blit(self.buttons_bar_mid,[0,size[1]/2])        
        screen.blit(self.buttons_bar,[0,size[1]])
        screen.blit(self.creators_bar,[size[0]/2-self.creators_bar_size[0]/2,size[1]+20-self.creators_bar_size[1]/2])
        
        self.all_foreground_sprites.draw(screen)

        if self.last_creature_time == 100:
            screen.blit(self.skull_image,(size[0]/2-60,200-168))
        
        font = pygame.font.SysFont("Verdana",18)
        img=copy(self.goldscore_image)
        text = font.render(str(self.player_left.fund),True,(90,0,90))
        img.blit(text,(20,0))
        screen.blit(img,(10,60))
        text = font.render(str(self.player_right.fund),True,(90,0,90))
        img=copy(self.goldscore_image)
        img.blit(text,(20,0))
        screen.blit(img,(size[0]-80,60))
        
    def normalDisplay(self,screen):
#        self.battlescreen.fill((250,250,250))
        screen.blit(self.bgImg,(0-game.screen_center_x + size[0]/2,0))        
        screen.blit(self.player_left.base.image,[self.player_left.base.pos[0]-self.player_left.base.swift+size[0]/2-self.screen_center_x,self.player_left.base.pos[1]])
        screen.blit(self.player_right.base.image,[self.player_right.base.pos[0]-self.player_right.base.swift+size[0]/2-self.screen_center_x,self.player_right.base.pos[1]])
        
        if self.time%15==0: prev_time = time.time()
        for army in [self.player_left.army,self.player_right.army]:
            for crea in army:
                #(w,h,x,y) = crea.hit_box
                #pygame.draw.rect(screen,(25,25,25),(crea.rect.x+x,crea.rect.y+y,w,h),4)
                #crea.b3 -= 1 #a supprimer
                crea.blit_on_surface(screen)
                #pygame.draw.rect(screen,(150,150,0),(crea.center_x + self.size[0]/2-self.screen_center_x-4,crea.center_y-4,8,8),0)
                #screen.blit(crea.image, [crea.rect.x,crea.rect.y])
        if self.time%15==0: print("display : time spent for the display of creatures: ",round((time.time()-prev_time)*1000,3)," ns");prev_time = time.time()
        
        self.all_battlefield_sprites.draw(screen)
        self.temporary_sprites.draw(screen)
        for e in self.all_effects:
            screen.blit(e.image,e.rect)
#        self.battlescreen.set_alpha(self.alpha)
#        
#        screen.blit(self.battlescreen,[0,0])
        screen.blit(self.buttons_bar,[0,size[1]])
        screen.blit(self.creators_bar,[size[0]/2-self.creators_bar_size[0]/2,size[1]+20-self.creators_bar_size[1]/2])
#        
        self.all_foreground_sprites.draw(screen)

        if self.last_creature_time == 100:
            screen.blit(self.skull_image,(size[0]/2-60,200-168))
#        
#        #barre d'alignement en bas, à enlever
#        screen.blit(pygame.Surface((3000,10)),[0,750])
        img=copy(self.goldscore_image)
        text = self.default_font.render(str(self.player_left.fund),True,(90,0,90))
        img.blit(text,(20,0))
        screen.blit(img,(10,60))
        text = self.default_font.render(str(self.player_right.fund),True,(90,0,90))
        img=copy(self.goldscore_image)
        img.blit(text,(20,0))
        screen.blit(img,(size[0]-100,60))
        
        if self.dramatic_entrance_effect!=0 and 0: #option desactivated
            screen.fill((255, 100+(155*15)//(15+self.dramatic_entrance_effect), 100+(155*15)//(15+self.dramatic_entrance_effect), 0), None, pygame.BLEND_RGBA_MULT)
        
        text = self.default_font.render(str(int(clock.get_fps())),True,(90,0,200))
        screen.blit(text,(10,120))
        pass

AUKTAV = False
try:
        pygame.mixer.init()
        SOUND = True
except:
        SOUND = False
    
if SOUND:    
    pygame.mixer.music.load("Sounds/Time.mp3")
    pygame.mixer.music.play(-1)
    son_cor=pygame.mixer.Sound("Sounds/cor.wav")
    
fps = 30

def runGame(game_):
    global screen
    screen = pygame.display.set_mode(screen_size)
    global game
    game = game_    #removed "Img/bg_night.jpg"  

    game.initialize()
    global clock
    clock = pygame.time.Clock()
    game.done = False
    i=0
    while not(game.done):
        i=(i+1)%1000
        screen.fill((0,0,0))
        init_time = time.time()
        game.update()
        second_time = time.time()
        #print("\ntime for game.update()",round((second_time-init_time)*1000,2),"ms")
        game.display(screen)
        third_time = time.time() 
        #print("time for game.display()",round((third_time-second_time)*1000,2),"ms")
        pygame.display.flip()
        fourth_time = time.time()
        #print("time for flip",round((fourth_time-third_time)*1000,2),"ms")
        clock.tick(fps)

    if game.defeated!=None:
        game.last_phase()

if __name__ == "__main__":
    screen = pygame.display.set_mode(screen_size)
    game = Game()
    game.MODE = ["pvp","pv1","pv2","test","battle","planned"][1]
    if game.MODE == "test" or game.MODE == "planned":
        game.PLAYERS = (HumanPlayer,HumanPlayer2)
        game.GOLDATTHEBEGINING = 100000
        game.COOLDOWNS = False
        game.HB_MODE = "manual"
        game.DOUBLE_UPGRADES = True
        game.DOUBLE_CREATURE_BAR = True
        game.getUnitsOfPlayer = game.testUnitsOfPlayer
        game.getUpgradePos = game.pvpUpgradeButtonPosition
        if game.MODE == "planned":
            game.magister = Magister(game)
            game.COOLDOWNS = True
    else:
        game.GOLDATTHEBEGINING = 0
        game.COOLDOWNS = True
        if game.MODE == "pvp":
            game.PLAYERS = (HumanPlayer,HumanPlayer2)
            game.getUpgradePos = game.pvpUpgradeButtonPosition
            game.DOUBLE_CREATURE_BAR = True
            game.DOUBLE_UPGRADES = True
            game.HB_MODE = "automatic"
        if game.MODE in ["pv1","pv2"]:
            game.DOUBLE_UPGRADES = False
            game.HB_MODE = "manual"
            game.PLAYERS = (HumanPlayer,[ComputerPlayer,ComputerPlayer2][game.MODE=="pv2"])
            game.DOUBLE_CREATURE_BAR = False
            game.getUpgradePos = game.pvpUpgradeButtonPosition
        if game.MODE=="battle":
            game.DOUBLE_UPGRADES = False
            game.HB_MODE = "automatic"
            game.PLAYERS = (ComputerPlayer,ComputerPlayer)
            game.DOUBLE_CREATURE_BAR = True
            game.getUpgradePos = game.defaultUpgradeButtonPosition
        game.getUnitsOfPlayer = game.defaultUnitsOfPlayer
    game.TURRETS = [SWC_Units.CrossBow]
    
    game.player_left = game.PLAYERS[0](game,"left",200,["Img/bastion.png","Img/bastion_open.png"],430,[[490,315],[350,30],[200,310]])
    game.player_right = game.PLAYERS[1](game,"right",length-350,["Img/castle.png","Img/castle_open.png"],150,[[270,300],[535,290],[413,130]])
    
    runGame(game)
    pygame.quit()

