from Werewolf.Game import WerewolfException
from Werewolf.BaseClass import BaseChanClass

class Lobby(BaseChanClass):
    

    def __init__(self, channels, serv, channame, startfunc, StasisDict):
        self.plylist = []
        self.channels, self.serv, self.channame = channels, serv, channame, startfunc
        self.StasisDict = StasisDict

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
        if hostmask in self.StasisDict.keys():
            return "no"

        elif hostmask in self.plylist:
            return "you have already joined you derpface"

        for chan in self.channels:
            # Can't play in two chans at a time.
            if (authorname in
                self.channels[chan].users()+self.channels[chan].voiced()+self.channels[chan].opers()):
                return "Nein"

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
            self.StasisDict[hostmask] = int(penalty)

        else:
            self.StasisDict[hostmask] += int(penalty)

        if hostmask in self.plylist:
            self.leave(self.find_hostmask(targetname)) # Rude :>
