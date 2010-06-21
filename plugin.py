# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

import sys
import re

class IrssiPlugin( object ):

    prefix = "[bot] "

    def __init__(self, name, exports ):
        self.name = name
        self.exports = exports
        self.init()

    def init(self ):
        pass

    def reply(self, info, msg ):
        if info['type'] == "pubmsg":
            cmd = "/msg %s %s%s" % (info['target'], self.prefix, msg)
        elif info['type'] == "privmsg":
            cmd = "/msg %s %s%s" % (info['nick'], self.prefix, msg)
        elif info['type'] == "ownmsg":
            cmd = "/msg %s %s%s" % (info['target'], self.prefix, msg)
        else:
            print >>sys.stderr, "unable to reply"
        self.exports['bot'].commands.append( cmd )

    def help(self, info ):
        return "No help availible for '%s'." % self.name

class IrssiCmdPlugin( IrssiPlugin ):

    def __init__(self, name, command, exports ):
        super(IrssiCmdPlugin, self).__init__( name, exports )
        self.command = command
        self.rx = re.compile( r"^!%s([!@#$%%^&*()-_=+?]?)\s*$" % self.command )

        self.exports['bot'].add_hook( self.command, "msg", self.on_msg )

    def on_msg(self, info ):

        if info['msg'].startswith( self.prefix ):
            return

        cmd, params = (info['msg'].split(None, 1)+[None])[:2]

        match = self.rx.match( cmd )
        if match:
            subcmd = match.group(1)
            if subcmd == "?":
                self.reply( info, self.help(info) )
            else:
                self.handle_command( info, subcmd, params )


# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

