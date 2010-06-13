# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

from plugin import IrssiCmdPlugin
import re
import urllib2
from cgi import escape

def title( s ):
    s = s.title()
    s = s.replace( "'T", "'t" )
    s = s.replace( "'S", "'s" )
    s = s.replace( "A ", "a " )
    return s


class ThreeFMCmdPlugin( IrssiCmdPlugin ):

    def nowplaying(self ):
        response = None
        try:
            response = urllib2.urlopen( "http://www.3fm.nl/ajax/nowplaying" )
            data = response.read()
        except IOError, e:
            return "failed"
        finally:
            if response:
                response.close()
        try:
            artist = re.search( "<artist>(.+)</artist>", data ).group(1)
            track  = re.search( "<track>(.+)</track>", data ).group(1)
            return escape(title(artist)) + " - " + escape(title(track))
        except (AttributeError, ValueError, TypeError), e:
            return "failed"

    def handle_command(self, info, sub, params ):
        self.reply( info, self.nowplaying() )

    def help(self, info):
        return "Get the current track of 3FM."

def main( exports ):
    return ThreeFMCmdPlugin( "3fm", "3fm", exports )

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

