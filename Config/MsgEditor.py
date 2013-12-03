import json
import sys, traceback

def display(text):
    sys.stdout.write(text+'\n') # To avoid 2.x/3.x compatibility issues

class Commands:
    
    def _load(self):
        try:
            return (json.loads(open("msgs.txt").read()))

        except IOError:
            display("Please don't mess with msgs.txt. ")

        except:
            traceback.print_exc()
            
    def get(self, x):
        display(self._load()[x])

    def set(self, x):
        try:
            newmsg = raw_input("Please provide a new message. ")

        except KeyboardInterrupt:
            return

        dict = self._load()
        print dict
        dict[x] = newmsg
        open("msgs.txt", "w").write(json.dumps(dict))

Commands = Commands()

if __name__ == "__main__":

    while 1:
        data = raw_input(">> ").split(' ')
        if data[0][0] == "_":
            display("Internal command. ")
        
        try:
            getattr(Commands, data[0])(*data[1:])

        except:
            traceback.print_exc()
