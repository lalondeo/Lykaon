import time, traceback
from threading import Thread

BADELEMENTAMOUNT = "ERROR: Object {0} of event\
loop is containing bad amount of elements({1}): {2}"

class TimeManager:
    # Everything related to time
    # (e.g. Idling players slaying, coin tossing, game phase switch, etc.)
    # is computed here.
    def __init__(self, serv, GameContainer):
        self.serv, self.GameContainer = serv, GameContainer
        Thread(target=self.infiniteloop).start() # Start eet
        

    # Format: (timestamp, function, args)
    # Function's first arg is a TimeManager instance.
    event_bank = []

    def addfunc(self, func, delay, *args):
        event = [time.time()+delay, func]+list(args)
        self.event_bank.append(event)
        return event

    def call(self, func, args):
        try:
           
            func(self, *args)

        except:
            print traceback.print_exc()
        
    def infiniteloop(self):
        while 1:
            time.sleep(1)
            timestamp = time.time()
            for game in list(self.GameContainer):
                if hasattr(game, "PlayerList"):
                    game.on_tick()
                
            for obj in self.event_bank:
                if len(obj) < 2:
                    # We won't make the bot crash because of this
                    print BADELEMENTAMOUNT.format(
                            str(self.event_bank.index(obj)),
                            str(len(obj)),
                            str(obj))

                else:

                    if obj[0] <= timestamp:
                        
                        self.call(obj[1], obj[2:])
                        # Object expires after call.
                        # That's why self.call provides a TimeManager instance.
                        self.event_bank.remove(obj)

    def asdf(self):
        pass
                
                
                        

                
        
