import Game, random

playermsg = "{0} players: {1}.  "


class BaseChanClass:
    # Very ugly indeed, but I didn't find any better way of doing that.
    # Please note that these commands shouldn't be usable in query.

    landfunc = lambda self, x, serv, item, landpoint: serv.pubmsg(
        self.target,
        "The {0} lands on {1}".format(item, landpoint))



    def playerlist(self):
        "Get the list of players. "
        return playermsg.format(str(len(self.players)), ", ".join(self.players))       

    def cointoss(self):
        
        print self.author.split('!')[0] + " tosses a coin into the air..."
        self.serv.TimeManager.addfunc(self.landfunc, 3, self.serv, "coin",
                                      random.choice(["heads", "tails"]))

    def ponytoss(self):
        print self.author.split('!')[0] + " throws a pony into the air..."
        self.serv.TimeManager.addfunc(self.landfunc, 3, self.serv, "pony",
                                      random.choice(["hoof", "plot"]))


