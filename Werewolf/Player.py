# Please notice that this is a license :P

import random, traceback, time, json
import Game as Game

msgs = json.loads(open("Config/msgs.txt").read())

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
        name.DEAD = True
        self.playerlist.remove(name)

        
    








class Player:

    def __init__(self, name, game):
        self.name, self.game = name, game
        self.death_events_table =  {Game.EVENT_WOLFKILL: "on_wolfdeath",
                                    Game.EVENT_LYNCHKILL: "on_lynchdeath"}
        
        self.LASTMSG = time.time() # asdf
        if hasattr(self, "init2"):
            self.init2()

    # Reperz

    

    def event_test(self, event):
        if self.game.channame != event.target():
            return False
        
    def on_pubmsgreaper(self, event):
        if not self.event_test(event): return
        
        self.GAVEWARNING = False
        self.LASTMSG = time.time()

    def on_actionreaper(self, event):
        self.on_pubmsgreaper(event)

    def on_joinreaper(self, event):
        if not self.event_test(event): return

        self.PARTTIME = self.QUITTIME = 0
        self.on_pubmsgreaper(event)

    def on_partreaper(self, event):
        if not self.event_test(event): return
        self.PARTTIME = time.time()

    def on_quitreaper(self, event):
        self.QUITTIME = time.time()

       

    name_singular = "<Not implemented>"
    name_plural = "<Still not implemented>" # :I
    
    BULLETS = 0
    GUN_HIT_CHANCES = 5.0/7
    # amount of bullets will be between 2 and round(CEIL*NB_OF_PEOPLE)
    BULLET_AMOUNT_CEIL = 0.12
    GUNNER_KILLS_WOLF_AT_NIGHT_CHANCE = 1.0/4
    WOLF_GUNNER_CHANCE = 1-GUNNER_KILLS_WOLF_AT_NIGHT_CHANCE
    SPECNAME = ""
    GETSPECMSG = lambda *args: None

    # For reaper.
    # these values (except for GAVEWARNING, which is bool) are timestamps.
    LASTMSG = 0
    PARTTIME = 0
    QUITTIME = 0
    GAVEWARNING = False


    # Data related to first night.  ROLEMSG will be PMd to the player.
    # If DISPLAYPLAYERS = True, a player list will be automatically sent too.
    ROLEMSG = ""
    DISPLAYPLAYERS = False

    # Helpers
    def chanmsg(self, msg):
        
        self.game.serv.privmsg(self.game.channame, msg)

    def usermsg(self, msg):
        
        self.game.serv.privmsg(self.name, msg)

    # What to do if ply dies.
    def on_death(self, ev, *args, **kw):
        if not ev in self.death_events_table:
            raise Exception("Unknown event type. ")

        # This stuff isn't really neat, but meh.
        # For the class and for aaaaall the parent classes, call the said attr.
        for klass in list(self.__class__.__bases__)+[self.__class__]:
            if not hasattr(klass, self.death_events_table[ev]):
                continue
            
            getattr(klass, self.death_events_table[ev])(self, *args, **kw)
        
    def on_wolfdeath(self):
        if self.BULLETS and self.game.PHASE == Game.PHASE_NIGHT:
            chosenwolf = random.choice(self.game.vote.votes[self])
            
            if random.random() > self.GUNNER_KILLS_WOLF_AT_NIGHT_CHANCE:

                self.chanmsg(msgs["WOLFGUNKILLATNIGHT"].format(self.name,
                                                               chosenwolf.name,
                                                               chosenwolf.name_singular)) # Yay!

            elif random.random() > self.WOLF_GUNNER_CHANCE:
                chosenwolf.usermsg(msgs["TOWOLFGUNNER"].format(self.name))
                chosenwolf.BULLETS = 2
                pass
            
        return True
            
    def on_night__(self):
        
        if self.game.first_night and self.ROLEMSG:
            self.usermsg(self.ROLEMSG)

        specmsg = self.GETSPECMSG(self)
        
        if specmsg:
            self.usermsg(specmsg)

        if self.DISPLAYPLAYERS:
            self.usermsg(self.game.playerlist())

    

    # distribution: dict. refer yourself to Game.Game.distribute_roles
    distribution = NotImplemented 


    # Gun things
    GUN_MISS_CHANCES = 1.0/7
    GUN_SUICIDE_CHANCES = 2.0/7
    HEADSHOT_CHANCES = 2.0/5


    SEEN = ""

    
    # Might sound retarded, but harlot/werecrow/GA needs to keep a reference to Player.
    # Harlot needs to find out if the visited user is dead.
    DEAD = False 

    OBSERVE = True
    GUARDED = False

    
    CURSED = None
    VOTE = True
    ONDEATHFUNCS = []

    def on_shoot(self, source):
        x = random.random()
        if x < self.HEADSHOT_CHANCES:
            return GUN_EVENT_HEADSHOT

        return GUN_EVENT_HIT

    

    def gunner_event_chance(self, target):
        eventdict = {Game.GUN_EVENT_HIT: self.GUN_HIT_CHANCES,
                     Game.GUN_EVENT_MISS: self.GUN_MISS_CHANCES,
                     Game.GUN_EVENT_SUICIDE: self.GUN_SUICIDE_CHANCES}

        returnevent = -1
        

        while returnevent == -1:
            x = eventdict.keys()
            random.shuffle(x)
            for i in x:
                seed = random.random()
                if seed < eventdict[i]:
                    # Nice
                    returnevent = i
                    break

        return returnevent
                        

    def interpret_event(self, target, event):
        info = (self.name, target, self.name_singular)
        kill = True

        if event == Game.GUN_EVENT_HIT:
    
            self.game.PlayerList[target].VOTE = None # They can't vote
            kill = False

        elif event == Game.GUN_EVENT_WOLFKILL:
            self.chanmsg(msgs["GUNNERWOLFHIT"].format(target))
            
        elif event == Game.GUN_EVENT_SUICIDE:
            self.chanmsg(msgs["SUICIDE"].format(self.name, self.name_singular))
            self.game.kill(self.name) # Bye
            kill = False

        elif event == Game.GUN_EVENT_HEADSHOT:
            self.chanmsg(msgs["HEADSHOTKILL"].format("", target))

        else:
            self.chanmsg(msgs["GUNNERMISS"].format(self.name))
            kill = False

        if kill:
            self.game.kill(target)


        
            
    def lynch(self, target, *args):
        if self.game.PHASE == Game.PHASE_NIGHT:
            raise Game.WerewolfException(msgs["PHASEERROR"].format("lynch", "day"))

        elif self.VOTE == None:
            self.game.serv.privmsg(self.game.channame, msgs["LYNCHWOUNDED"].format(self.name))
            return

        self.game.vote.vote(self.name, target)


                

    def _shoot(self, target):
        
        # Can be replaced for wolf/drunk/anything else
        event = self.gunner_event_chance(target)
        if event == Game.GUN_EVENT_HIT:
            event = self.game.PlayerList[event].on_shoot(self.name)
        
        self.interpret_event(target.name, event)
        
        
        
        

    def kill(*args):
        "You are not a wolf ..."
        raise Game.WerewolfException("You are not a wolf.") # Moo
        

    def on_wolfdeath(self):
        return True # In case the victim is harlot, he might not be dead after wolf kill

    def shoot(self, target, *args):
        "PEW! PEW! PEW! PEW! Used to shoot an user.  "
        if self.game.PHASE == Game.PHASE_NIGHT:
            raise Game.WerewolfException(msgs["PHASEERROR"].format("shoot",
                                                                   "day"))
        if self.BULLETS < 1: raise Game.WerewolfException("You have no bullets!")
        target = self.game.PlayerList[target]
        self.BULLETS-=1
        self._shoot(target)

        
        
        
a = 2
        
        

        
class Wolf(Player):
    name_singular = "wolf"
    name_plural = "wolves"
    distribution = {4:1, 10:2, 15:3, 20:4}
    ROLEMSG = msgs["WOLFROLEMSG"]
    MISSEDSHOT = False 

    CANKILL = True

    def on_privmsg(self, event):
        self.game.wolf_mass_msg(self.name, event.arguments()[0])

    def on_nightdisplaywolfroles(self):
        seq = []
        for player in self.game.PlayerList.playerlist:
            if player.name == self.name:
                # Uh oh
                continue

            elif issubclass(player.__class__, Wolf):
                seq.append(player.name+' ('+player.name_singular+')')

            else:
                seq.append(player.name)

        self.usermsg(", ".join(seq))

    def on_nightresetmissedshot(self):
        self.MISSEDSHOT = False

    def kill(self, target, *args):
        "Used in order to kill someone"
        if not self.CANKILL:
            raise Game.WerewolfException("You are not allowed to vote.")
            
        if self.game.PHASE != Game.PHASE_NIGHT:
            raise Game.WerewolfException(msgs["PHASEERROR"])

        elif self.game.PlayerList.deep_istype(self.game.PlayerList[target], Wolf):
            raise Game.WerewolfException(msgs["KILLINGWOLFERROR"])

        self.game.vote.vote(self.name, target)
        self.chanmsg(msgs["WOLFKILLMSG"].format(target))
        
            
            
    def _shoot(self, target):
        event = self.gunner_event_chance()
        if self.game.PlayerList.deep_istype(self.game.PlayerList[target], self.__class__):
            event = Game.GUN_EVENT_MISS # Obviously .______.
            self.MISSEDSHOT = True
            
        event = self.gunner_event_chance()
        if self.BULLETS == 1 and not self.MISSEDSHOT:
            event = Game.GUN_EVENT_MISS

        elif event == Game.GUN_EVENT_MISS:
            self.MISSEDSHOT = True
            
        
            
        self.interpret_event(event)



    BULLETS = OBSERVE = None


class Werecrow(Wolf):
    name_singular = "werecrow"
    name_plural = "werecrows"
    SEEN = "wolf"
    ROLEMSG = msgs["CROWROLEMSG"]

    distribution = {12:1}


    def on_day(self):
        if not self.OBSERVING:
            return
        
        msg = msgs["WERECROWWASINBED"] if self.OBSERVING.OBSERVE else msgs["WERECROWWASNTINBED"]

        self.usermsg(msg.format(self.OBSERVING.name))
        self.OBSERVING = None


    def observe(self, target, *args):
        "Used in order to observe someone.  "
        if self.OBSERVING:
            raise Game.WerewolfException(
                msgs["CROWOBSERVEERROR"].format(self.OBSERVING.name))

        elif self.game.PlayerList.deep_istype(self.game.PlayerList[target], Wolf):
            raise Game.WerewolfException(
                msgs["WERECROWOBSERVINGWOLFERROR"])

        elif self.game.PHASE != Game.PHASE_NIGHT:
            raise Game.WerewolfException(
                msgs["PHASEERROR"].format("observe", "night"))

        elif self.game.vote.get_vote(self):
            raise Game.WerewolfException(msgs["WERECROWALREADYKILLING"])


        self.CANKILL = False
        self.OBSERVING = self.game.PlayerList[target]
        self.usermsg(msgs["WERECROWOBSERVE"].format(target))
   
            
        

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
    ROLEMSG = msgs["TRAITORROLEMSG"]
    
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
        self.BULLET_AMOUNT_CEIL = Player.BULLET_AMOUNT_CEIL*3
    


    distribution = {8:1}
        
    CURSED = None
    name_singular = "drunk"
    name_plural = "drunks"
    GUN_HIT_CHANCES = 2.0/7
    GUN_MISS_CHANCES = 3.0/7
    GUN_SUICIDE_CHANCES = 2.0/7
    ROLEMSG = msgs["DRUNKROLEMSG"]
    

class OneUseCommandPlayer(Villager):
    # Fancy name
    # Like seer, det, GA
    # Werecrow doesn't use it because it requires Wolf and is slightly different
    DISPLAYPLAYERS = True
    
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
    distribution = NotImplemented # asfd
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
            raise Game.WerewolfException(msgs["DOONHIMSELF"].format(self.OPERATIONNAME))

        elif self.game.PHASE != self.PHASE:
            raise Game.WerewolfException(
                msgs["PHASEERROR"].format(self.OPERATIONNAME, self.convert_name(self.PHASE)))

        elif self.USEDTHECOMMAND:
            raise Game.WerewolfException(msgs["ALREADYUSEDCMD"].format(self.OPERATIONNAME))

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

        return msgs["SEERSEE"].format(player.name, kind)
        
        

        
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
            self.game.wolf.mass_msg(msgs["DETREVEAL"].format(self.name)) 
            
        return(msgs["DETINVEST"].format(self.game.PlayerList[target].name
                                   , self.game.PlayerList[target].name_singular))
        
        

class Harlot(OneUseCommandPlayer):
    name_singular = "harlot"
    name_plural = "harlots"
    distribution = {8:1}

    def init2(self):
        self.PHASE = Game.PHASE_NIGHT
        self.OPERATIONNAME = "visit"
        
        self.build()

    VISITING = ""
    FAILKILLMSG = msgs["HARLOTFAILKILL"]
    def on_day(self):
        if not self.VISITING:
            return # moo
        
        if self.game.PlayerList.iswolf(self.VISITING):
            self.chanmsg(msgs["HARLOTKILLATNIGHT"].format(self.name, "a wolf's house"))
            self.game.kill(self.name)

        elif self.VISITING.DEAD == True:
            self.chanmsg(msgs["HARLOTKILLATNIGHT"].format(self.name, "the victim's house"))
            self.game.kill(self.name)

        self.OBSERVE = True
        self.VISITING = ""
        
    def on_wolfdeath(self):
        return not bool(self.VISITING)

    def _cmd(self, target):
        self.VISITING = self.game.PlayerList[target]
        self.VISITING.usermsg(msgs["HARLOTVISITMSG"].format(self.name))

        return msgs["HARLOTVISITMSG"].format(self.VISITING.name)
          
            


        
    
        
    
    



