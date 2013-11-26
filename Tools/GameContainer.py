from Werewolf.Game import Game
from Werewolf.Lobby import Lobby



class GameContainer:
    # Contains all the games
    stasisdicts = {}

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
        if not chan in self.stasisdicts.keys():
            self.stasisdicts[chan] = {}
        if chan in self.container.keys():
            del self.container[chan]
            
        self.container[chan] = Lobby(self.channels,
                                     self.serv,
                                     chan,
                                     self.start_game,
                                     self.stasisdicts[chan],
                                     self.container)

    def start_game(self, chan):

        ## TODO: add tests
        plylist = self.container[chan].players
        del self.container[chan]
        self.container[chan] = Game(plylist,
                                         self.serv,
                                         self.createlobby,
                                         lambda *args: None,
                                         chan)

    #def    
