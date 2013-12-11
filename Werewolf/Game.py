import Player as Player
from Vote import Vote
from BaseClass import BaseChanClass
import random, math, time, traceback, datetime
import copy, json
from Tools import config

spectext = "Out of these players, there are {0}"

msgs = json.loads(open("Config/msgs.txt").read())

YAMLDATA = NotImplemented # :^)

class WerewolfException(Exception): pass

        
    
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
GUN_EVENT_WOLFKILL = 1
GUN_EVENT_MISS = 2
GUN_EVENT_SUICIDE = 3
GUN_EVENT_HEADSHOT = 4




# Msg tables

gunner_msg_dict = {GUN_EVENT_MISS: msgs["GUNNERMISS"],
                   GUN_EVENT_SUICIDE: msgs["SUICIDE"],
                   GUN_EVENT_HEADSHOT: msgs["HEADSHOTKILL"]}
                   


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
        
        self.players, self.serv, self.on_end = copy.deepcopy(players), serv, on_end_func

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

        to_night = lambda: self.do_phase_change("on_night",  PHASE_NIGHT, self.get_votingwolfcount, EVENT_WOLFKILL)
        to_day = lambda: self.do_phase_change("on_day", PHASE_DAY, self.get_nonwoundedcount, EVENT_LYNCHKILL)
        
        self.events[EVENT_LYNCHKILL].append(lambda: self.kill_victim(to_night, "NIGHTMSG"))
        self.events[EVENT_WOLFKILL].append(lambda: self.kill_victim(to_day, "DAYMSG"))
        
        


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
        to_night()
        

    def on_tick(self):
        # Called every 1 second.
        self.reaper()
        if self.vote:
            # Not much useful, since every special command uses it, but it will avoid bugs in case of a faulty modded function.
            self.vote.update()
        

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
                    self.current_specs.append((spec_table[spec], player)) # asdf
                    setattr(player, spec, specs[spec][1](self, player))
                    used.append(player)
                    break
                    

                    
        print "*** DISTRIBUTION ***"

        return result

    def reaper(self):
        # Will reap the idlers from the game. 8)

        tests = {
            (lambda tmstp, ply: (tmstp-ply.LASTMSG) > IDLE_WARNING and not ply.GAVEWARNING): (msgs["IDLEWARN"], False, ("GAVEWARNING", True)),
            (lambda tmstp, ply: (tmstp-ply.LASTMSG) > IDLE_TIMEOUT): (msgs["IDLEKILL"], True),
            (lambda tmstp, ply: (tmstp-ply.PARTTIME) > PART_WAIT_TIME and ply.PARTTIME != 0): (msgs["PARTMSG"], True),
            (lambda tmstp, ply: int(tmstp-ply.QUITTIME) > QUIT_WAIT_TIME and ply.QUITTIME != 0): (msgs["QUITMSG"], True)}

        
        for player in self.PlayerList.playerlist:
            timestamp = time.time()
            # Execute all the tests.
            for test in tests.keys():
                if test(timestamp, player):
                    print tests[test][0]
                    self.serv.privmsg(self.chan, (tests[test][0]).format(player.name, player.name_singular))

                    if len(tests[test]) == 3:
                        setattr(player, tests[test][2][0], tests[test][2][1])
                        
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


            if not player.CANKILL: continue

            num+=1
        return num

    def revealroles(self, singularverb = "is", pluralverb = "are"):
        "asdfasdfasdf"

        print traceback.extract_stack()

        roles = {}
        for char in self.PlayerList.playerlist:
            nametuple = (char.name_singular, char.name_plural)
            if not nametuple in roles.keys():
                roles[nametuple] = [char.name]

            else:
                roles[nametuple].append(char.name)

        for spec in self.current_specs:
            if not spec[0] in roles.keys():
                roles[spec[0]] = []
            roles[spec[0]].append(spec[1].name)

        print roles
        result = []
        for names in roles.keys():
            verb = pluralverb
            rolename = names[1]
            plynames = roles[names]
            
            if len(plynames) == 1:
                result.append("The "+names[0]+' '+singularverb+' '+plynames[0])
                continue

            result.append("The "+" ".join([rolename, verb+' '])+", ".join(plynames[:-1])+' and '+plynames[-1])
        return ". ".join(result)
            

            

        
        

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
        "Let's shooooooooooot PEW PEW"
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
    
    def mass_call(self, methodname, *args, **kw):
        # For phase changes and deaths.  
        for player in self.PlayerList.playerlist:
            for i in dir(player):
                if i.startswith(methodname):
                    # Call eeeeeeet
                    getattr(player, i)(*args, **kw)


    def phase_test(self, func):
        # moo
        if (time.time() - self.PHASESTART) < 10:
            self.serv.TimeManager.addfunc(func, time.time()-self.PHASESTART)
            return False # NEIN

        return True


    def do_phase_change(self, event_name, phaseid, votetestfunc, event):
        # Either night to day or day to night
        self.mass_call(event_name)
        self.PHASE = phaseid
        self.PHASESTART = time.time()
        self.PHASEWARN = 0 
        
        self.vote = None
        self.vote = Vote(self, votetestfunc, event)

        if self.PHASE == PHASE_DAY:
            self.serv.privmsg(self.channame, msgs["WHOMTOLYNCH"]).format(
                config.COMMANDCHAR, round(self.getnonwoundedcount()/2.0))


    msgtable = {PHASE_NIGHT: ("NOKILL", "WOLFKILL"),
                PHASE_DAY: ("NOLYNCH", "LYNCHKILL")}

    def kill_victim(self, phasechangefunc, msg):
        victim = self.vote.get_victim()
        victim.chanmsg(msgs[msg].format(
            str(datetime.timedelta(seconds=round(time.time()-self.PHASESTART)))[2:]))
            
        if not victim:
            self.serv.privmsg(self.channame, msgs[self.msgtable[self.PHASE][0]])

        else:
            # TODO: send da message
            self.RESULTS = []
            victim.on_death(EVENT_WOLFKILL if self.PHASE == PHASE_NIGHT else EVENT_LYNCHKILL)
            if not False in self.RESULTS:
                self.serv.privmsg(self.channame, msgs[self.msgtable[self.PHASE][1]].format(victim.name, victim.name_singular))
                self.kill(victim.name)


        phasechangefunc()
        
        
        

    def RunEvent(self, event, *args):
        # Ugly, but meh.
        for func in self.events[event]:
            func(*args)

    def end(self, happyending=True):
        # End eet
        # happyending = villagers have won or not
        print "moo"
        self.ENDED = True
        text = ""
        if happyending:
            text = "VILWIN"

        elif happyending == False:
            text = "WOLFWIN"

        else:
            text = "NOWIN" # Some big meanie aborted it



        self.serv.privmsg(self.channame, msgs[text])
        self.serv.privmsg(self.channame, self.revealroles(singularverb = "was", pluralverb = "were"))
        self.on_end()
        

        
    


    def isgameover(self):
        x = self.PlayerList.deepcount(Player.Wolf)
        if x == 0:
            self.end(happyending = True)

        
        elif x >= len(self.PlayerList.playerlist)/2.0:
            self.end(happyending = False)

        else:
            return False

        

   
    def kill(self, target):
        del self.PlayerList[target]
        self.players.remove(target)
        self._kill(target)
        



