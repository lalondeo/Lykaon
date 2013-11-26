import Game

playermsg = "{0} players: {1}.  "


class BaseChanClass:
    # Very ugly indeed, but I didn't find any better way of doing that.
    # Please note that these commands shouldn't be usable in query.

    landfunc = lambda x, serv, item, obj: "The {0} lands on {0}".format(
        item, obj)



    def playerlist(self):
        "Get the list of players. "
        return playermsg.format(str(len(self.players)), ", ".join(self.players))       

    def cointoss(self):
        print self.target+" tosses a coin into the air..."
        self.serv.TimeManager.addfunc(self.landfunc, 5, self.serv, "coin",
                                      random.choice(["heads", "tails"]))

    def ponytoss(self):
        print self.target+" throws a pony into the air..."
        self.serv.TimeManager.addfunc(self.landfunc, 5, self.serv, "pony",
                                      random.choice(["hoof", "plot"]))
