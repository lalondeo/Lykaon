from Werewolf import Game

class GameContainer:
    # Contains all the games

    def __init__(self, channels, serv):
        self.channels, self.serv = channels, serv
        self.container = {}

    def find_game(self, ply):
        # Will browse in all the games to find the one in which ply is participating :oooo

        for chan in self.container.keys():
            if ply in self.container[chan].players:
                return chan

        return None

    def createlobby(self, chan):
        del self.container[chan]
        self.container[chan] = Game.Lobby(self.channels, self.serv, chan)

    def start_game(self, chan):

        ## TODO: add tests
        plylist = self.container[chan].plylist
        del self.Games[chan]
        self.container[chan] = Game.Game(plylist,
                                         self.serv,
                                         self.createlobby,
                                         lambda *args: None,
                                         chan)

    #def    
