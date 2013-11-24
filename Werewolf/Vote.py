# ASDF

class Vote:
    #Used for both vote/kill events
    def __init__(self, game, votenum_func, event):
        self.game, self.votenum_func = game, votenum_func
        self.event = event
        self.votes = {}

    def ismajority(self, votenum):
        return (votenum >= (self.votenum_func()+0.0)/2)
            
    def vote(self, source, target):
        source, target = self.game.PlayerList[source], self.game.PlayerList[target]
        for i in self.votes.keys():
            if source in self.votes[i]:
                self.votes[i].remove(source) #No multiple votes ._______.

        if not target in self.votes.keys():
            self.votes[target] = [source]

        else:
            self.votes[target].append(source)
            
        if self.ismajority(len(self.votes[target])):
            self.game.RunEvent(self.event, target)
            self.victim = target
