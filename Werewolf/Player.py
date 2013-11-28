# Please notice this is a license :P

import random, traceback
import Game as Game


YAMLDATA = NotImplemented # :^)

class PlayerList:

    def __init__(self):
        self.playerlist = []
    
    def addplayer(self, player):
        self.playerlist.append(player)

    def extend(self, list):
        self.playerlist.extend(list)

    def istype(self, player, classtype):
        "Will check if player instance is of this type"
        if player.name_singular == classtype.name_singular:
            return True

        return False

    def iswolf(self, player):
        "To check if the player is wolf/werecrow/any weird kind of modded wolf. Traitor/cursed doesn't count."
        return player.__class__.kill.func_code.co_code != Player.kill.func_code.co_code

    def deep_istype(self, player, classtype):
        "Same as istype, but it will instead check if the class of player has inherited from classtype."
        # E.G.: istype([traitor], Wolf) => False
        #       deep_istype([werecrow], Wolf) => True
        
        if classtype in player.__class__ .__bases__ or self.istype(player, classtype):
            return True

        return False

    

    

    def deepcount(self, klass):
        return [(1 if self.deep_istype(i, klass) else 0) for i in self.playerlist].count(1)

    def count(self, klass):
        return [(1 if self.istype(i, klass) else 0) for i in self.playerlist].count(1)



    def __getitem__(self, name):
        # Allows this:
        # foo = PlayerList()
        # PlayerList.addplayer(Wolf("foobar", game))
        # print PlayerList["foobar"].BULLETS
        # Also supports dat:
        # print PlayerList["FooBA"].BULLETS => foobar's bullets
   
        possiblenameslist = []

        # For every player in the list:
        # if his name starts with the given string, append him to the list
        for player in self.playerlist:
            if player.name.lower().startswith(name.lower()):
                possiblenameslist.append(player)

        #Pretty obvious stuff
        _len = len(possiblenameslist)
        if _len == 0:
            raise Game.WerewolfException("No player matching that name: "+name)

        elif _len > 1:
            raise Game.WerewolfException(
                "Too many (%s) players matching that name: %s." % str(_len) )

        return possiblenameslist[0]

    def __delitem__(self, name):
        name = self[name]
        if not name.on_death():
            raise Game.WerewolfException("Le fail") # Veri tru
        
        name.DEAD = True
        self.playerlist.remove(name)

        
    








class Player:

    def __init__(self, name, game):
        self.name, self.game = name, game
        if hasattr(self, "init2"):
            self.init2()

       

    name_singular = "<Not implemented>"
    name_plural = "<Still not implemented>" # :I
    
    BULLETS = 0
    GUN_HIT_CHANCES = 5.0/7
    # amount of bullets will be between 2 and round(CEIL*NB_OF_PEOPLE)
    BULLET_AMOUNT_CEIL = 0.12
    SPECFUNCMSG = lambda *args: None
    ROLEMSG = ""
    DISPLAYPLAYERS = False

    def on_death(self):
        pass 
        
    def on_night__(self):
        
        if self.game.first_night and self.ROLEMSG:
            self.game.serv.privmsg(self.name, self.ROLEMSG)

        specmsg = self.SPECFUNCMSG(self)
        if specmsg:
            self.game.serv.privmsg(self.name, specmsg)

        if self.DISPLAYPLAYERS:
            self.game.serv.privmsg(self.name, self.game.players())

    

    distribution = NotImplemented # You have to do eet yourself :)

        
    GUN_MISS_CHANCES = 1.0/7
    GUN_SUICIDE_CHANCES = 2.0/7
    INVINCIBLE = False
    HEADSHOT_CHANCES = 2.0/5
    SEEN = ""
    FAILKILLMSG = "" # Currently only used by harlot and GA, is printed if wolf_is_dead returns False
    
    # Might sound retarded, but harlot/werecrow/GA needs to keep a reference to Player.
    # Harlot needs to find out if the visited user is dead.
    DEAD = False 

    OBSERVE = True
    GUARDED = False

    
    CURSED = None
    VOTE = True
    ONDEATHFUNCS = []

    

    def gunner_event_chance(self, target):
        eventdict = {Game.GUN_EVENT_HIT: self.GUN_HIT_CHANCES,
                     Game.GUN_EVENT_MISS: self.GUN_MISS_CHANCES,
                     Game.GUN_EVENT_SUICIDE: self.GUN_SUICIDE_CHANCES}

        returnevent = -1
        

        while returnevent == -1:
            x = eventdict.keys()
            random.shuffle(x)
            print x

            for i in x:
                seed = random.random()
                
                if seed < eventdict[i]:
                    # Nice
                    returnevent = i
                    break

        if (returnevent == Game.GUN_EVENT_HIT) and not (
            self.game.PlayerList.deep_istype(self.game.PlayerList[target], Wolf)) and not (
                random.random() > self.HEADSHOT_CHANCES) and not(
                    self.game.PlayerList.istype(self.game.PlayerList[target], Traitor)):


            return GUN_EVENT_HEADSHOT

        return returnevent
                        

    def interpret_event(self, target, event):
        info = (self.name, target, self.name_singular)
        print Game.MSG_GUNNERHIT.format(*info)
        print Game.gunner_msg_dict[event].format(*info)

        if event == Game.GUN_EVENT_HIT:
            if self.game.PlayerList.iswolf(self.game.PlayerList[target]):
                self.game.kill(target)

            else:
                self.game.PlayerList[target].VOTE = None # They can't vote

        elif event == Game.GUN_EVENT_SUICIDE:
            self.game.kill(self.name) # Bye

        elif event == Game.GUN_EVENT_HEADSHOT:
            self.game.kill(target) # Bye too 


        
            
    def lynch(self, target, *args):
        if self.game.PHASE == Game.PHASE_NIGHT:
            raise Game.WerewolfException(Game.MSG_PHASEERROR.format("lynch", "day"))

        elif self.VOTE == None:
            print Game.MSG_LYNCHWOUNDED.format(self.name)
            return

        self.game.vote.vote(self.name, target)


                

    def _shoot(self, target):
        
        # Can be replaced for wolf/drunk/anything else
        self.interpret_event(target.name, self.gunner_event_chance(target))
        
        
        
        

    def kill(*args):
        "You are not a wolf ..."
        raise Game.WerewolfException("You are not a wolf.") # Moo
        

    def wolf_is_dead(self):
            
            
        return True # In case the victim is harlot, he might not be dead after wolf kill

    def shoot(self, target, *args):
        "PEW! PEW! PEW! PEW! Used to shoot an user.  "
        if self.game.PHASE == Game.PHASE_NIGHT:
            raise Game.WerewolfException("You may only shoot people during day")
        if self.BULLETS < 1: raise Game.WerewolfException("You have no bullets!")
        target = self.game.PlayerList[target]
        self.BULLETS-=1
        self._shoot(target)

        
        
        
a = 2
        
        

        
class Wolf(Player):
    name_singular = "wolf"
    name_plural = "wolves"
    distribution = {4:1, 10:2, 15:3, 20:4}
    ROLEMSG = 'You are a wolf. It is your job to kill all the villagers. \
Use "kill <nick>" to kill a villager.'

    CANKILL = True

    def kill(self, target, *args):
        "Used in order to kill someone"
        if not self.CANKILL:
            raise Game.WerewolfException("You are not allowed to vote.")
            
        if self.game.PHASE != Game.PHASE_NIGHT:
            raise Game.WerewolfException(Game.MSG_PHASEERROR)

        elif self.game.PlayerList.deep_istype(self.game.PlayerList[target], Wolf):
            raise Game.WerewolfException(Game.MSG_KILLINGWOLFERROR)

        print "okhey", self.name, target
        self.game.vote.vote(self.name, target)
            
            
    def _shoot(self, target):
        event = self.gunner_event_chance()
        if self.game.PlayerList.deep_istype(self.game.PlayerList[target], self.__class__):
            event = Game.GUN_EVENT_MISS # Obviously .______.
        
            
        self.interpret_event(self.gunner_event_chance())



    BULLETS = OBSERVE = None


class Werecrow(Wolf):
    name_singular = "werecrow"
    name_plural = "werecrows"
    SEEN = "wolf"
    ROLEMSG = 'You are a werecrow. You are able to fly at night. \
Use "kill <nick>" to kill a a villager. Alternatively, you can\
use "observe <nick>" to check if someone is in bed or not. \
Observing will prevent you from participating in a killing.'

    distribution = {12:1}


    def on_day(self):
        if not self.OBSERVING:
            return
        
        msg = Game.MSG_WERECROWWASINBED if self.OBSERVING.OBSERVE else Game.MSG_WERECROWWASNTINBED

        print msg.format(self.OBSERVING.name)
        self.OBSERVING = None


    def observe(self, target, *args):
        "Used in order to observe someone.  "
        if self.OBSERVING:
            raise Game.WerewolfException(
                Game.MSG_WERECROWOBSERVEERROR.format(self.OBSERVING.name))

        elif self.game.PlayerList.deep_istype(self.game.PlayerList[target], Wolf):
            raise Game.WerewolfException(
                Game.MSG_OBSERVINGWOLFERROR)

        elif self.game.PHASE != Game.PHASE_NIGHT:
            raise Game.WerewolfException(
                Game.MSG_PHASEERROR.format("observe", "night"))

        elif self.game.vote.get_vote(self):
            raise Game.WerewolfException(Game.MSG_CROWALREADYKILLING)


        self.CANKILL = False
        self.OBSERVING = self.game.PlayerList[target]
        print Game.MSG_WERECROWOBSERVE.format(target)
   
            
        

    OBSERVING = ""



class Villager(Player):
    name_singular = "villager"
    name_plural = "villagers"
    CURSED = False
    OBSERVE = True
    
    


class Traitor(Wolf):
    distribution = {8:1}
    name_singular = "traitor"

    name_plural = "traitors"
    SEEN = Villager.name_singular
    ROLEMSG = "You are a traitor. You are exactly like a\
                               villager and not even a seer can see your true identity. \
                               Only detectives can. "
    
    CURSED = False
    kill = Player.kill
    
        
    def turnintowolf(self):
        result = Wolf(self.name, self.game)

        # Give all the player's properties to the Wolf :O
        for object in dir(self):
            obj = getattr(self, object)
            if type(obj) in (type(self.on_night), type(self.__class__), type(self)):
                continue

            elif object in ("name_singular", "name_plural", "SEEN"):
                continue

            setattr(result, object, obj)
        

        del self.game.PlayerList.playerlist[self] # R.I.P. :(
        self.game.PlayerList.addplayer(result) # Raoooooooor
        
    def on_night(self):
        if self.game.PlayerList.deepcount(Wolf) == self.game.PlayerList.count(self.__class__):
            self.turnintowolf()
        
    



class Drunk(Villager):

    ROLEMSG = "You have been drinking too much: you are the village drunk!"

    def init2(self):
        self.BULLET_AMOUNT_CELL = Player.BULLET_AMOUNT_CEIL*3
    
    def on_night(self):
        print self.name+": "+Game.MSG_DRUNK

    distribution = {8:1}
        
    CURSED = None
    name_singular = "drunk"
    name_plural = "drunks"
    GUN_HIT_CHANCES = 2.0/7
    GUN_MISS_CHANCES = 3.0/7
    GUN_SUICIDE_CHANCES = 2.0/7
    

class OneUseCommandPlayer(Villager):
    # Fancy name
    # Like seer, det, GA
    # Werecrow doesn't use it because it requires Wolf and is slightly different

    def build(self):
        if not self.OPERATIONNAME:
            raise Game.GameCreateError("You have to define the OPERATIONNAME attribute. ")

        if not self.OPERATIONDOC:
            doc = "Used in order to %s someone" % self.OPERATIONNAME

        else:
            doc = self.OPERATIONDOC

        setattr(self, self.OPERATIONNAME, (lambda target, *args: self.runcommand(target)))
        setattr(getattr(self, self.OPERATIONNAME), "__doc__", doc)
        
        
    
    USEDTHECOMMAND = False
    distribution = NotImplemented # 
    PHASE = 0
    OPERATIONNAME = ""
    OPERATIONDOC = None
    
    def convert_name(self, x):
        PhaseTable = {Game.PHASE_NIGHT: "night",
                  Game.PHASE_DAY: "day"}

        return PhaseTable[x]

    def on_day_(self):
        if self.PHASE == Game.PHASE_NIGHT:
            self.USEDTHECOMMAND = False

    def on_night_(self):
        if self.PHASE == Game.PHASE_DAY:
            self.USEDTHECOMMAND = False

    def _cmd(self, target):
        return "potato" # Implement it

    def runcommand(self, target):
        if target == self.name:
            raise WerewolfException(Game.MSG_OPERHIMSELF.format(self.OPERATIONNAME))

        elif self.game.PHASE != self.PHASE:
            raise Game.WerewolfException(
                Game.MSG_PHASEERROR.format(self.OPERATIONNAME, self.convert_name(self.PHASE)))

        elif self.USEDTHECOMMAND:
            raise Game.WerewolfException(Game.MSG_ALREADYUSEDCMD.format(self.OPERATIONNAME))

        self.USEDTHECOMMAND = True
        self.game.serv.privmsg(self.name, self._cmd(target))
    
        
class Seer(OneUseCommandPlayer):

    distribution = {4:1}

    def init2(self):
        self.PHASE = Game.PHASE_NIGHT
        self.OPERATIONNAME = "see"
        self.build()

    name_singular = "seer"
    name_plural = "seers"
    OBSERVE = False

    

 
        
    def _cmd(self, target):

        player = self.game.PlayerList[target]
        if player.CURSED == True:
            kind = Wolf.name_singular # Maybe edited ...

        elif player.SEEN:
            kind = player.SEEN # Werecrow and traitor and maybe more

        else:
            kind = player.name_singular

        print Game.MSG_SEER.format(player.name, kind)
        

        
class Detective(OneUseCommandPlayer):

    USEDID = False
    distribution = {12:1}
    DETREVEALODDS = 2.0/5
    name_singular = "detective"
    name_plural = "detectives"
    

    def init2(self):
        self.PHASE = Game.PHASE_DAY
        self.OPERATIONNAME = "investigate"
        self.build()

    def on_night(self):
        self.USEDID = False

    def _cmd(self, target):
        # Bluaheblerg
        if random.random() > self.DETREVEALODDS:
            # R.I.P. :>
            self.game.wolf.mass_msg(Game.MSG_DEATREVEAL.format(self.name)) 
            
        return Game.MSG_DET.format(self.game.PlayerList[target].name
                                   , self.game.PlayerList[target].name_singular)
        
        

class Harlot(OneUseCommandPlayer):
    name_singular = "harlot"
    name_plural = "harlots"
    distribution = {8:1}

    def init2(self):
        self.PHASE = Game.PHASE_NIGHT
        self.OPERATIONNAME = "visit"
        self.build()

    VISITING = ""
    FAILKILLMSG = "The wolves' selected victim was a harlot, \
who was not at home last night." # BWAHAHAHAHAHAHAHAHAHAAAAAA
    def on_day(self):
        if not self.VISITING:
            return # Dumb harlot
        
        if self.game.PlayerList.iswolf(self.VISITING):
            print "O NOEZ I VIZIT WULV"
            self.game.kill(self.name)

        elif self.VISITING.DEAD == True:
            print "O NAWZ I VIZIT VIKTUM"
            self.game.kill(self.name)

        self.OBSERVE = True
        self.VISITING = ""

    def wolf_is_dead(self):
        return not bool(self.VISITING)

    def _cmd(self, target):
        self.VISITING = self.game.PlayerList[target]
          
            


        
    
        
    
    



