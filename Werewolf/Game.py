import Player as Player
from Vote import Vote
from BaseClass import BaseChanClass
import random, math, time
import copy, json

spectext = "Out of these players, there are {0}"

msgs = json.loads(open("Config/msgs.txt").read())

YAMLDATA = NotImplemented # :^)

class WerewolfException(Exception): pass

class GameCreateError(Exception):
    pass

        
    
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
IDLE_TIMEOUT = IDLE_WARNING + 180
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

MSG_SELECTED = "{0} has selected {1} to be {2}!" # 1) author 2) target 3) action

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
MSG_DETREVEAL = "Someone accidentally drops a paper. \
The paper reveals that {0} is a detective!" # o noez

# Msg tables

gunner_msg_dict = {GUN_EVENT_MISS: MSG_GUNNERMISS,
                   GUN_EVENT_SUICIDE: MSG_GUNNERSUICIDE,
                   GUN_EVENT_HEADSHOT: MSG_GUNNERHEADSHOTKILL}
                   


# Time
PHASE_NIGHT = 0
PHASE_DAY = 1



specs = {
    "BULLETS": ({10:1}, lambda game, ply: random.randint(
        2, int(math.ceil(ply.BULLET_AMOUNT_CEIL*len(game.PlayerList.playerlist))))),
    "CURSED": ({6:1}, lambda *args: True),

}

# If you add a spec, please add the corresponding name to the field
# so that stats work
spec_table = {"BULLETS":("gunner", "gunners"),
              "CURSED":("cursed person", "cursed people")}
    

                
                    

class Game(BaseChanClass):

    

    def __init__(self, players, serv, on_end_func, kill_func, channel):
        serv.action(channel, "sets mode +m on "+channel)
        
        self.PHASE = PHASE_NIGHT

        
       
        self.players, self.serv, self.on_end = players, serv, on_end_func

        self._kill, self.chan = kill_func, channel
        self.channame = channel
        self.events = {
            EVENT_GUNNERKILL:[],
            EVENT_LYNCHKILL:[],
            EVENT_WOLFKILL:[]}
        
        self.vote = None
        self.ENDED = False
        self.first_night = True
        self.role_list = []
        self.PlayerList = Player.PlayerList()
        
        self.events[EVENT_LYNCHKILL].append(self.event_lynch)
        self.events[EVENT_WOLFKILL].append(self.event_kill)
        self.PHASESTART = time.time()
        


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
        self.mass_call("on_night")
        self.start_kill()

    def distribute_roles(self, players):
        print "*** DISTRIBUTION ***"
        
        result = []
        length = len(players)
        players = copy.deepcopy(players)
        
        for role in self.role_list:
            
            for x in range(self.getcount(role.distribution, length)):
                
                print role, x

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

            for i in range(len(result)*50):
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
                    

                    
        print "*** DISTRIBUTION ***"

        return result

    def reaper(self):
        # Will reap the idlers from the game. 8)

        tests = {
            (lambda tmstp, ply: tmstp-ply.LASTMSG > IDLE_WARNING and not ply.GAVEWARNING): (msgs["IDLEWARN"], False),
            (lambda tmstp, ply: tmstp-ply.LASTMSG > IDLE_TIMEOUT): (msgs["IDLEKILL"], True),
            (lambda tmstp, ply: tmstp-ply.PARTTIME > PART_WAIT_TIME): (msgs["PARTKILL"], True),
            (lambda tmstp, ply: tmstp-ply.QUITTIME > QUIT_WAIT_TIME): (msgs["QUITTIME"], True)}

        time.sleep()
        for player in self.PlayerList.playerlist:
            timestamp = time.time()
            # Execute all the tests.
            for test in tests.keys():
                if test(timestamp, player):
                    serv.privmsg(self.chan, tests[test][0].format(player.name))
                    if tests[test][1]:
                        # Not a warning, we have to murder *evil face*
                        self.kill(player.name)

                

                 
            
            

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
        # Since shot people don't count as voting people,
        # 10 people with two shot -> 8 -> 5 = majority
        num = 0
        for player in self.PlayerList.playerlist:
            if player.VOTE: num+=1

        return num

    def get_votingwolfcount(self):
        # Excluding wurcrawez
        num = 0
        for player in self.PlayerList.playerlist:
            if not self.PlayerList.iswolf(player):
                continue


            if player.__class__ == Player.Werecrow and player.OBSERVING: continue

            num+=1
        return num

    def revealroles(self):
        "asdfasdfasdf"
        result = ""
        for ply in self.PlayerList.playerlist:
            result+=ply.name+': '+ply.name_singular+' '

        return result

    def generate_rolestats(self, roles):
        seq = []

        for role in roles.keys():
            text = role.name_singular
            
            if roles[role] != 1:
                text = role.name_plural

            seq.append(str(roles[role])+' '+text)

        txt = ", ".join(seq[:-1])
        txt += " and "+seq[-1]
        return txt
                
    def generate_specs(self, specs):
        seq = []

        for spec in specs.keys():
            text = spec_table[spec][0]
            
            if specs[spec] != 1:
                text = spec_table[spec][1]

            seq.append(str(specs[spec])+' '+text)


        txt = ""
        txt = txt+", ".join(seq[:-1])
        txt += " and "+seq[-1]
        return spectext.format(txt)
        
        
    def rolestats(self):
        "Get the distribution of roles/specs"

        if not hasattr(self, "PlayerList"):
            raise Game.WerewolfException("No game is going on yet. ")

        roles = {}

        for player in self.PlayerList.playerlist:
            if not player.__class__ in roles.keys():
                roles[player.__class__] = 0
            
            roles[player.__class__]+=1

        specs = {}
        for tuple in self.current_specs:
            if tuple[1].DEAD:
                # No
                continue

            if not tuple[0] in specs.keys():
                specs[tuple[0]] = 0
        
            specs[tuple[0]] += 1

        return "There are "+self.generate_rolestats(roles)+". "+self.generate_specs(specs)+". "

    def lynch(self, target, *args):
        "Lynch lynch lynch lynch :O"
        return self.PlayerList[self.authorname.split('!')[0]].lynch(target)

    def shoot(self, target, *args):
        return self.PlayerList[self.authorname.split('!')[0]].shoot(target)



    def wolf_mass_msg(self,
                    nick = "",
                    msg = "",
                    function = (lambda serv: serv.privmsg),
                    _format = "<{1}> {0}"):
        
        # Sent to all the wolves.
        
        for player in self.PlayerList.playerlist:
            if player.name == nick or not issubclass(player.__class__, Player.Wolf):
                continue

            # Yes, function may seem retaaaaaaaaarded, but it is used for action too
            function(self.serv)(player.name, _format.format(msg, nick)) # asdf


    def kill_victim(self):
        if hasattr(self.vote, "victim"):
            self.kill(victim)
            
    def clear_vote(self):
        if hasattr(self, "vote"):
            if self.vote:
                del self.vote


    def phase_test(self, func):
        if (time.time() - self.PHASESTART) < 10:
            self.serv.TimeManager.addfunc(func, self.PHASESTART+10)
            return False # NEIN

        return True

    def set_phasestart(self):
        self.PHASESTART = time.time()
        
        
    def start_kill(self):
        # Roughly means "day -> night"
        if not self.phase_test(self.start_kill):
            pass
        
        self.clear_vote()
        self.set_phasestart()
        self.vote = Vote(self, self.get_votingwolfcount, EVENT_WOLFKILL)

    def start_lynch(self):
        # Roughly means "night -> day"
        if not self.phase_test(self.start_kill):
            pass
        
        self.first_night = False
        self.clear_vote()
        self.set_phasestart()
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
        print "Game stats: Wolves:", x, "Villies: ", len(self.PlayerList.playerlist)-x
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
        del self.PlayerList[target]
        self._kill(target)
        



