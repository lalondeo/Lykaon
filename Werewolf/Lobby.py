import Game
import BaseClass, time, json

msgs = json.loads(open("Config/msgs.txt").read())

MINJOINTIME = 60
WAITTIMEADD = 20
MAXWAITCOUNT = 5

class Lobby(BaseClass.BaseChanClass):
    

    def __init__(self, channels, serv, channame, startfunc, userdict,
                 container):

        self.starttime = 0
        self.waitcount = 0
        self.players = []
        self.hostmasks = []
        self.admins = userdict["adminlist"]
        self.stasisdict = userdict["stasisdict"]

        
        self.channels, self.serv, self.channame, self.startfunc = channels, serv, channame, startfunc
        self.userdict, self.container = userdict, container

        for accname in self.stasisdict.keys():
                if self.stasisdict[accname] > 0: # -1 means banned
                    self.stasisdict[accname] -= 1

                    if self.stasisdict[accname] == 0:
                        del self.stasisdict[accname] # 4phun

        # moo

    # Handlers

    def on_part(self, event):
        self.author = event.source()
        self.leave(errmsg=False, msg=msgs["LOBBYLEAVEMSG"])

    def on_quit(self, event):
        self.author = event.source()
        self.leave(errmsg=False, msg=msgs["QUITMSG"])

    def on_kick(self, event):
        self.author = event.source()
        self.leave(errmsg = False, msg = msgs["KICKMSG"])


    # Helpers

    def get_nickname(self, authorname):
        return authorname.split('!')[0]
    
    def get_hostmask(self, authorname):
        return authorname.split('!')[1].split('@')[1]

    def display_plycount(self):
        self.serv.privmsg(self.channame, msgs["LOBBYPLYCOUNT"].format(str(len(self.players))))

    # Actual commands
    
    def join(self):
        "Join the game. "
        if len(self.players) == 0:
            self.starttime = time.time()
            
        authorname = self.author
        name = self.get_nickname(authorname)
        
        hostmask = self.get_hostmask(authorname)
        if hostmask in self.userdict["stasisdict"].keys():
            self.serv.notice(name, "Sorry, but you are in stasis for %s games" % self.userdict["stasisdict"][hostmask])

        elif name in self.players:
            raise Game.WerewolfException("You are already in the game. ")

        for chan in list(self.channels):
            # Can't play in two chans at a time.
            if (name in self.container[chan].players):
                raise Game.WerewolfException("You can't play in two channels at a time. ")

        print "OKEY"
        self.players.append(name)
        self.hostmasks.append(hostmask)
        self.serv.privmsg(self.channame, msgs["JOINMSG"].format(name))
        self.display_plycount()

        # Voice him 
        self.serv.mode(self.channame, "+v "+name)



    def leave(self, errmsg=True, msg = msgs["LOBBYLEAVEMSG"]):
        "leave teh game. "
        try:
            if type(errmsg) != type(False):
                return # NO .____________.
            
            
            hostmask = self.get_hostmask(self.author)
            name = self.get_nickname(self.author)
                                                                
            if not name in self.players:
                raise Game.WerewolfException("You didn't join yet")

            index = self.players.index(name)
            del self.players[index]
            del self.hostmasks[index]

            self.serv.privmsg(self.channame, msg.format(name, "player"))
            self.display_plycount()
            self.serv.mode(self.channame, "-v "+name)

             # Reset the stats because we have to.
            if len(self.players) == 0:
                self.starttime = None
                self.waitcount = 0

        except:
            if errmsg:
                raise
            

    quit = leave

    def wait(self):
        "Extend the waiting time to prevent too quick !start"
        if self.waitcount >= MAXWAITCOUNT:
            raise Game.WerewolfException("The wait time can't be extended anymore. ")

        

        self.starttime += WAITTIMEADD
        self.waitcount += 1
        return "The wait time has been extended of {0} seconds. ".format(str(WAITTIMEADD))
    
        

    def start(self):
        "Start eet. "
        
        if len(self.players) < 4:
            raise Game.WerewolfException("Not enough players. ")

        elif not self.authorname.split('!')[0] in self.players:
            raise Game.WerewolfException("You have to join first ...")

        elif (time.time()-self.starttime) < MINJOINTIME:
            raise Game.WerewolfException("Please wait at least "+str(int(round(MINJOINTIME-time.time()+self.starttime)))+" more seconds")
            
        self.startfunc(self.channame)

    def find_hostmask(self, name):
        for _list in (self.channels[self.channame].users(),
                                self.channels[self.channame].voiced()):

            for user in _list:
                if user.split('!')[0] == name:
                    return user

        raise WerewolfException("Name not found")
            

    def setstasis(self, targetname, penalty):
        "moo. "
        if not penalty.isdigit() or not penalty:
            return "you must provide a valid integer. "
            
        hostmask = self.get_hostmask(self.find_hostmask(targetname))
        if not hostmask in StasisDict.keys():
            self.StasisDict[hostmask] = int(penalty)

        else:
            self.StasisDict[hostmask] += int(penalty)

        if hostmask in self.players:
            self.leave(self.find_hostmask(targetname)) # Rude :>

    admincmdlist = [setstasis]
