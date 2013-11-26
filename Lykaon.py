#!usr/bin/env/python

import irclib, ircbot, TimeManager
irclib.DEBUG = 1
from Werewolf import Game
from Werewolf import BaseClass
from threading import Thread
import traceback, sys
import Commands
from Tools.GameContainer import GameContainer
import Tools.config as config

if sys.version_info[0] == 3:
    import imp
    reload = imp.reload # I know, it's retarded, live with it.


for obj in globals().keys():
    if type(globals()[obj]) == type(sys) and globals()[obj] != sys:
        print obj
        reload(globals()[obj])

class Lykaon(ircbot.SingleServerIRCBot):

    Games = {} 

    def __init__(self):
        ircbot.SingleServerIRCBot.__init__(self, [(config.SERVER, 6667)],
                                           config.NICK,
                                           config.REALNAME)

        self.nick = config.NICK # Yes, yes :^)
        
        try:
          a = Thread(target = self.start)
          a.start()
        except KeyboardInterrupt:
          self.connection.quit("Ctrl-C at console")
          
          
        except Exception, e:
          traceback.print_exc()
          self.connection.quit("%s: %s" % (e.__class__.__name__, e.args))
          raise

        except:
            traceback.print_exc()


        

    def on_welcome(self, serv, event):
        # Useful
        self.serv = serv
        
        self.CommandClass = Commands.CommandClass(self.channels, serv)
        serv.TimeManager = TimeManager.TimeManager(serv) # ASDF
        self.GameContainer = GameContainer(self.channels, serv)
        
        for chan in config.CHANS:
            serv.join(chan)

    def on_join(self, serv, event):
        
        chan = event.target()
        authorname = event.source().split('!')[0]
        if authorname == self.nick:
            self.GameContainer.createlobby(chan)
            return

        # TODO: Voice the player if Game

    def find_game(self, user):
        chan = self.GameContainer.find_game(user)
        if not chan:
            return
        
        namespace = self.GameContainer.container[chan]
        if issubclass(namespace, GameContainer.Lobby):
            return # Nein

        return namespace
                
    def on_privmsg(self, serv, event):
        self.on_pubmsg(serv, event) # A bit hacky, but meh.
        user = event.source().split('!')[0]
        chan = self.find_game(user)

        if not chan: return
        if chan.PlayerList.deep_istype(chan.PlayerList[user], Game.Player.Wolf):
            chan.wolf_mass_msg(user, event.arguments()[0])

        
        
    
    def on_pubmsg(self, serv, event):
        try:
            target = event.target()
            user = event.source().split('!')[0]
            if target[0] != "#":
                chan = self.find_game(user)
                if not chan:
                    return

                

            else:
                namespace = self.GameContainer.container[target] # Must work

            text = event.arguments()[0]
            if text[0] == config.COMMANDCHAR:
                self.CommandClass.call_func(target, event.source(), namespace, text[1:])

        except Game.WerewolfException:
            serv.notice(event.source().split('!')[0], sys.exc_info()[1].message)


        except:
            serv.privmsg(target, "Ooops, an exception logged in console. ")
            traceback.print_exc()

    def on_nick(self, serv, event):
        lastnick = event.source().split('!')[0]
        newnick = event.target()

        if lastnick == self.nick:
            self.nick = newnick
            return

        chan = self.GameContainer.find_game(lastnick)
        if not chan:
            return # Nothing to change

        klass = self.GameContainer.container[chan]
        if klass.__class__.__name__ == "Lobby":
            klass.players.remove(lastnick)
            klass.players.append(newnick)

        else:
            klass.PlayerList[lastnick].name = newnick
        

#Lykaon = Lykaon()



sample = "%s!foo@bar"

def test():
    global Lykaon
    serv = Commands.FakeServ()
    Lykaon.start = lambda *args, **kw: None
    Lykaon = Lykaon()
    Lykaon.on_welcome(serv, None)
    event0 = irclib.Event("asdf", sample%"Lykaon", target="#asdf")
    Lykaon.on_join(serv, event0)
    
    for name in ["foo", "bar", "asdf", "nigga", "fucker", "Ristovski", 
                 "Yo mama", "blah", "bluerg", "mudafeka", "bob", "bill",
                 "bernie"]:
        
        event1 = irclib.Event("asdf", sample%name,
                          "#asdf", arguments=["!join"])
    

        Lykaon.on_pubmsg(serv, event1)

    print Lykaon.GameContainer.container["#asdf"].playerlist()


        
    Lykaon.GameContainer.container["#asdf"].start()
    print Lykaon.GameContainer.container["#asdf"].revealroles()
    


test()

while 1:
    try:
        exec raw_input(">> ")

    except:
        traceback.print_exc()
