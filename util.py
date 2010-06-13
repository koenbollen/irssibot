#!/usr/bin/env python
#


class CallbackFile( object ):
    def __init__(self, writecallback=None, strip=False ):
        self.writecallback = writecallback
        self.strip = strip

    def write(self, msg ):
        if self.writecallback:
            if self.strip:
                msg = msg.rstrip()
            self.writecallback( msg )

    def close(self ):
        self.writecallback = None

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

