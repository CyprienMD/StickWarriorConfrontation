# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 16:15:54 2016

@author: test
"""
from types import FunctionType,MethodType
from Animation import Animation,ProjectileAnimation,Fade,ImageEffect,OscilationY
import random
import math
import pygame
from copy import copy

GREEN = (0,0,255)

class Power():
    attack_range = 30
    damage_type = "physical"
    def __init__(self,monster):
        self.monster = monster
    
    def initialise(self,monster):
        pass
    
    def update(self):
        pass
    
    def death(self,source):
        pass

    def damage_before(self,enemy):
        return 0
    
    def get_add_magic_dps(self,enemy):
        return 0
    
    def get_magic_att_add(self,enemy):
        return 0
    
    def get_physic_att_add(self,enemy):
        return 0

    def modify_taken_dps(self,dps,enemy):
        return dps

class PowerOnAttack(Power):
    attack_range = 30
    damage_type = "physical"
    def __init__(self,monster,attack):
        self.monster = monster
        self.attack = attack

class MummyInvocation(PowerOnAttack):
    only_once = True
    def initialise(self,monster):
        self.attack.functiunEffects.append(self.invocation)
        from SWC_Units import Mummy
        self.invocation_type = Mummy
    
    def invocation(self,attack,target):
        creature = self.invocation_type(self.monster.game,self.monster.player)
        creature.setPosition([target.center_x+random.choice([35,40,45,50,55])*(-self.monster.direction),creature.center_y])
        creature.origin = "Invocation"
        #creature.game.all_battlefield_sprites.add(creature)
        if hasattr(self.monster,"mummy_number"):
            ancient_die = creature.die
            def d(creature_self,cause,animation=True):
                ancient_die(cause,animation)
                self.monster.mummy_number -= 1
            creature.die = MethodType(d,creature)
            
            self.monster.mummy_number += 1
        #attack.functiunEffects.remove(self.invocation)


def color_surface(surface, color_to_change, color):
    arr = pygame.surfarray.pixels3d(surface)
    for a in range(len(arr)):
        for b in range(len(arr[len(arr)-1])):
            if [arr[a,b,0],arr[a,b,1],arr[a,b,2]]==color_to_change:
                arr[a,b,0] = color[0]
                arr[a,b,1] = color[1]
                arr[a,b,2] = color[2]

class Charge(Power):
    bonus = 2
    multiplicator = 3.0
    def initialise(self,monster):
        self.done = False

        self.bonus = self.bonus+(12*self.monster.magic_power_bonus)/100
        self.multiplicator = self.multiplicator+round((self.monster.magic_power_bonus*1.5)/100.0,2)
        self.monster.cooldown = self.monster.game.fps*60/self.monster.att_speed
        self.initial_speed = self.monster.speed
        self.monster.speed = self.initial_speed*2

        self.ancient_inflict = self.monster.attacks[0].inflict
        def new_inflict(attack_self,target=None):
            multiplicator=self.multiplicator*(self.monster.actual_speed-3)/15.
            attack_self.last_target.receive(int(attack_self.physical_damage*multiplicator+self.bonus),attack_self.magical_damage,attack_self)
            self.monster.attacking = False
            #attack_self.hit = MethodType(self.ancient_inflict,attack_self)
            #self.monster.speed = self.initial_speed
            #self.monster.initStepAnimation = self.mInitStepAnimation
            #attack_self.animation = self.mHitAnimation
        
        self.monster.attacks[0].inflict = MethodType(new_inflict,self.monster.attacks[0])
        self.mInitStepAnimation,self.mHitAnimation = self.monster.initStepAnimation,self.monster.attacks[0].animation
        if hasattr(monster,"initChargeAnimation"):
            print("use of monsters init charge animation")
            self.monster.initStepAnimation = self.monster.initChargeAnimation        
        else:
            print("no charge animation")
        if hasattr(monster,"hitChargeAnimation"):
            self.monster.attacks[0].animation = self.monster.hitChargeAnimation
            
    def update(self):
        pass
        # inutile depuis que les dégats dépendent de la vitesse
        """
        if self.monster.blocked and not(self.done):
            if not(self.monster.attacking):
                self.monster.attacks[0].inflict = self.ancient_inflict
                self.monster.initStepAnimation = self.mInitStepAnimation
                self.monster.attacks[0].animation = self.mHitAnimation
                self.monster.speed = self.initial_speed    
                self.done = True
        elif self.monster.blocked:
            print("charge cancelled")"""

    def damages_before(self,enemy):
        return (self.monster.attacks[0].physical_damages*self.multiplicator+self.bonus)*(100-enemy.armor)/100

class OneTry(Power):
    def initialise(self,monster):
        self.ancient_inflict = FunctionType(self.monster.attacks[0].inflict.__code__,globals(),closure=self.monster.attacks[0].inflict.__closure__) 
        def new_inflict(attack_self,target=None):
            if target == None:
                target = attack_self.last_target
            target.receive(int(attack_self.physical_damage),attack_self.magical_damage,attack_self)
            self.monster.attacking = False
            self.monster.die(self)
            print("dead ")
        self.monster.attacks[0].inflict = MethodType(new_inflict,self.monster.attacks[0])
        self.mInitStepAnimation,self.mHitAnimation = self.monster.initStepAnimation,self.monster.attacks[0].animation
        if hasattr(monster,"initChargeAnimation"):
            self.monster.initStepAnimation = self.monster.initChargeAnimation        
        if hasattr(monster,"hitChargeAnimation"):
            self.monster.attacks[0].animation = self.monster.hitChargeAnimation
    
        
class Teleport(Power):
    power_range = 400
    loading = 10.0
    multiplicator = 2.5
    aditional = 10
    attack_range = 30
    react_range  = 100
    def initialise(self,monster):     
        self.cooldown = 0
        self.last_target = None
        self.power_range = self.power_range*(100+self.monster.magic_power_bonus)/100
        self.aditional = int(self.aditional*(100+self.monster.magic_power_bonus*2)/100)
        self.loading = self.loading*(100-self.monster.magic_power_bonus)/100
        if not(hasattr(monster,"assassinateAnimation")):
            def assassinateAnimation(creature_self,enemy):
                creature_self.attacking = True
                creature_self.last_target = enemy
                self.last_target = enemy
                creature_self.cooldown = 0
                pos_x,pos_y = creature_self.left_arm.getPosition()
                size_x,size_y = creature_self.left_arm.size
                angle = creature_self.left_arm.angle
                phase1 = [(pos_x,pos_y),7,0,None,angle-20]
                phase2 = [(pos_x,pos_y),3,0,None,angle+170]
                phase3 = [(pos_x,pos_y),7,0,self.inflict,angle]
                creature_self.animations.append(Animation(creature_self.left_arm,[phase1,phase2,phase3],creature_self))
            def hit(creature_self,enemy):
                #print("attacked"
                pass
            monster.assassinateAnimation = MethodType(assassinateAnimation,monster)
            monster.hitAnimation  = MethodType(hit,monster)
            
    def inflict(self):
        if self.last_target.targetable:
            self.last_target.receive(int(self.monster.attacks[0].physical_damage*self.multiplicator),self.aditional,self)
        self.monster.attacking = False
        
    def update(self):
        if self.cooldown < self.loading*self.monster.game.fps:
            self.cooldown += 1
        
        weakest = [None,9000000000]
        need_to_react = False
        if self.cooldown>=self.loading*self.monster.game.fps and self.monster.attacking == False and not(self.last_target and self.last_target.hp > 0):
            for enemy in self.monster.enemies:
                distance = abs(self.monster.center_x+(self.monster.size[0]/8)*self.monster.direction-enemy.center_x-(enemy.size[0]/8)*enemy.direction)
                health = enemy.hp
                if distance < self.power_range:
                    if distance < self.react_range:
                        need_to_react = True
                    if  health < weakest[1]:
                        weakest = [enemy,health]
                        #print("minimum health is ",weakest[1]
            if weakest[0] and (weakest[0].hp < self.monster.attacks[0].physical_damage*self.multiplicator+self.aditional or need_to_react):
                enemy = weakest[0]
                #print(need_to_react,self.monster.attacks[0].physical_damage*self.multiplicator+self.aditional
                #print("Assassinate"
                self.monster.center_x = enemy.center_x +(enemy.size[0]/8)*enemy.direction -(self.monster.size[0]/8)*self.monster.direction
                self.monster.assassinateAnimation(enemy)
                self.last_target = enemy
                self.cooldown = 0
    
    def damages_before(self,enemy):
        return (self.monster.attacks[0].physical_damages*self.multiplicator+self.additional)*(100-enemy.armor)/100

class ManaBloodshed(Power):
    damage_mult = 1.5
    attack_speed_mult = 1.5
    cooldown = 0.4
    decrease_cd = 0.4
    def initialise(self,monster):
        from SWC_Units import UnalterableProjectile
        self.new_projectiles = UnalterableProjectile
        self.active = False
        self.time = 0
        self.time_since_enemies = 0
        self.game = monster.game
        #self.cooldown = round(self.cooldown*(100.0-self.monster.magic_power_bonus)/100,3)
        self.monster.att_speed_beforembs = self.monster.att_speed
        self.monster.speed_beforembs = self.monster.speed
        for a in self.monster.attacks:
            a.magical_damage_beforembs = a.magical_damage
            if hasattr(a,"projectile"):
                a.projectile_beforembs = a.projectile            
            if hasattr(a,"projectile_image"):
                a.projectile_image_beforembs = a.projectile_image
        self.monster_img_mode = "normal"
        
    def update(self):
        self.time += 1
        if not(self.active):
            if self.time >= int(self.cooldown*self.game.fps):
                self.monster.mana = min([self.monster.max_mana,self.monster.mana+1])
                self.time = 0
        else:
            if self.time >= int(self.decrease_cd*self.game.fps):
                self.monster.mana = max([0,self.monster.mana-2])
                self.time = 0
        
        if not(self.active) and self.monster.mana==self.monster.max_mana:
            if hasattr(self.monster,"beginManaRageMode") and self.monster_img_mode != "rage":
                self.monster.beginManaRageMode()
                self.monster_img_mode = "rage"
            if  self.enemiesInRange():
                self.active = True
                self.time_since_enemies = 0
                self.monster.att_speed = int(self.monster.att_speed*self.attack_speed_mult)
                self.monster.speed = 0                
                up_to_air_anim = Animation(self.monster,[[[self.monster.center_x,self.monster.center_y-50],40,None,self.initOscilation,None]],self.monster)
                self.monster.animations.append(up_to_air_anim)
                for a in self.monster.attacks:
                    a.magical_damage = int(a.magical_damage*self.damage_mult)
                    if hasattr(a,"projectile"):
                        a.projectile = self.new_projectiles
                        a.projectile_image ="Img/fire_orb.png"
                        a.damages_on_base = 0.5
                
                self.m_ancient_receive=self.monster.receive
                def r(creature_self,damage,magic_damage,attack):
                    if max([((damage)*(100-creature_self.armor))/100+((magic_damage)*(100-creature_self.magic_resistance))/100,1])>=creature_self.hp:
                        creature_self.hp = 1
                    else:
                        self.m_ancient_receive(damage,magic_damage,attack)
                self.monster.receive = MethodType(r,self.monster)
                    
        enemies = self.enemiesInRange()
        if self.active and not(enemies):
            self.time_since_enemies += 1
        elif self.active and enemies:
            self.time_since_enemies = 0
        
        if self.active and (self.monster.mana==0 or self.time_since_enemies>self.game.fps*2):
            self.active = False
            self.monster.mana=0
            self.monster.att_speed = self.monster.att_speed_beforembs
            try:
                self.monster.receive = self.m_ancient_receive
            except:
                print(self," error for new receive")
            for a in self.monster.attacks:
                a.magical_damage = a.magical_damage_beforembs
                a.damages_on_base = 1.0
                if hasattr(a,"projectile"):
                    a.projectile = a.projectile_beforembs
                if hasattr(a,"projectile_image"):
                    a.projectile_image = a.projectile_image_beforembs
            if hasattr(self.monster,"endManaRageMode"):
                self.monster.endManaRageMode()
                self.oscilation_anim.shouldStop()
                self.monster_img_mode = "normal"

    def initOscilation(self):
        print("Center Y of Purifier",self.monster.center_y)
        self.oscilation_anim = OscilationY(self.monster,20,self.endOscilation,self.monster)
        self.monster.animations.append(self.oscilation_anim)
        self.monster.step_stopped = True
    
    def endOscilation(self):
        print("end oscillation called")
        print("Center Y of Purifier",self.monster.center_y    )  
        back_to_earth_anim = Animation(self.monster,[[[self.monster.center_x,self.monster.center_y+50],40,None,self.reset_monster_speed,None]],self.monster)
        self.monster.animations.append(back_to_earth_anim)
       
    def reset_monster_speed(self):
        print("reset monster speed called")
        print("Center Y of Purifier",self.monster.center_y)
        #if self.monster.step_stopped:
        self.monster.blocked = True
        #self.monster.initStepAnimation()        
        self.monster.speed = self.monster.speed_beforembs
        
    def enemiesInRange(self):        
        for enemy in self.monster.enemies:
            if self.monster.get_distance(enemy)< self.monster.attack.attack_range and self.monster.center_x*self.monster.direction<enemy.center_x*self.monster.direction:
               return True
        if -(self.monster.center_x*self.monster.direction-self.monster.player.adv.base.pos[0]*self.monster.direction) < self.monster.attacks[0].attack_range+40:
            return True
        return False    

 
class Heal(Power):
    heal_points = 6
    loading = 1.3
    power_range = 250
    def initialise(self,monster):     
        self.cooldown = 0
        from SWC_Units import AllieProjectile
        self.projectile = AllieProjectile
        self.projectileMaker = monster.makeProjectile
        self.heal_points = self.heal_points*(100+self.monster.magic_power_bonus)/100
        def healAnimation(creature_self,allie):
            for member in creature_self.left_arm,creature_self.right_arm:
                member.resetPosition()
            creature_self.attacking = True
            creature_self.last_target = allie
            self.last_target = allie
            creature_self.cooldown = 0
            pos_x,pos_y = creature_self.left_arm.getPosition()
            size_x,size_y = creature_self.left_arm.size
            angle = creature_self.left_arm.angle
            mod = float(creature_self.game.fps*60)/(60/self.loading)
            phase1 = [(pos_x,pos_y),int(0.7*mod),0,None,angle+170]
            phase2 = [(pos_x,pos_y),int(0.1*mod),0,None,None]
            phase3 = [(pos_x,pos_y),int(0.1*mod),0,self.shoot,angle]
            creature_self.animations.append(Animation(creature_self.left_arm,[phase1,phase2,phase3],creature_self))
        if hasattr(monster,"healAnimation"):
            pass
        else:
            monster.healAnimation = MethodType(healAnimation,monster)
    def heal(self,allie): 
        allie.hp = min([allie.max_hp,allie.hp+self.heal_points])
        self.cooldown = 0
        self.monster.game.damageEffect(allie,"+"+str(self.heal_points),color=GREEN)   
        self.monster.attacking = False
        
    def inflict(self):
        self.last_target.receive(int(self.monster.attacks[0].physical_damage*self.multiplicator),self.aditional,self)
        self.monster.attacking = False
        
    def update(self):
        if self.cooldown < self.loading*self.monster.game.fps:
            self.cooldown += 1
        
        if self.cooldown>=self.loading*self.monster.game.fps and self.monster.attacking == False:
            for allie in self.monster.allies:
                if allie != self.monster:
                    distance = abs(self.monster.center_x+(self.monster.size[0]/8)*self.monster.direction-allie.center_x-(allie.size[0]/8)*allie.direction)
                    if distance < self.power_range and allie.hp<allie.max_hp:
                        self.monster.healAnimation(allie)
        
    def shoot(self):
        ally = self.last_target
        projectile = self.projectileMaker(ally,self)
        self.monster.game.all_battlefield_sprites.add(projectile)
        self.monster.attacking = False
                      

class Dodge(Power):
    level = 40
    def initialise(self,monster):
        self.level =int(self.level *(100+self.monster.magic_power_bonus/2)/100)
        ancient_receive = FunctionType(self.monster.receive.__code__,globals(),closure=self.monster.receive.__closure__)
        def r(creature_self,damage,magic_damage,attack):
            if attack.damage_type != "force" and random.randrange(1,100) in range(1,self.level):
                self.monster.game.damageEffect(self.monster,"Missed")
            else:
                MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
        self.monster.receive = MethodType(r,self.monster)

class MagicShield(Power):
    level = 60
    damage_type = "force"
    def initialise(self,monster):
        ancient_receive = FunctionType(self.monster.receive.__code__,globals(),closure=self.monster.receive.__closure__)
        self.level = self.level*(100+self.monster.magic_power_bonus)/100
        def r(creature_self,damage,magic_damage,attack):
            hp = self.monster.hp
            MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
            """
            if hasattr(attack,"monster"):
                attack.monster.receive(0,(damage + magic_damage)*self.level/100,self)
            """
            if hasattr(attack,"source") and not(hasattr(attack,"is_effect")):
                attack.source.receive(0,int(min([damage + magic_damage,hp])*self.level/100),self)
            """
            else:
                print("ERROR"
            """
        self.monster.receive = MethodType(r,self.monster)

class NatureSpirit(Power):
    def initialise(self,monster):
        self.done = False

    def death(self,source):
        if not(self.done):
            if hasattr(source,"source"):
                if hasattr(source.source,"source"):
                    source.source.source.new_effect(IvyGrip,self)
                elif hasattr(source.source,"monster"):
                    source.source.monster.new_effect(IvyGrip,self)
                elif hasattr(source.source,"new_effect"):
                    source.source.new_effect(IvyGrip,self)
            if hasattr(source,"monster") and hasattr(source.monster,"new_effect"):
                source.monster.new_effect(IvyGrip,self)
            self.done = True

class ThorianSpeed(Power):
    level = 50
    def initialise(self,monster):
        ancient_receive = FunctionType(self.monster.receive.__code__,globals(),closure=self.monster.receive.__closure__)
        def r(creature_self,damage,magic_damage,attack):
            if attack.attack_range > 150 and attack.source.instance_type!= "turret" and random.randrange(1,100) in range(1,self.level):
                self.monster.game.damageEffect(self.monster,"Missed")
            else:
                MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
        self.monster.receive = MethodType(r,self.monster)

class Regeneration(Power):
    cooldown = 0.4
    def initialise(self,monster):
        self.time = 0
        self.game = self.monster.game
    def update(self):
        self.time += 1
        if self.time >= int(self.cooldown*self.game.fps):
            self.monster.hp = min([self.monster.max_hp,self.monster.hp+1])
            self.time = 0

class ManaRegeneration(Power):
    cooldown = 0.4
    def initialise(self,monster):
        self.time = 0
        self.game = self.monster.game
        #self.cooldown = round(self.cooldown*(100.0-self.monster.magic_power_bonus)/100,3)
    def update(self):
        self.time += 1
        if self.time >= int(self.cooldown*self.game.fps):
            self.monster.mana = min([self.monster.max_mana,self.monster.mana+1])
            self.time = 0
        

class Heroism(Power):
    threshold = 15
    threshold2 = 9
    armor = 50
    armor2 = 70
    att_speed = 1.5 # multiplicator
    def initialise(self,monster):
        self.done1 = False
        self.done2 = False
        self.base_armor = monster.armor
        ancient_receive = FunctionType(self.monster.receive.__code__,globals(),closure=self.monster.receive.__closure__)
        def r(creature_self,damage,magic_damage,attack):
            MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
            if creature_self.hp < self.threshold and not(self.done1):
                creature_self.armor = self.armor
                creature_self.att_speed = int(creature_self.att_speed * self.att_speed  ) 
                self.done1 = True
            if creature_self.hp < self.threshold2 and not(self.done2):
                creature_self.armor = self.armor2
                self.done2 = True
        self.monster.receive = MethodType(r,self.monster)
    
    def update(self):
        if self.done1 and self.monster.hp > self.threshold:
            self.monster.armor = self.base_armor
            self.monster.att_speed = int(self.monster.att_speed/self.att_speed  ) 
            self.done1 = False
        if self.done2 and self.monster.hp > self.threshold2:
            if self.monster.hp < self.threshold:
                self.monster.armor = self.armor
            else:
                self.monster.armor = self.base_armor
            self.done2 = False
            

class HealingSword(Power):
    heal = 4
    def initialise(self,monster):
        ancient_hit = FunctionType(self.monster.attacks[0].inflict.__code__,globals(),closure=self.monster.attacks[0].inflict.__closure__)
        def i(attack_self,target=None):
            MethodType(ancient_hit,attack_self)(target)
            h = int(self.heal+(4.0*self.monster.magic_power_bonus)/100)
            self.monster.hp = min([self.monster.hp+h,self.monster.max_hp])
            self.monster.game.damageEffect(self.monster,"+"+str(h),color=GREEN)
            #print("healed"
        self.monster.attacks[0].inflict = MethodType(i,self.monster.attacks[0])

class RenegadeSpawn(Power):
    lifes = 1.0
    speed_mult = 0.7
    att_speed_mult = 0.7
    def initialise(self,monster):
        self.magic_power_bonus = self.monster.magic_power_bonus
        self.last_target = None        
        
        for a in self.monster.attacks:
            ancient_hit = a.inflict
            def new_inflict(attack_self,target=None):
                if not(target):
                    m = attack_self.last_target
                else:
                    m= target
                if m.__class__.__name__ != "Base" and not(m.is_a_zombie) and not(m.origin == "Invocation"):          
                    ancient_d,ancient_da = m.die,m.deathAnimation
                    def riseAnimation():
                        print("begining of a dead rising by ",self.monster)
                        for e in reversed(m.animations):
                            e.stop()
                        for i in m.getRibsOrder():
                            i.resetPosition()
                            color_surface(i.graphism,[0,0,0],[230,230,230])
                            for image in i.potential_images:
                                color_surface(image,[0,0,0],[230,230,230])
                            i.imageUpdate()
                        m.direction = self.monster.direction
                        pos_x,pos_y = m.getPosition()
                        print("initial m pos is now ",self.initial_m_pos)
                        phase1 = [(pos_x,self.initial_m_pos),30,0,takeControl,None]
                        m.animations.append(Animation(m,[phase1],m))
                        
                    def takeControl():
                        while m in self.monster.game.obstacles: #devrait arriver une fois exactement
                            self.monster.game.obstacles.remove(m)
                        print("took control over ",self.monster)
                        monster = self.monster
                        if not(abs(m.center_y-self.initial_m_pos)<3):
                            print("error monster center y is not what it is supposed to be")
                            print(m.center_y,self.initial_m_pos)
                        for e in reversed(m.effects):
                            e.death()
                            m.effects.remove(e)
                        m.max_hp = m.max_hp*(100+self.magic_power_bonus)/100
                        m.hp = int(m.max_hp*self.lifes)
                        m.speed = int(m.speed*self.speed_mult)
                        m.att_speed = int(m.att_speed*self.speed_mult)
                        m.attacking = False
                        m.cooldown = 0
                        m.enemies = monster.enemies
                        #m.deathAnimation = self.ancient_da
                        m.allies = monster.allies
                        m.player = monster.player
                        m.direction = self.monster.direction
                        m.is_a_zombie = True
                        m.is_dead = False
                        #monster.game.all_battlefield_sprites.add(m)
                        monster.player.army.add(m)
                        m.game.temporary_sprites.remove(m)
                        #for p in m.powers:
                        #    p.initialise(m)
                        #    print(p," re initialised")
                        if not(any([p.__class__ == RenegadeSpawn for p in m.powers])):
                            r = RenegadeSpawn(m)
                            m.powers.append(r)
                            r.initialise(m)
                            r.magic_power_bonus = self.magic_power_bonus

                    def new_death(creature_self,source,animation=True):
                        ancient_d(source,animation=True)
                        creature_self.game.temporary_sprites.add(creature_self)
                    def deathAnimationPart1(creature_self):
                        print("begining of a dead possession by ",self.monster)
                        pos_x,pos_y = creature_self.getPosition()
                        self.initial_m_pos = pos_y
                        phase1 = [(pos_x,pos_y+creature_self.size[1]),30,0,riseAnimation,None]
                        a = Animation(creature_self,[phase1],creature_self)
                        
                        
                        for anim in creature_self.animations:
                            if anim.subject == creature_self and anim.paused == False:
                                a.pause(anim)
                            else:
                                anim.stop()
            
                        creature_self.animations.append(a)
                    m.die,m.deathAnimation = MethodType(new_death,m),MethodType(deathAnimationPart1,m)
                    print("attacks ",m)
                    ancient_hp = m.hp
                    print("ancient inflict called with target = ",target)
                    ancient_hit(target=target)
                    if m.hp <= 0 and ancient_hp > 0:
                        self.last_target = m
                        self.monster.game.obstacles.append(m)
                    m.die,m.deathAnimation = ancient_d,ancient_da
                else:
                    ancient_hit(target=target)
            
            a.inflict = MethodType(new_inflict,a)
        print("power renegade is initialised for ",monster)
        #self.last_target = None

class Critical(Power):
    effects = [1,"os","os",3,3,3]
    chances = [0,40,20,20,20,20]
    def initialise(self,monster):
        ancient_inflict = monster.attacks[0].inflict
        def inflict(attack_self,enemy):
            if not(enemy.__class__.__name__ == "Base"):
                lev = enemy.level
                if random.randrange(100)<self.chances[lev]:
                    print("Critical!")
                    if self.effects[lev] =="os":
                        self.monster.game.damageEffect(enemy,"One Shot")
                        enemy.die(attack_self)
                    else:
                        attack_self.physical_damage *= self.effects[lev]
                        ancient_inflict(enemy)
                        attack_self.physical_damage /= self.effects[lev]
                else:
                    ancient_inflict(enemy)
            else:
                ancient_inflict(enemy)
        monster.attacks[0].inflict_range_damage = MethodType(inflict,monster.attacks[0])
                    
        

class MassAttack(Power):
    max_target = 3
    zone_length = 200
    def initialise(self,monster):
        self.attack = self.monster.attacks[0]
        def new_inflict(attack_self,target=None):
            attack_self.last_target.receive(attack_self.physical_damage,attack_self.magical_damage,attack_self)
            attacked = 1
            for enemy in self.monster.enemies:
                if enemy!=attack_self.last_target and abs(enemy.center_x-self.monster.last_target.center_x)<self.zone_length/2:
                    attacked += 1
                    enemy.receive(attack_self.physical_damage,attack_self.magical_damage,attack_self)
                    if attacked > self.max_target-1:
                        break
            self.monster.attacking = False
            self.imageEffect(attack_self.last_target)
        self.attack.inflict = MethodType(new_inflict,self.attack)
        
    
    def imageEffect(self,monster):
        pass

class PriorityPass(Power):
    destination = "base"
    
    def update(self):
        for ally in self.monster.allies:
            if ally != self:
                if (not(ally.stealth) and self.monster.center_x*self.monster.direction<ally.center_x*self.monster.direction) and (self.monster.get_distance(ally) < 5 or (self.monster.get_distance(ally)+(ally.speed * (1-ally.played_this_turn))<self.monster.speed*2)):
                     if ally.level<self.monster.level and not(self.monster.attacking):
                         self.monster.throwAnimation(ally,None)
                         self.last = ally
                         self.throw()
    def throw(self):
        #self.monster.attacking = False
        ally = self.last
        ally.targetable = False
        for unit in ally.player.adv.army:
            if unit.attacking and unit.last_target == ally:
                unit.attack.interrupt() #en espèrant sque l'attaque séléctionnée est toujours la bonne
        if ally.attacking:
            ally.attack.interrupt()
        ally.new_effect(Stun,self)
        ally.player.army.remove(ally)
        ally.game.temporary_sprites.add(ally)
        def res(unit_self):
            ally.player.army.add(ally)
            ally.targetable = True
            ally.game.temporary_sprites.remove(ally)
        ally.restart = MethodType(res,ally)
        dest_x = [ally.player.base.pos[0]+ally.direction*100,self.monster.center_x-ally.direction*200][self.destination=="behind"]
        time = int((abs(ally.center_x-dest_x)/1000+0.6)*self.monster.game.fps)
        ally.animations.append(ProjectileAnimation(ally,[dest_x,ally.center_y],time,[400,200][self.destination=="behind"],ally.restart))
        

class PriorityPassZombies(PriorityPass):
    destination = "behind"
    def update(self):
        for ally in self.monster.allies:
            if ally != self:
                if not(ally.stealth) and self.monster.get_distance(ally) < 5 and self.monster.center_x*self.monster.direction<ally.center_x*self.monster.direction:
                     if ally.level<self.monster.level and ally.is_a_zombie and not(self.monster.attacking):
                         self.monster.throwAnimation(ally,None)
                         self.last = ally
                         self.throw()    


class PriorityPassNinja(PriorityPass):
    def update(self):
        for ally in self.monster.allies:
            if ally != self:
                if not(ally.stealth) and self.monster.get_distance(ally) < 5 and self.monster.center_x*self.monster.direction<ally.center_x*self.monster.direction:
                     if not(self.monster.attacking):
                         self.monster.throwAnimation(ally,None)
                         self.last = ally
                         self.throw()       

class SealedKilled(Power):
    level = 5
    def initialise(self,monster):
        self.attack = self.monster.attacks[0]
        def new_inflict(attack_self,target=None):
            damage = attack_self.physical_damage+int((self.level+(5.0*self.monster.magic_power_bonus)/100)*[isinstance(p,Seal) for p in attack_self.last_target.effects].count(True))
            print(attack_self.physical_damage,damage)
            attack_self.last_target.receive(damage,attack_self.magical_damage,attack_self)
            attack_self.source.attacking = False
            for e in attack_self.effects:
                if not(any([eff.__class__ == e for eff in attack_self.last_target.effects]) and e.cummulable == False)  and [eff.__class__ == e for eff in attack_self.last_target.effects].count(True)<e.max_cummulation:
                    attack_self.last_target.new_effect(e,self)
        self.attack.inflict = MethodType(new_inflict,self.attack)

class PainDevouration(Power):
    level = 1
    waiting_time = 150
    wait = True
    size_increase = 8
    def initialise(self,monster):
        self.received_before = {}
        self.monsters_touched = []
        self.bonus = 0
        self.size_additional = 0
        for m in self.monster.allies:
            if m != self.monster:
                self.effect(m)
        
        if self.wait:
            self.initial_speed = self.monster.speed
            self.monster.stealth = True
            self.monster.speed = 0
            self.time = self.waiting_time
        
        """
        ancient_getImage = FunctionType(self.monster.get_image.__code__,globals(),closure=self.monster.get_image.__closure__)
        def gI(creature_self):
            image = MethodType(ancient_getImage,creature_self)()
            image = pygame.transform.scale(image,[self.monster.size[0]+self.size_additional,self.monster.size[1]+self.size_additional])
            return image
        self.monster.get_image = MethodType(gI,self.monster)
        """
                
    def effect(self,m):
                ancient_receive = FunctionType(m.receive.__code__,globals(),closure=m.receive.__closure__)
                def r(creature_self,damage,magic_damage,attack):
                    MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
                    self.monster.max_hp += int(self.level*2+(self.monster.magic_power_bonus*2.0)/100)
                    self.monster.hp += int(self.level*2+(self.monster.magic_power_bonus*2.0)/100)
                    print("+",self.bonus)
                    self.bonus = range(self.level+1)[1-self.bonus]
                    for a in self.monster.attacks:
                        a.physical_damage += self.bonus
                    """
                    for p in self.monster.getRibsOrder():
                        p.setSize([(p.size[0]*105)/100,(p.size[1]*105)/100],swift=True)
                    self.monster.size = [(self.monster.size[0]*105)/100,(self.monster.size[1]*105)/100]
                    """
                    self.monster.setSize([self.monster.size[0]+self.size_increase,self.monster.size[1]+self.size_increase])
                    self.monster.posUpdate()
                m.receive = MethodType(r,m)
                self.received_before[m] = ancient_receive
                self.monsters_touched.append(m)
                
    def death(self,source):
        for m in self.monsters_touched:
            if m.hp > 0:
                m.receive = MethodType(self.received_before[m],m)
    
    def update(self):
        if self.time:
            self.time -= 1
            if not(self.time):
                self.monster.stealth = False
                self.monster.speed = self.initial_speed
                self.monster.initStepAnimation()
                
        for m in self.monster.enemies.sprites()+self.monster.allies.sprites():
            if m!= self.monster and not(m in self.monsters_touched):
                self.effect(m)
                print("a new enemy is touched")
                
        
    
    def imageEffect(self,monster):
        pass

class FireAura(Power):
    cooldown = 2.0
    attack_range = 30
    power_range = 300
    damage = 20
    damage_per_second = 1
    damage_type = "fire"
    def initialise(self,monster):
        self.time = 0
        self.time0 = 0
        self.damage = 10*(100+self.monster.magic_power_bonus)/100
    def update(self):
        self.time += 1
        self.time0 += 1
        if self.time >= self.monster.game.fps*self.cooldown:
            self.time = 0
            for m in self.monster.enemies:
                if abs(m.center_x-self.monster.center_x)<self.power_range:
                    m.receive(0,self.damage,self)
            for m in self.monster.allies:
                if abs(m.center_x-self.monster.center_x)<self.power_range and m != self.monster:
                    m.receive(0,self.damage,self)            
            self.imageEffect(self.monster)
        if self.time0 >= self.monster.game.fps/self.damage_per_second:
            self.monster.hp -= 1
            if self.monster.hp < 1:
                self.monster.die(self)
            self.time0 = 0
    
    def imageEffect(self,monster):
        ie = ImageEffect([monster.center_x,690],"Img/mur-des-flammes.png",15,self.monster.game)
        self.monster.animations.append(Fade(ie,[[17,10,None]],self.monster))
        self.monster.game.all_battlefield_sprites.add(ie)

class EffectAura(Power):
    power_range = 300
    def initialise(self,monster):
        self.effect = self.get_effect()
        self.image_did = False
        self.power_range = self.power_range*(100+self.monster.magic_power_bonus)/100
    def update(self):
        for m in self.get_target():
            if m!= self.monster and abs(m.center_x-self.monster.center_x)<self.power_range:
                has = False
                for e in m.effects:
                    if isinstance(e,self.effect):
                        e.cooldown = 0
                        has = True
                if not(has):
                    m.new_effect(self.effect,self)
                if not(self.image_did):
                    self.image_did = True
                    self.imageEffect()
    def imageEffect(self):
        pass

class CourageAura(EffectAura):
    power_range = 230
    def get_target(self):
        return self.monster.allies
    def get_effect(self):
        return Courage

class WeaknessAura(EffectAura):
    def get_effect(self):
        return Weakness
        
    def get_target(self):
        return self.monster.enemies

class CrowAura(WeaknessAura):
    image_effect = False
    def imageEffect(self):
        class CrowImageEffect(pygame.sprite.Sprite):
            def __init__(self,unit,delay,game):
                pygame.sprite.Sprite.__init__(self)
                self.unit = unit
                self.dying = False
                self.alpha = 255
                self.center_x = unit.getPosition()[0]
                self.center_y = unit.bottom_y-70
                self.game = game
                self.delay = delay
                self.phase_time = 0
                self.animations = []
                self.all_crows = []                
                self.crow_image_size = [60,75]
                self.crow_image = pygame.transform.scale(pygame.image.load("Img/crow1.png"),self.crow_image_size)
                self.crow_image2 = pygame.transform.scale(pygame.image.load("Img/crow2.png"),self.crow_image_size)
                class Crow():
                    pass
                for c in range(20):
                    crow=Crow()
                    crow.center_x,crow.center_y = [250,100]
                    crow.direction = random.randrange(360)
                    crow.wing = 0
                    crow.time = random.randint(0,4)
                    self.all_crows.append(crow)
                self.makeImage()
                self.size = self.image.get_size()
                self.rect = self.image.get_rect()                
                self.rect.x = self.center_x + self.game.size[0]/2 - self.game.screen_center_x -self.size[0]/2
                self.rect.y = self.center_y -self.size[1]/2
            
            def makeImage(self):
                self.image = pygame.Surface([500,200])
                self.image.fill((0,0,0))
                for c in self.all_crows:
                    if c.direction>=270 or c.direction<=90:
                        flip = False
                    else:
                        flip = True
                    c_i = pygame.transform.rotate([self.crow_image,self.crow_image2][c.wing],180*flip+c.direction*(1-flip*2))
                    if flip:
                        c_i = pygame.transform.flip(c_i,1,0)
                    self.image.blit(c_i,[c.center_x-self.crow_image_size[0]/2,c.center_y-self.crow_image_size[1]/2])
                self.image.set_colorkey((0,0,0))
                self.image.convert_alpha()
                
            def update(self):
                if self.delay:
                    self.phase_time += 1
                    if self.phase_time > self.delay-1:
                        for a in self.animations:
                            a.stop()
                        self.kill()
                    
                for c in self.all_crows:
                    c.center_x += math.cos(math.radians(c.direction))*5
                    c.center_y -= math.sin(math.radians(c.direction))*5
                    c.time += 1
                    if c.time == 5:
                        c.wing = 1-c.wing
                        c.time = 0
                    
                    if c.center_x > 500-self.crow_image_size[0]/2 or c.center_x <= self.crow_image_size[0]/2:
                        c.direction = (180-c.direction)%360
                        print(c.direction)
                    if c.center_y > 200-self.crow_image_size[0]/2 or c.center_y<=self.crow_image_size[0]/2:
                        c.direction = (-c.direction)%360
                        print(c.direction)
                
                if self.dying:
                    del self.all_crows[0]
                    if not(self.all_crows):
                        self.kill()
                self.makeImage()
                self.posUpdate()
            
            def posUpdate(self):
                self.center_x = self.unit.getPosition()[0]
                self.center_y = self.unit.bottom_y-70
                self.rect.x = self.center_x + self.game.size[0]/2 - self.game.screen_center_x -self.size[0]/2
                self.rect.y = self.center_y -self.size[1]/2
                
        
            def imageUpdate(self):
                self.image.set_alpha(self.alpha)
            
            def die(self):
                self.dying = True
        
        ie = CrowImageEffect(self.monster,10000000000,self.monster.game)
        self.image_effect = ie
        self.monster.game.all_battlefield_sprites.add(ie)

    def death(self,source):
        if self.image_effect:
            self.image_effect.die()
                
class EffectImmunity(Power):
    def initialise(self,monster):
        ancient_new_effect = FunctionType(self.monster.new_effect.__code__,globals(),closure=self.monster.new_effect.__closure__)
        def n_e(creature_self,effect,cause):
            if effect==Seal or effect==Courage or effect==Stun:                
                MethodType(ancient_new_effect,creature_self)(effect,cause)
            else:
                pass
        self.monster.new_effect = MethodType(n_e,self.monster)


class FireImmunity(Power):
    def initialise(self,monster):
        ancient_receive = FunctionType(self.monster.receive.__code__,globals(),closure=self.monster.receive.__closure__)
        def r(creature_self,damage,magic_damage,attack):
            if attack.damage_type != "fire":
                MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
        self.monster.receive = MethodType(r,self.monster)

class ManaRageImmunity(Power):
    def initialise(self,monster):
        ancient_receive = FunctionType(self.monster.receive.__code__,globals(),closure=self.monster.receive.__closure__)
        def r(creature_self,damage,magic_damage,attack):
            if attack.damage_type != "mana":
                MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
            else:
                if hasattr(attack,"source"):
                    if attack.source.player==self.monster.player.adv :
                        MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
        self.monster.receive = MethodType(r,self.monster)

class SkullBuff(Power):
    level = 50
    def initialise(self,monster):
        ancient_receive = FunctionType(self.monster.receive.__code__,globals(),closure=self.monster.receive.__closure__)#voir des lignes similaires pour compléter si nécessaire
        #self.monster.head.setImage("Img/dark_skull.png")
        self.spoilt = False
        def r(creature_self,damage,magic_damage,attack):
            if monster.hp < max([((damage)*(100-self.monster.armor))/100+((magic_damage)*(100-self.monster.magic_resistance))/100,1]) and not(self.spoilt):
                self.spoilt = True
                self.monster.hp = 5+self.monster.max_hp/20
                self.monster.game.damageEffect(self.monster," -"+str(int(max([((damage)*(100-self.monster.armor))/100+((magic_damage)*(100-self.monster.magic_resistance))/100,0]))))
            else:
                if hasattr(attack,"source") and not(hasattr(attack,"is_effect")) and attack.source.instance_type=="turret":                        
                    MethodType(ancient_receive,creature_self)(int(damage*self.level/100),int(magic_damage*self.level/100),attack)
                else:
                    MethodType(ancient_receive,creature_self)(damage,magic_damage,attack)
        
        self.monster.receive = MethodType(r,self.monster)
        


class Lightning(MassAttack):
    max_target = 3
    zone_length = 200
    def imageEffect(self,monster):
        ie = ImageEffect([monster.center_x,350],"Img/lightning_bolt.png",15,self.monster.game)
        self.monster.animations.append(Fade(ie,[[10,10,None]],self.monster))
        self.monster.game.all_battlefield_sprites.add(ie)

class HeavySword(MassAttack):
    max_target = 3
    zone_length = 150

class Effect():
    cummulable = False
    is_effect = True
    max_cummulation = 1
    attack_range = 30
    damage_type = "physical"
    def __init__(self,monster,cause):
        self.source = cause        
        self.initialise(monster)
    def update(self):
        pass
    def death(self):
        pass

class Slow(Effect):
    duration = 5
    multiplicator = 0.2
    def initialise(self,monster):
        self.initial_speed = monster.speed
        self.monster= monster
        monster.speed *= self.multiplicator
        self.cooldown = 0
    def update(self):
        self.cooldown += 1
        if self.cooldown >= self.duration*self.monster.game.fps:
            self.end()
    def end(self):
        self.monster.speed = self.initial_speed
        self.monster.effects.remove(self)

class Weakness(Slow):
    duration = 3
    speed_multiplicator = 0.2
    armor_multiplicator = 0.5
    damage_multiplicator = 0.5
    def initialise(self,monster):
        self.initial_speed = monster.speed
        monster.speed *= self.speed_multiplicator
        self.initial_damages = [a.physical_damage for a in monster.attacks]
        for a in monster.attacks:
            a.physical_damage = int(a.physical_damage * self.damage_multiplicator)
        self.initial_armor = monster.armor
        monster.armor = int(self.armor_multiplicator*monster.armor)
        self.monster= monster
        self.cooldown = 0
    def update(self):
        self.cooldown += 1
        if self.cooldown >= self.duration*self.monster.game.fps:
            self.end()
    def end(self):
        self.monster.speed = self.initial_speed
        for e,a in enumerate(self.monster.attacks):
            a.physical_damage = self.initial_damages[e]
        self.monster.armor = self.initial_armor
        self.monster.effects.remove(self)

class Courage(Effect):
    duration = 3
    speed_multiplicator = 1
    armor_bonus = 20
    magic_resistance_bonus = 20
    damage_multiplicator = 1.3
    att_speed_multiplicator = 1.5
    def initialise(self,monster):
        self.initial_speed = monster.speed
        monster.speed *= self.speed_multiplicator
        self.initial_damages = [a.physical_damage for a in monster.attacks]
        for a in monster.attacks:
            a.physical_damage = int(a.physical_damage * self.damage_multiplicator)
        self.initial_armor = monster.armor
        monster.armor = int(self.armor_bonus+monster.armor)
        self.initial_mr = monster.magic_resistance
        if monster.magic_resistance<80:
            monster.magic_resistance = int(self.magic_resistance_bonus+monster.magic_resistance)
        self.initial_att_speed = monster.att_speed
        monster.att_speed = int(self.att_speed_multiplicator*monster.att_speed)
        self.monster= monster
        self.cooldown = 0
    def update(self):
        self.cooldown += 1
        if self.cooldown >= self.duration*self.monster.game.fps:
            self.end()
    def end(self):
        self.monster.speed = self.initial_speed
        for e,a in enumerate(self.monster.attacks):
            a.physical_damage = self.initial_damages[e]
        self.monster.armor = self.initial_armor
        self.monster.magic_resistance = self.initial_mr
        self.monster.att_speed = self.initial_att_speed
        self.monster.effects.remove(self)

class WeaknessHex(Weakness):
    duration = 8

class Stun(Effect):
    duration = 2
    def initialise(self,monster):
        self.monster= monster
        self.attacking_before = monster.attacking
        monster.attacking = True
        monster.blocked=True
        self.cooldown = 0
        for a in self.monster.animations:
            a.pause(self)
    def update(self):
        self.monster.blocked=True
        self.cooldown += 1
        if self.cooldown >= self.duration*self.monster.game.fps:
            self.end()
    def end(self):
        self.monster.attacking = self.attacking_before
        for a in self.monster.animations:
            if a.paused and a.pause_factor==self:
                a.run()
        print("STUN ended")
        #♠print("attacking before: ",self.attacking_before)
        self.monster.effects.remove(self)

class ArmorDestruction(Effect):
    multiplicator = 0.6
    def initialise(self,monster):
        self.monster= monster
        monster.armor = int(monster.armor * self.multiplicator)
    def update(self):
        self.end()
    def end(self):
        self.monster.effects.remove(self)

class Seal(Effect):
    cummulable = True
    activing_num = 5
    max_cummulation = 5
    def initialise(self,monster):
        self.monster= monster
        if [isinstance(p,self.__class__) for p in self.monster.effects].count(True) > self.activing_num-2:
            self.monster.new_effect(FireCurse,self.source)
    def end(self):
        self.monster.effects.remove(self)

class Poison(Effect):    
    duration = 10
    damage_per_second = 4
    def initialise(self,monster):
        self.monster= monster
        self.cooldown = 0
    def update(self):
        self.cooldown += 1
        if self.cooldown >= self.duration*self.monster.game.fps:
            self.end()
        if self.cooldown%int(1.0*self.monster.game.fps/self.damage_per_second) == 0:
            self.monster.hp -= 1
            if self.monster.hp < 1:
                self.monster.die(self)
    def end(self):
        self.monster.effects.remove(self)

class IvyGrip(Effect):    
    duration = 6
    damage_per_second = 2
    speed_mult = 0.25
    cummulable = False
    damage_type = "magical"
    def initialise(self,monster):
        self.monster= monster
        self.cooldown = 0
        self.monster_initial_speed = self.monster.speed
        self.monster.speed = max([int(self.monster.speed*self.speed_mult),1])
    def update(self):
        self.cooldown += 1
        if self.cooldown >= self.duration*self.monster.game.fps:
            self.end()
        if self.cooldown%int(2.0*self.monster.game.fps/self.damage_per_second) == 0:
            self.monster.receive(0,2,self)
    def end(self):
        self.monster.speed = self.monster_initial_speed
        self.monster.effects.remove(self)


  
class FireCurse(Poison): 
    damage_per_second = 7
    """
    def __init__(self,monster):
        self.monster= monster
        self.cooldown = 0        
        self.damage_per_second = (self.damage_per_second+(10*monster.magic_power_bonus)/100)
        print("Fire Curse damages = ",self.damage_per_second
    """

class Plague(Poison):    
    damage_per_second = 15 #*2
    def initialise(self,monster):
        self.monster= monster
        self.cooldown = 0
        self.damage_per_second = min([monster.hp/100 + self.__class__.damage_per_second,20 ])
    def update(self):
        self.cooldown += 1
        if self.cooldown >= self.duration*self.monster.game.fps:
            self.end()
        if self.cooldown%int(1.0*self.monster.game.fps/self.damage_per_second) == 0:
            self.monster.hp -= 2
            if self.monster.hp < 1:
                self.monster.die(self,animation=False)

