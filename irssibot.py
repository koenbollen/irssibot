# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

import os
import sys
import logging
import util

class IrssiBot( object ):

    def __init__(self, root ):
        self.root = root
        self.exports = {}
        self.exports['root'] = root
        self.exports['bot'] = self
        self.commands = []
        self.__plugins = {}
        self.__hooks = {}

        self.__autoload()

    def __autoload(self ):
        path = os.path.join( self.root, "plugins/autoload" )
        if not os.path.exists( path ):
            return
        if path not in sys.path:
            sys.path.insert( 0, path )
        files = os.listdir( path )
        for file in files:
            name, _ = os.path.splitext( file )
            mod = __import__(name)
            try:
                inst = mod.main(self.exports)
                self.__plugins[name] = inst
            except AttributeError:
                print >>sys.stderr, "unable to load plugin:", name
            logging.info( "plugin '%s' loaded", name )

    def add_hook(self, name, type, func ):
        logging.debug( "hook added: %s %s", name, type )
        if type not in self.__hooks:
            self.__hooks[type] = {}
        self.__hooks[type][name] = func

    def del_hook(self, name, type ):
        logging.debug( "hook deleted: %s %s", name, type )
        try:
            del self.__hooks[type][name]
        except KeyError:
            pass

    def handle(self, info ):

        if not info['msg']:
            return

        logging.debug( "roothandle: %r", info )

        if None not in info.values():
            type = "pubmsg"
        elif not info['nick'] and not info['mask'] and info['target']:
            type = "ownmsg"
        elif not info['target'] and info['nick'] and info['mask']:
            type = "privmsg"
        else:
            return
        info['type'] = type

        hooks = []
        if type in self.__hooks:
            hooks += self.__hooks[type].values()
        if "msg" in self.__hooks:
            hooks += self.__hooks["msg"].values()
        for func in hooks:
            logging.debug( "calling hook %s for '%s'", type, func.__name__ )
            try:
                func( info )
            except Exception, e:
                pass

        while self.commands:
            command = self.commands.pop(0)
            if not command:
                continue
            sys.__stdout__.write( command.rstrip() + "\n" )

def main():

    keys = ( 'msg', 'nick', 'mask', 'target' )
    args = []
    for arg in sys.argv[1:]:
        if not arg:
            args.append( None )
        else:
            args.append( arg.strip() )
    info = dict( zip( keys, (args + [None]*4)[:4] ) )

    if __name__ == "__main__":
        root = os.path.dirname( os.path.realpath( sys.argv[0] ) )
    else:
        root = os.path.dirname( __name__ )

    logfile = os.path.join( root, "irssibot.log" )
    logging.basicConfig(
            filename=logfile,
            level=logging.DEBUG,
            format="%(levelname)-8s %(message)s"
        )
    sys.stdout = util.CallbackFile(
        writecallback=lambda msg:msg.strip() and logging.debug(msg.rstrip())
        )

    bot = IrssiBot( root )
    bot.handle( info )

    logging.info( "quit irssibot" )
    logging.info( "" )

if __name__ == "__main__":
    main()

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

