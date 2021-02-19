# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 18:35:14 2016

@author: test
"""
import pygame
import SWC_Units
import SWC_The_Game2
from copy import copy

SWC_The_Game = SWC_The_Game2

RED = (255,0,0)
ORANGE = (255,120,0)
BLUE = [10,30,190]
BLACK = [0,0,0]

size = [1000,900]
screen = pygame.display.set_mode(size)

class Button(pygame.sprite.Sprite):
    def __init__(self,game,pos,image_name,functiun,args,text=None):
        pygame.sprite.Sprite.__init__(self)
        
        self.game = game
        self.functiun = functiun
        self.args = args
        self.image_name = image_name
        self.text = text
        
        self.makeImage(image_name,text)
        
        self.rect = self.image.get_rect()
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.rect.x = pos[0]-self.size[0]/2
        self.rect.y = pos[1]-self.size[1]/2
        
    def makeImage(self,image_name,text,size=None):
        self.image = pygame.image.load(image_name)
        if size:
            self.image = pygame.transform.scale(self.image,size)
            self.size = size
        else:
            self.size = self.image.get_size()
        self.image.convert_alpha()

    def update(self):
        if self.game.clicked and abs(self.game.mouse_pos[0]-self.center_x)<self.size[0]/2 and abs(self.game.mouse_pos[1]-self.center_y)<self.size[1]/2:
            self.functiun(*self.args)
    
    def refresh_image(self):
        self.makeImage(self.image_name,self.text)

class FloatingImage(Button):
    def __init__(self,game,pos,image_name,size=None,text=None):
        pygame.sprite.Sprite.__init__(self)        
        self.game = game        
        self.makeImage(image_name,text,size)        
        self.rect = self.image.get_rect()
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.rect.x = pos[0]-self.size[0]/2
        self.rect.y = pos[1]-self.size[1]/2
    
    def update(self):
        pass

class FloatingText(pygame.sprite.Sprite):
    def __init__(self,game,pos,text,font):
        pygame.sprite.Sprite.__init__(self)        
        self.game = game        
        self.makeImage(text,font)        
        self.rect = self.image.get_rect()
        self.center_x = pos[0]
        self.center_y = pos[1]
        self.rect.x = pos[0]-self.size[0]/2
        self.rect.y = pos[1]-self.size[1]/2
        
    def makeImage(self,text,font):
        self.image = pygame.Surface(font.size(text))
        self.size = self.image.get_size()
        #font = pygame.font.SysFont("Times New Roman",text_size)
        image_text = font.render(text,False,ORANGE)
        self.image.blit(image_text,[0,0])
        self.image.set_colorkey(BLACK)

class UnitDescription(FloatingImage):
    def __init__(self,game,pos,image_name,unit,size):
        self.unit_class = unit
        FloatingImage.__init__(self,game,pos,image_name,size,text=None)
        
    def makeImage(self,image_name,text,size):
        if image_name:
            self.image = pygame.image.load(image_name)
            self.image = pygame.transform.scale(self.image,size)
            self.size = self.image.get_size()
        else:
            self.image = pygame.Surface(size)
            self.size = size
        font = pygame.font.SysFont("Times New Roman",25)
        text = font.render(self.unit_class.__name__,False,[0,20,0])
        self.image.blit(text,[55,20])
        font = pygame.font.SysFont("Times New Roman",18)
        text3="";text = []
        for let in self.unit_class.description :
            text3+=let
            if let==" " and len(text3)>50:            
                text.append(text3)
                text3=""
        text.append(text3)
        for i,t in enumerate(text) :
                line = font.render(t,False,(0,20,0))
                self.image.blit(line,(55,60+i*25))
        self.image.set_colorkey([0,0,0])

class TextButton(Button):
    def makeImage(self,image_name,text,size=None):
        self.image = pygame.image.load(image_name)
        if size:
            self.image = pygame.transform.scale(self.image,size)
            self.size = size
        else:
            self.size = self.image.get_size()
        text_size = 30-(len(text)>12)*(len(text)-12)*2
        font = pygame.font.SysFont("Times New Roman",text_size)
        image_text = font.render(text,False,BLUE)
        self.image.blit(image_text,[int(self.size[0]/2-len(text)*text_size/4.5),21])
        self.image.convert_alpha()

class ButtonSelection(pygame.sprite.Sprite):
    def __init__(self,image,button):
        pygame.sprite.Sprite.__init__(self)        
        self.image = image
        self.image.set_colorkey(BLACK)
        self.size = self.image.get_size()
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.game = button.game
        self.button = button
        
        self.button.image.blit(self.image,self.rect)
    
    def goTo(self,button):
        self.button.refresh_image()
        
        self.button = button
        self.rect.x = 0
        self.rect.y = 0
        self.button.image.blit(self.image,self.rect)
        
    def update(self):
        pass

class Lobby():
    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.background_color = RED
        self.done = False
        self.img_background = pygame.transform.scale(pygame.image.load("Img/lobby_background.png"),size)
        self.initialise()
    
    def initialise(self):
        self.previous = self.initialise        
        for [name,menu,pos] in [["Play 1vs1",self.prepare1v1,[size[0]/4,size[1]/2]],["Play against AI",self.prepare1vsIA,[size[0]*3/4,size[1]/2]],["Play Test",self.prepareTest,[size[0]/2,size[1]*1/4]] ]:#, ["Hard Computer",self.prepare1vsIALvl2,[size[0]/2,size[1]*3/4]]]:
            self.all_sprites.add(TextButton(self,pos,"Img/empty_button.png",menu,[],name))
    
    def slaughter(self):
        for s in reversed(self.all_sprites.sprites()):
            s.kill()
    
    def prepare1v1(self):
        self.player_2 = True
        self.creatureSelection("1vs1")
        
    def prepare1vsIA(self):
        self.player_2 = False
        self.creatureSelection("1vsIA")
            
    def prepare1vsIALvl2(self):
        self.player_2 = False
        self.creatureSelection("1vsIALv2")
    
    def prepareTest(self):
        self.player_2 = True
        self.creatureSelection("test")
        """      
    def prepareDuel(self):
        game = SWC_The_Game.Game()
        game.MODE = "pv1"
        
        game.getUpgradePos = game.defaultUpgradeButtonPosition
        game.HB_MODE = "manual"
        game.DOUBLE_UPGRADES = False
        game.GOLDATTHEBEGINING = 0
        game.COOLDOWNS = True 
        game.PLAYERS = (SWC_The_Game.StaticPlayer,SWC_The_Game.StaticPlayer)
        game.DOUBLE_CREATURE_BAR = False
        game.TURRETS = [SWC_Units.CrossBow]
        game.player_left = game.PLAYERS[0](game,"left",200,["Img/bastion.png","Img/bastion_open.png"],430,[[490,315],[350,30],[200,310]])
        game.player_right = game.PLAYERS[1](game,"right",SWC_The_Game.length-350,["Img/castle.png","Img/castle_open.png"],150,[[270,300],[535,290],[413,130]])
        game.units_of_player = {"1":SWC_Units.getUnitsOfPlayer(game.player_right),"2":SWC_Units.getUnitsOfPlayer(game.player_left)}
        game.getUnitsOfPlayer = game.customUnitsOfPlayer #?
        
        army1 = [eval("SWC_Units."+name) for name in ["Titan","Clerk"]]
        army2 = [eval("SWC_Units."+name) for name in ["ScourgeMan","Purifier"]]
        for (army,player) in ((army1,game.player_left),(army2,game.player_right)):
            for u in army:
                player.fund += game.all_costs[u.level]
                player.train(u)
        
        SWC_The_Game.runGame(game)
        
        global screen
        screen = pygame.display.set_mode(size)
        
        self.slaughter()
        self.previous()        
        """
    def creatureSelection(self,mode):
        self.chosen_units = []
        self.selected_first = False
        self.active_selector,self.active_description = None,None
        self.button_selection = None
        self.unitSelectionStep(1,mode)
    
    def SecondCreatureSelection(self,mode):
        self.chosen_units2 = self.chosen_units
        self.selected_first = True
        self.chosen_units = []
        self.active_selector,self.active_description = None,None
        self.button_selection = None
        self.unitSelectionStep(1,mode)        
    
    def unitSelectionStep(self,lvl,mode,unit_chosen=None):
        self.slaughter()
        self.buttons  = {}
        self.previous_button = None
        self.all_sprites.add(FloatingText(self,[size[0]/2,80],("Player 1 Select","Player 2 Select")[self.player_2 and self.selected_first],pygame.font.SysFont("Verdanna",45)))
        self.all_sprites.add(FloatingText(self,[size[0]/2,110],("Level "+str(lvl),"Any level")[lvl>5],pygame.font.SysFont("Times New Roman",35)))       
        if unit_chosen:
            self.chosen_units.append(unit_chosen)
        for e,unit in enumerate(self.chosen_units):
            self.all_sprites.add(FloatingImage(self,[30+(size[0]-60)*(e+1)/8,size[1]-150],"Img/Creators/"+unit.creator_image))
        if lvl <= 7:
            for e,unit in enumerate(all_creatures_level[lvl]):
                if not(unit in self.chosen_units):
                    button = Button(self,[30+(size[0]-60)*(e%7+1)/min([len(all_creatures_level[lvl])+1,8]),size[1]/2-30*int(len(all_creatures_level[lvl])/7)+60*int(e/7)],"Img/Creators/"+unit.creator_image,self.unitDescription,[lvl+1,mode,unit])
                    self.all_sprites.add(button)
                    self.buttons[unit] = button
        else:
            if self.player_2:
                self.all_sprites.add(TextButton(self,[size[0]/2,250],"Img/empty_button.png",[self.SecondCreatureSelection,self.Play][self.selected_first],[mode],text=["Select for Player 2","Ready for the Fight"][self.selected_first]))
            else:
                self.all_sprites.add(TextButton(self,[size[0]/2,250],"Img/empty_button.png",self.Play,[mode],text="Ready for Battle"))
                
    def unitDescription(self,lvl,mode,unit_chosen):
        if self.active_selector:
            self.active_selector.kill()
        self.active_selector = TextButton(self,[size[0]-200,250],"Img/empty_button.png",self.unitSelectionStep,[lvl,mode,unit_chosen],text="Select")
        self.all_sprites.add(self.active_selector)
        if self.active_description:
            self.active_description.kill()
        self.active_description = UnitDescription(self,[400,210],"Img/old_paper.png",unit_chosen,[600,220])
        self.all_sprites.add(self.active_description)
        if self.button_selection:
            self.button_selection.goTo(self.buttons[unit_chosen])
        else:
            self.button_selection = ButtonSelection(pygame.image.load("Img/creator_selection.png"),self.buttons[unit_chosen])
        self.buttons[unit_chosen].functiun = self.unitSelectionStep
        if self.previous_button:
            self.previous_button.functiun = self.unitDescription
        self.previous_button = self.buttons[unit_chosen]
        
    def update(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.all_sprites.update()
    
    def display(self,screen):
        screen.fill(self.background_color)
        screen.blit(self.img_background,[0,0])
        self.all_sprites.draw(screen)
    
    def getPreviousScreen(self):
        self.slaughter()
        self.previous()
    
    def Play(self,mode):
        print(", ".join([unit.__name__ for unit in self.chosen_units]))
        if hasattr(self,"chosen_units2") and self.chosen_units2 != None:
            print(", ".join([unit.__name__ for unit in self.chosen_units2]))
        if mode=="1vs1":
            self.AgaistOtherPlayerPlay()
        elif mode == "1vsIA":
            self.AgainstIAPlay()
        elif mode == "1vsIALv2":
            self.AgainstIALv2Play()
        else:
            self.TestPlay()
    
    def AgainstIAPlay(self):
        game = SWC_The_Game.Game()
        game.MODE = "pv1"
        
        game.getUpgradePos = game.defaultUpgradeButtonPosition
        game.HB_MODE = "manual"
        game.DOUBLE_UPGRADES = False
        game.GOLDATTHEBEGINING = 0
        game.COOLDOWNS = True 
        game.PLAYERS = (SWC_The_Game.HumanPlayer,SWC_The_Game.ComputerPlayer)
        game.DOUBLE_CREATURE_BAR = False
        game.TURRETS = [SWC_Units.CrossBow]
        game.player_left = game.PLAYERS[0](game,"left",200,["Img/bastion.png","Img/bastion_open.png"],430,[[490,315],[350,30],[200,310]])
        game.player_right = game.PLAYERS[1](game,"right",SWC_The_Game.length-350,["Img/castle.png","Img/castle_open.png"],150,[[270,300],[535,290],[413,130]])
        game.units_of_player = {"1":self.chosen_units,"2":SWC_Units.getUnitsOfPlayer(game.player_right)}
        game.getUnitsOfPlayer = game.customUnitsOfPlayer
        
        SWC_The_Game.runGame(game)
        
        global screen
        screen = pygame.display.set_mode(size)
        
        self.slaughter()
        self.previous()

    def AgainstIALv2Play(self):
        game = SWC_The_Game.Game()
        game.MODE = "pv1"
        
        game.getUpgradePos = game.defaultUpgradeButtonPosition
        game.HB_MODE = "manual"
        game.DOUBLE_UPGRADES = False
        game.GOLDATTHEBEGINING = 0
        game.COOLDOWNS = True 
        game.PLAYERS = (SWC_The_Game.HumanPlayer,SWC_The_Game.ComputerPlayer2)
        game.DOUBLE_CREATURE_BAR = False
        game.TURRETS = [SWC_Units.CrossBow]
        game.player_left = game.PLAYERS[0](game,"left",200,["Img/bastion.png","Img/bastion_open.png"],430,[[490,315],[350,30],[200,310]])
        game.player_right = game.PLAYERS[1](game,"right",SWC_The_Game.length-350,["Img/castle.png","Img/castle_open.png"],150,[[270,300],[535,290],[413,130]])
        game.units_of_player = {"1":self.chosen_units,"2":SWC_Units.getUnitsOfPlayer(game.player_right)}
        game.getUnitsOfPlayer = game.customUnitsOfPlayer
        
        SWC_The_Game.runGame(game)
        
        global screen
        screen = pygame.display.set_mode(size)
        
        self.slaughter()
        self.previous()
    
    def TestPlay(self):
        game = SWC_The_Game.Game()
        game.MODE = "test"
        game.PLAYERS = (SWC_The_Game.HumanPlayer,SWC_The_Game.HumanPlayer2)
        
        game.getUpgradePos = game.pvpUpgradeButtonPosition
        game.HB_MODE = "manual"
        game.GOLDATTHEBEGINING = 1000000000000000000
        game.COOLDOWNS = False
        game.DOUBLE_UPGRADES = True
        game.DOUBLE_CREATURE_BAR = True
        
        game.TURRETS = [SWC_Units.CrossBow]
        game.player_left = game.PLAYERS[0](game,"left",200,["Img/bastion.png","Img/bastion_open.png"],430,[[490,315],[350,30],[200,310]])
        game.player_right = game.PLAYERS[1](game,"right",SWC_The_Game.length-350,["Img/castle.png","Img/castle_open.png"],150,[[270,300],[535,290],[413,130]])
        game.units_of_player = {"1":self.chosen_units2,"2":self.chosen_units}
        game.getUnitsOfPlayer = game.customUnitsOfPlayer
        
        SWC_The_Game.runGame(game)
        
        global screen
        screen = pygame.display.set_mode(size)
        
        self.slaughter()
        self.previous()
    
    def AgaistOtherPlayerPlay(self):
        game = SWC_The_Game.Game()
        game.MODE = "pvp"
        game.PLAYERS = (SWC_The_Game.HumanPlayer,SWC_The_Game.HumanPlayer2)
        
        game.getUpgradePos = game.pvpUpgradeButtonPosition
        game.HB_MODE = "automatic"
        game.GOLDATTHEBEGINING = 0
        game.COOLDOWNS = True
        game.DOUBLE_UPGRADES = True
        game.DOUBLE_CREATURE_BAR = True
        
        game.TURRETS = [SWC_Units.CrossBow]
        game.player_left = game.PLAYERS[0](game,"left",200,["Img/bastion.png","Img/bastion_open.png"],430,[[490,315],[350,30],[200,310]])
        game.player_right = game.PLAYERS[1](game,"right",SWC_The_Game.length-350,["Img/castle.png","Img/castle_open.png"],150,[[270,300],[535,290],[413,130]])
        game.units_of_player = {"1":self.chosen_units2,"2":self.chosen_units}
        game.getUnitsOfPlayer = game.customUnitsOfPlayer
        
        SWC_The_Game.runGame(game)
        
        global screen
        screen = pygame.display.set_mode(size)
        
        self.slaughter()
        self.previous()


pygame.init()

all_creatures = SWC_Units.getUnits()
all_creatures_level=[[None],[],[],[],[],[]]
for u in all_creatures:
    all_creatures_level[u.level].append(u)
all_creatures_level.append(copy(all_creatures))
all_creatures_level.append(copy(all_creatures))
lobby = Lobby()

clock = pygame.time.Clock()


while not(lobby.done):
    lobby.clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            lobby.done = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            lobby.clicked = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                lobby.getPreviousScreen()
    lobby.update()
    lobby.display(screen)    
    pygame.display.flip()
    clock.tick(20)

pygame.quit()
