# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

from plugin import IrssiCmdPlugin
import urllib2
import os
from BeautifulSoup import BeautifulSoup

class XKCDCmdPlugin( IrssiCmdPlugin ):

    def init(self ):

        self.rgb = {}

        try:
            if os.path.exists( "/tmp/xkcd.rgb.txt" ):
                fp = open( "/tmp/xkcd.rgb.txt" )
                data = fp.read()
                fp.close()
            else:
                res = urllib2.urlopen( "http://xkcd.com/color/rgb.txt" )
                data = res.read()
                res.close()
                fp = open( "/tmp/xkcd.rgb.txt", "wb" )
                fp.write( data )
                fp.close()

            for line in data.splitlines():
                color, value = line.rsplit(None, 1)
                self.rgb[color] = value
        except IOError:
            return

    def xkcd(self, n=None, random=False ):
        url = "http://xkcd.com/"
        if random:
            url = "http://dynamic.xkcd.com/random/comic/"
        elif n is not None:
            url = "http://xkcd.com/%d/" % n
        res = urllib2.urlopen( url )
        data = res.read()
        res.close()
        soup = BeautifulSoup( data )
        h1 = soup.find( "h1" )
        if not h1:
            return None
        title = h1.string

        h3 = soup.find( "h3" );
        if not h3:
            return None
        url = h3.string.split()[-1]
        return title, url


    def handle_command(self, info, sub, params ):
        if sub == "$":
            res = self.xkcd( random=True )
            return self.reply( info, "random XKCD: '%s' (%s)" % res )
        try:
            n = int( params )
            res = self.xkcd( n )
            return self.reply(info, "XKCD #%d: '%s' (%s)" % (n,res[0],res[1]))
        except (TypeError, ValueError):
            pass
        if params is None or len(params.strip()) < 1:
            res = self.xkcd()
            return self.reply( info, "latest XKCD: '%s' (%s)" % res )
        if params.strip() in self.rgb:
            res = False
            return self.reply( info, "XKCD color: %s = %s"%(params,self.rgb[params]))
        return self.reply( info, "XKCD: comic or color not found!" )

    def help(self, info):
        return "Retrieve the latest XKCD title and url (or color). ( random: !xkcd$ )"

def main( exports ):
    return XKCDCmdPlugin( "XKCD", "xkcd", exports )

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

