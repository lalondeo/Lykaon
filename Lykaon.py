#!usr/bin/env/python

import irclib, ircbot, TimeManager
irclib.DEBUG = 1
from Werewolf import Game
from threading import Thread
import traceback, sys
import Commands
from Tools.GameContainer import GameContainer
import Tools.config as config

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
        self.CommandClass = Commands.CommandClass(self.channels, serv)
        serv.TimeManager = TimeManager.TimeManager(serv) # ASDF
        self.GameContainer = GameContainer(self.channels, serv)
        serv.privmsg("nickserv", "identify incredible quenya")
        
        for chan in config.CHANS:
            serv.join(chan)

    def on_join(self, serv, event):
        
        chan = event.target()
        authorname = event.source().split('!')[0]
        if authorname == self.nick:
            self.GameContainer.createlobby(chan)
            return

        # TODO: Voice the player if Game

    def on_privmsg(self, serv, event):
        self.on_pubmsg(serv, event) # A bit hacky, but meh.
    
    def on_pubmsg(self, serv, event):
        try:
            target = event.target()
            user = event.source().split('!')[0]
            if target[0] != "#":
                chan = self.GameContainer.find_game(user)
                if not chan:
                    return
                
                namespace = self.GameContainer.container[chan]
                if issubclass(namespace, GameContainer.Lobby):
                    return # Nein

                

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

        if lastnick == self.NICK:
            self.NICK = newnick
            return

        chan = self.GameContainer.find_game(user)
        if not chan:
            return # Nothing to change

        klass = self.GameContainer.container[chan]
        if issubclass(klass, Lobby):
            klass.plylist.remove(lastnick)
            klass.plylist.append(newnick)
        

Lykaon = Lykaon()
while 1:
    exec raw_input(">> ")
        
        

        


