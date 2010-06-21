# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

import os
import sys
import logging
import util
import ConfigParser

class IrssiBot( object ):

    def __init__(self, root ):
        self.root = root
        self.exports = {}
        self.exports['root'] = root
        self.exports['bot'] = self
        self.commands = []
        self.__plugins = {}
        self.__hooks = {}

        self.__config()
        logging.info( "irssibot started" )
        self.__setup()
        self.__autoload()

    def __autoload(self ):
        path = os.path.join( self.root, "plugins/autoload" )
        if not os.path.exists( path ):
            return
        if path not in sys.path:
            sys.path.insert( 0, path )
        files = os.listdir( path )
        for file in files:
            name, ext = os.path.splitext( file )
            if ext != ".py":
                continue
            mod = __import__(name)
            try:
                inst = mod.main(self.exports)
                self.__plugins[name] = inst
            except AttributeError, e:
                logging.error( "unable to load plugin:", name, "(", e, ")" )
            logging.info( "plugin '%s' loaded", name )

    def __setup(self ):
        self.dba = None
        self.dbc = None
        if self.cfg.has_option( "db", "type" ):
            dbtype  = self.cfg.get( "db", "type" )
            connect = self.cfg.get( "db", "connect" )
            try:
                self.dba = __import__( dbtype )
            except ImportError:
                logging.critical("unable to import database module: "+dbtype)
                sys.exit(1)
            try:
                self.dbc = self.dba.connect( connect )
            except self.dba.DatabaseError, e:
                logging.critical("unable to connect to the database: %s",e)
                sys.exit(1)
            logging.info("connected to the database" )
            self.exports['hasdb'] = True
        else:
            logging.info("no database connected" )
            self.exports['hasdb'] = False
        self.exports['dba'] = self.dba
        self.exports['dbc'] = self.dbc


        self.exports['cache'] = self.cache = util.Cache( self.dbc )


    def __config(self ):
        path = os.path.join( self.root, "config" )
        self.cfg = ConfigParser.ConfigParser( {'root': self.root} )
        read = self.cfg.read( path )
        self.exports['cfg'] = self.cfg

        if self.cfg.has_option("logging", "level"):
            lvls = ('debug', 'info', 'warn', 'err', 'crit')
            level = self.cfg.get("logging", "level")
            for i,l in enumerate(lvls):
                if level.lower().startswith(l):
                    level = (i+1)*10
                    break
            logging.getLogger().setLevel( level )

        logging.debug( "configuration files: %r", read )



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
                logging.error( "hook %s failed: %s" % (func.__name__, e) )

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
        root = os.path.dirname( __file__ )

    logfile = os.path.join( root, "log" )
    logging.basicConfig(
            filename=logfile,
            level=logging.DEBUG,
            format="%(levelname)-8s %(message)s"
        )
    sys.stdout = util.CallbackFile(
        writecallback=lambda msg:msg.strip() and logging.info(msg.rstrip())
        )

    bot = IrssiBot( root )
    bot.handle( info )

    logging.info( "quit irssibot" )
    logging.info( "" )

if __name__ == "__main__":
    main()

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

