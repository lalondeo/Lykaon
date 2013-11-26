import Game

playermsg = "{0} players: {1}"
spectext = "Out of these players, there are {0}. "

class BaseChanClass:
    # Very ugly indeed, but I didn't find any better way of doing that.
    # Please note that these commands shouldn't be usable in query.

    landfunc = lambda x, serv, item, obj: "The {0} lands on {0}".format(
        item, obj)

    def players(self):
        "Get the list of players. "
        if issubclass(self, Game.Game):
            players = self.players
            
        else:
            try:
                players = self.plylist

            except:
                
                raise Game.WerewolfException("Unknown namespace type.")
        
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
        print self.__class__, Game.Game
        if not issubclass(self.__class__, Game.Game):
            raise Game.WerewolfException("No game is going on yet. ")

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
