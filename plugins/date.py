# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

from plugin import IrssiCmdPlugin
from datetime import datetime

class DatePlugin( IrssiCmdPlugin ):

    def handle_command(self, info, sub, params ):
        now = datetime.now()
        self.reply( info, now.ctime() )

    def help(self, info ):
        return "This command displays the current date."

def main( exports ):
    return DatePlugin( "date", "date", exports )


# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

