# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

from plugin import IrssiCmdPlugin

class EchoCmdPlugin( IrssiCmdPlugin ):

    def handle_command(self, info, sub, params ):
        if params:
            self.reply( info, params )

    def help(self, info):
        return "This command simply replies arguments."

def main( exports ):
    return EchoCmdPlugin( "echo", "echo", exports )

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

