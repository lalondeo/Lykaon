# ASDF
#import Game

class Vote:
    #Used for both vote/kill events
    def __init__(self, game, votenum_func, event):
        self.game, self.votenum_func = game, votenum_func
        self.event = event
        self.votes = {}

    def ismajority(self, votenum):
        return (votenum >= (self.votenum_func()+0.0)/2)

    def get_vote(self, player):
        for targ in self.votes:
            if player in self.votes[targ]:
                return targ
            
    def vote(self, source, target):
        source, target = self.game.PlayerList[source], self.game.PlayerList[target]
        for i in self.votes.keys():
            if source in self.votes[i]:
                self.votes[i].remove(source) #No multiple votes ._______.

        if not target in self.votes.keys():
            self.votes[target] = [source]

        else:
            self.votes[target].append(source)
            
        self.update()

    def update(self):
        
        for ply in self.votes.keys():
            if not ply in self.game.PlayerList.playerlist:
                del self.votes[ply]

            else:
                for voter in self.votes[ply]:
                    if not voter in self.game.PlayerList.playerlist:
                        del self.votes[ply][voter]

                if self.ismajority(len(self.votes[ply])):
                    self.game.RunEvent(self.event)
                    break

    def get_victim(self, forced=False):
        countbank = [len(self.votes[x]) for x in self.votes.keys()]
        if countbank.count(max(countbank)) != 1:
            return # Even split :(

        if self.votenum_func() > max(countbank)*2 and not forced:
            return 

        for ply in self.votes.keys():
            if len(self.votes[ply]) == max(countbank):
                return ply

            
