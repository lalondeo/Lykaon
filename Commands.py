#!usr/bin/env/python
from threading import Thread
import traceback, sys
from Werewolf.Game import WerewolfException # :oo

owners = ["unaffiliated/incredible"]

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
    
        def get_func(self, channel, author, *args):

                cmdname = args[0].lower()
                authorhostmask = author.split('!')[1].split('@')[1]
                try:
                        target = getattr(self.namespace, cmdname)
                        
                except AttributeError, SyntaxError:
                        a = search_object(
                            self.find_callable_attrs(),
                            cmdname, verbose=False)

                        if not a: 
                            return "Attribute not found. "

                        return "Error: Attribute not found, did you mean "+a+"?"

                except WerewolfException as exception:
                    return str(exception)

                if ((cmdname in namespace.admincmds and not authorhostmask in namespace.adminlist and not authorhostmask in owners) or
                    cmdname in namespace.ownercmds and not authorhostmask in owners):
                    raise WerewolfException("You need a higher security level to use these commands.")
                    
                    
                                   
                if type(target) == type(self.get_func) or type(target) == type(lambda: 0):
                    if not target.__doc__:
                        raise WerewolfException("You are disallowed to call this command. ")
                    
                    target(*args[1:])
                         
                else:
                          return "OOPS"
                                                         
        def fhelp(self):
            pass
        
        def call_func(self, target, author, namespace, cmdtext):
                
                try:
                        self.namespace = namespace
                        self.target, self.namespace.target = target, target
                        self.author, self.namespace.author = author, author
                        self.namespace.authorname = author
                        
                        cmdtext = cmdtext.split(' ')

                        
                        result = self.get_func(target, author, *cmdtext)
                        if not result: return
                        
                        
                        self._OutputMethod(target, result, author)

                except:
                    
                        message = str(sys.exc_info()[1])
                        author = author.split('!')[0]
                        if type(message) == type(1):
                                print("TARGET: "+target, " MESSAGE: "+str(message), " AUTHOR: "+author)
                                self._OutputMethod(target,
                                                   "Error: "+str(message), author)
                                return

                        traceback.print_exc()

                        return self._OutputMethod(target,
                                                  message, author)

        

        def find_callable_attrs(self):
            result = []
            for obj in dir(self.namespace):
                _type = type(getattr(self.namespace, obj))
                if _type == type(self.find_callable_attrs):
                    result.append(obj)

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



    
