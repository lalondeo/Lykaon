#!usr/bin/env/python

import irclib, ircbot, TimeManager
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
        self.GameContainer = GameContainer()
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
            user = event.source()
            if target[0] != "#":
                namespace = self.GameContainer.find_game(target)

            else:
                namespace = self.GameContainer.container[target]
            
            if not game:
                return # ASDF

            text = event.arguments()[0]
            if text[0] == "!":
                self.CommandClass.call_func(user, user, namespace, text[1:])

        except Game.WerewolfException:
            serv.notice(event.source(), sys.exc_info()[1].message)

        except:
            serv.privmsg(target, "Ooops, an exception logged in console. ")
            traceback.print_exc()

        
        
        
        
        

        


