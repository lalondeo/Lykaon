import Game
import BaseClass, time

MINJOINTIME = 60
WAITTIMEADD = 20
MAXWAITCOUNT = 5

class Lobby(BaseClass.BaseChanClass):
    

    def __init__(self, channels, serv, channame, startfunc, StasisDict,
                 container):

        self.starttime = 0
        self.waitcount = 0
        self.players = []
        self.hostmasks = []

        
        self.channels, self.serv, self.channame, self.startfunc = channels, serv, channame, startfunc
        self.StasisDict, self.container = StasisDict, container

        if channame in StasisDict.keys():
            for accname in StasisDict[channame].keys():
                if accame in StasisDict[channame]:
                    if StasisDict[channame][accname] > 0: # -1 means banned
                        StasisDict[channame][accname] -= 1

                    if StasisDict[channame][accname] == 0:
                        del StasisDict[channame][accname] # 4phun

        # moo

    def get_hostmask(self, authorname):
        print authorname
        return authorname.split('!')[1].split('@')[1]
    
    def join(self):
        if len(self.players) == 0:
            self.starttime = time.time()
            
        authorname = self.author
        name = authorname.split('!')[0]
        
        hostmask = self.get_hostmask(authorname)
        if hostmask in self.StasisDict.keys():
            self.serv.notice(name, "Sorry, but you are in stasis for %s games" % self.StasisDict[hostmask])

        elif name in self.players:
            raise Game.WerewolfException("You are already in the game. ")

        for chan in list(self.channels):
            # Can't play in two chans at a time.
            if (name in self.container[chan].players):
                raise Game.WerewolfException("You can't play in two channels at a time. ")

        self.players.append(name)
        self.hostmasks.append(hostmask)

        # Voice him 
        self.serv.mode(self.channame, "+v "+name)

    def leave(self):
        hostmask = self.get_hostmask(self.author)
        name = self.author.split('!')[0]
        if not name in self.players:
            raise Game.WerewolfException("You didn't join yet")

        index = self.players.index(name)
        del self.players[index]
        del self.hostmasks[index]
              
        self.serv.mode(self.channame, "-v "+name)

        if len(self.players) == 0:
            self.starttime = 0
            self.waitcount = 0
            

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

        elif not self.get_hostmask(self.authorname) in self.players:
            raise Game.WerewolfException("You have to join first ...")

        elif (time.time()-self.starttime) < MINJOINTIME:
            raise Game.WerewolfException("Please wait at least "+str(time.time()-self.waitcount())+" more seconds")
            
        self.startfunc(self.channame)

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
            self.StasisDict[hostmask] = int(penalty)

        else:
            self.StasisDict[hostmask] += int(penalty)

        if hostmask in self.players:
            self.leave(self.find_hostmask(targetname)) # Rude :>
