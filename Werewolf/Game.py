import Werewolf.Player as Player
from Werewolf.Vote import Vote
import random, math

YAMLDATA = NotImplemented # :^)

class WerewolfException(Exception): pass

class GameCreateError(Exception):
    pass

# keys = chan names,  values = dicts (acc: stasislength)
StasisDict = {}
playermsg = "{0} players: {1}"
spectext = "Out of these players, there are {0}. "

class BaseChanClass:
    # Very ugly indeed, but I didn't find any better way of doing that.
    # Please note that these commands shouldn't be usable in query.

    landfunc = lambda x, serv, item, obj: "The {0} lands on {0}".format(
        item, obj)

    def players(self):
        "Get the list of players. "
        if issubclass(self, Lobby):
            players = self.plylist

        elif issubclass(self, Game):
            players = self.players
            
        else:
            raise WerewolfException("U w00t?")
        
        return playermsg.format(str(len(players)), ", ".join(players))

    def generate_rolestats(self, roles):
        seq = []

        for role in roles.keys():
            text = role.name_singular
            
            if roles[role] != 1:
                text = role.name_plural

            seq.append(str(roles[role])+' '+text)

        txt = "there is "
        if roles[roles.keys()[0]]:
            txt = "there are "

        txt = txt+", ".join(seq[:-1])
        txt += " and "+seq[-1]
        return txt
                
    def generate_specs(self, specs):
        seq = []

        for spec in specs.keys():
            text = spec_table[spec][0]
            
            if roles[role] != 1:
                text = spec_table[spec][1]

            seq.append(str(specs[spec])+' '+text)


        txt = ""
        txt = txt+", ".join(seq[:-1])
        txt += " and "+seq[-1]
        return spectext.format(txt)
        
        
    def rolestats(self):
        "Get the distribution of roles/specs"
        if not issubclass(self, Game):
            raise WerewolfException("No game is going on yet. ")

        roles = {}

        for player in self.PlayerList.playerlist:
            if not player.__class__ in roles.keys():
                roles[player.__class__] = 0
            
            roles[player.__class__]+=1

        specs = {}
        for tuple in self.currentspecs:
            if tuple[1].DEAD:
                # No
                continue

            if not tuple[0] in specs.keys():
                specs[tuple[0]] = 0
        
            specs[tuple[0]] += 1

        return self.generate_rolestats(roles)+self.generate_specs(specs)


       

    def cointoss(self):
        print self.target+" tosses a coin into the air..."
        self.serv.TimeManager.addfunc(self.landfunc, 5, self.serv, "coin",
                                      random.choice(["heads", "tails"]))

    def ponytoss(self):
        print self.target+" throws a pony into the air..."
        self.serv.TimeManager.addfunc(self.landfunc, 5, self.serv, "pony",
                                      random.choice(["hoof", "plot"]))
        
    

class Lobby:
    

    def __init__(self, channels, serv, channame, startfunc):
        self.plylist = []
        self.channels, self.serv, self.channame = channels, serv, channame, startfunc
        

        if channame in StasisDict.keys():
            for accname in StasisDict[channame].keys():
                if accame in StasisDict[channame]:
                    if StasisDict[channame][accname] > 0: # -1 means banned
                        StasisDict[channame][accname] -= 1

                    if StasisDict[channame][accname] == 0:
                        del StasisDict[channame][accname] # 4phun

        # moo

    def get_hostmask(self, authorname):
        return authorname.split('!')[1].split('@')[1]
    
    def join(self, authorname):
        hostmask = self.get_hostmask(authorname)
        if hostmask in StasisDict.keys():
            return "no"

        elif hostmask in self.plylist:
            return "you already joined you derpface"

        self.plylist.append(hostmask)

        # Voice him 
        self.serv.mode(authorname.split('!')[0], "+v")

    def leave(self, authorname):
        hostmask = self.get_hostmask(authorname)
        if not hostmask in self.plylist:
            return "You didn't join yet you bonehead"

        self.plylist.remove(hostmask)
        self.serv.mode(authorname.split('!')[0], "+v")

    quit = leave

    def find_hostmask(self, name):
        for _list in (self.channels[self.channame].users(),
                                self.channels[self.channame].voiced()):

            for user in _list:
                if user.split('!')[0] == name:
                    return user

        raise WerewolfException("Name not found")
            

    def fstasis(self, targetname, penalty):
        if not penalty.isdigit() or not penalty:
            return "you must provide a valid integer. "
            
        hostmask = self.get_hostmask(self.find_hostmask(targetname))
        if not hostmask in StasisDict.keys():
            StasisDict[hostmask] = int(penalty)

        else:
            StasisDict[hostmask] += int(penalty)

        if hostmask in self.plylist:
            self.leave(self.find_hostmask(targetname)) # Rude :>

        
        
        

    


# events
EVENT_GUNNERKILL = 0
EVENT_LYNCHKILL = 1
EVENT_WOLFKILL = 2
EVENT_NIGHTEND = 3
EVENT_DAYEND = 4

# Timeouts
DAY_TIME_WARNING = 30 # Obviously not 30. Computed with plycount*DAY_TIME_WARNING
DAY_TIME_CHANGE = 120 # Nb of seconds between the warning and the forced end

NIGHT_TIME_LIMIT = 120

RATE_LIMIT = 60 # Time between each rate-limited commands

# Shortened. Idlers suck.
IDLE_WARNING = 120
IDLE_TIMEOUT = 180
PART_WAIT_TIME = 10
QUIT_WAIT_TIME = 30


# For gunner
GUN_EVENT_HIT = 0
GUN_EVENT_MISS = 1
GUN_EVENT_SUICIDE = 2
GUN_EVENT_HEADSHOT = 3


# Messages
MSG_GUNNERHIT = "{0} shoots {1} with a silver bullet!"
MSG_GUNNERWOLFKILL = "{0} is a wolf, and is dying from the silver bullet."
MSG_GUNNERHEADSHOTKILL = "{1} is not a wolf but was accidentally fatally injured."
MSG_GUNNERNONWOLFHIT = "{1} is a villager and was injured. Luckily "+\
                          "the injury is minor and will heal after a day of "+\
                          "rest."
MSG_GUNNERSUICIDE = "Oh no! {0}'s gun was poorly maintained and has exploded! "+\
                       "The village mourns a gunner-{2}."
MSG_GUNNERMISS = "{0} is a lousy shooter and missed!"

# Moo
MSG_PHASEERROR = "You may only {0} people during {1}." # Shoot, see, kill, observe, id, guard, ect. ect. ect.
MSG_ALREADYUSEDCMD = "You may only {0} once per round. "


MSG_LYNCHWOUNDED = "You are wounded and resting, thus you are unable to vote for the day."

#WereCrow
MSG_WERECROWOBSERVEERROR = "You are already observing {0}. "
MSG_WERECROWWASINBED = "As the sun rises, you conclude that {0} was sleeping \
all night long, and you fly back to your house."
MSG_WERECROWWASNTINBED = "As the sun rises, you conclude that {0} was not in bed all night\
, and you fly back to your house."
MSG_OBSERVINGWOLFERROR = "Flying to another wolf's house is a waste of time."
MSG_WERECROWOBSERVE = "You transform into a large crow and start your flight \
                   to {0}'s house. You will return after \
                  collecting your observations when day begins."
MSG_CROWALREADYKILLING = "You are already killing someone. "

MSG_KILLINGWOLFERROR = "You can't kill another wolf ..."

#Harlot
MSG_ALREADYVISITING = "You are already spending your night with {0}"

#Seer
MSG_OPERHIMSELF = "Why on earth would you {0} yourself..."
MSG_SEER = "You have a vision; in this vision, you see that {0} is a {1}!"

# Drunk
MSG_DRUNK = "You have been drinking too much! you are the village drunk. "

# Detective

MSG_DET = "The results of your investigation have returned. {0} is a... {1}!"
# Msg tables

gunner_msg_dict = {GUN_EVENT_MISS: MSG_GUNNERMISS,
                   GUN_EVENT_SUICIDE: MSG_GUNNERSUICIDE,
                   GUN_EVENT_HEADSHOT: MSG_GUNNERHEADSHOTKILL}
                   


# Time
PHASE_NIGHT = 0
PHASE_DAY = 1

# Roles



specs = {
    "BULLETS": ({10:1}, lambda game, ply: random.randint(
        2, int(math.cell(ply.BULLET_AMOUNT_CEIL*len(game.PlayerList.playerlist))))),
    "CURSED": ({6:1}, lambda *args: True),

}

# If you add a spec, please add the corresponding name to the field
# so that stats work
spec_table = {"BULLETS":("gunner", "gunners"),
              "CURSED":("cursed person", "cursed people")}
    

                
                    

class Game:

    

    def __init__(self, players, serv, on_end_func, kill_func, channel):
        self.PHASE = PHASE_NIGHT
        self.players, self.serv, self.on_end = players, serv, on_end_func

        self._kill, self.chan = kill_func, channel
        self.events = {
            EVENT_GUNNERKILL:[],
            EVENT_LYNCHKILL:[],
            EVENT_WOLFKILL:[]}
        
        self.vote = None
        self.ENDED = False
        self.role_list = []
        self.PlayerList = Player.PlayerList()
        
        self.events[EVENT_LYNCHKILL].append(self.event_lynch)
        self.events[EVENT_WOLFKILL].append(self.event_kill)
        


        self.current_specs = []

        # We're seeking for all the role classes
        for obj in dir(Player):
            obj = getattr(Player, obj)
            if type(obj) != type(self.__class__): continue

            if not issubclass(obj, Player.Player): continue

            if obj.distribution != NotImplemented:
                # Not theorical class, like OneUseCommandPlayer or Player itself
                # Means it has to be included
                self.role_list.append(obj)
                
            
    
        self.distribute_roles(players)
        self.start_kill()

    def distribute_roles(self, players):
        result = []
        for role in self.role_list:

            for x in range(self.getcount(role.distribution, len(players))):

                # Choose player, delete if from players and give him a role
                player = random.choice(players)
                players.remove(player)
                print player+' '+role.name_singular
                result.append(role(player, self))

        for player in players:
            # Every ply left is villie
            result.append(Player.Villager(player, self))



        self.PlayerList.extend(result)

        for spec in specs.keys():
            used = []

            random.shuffle(result) # Random of course
            
            for x in range(self.getcount(specs[spec][0], len(result))):
                # Add the specs
                for player in result:

                    # First object of specs tuple is distribution and second is lambda/func
                    # Lambda/func takes (Game Instance) and (Player instance) as params, returns the value of the field
                    # Game/Player currently only used by BULLETS (Gunner), but this program was designed to be extensible. 
                    if (getattr(player, spec) == None) or (player in used):
                        # If attribute value of player is None (e.g. BULLETS for wolf), just skip.
                        # Skip too if player has already the spec
                        continue
                    
                    print spec, player.name
                    self.current_specs.append((spec, player)) # asdf
                    setattr(player, spec, specs[spec][1](self, player))
                    used.append(player)
                    break
                    

                    
                

        return result
            

    def getcount(self, distribution, plycount):
        # Used to compute this:
        # getcount({4:1, 8:2, 20:3}, 18)
        # Result: (biggest number smaller than plycount) => 8 => 2

        num = 0

        for count in sorted(distribution.keys()):
            if count > plycount:
                break
            
            if distribution[count] > num:
                num = distribution[count]

        return num

    
        
    def get_nonwoundedcount(self):
        "Pretty obvious ..."
        num = 0
        for player in self.PlayerList.playerlist:
            if player.VOTE: num+=1

        return num

    def get_votingwolfcount(self):
        num = 0
        for player in self.PlayerList.playerlist:
            if not self.PlayerList.iswolf(player):
                continue


            if player.__class__ == Player.Werecrow and player.OBSERVING: continue

            num+=1
        return num


    def kill_victim(self):
        if hasattr(self.vote, "victim"):
            self.kill(victim)
            
    def clear_vote(self):
        if hasattr(self, "vote"):
            if self.vote:
                del self.vote
        
        
    def start_kill(self):
        self.clear_vote()
        self.vote = Vote(self, self.get_votingwolfcount, EVENT_WOLFKILL)

    def start_lynch(self):
        self.clear_vote()
        self.vote = Vote(self, self.get_nonwoundedcount, EVENT_LYNCHKILL)
        

    def votenum_func(self):
        if self.PHASE == PHASE_DAY:
            return self.get_nonwoundedcount()

        return self.get_votingwolfcount()
        

    def startvote(self):
        event = EVENT_LYNCHKILL if self.PHASE == PHASE_DAY else EVENT_WOLFKILL
        self.vote = Vote(self, self.votenum_func, event)
            



    def mass_call(self, methodname):
        for player in self.PlayerList.playerlist:
            for i in dir(player):
                if i.startswith(methodname):
                    getattr(player, i)()

    

    def event_lynch(self, target):
        self.mass_call("on_night")
        self.kill(target.name)
        self.PHASE = PHASE_NIGHT
        if not self.isgameover():
            self.start_kill()
        
    

    
    def event_kill(self, target):
        self.kill(target.name) if target.wolf_is_dead() else None
        self.mass_call("on_day")
        self.PHASE = PHASE_DAY
        if not self.isgameover():
            self.start_lynch()
        
        
        

    def RunEvent(self, event, *args):
        for func in self.events[event]:
            
            func(*args)



    def isgameover(self):
        x = self.PlayerList.deepcount(Player.Wolf)
        print "Game stats: Wolves:", x, "Villies: ", len(self.PlayerList.playerlist)
        if x == 0:
            print "All the wolves are dead :OOO"
            self.ENDED = True

        
        elif x >= len(self.PlayerList.playerlist)/2.0:
            print "O NOES VILLAGERS HAVE LOST"
            self.ENDED = True

        else:
            return False

        if self.ENDED:
            self.on_end(self.chan)

        return True
    
   
    def kill(self, target):
        print target+" was killed. "
        self._kill(target)
        del self.PlayerList[target]



