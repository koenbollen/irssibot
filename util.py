#!/usr/bin/env python
#

class CallbackFile( object ):
    def __init__(self, writecallback=None, strip=False ):
        self.wbuf = ""
        self.writecallback = writecallback
        self.strip = strip

    def write(self, msg ):
        if self.writecallback:
            if self.strip:
                msg = msg.rstrip()
            self.wbuf += msg
            while "\n" in self.wbuf:
                line, self.wbuf = self.wbuf.split("\n", 1)
                self.writecallback( line )

    def close(self ):
        self.writecallback = None

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

