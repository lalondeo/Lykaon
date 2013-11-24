#!usr/bin/env/python
from threading import Thread
import traceback, sys
from Game import WerewolfException # :oo

class FakeServ:
    "When testing offline. "
    def print_data(self, *args):
        print ", ".join(args)
        
    def __getattr__(self, name):
        # Badass
        print name, ":", 
        return self.print_data


def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in xrange(-1,lenstr1+1):
        d[(i,-1)] = i+1
    for j in xrange(-1,lenstr2+1):
        d[(-1,j)] = j+1
 
    for i in xrange(lenstr1):
        for j in xrange(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition
 
    return d[lenstr1-1,lenstr2-1]



def search_object(list, keyword, verbose=True):
    
        results = {}
        keyword = keyword.lower()
        for i in list:
                results[damerau_levenshtein_distance(keyword, i)] = i



        if sorted(results.keys())[0] > 5: #ugh
                if verbose:
                    return "No good matches found for your keyword"

                return None
                    
        return results[sorted(results.keys())[0]]




class CommandClass:

        
        def __init__(self, channels, serv):
            self.channels, self.serv = channels, serv
            
        def _OutputMethod(self, target, text, *args):
            if not text:
                return

            

            self.OutputMethod(target, text, *args)
                

        def OutputMethod(self, target, text, *args):
            
            self.serv.privmsg(target, args[0].split('!')[0]+': '+str(text))
            
        ChanOperValues = ["voiced", "opers"]

        def getuserrank(self, user, channel):

            try:
            
                for i in range(len(self.ChanOperValues)):
                    if user in getattr(self.channels[channel], self.ChanOperValues[i])():
                       
                        return i+1

            except:
                traceback.print_exc()
                
            
            return 0

        def execthreadedcommand(self, command, channel, author, *args):
            result = command(*args)
            self.OutputMethod(channel, str(result), author)

        
        
    
        def get_func(self, channel, author, *args):

                try:
                        
                        target = getattr(self.namespace, args[0].lower())
                    
                except AttributeError, SyntaxError:
                        a = search_object(
                            self.find_callable_attrs(),
                            args[0].lower(), verbose=False)

                        if not a: 
                            return "Attribute not found. "

                        return "Error: Attribute not found, did you mean "+a+"?"

                except WerewolfException:
                    return sys.exc_info()[1].message

                if target.func_name[0].lower() == "f":
                    if hasattr(self, target.func_name[1:]):
                        raise
                    
                

                   
                if type(target) == type(self.get_func) or type(target) == type(lambda: 0):
                    
                         target()

                else:
                          raise Exception(4)
                                                         
        def fhelp(self):
            pass
        
        def call_func(self, target, author, namespace, cmdtext):
                
                try:
                        self.namespace = namespace
                        self.target, self.namespace.target = target, target
                        self.author, self.namespace.author = author, author
                        
                        cmdtext = cmdtext.split(' ')

                        
                        result = self.get_func(target, author, *cmdtext)
                        if not result: return
                        
                        
                        self._OutputMethod(target, result, author)

                except:
                    
                        message = sys.exc_info()[1].message
                        author = author.split('!')[0]
                        if type(message) == type(1):
                                print("TARGET: "+target, " MESSAGE: "+self.errnos[message], " AUTHOR: "+author)
                                self._OutputMethod(target,
                                                   "Error: "+self.errnos[message], author)
                                return

                        traceback.print_exc()

                        return self._OutputMethod(target,
                                                  message, author)

        errnos = open("CommandCallingErrnos.txt").read().split('\n')

        def find_callable_attrs(self):
            result = []
            for i in dir(self):
                _type = type(getattr(self, i))
                if _type == type(self.find_callable_attrs) or _type == type(self):
                    result.append(i)

            return result
        
        def commandlist(self, authorname):
              "Will print a list of commands IN A QUERY."
              result = ""
              authorname = authorname.split('!')[0]
              
              for i in dir(self.namespace):
                x = getattr(self, i)

                if sys.getsizeof(result+i.upper()) > 250:
                   self.serv.privmsg(authorname, result)
                   result = ""

              
                if type(x) == type(self.commandlist) and x.__doc__:
                   result += x.func_name+', '
                 

              self.serv.privmsg(authorname, result[:-2])



       

        def help(self, *command):
              "Will hopefully find something useful"
              data = getattr(self.namespace, command[0]).__doc__
              return "Info for %s command: %s" % (command[0].upper(), data)

        namespace = None



    