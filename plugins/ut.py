# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

from plugin import IrssiCmdPlugin
import socket

class UTCmdPlugin( IrssiCmdPlugin ):

    address = ( "ut.claudia.sara.nl", 7787 )

    def query(self, query ):
        socket.setdefaulttimeout( 1 )
        s = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        nbytes = s.sendto( "\\%s\\" % query, self.address )
        try:
            data, addr = s.recvfrom(4096)
        except socket.timeout:
            return None
        return data

    def info(self ):
        data = self.query( "info" )
        if data is None:
            return None
        fields = data.strip("\\").split( "\\" )
        fields = dict( zip( map( str.lower, fields[::2]), fields[1::2] ) )
        try:
            del fields['queryid']
        except KeyError:
            pass
        return fields

    def players(self ):
        # \player_0\G4U\frags_0\0\ping_0\ 2240\team_0\0
        # \player_1\Nijntje\frags_1\9\ping_1\ 35\team_1\0
        # \queryid\9.1\final\
        data = self.query( "players" )
        if data is None:
            return None
        fields = data.strip("\\").split( "\\" )
        players = {}
        while True:
            name = fields.pop(0)
            if not name or name in ("queryid", "final"):
                break
            value = fields.pop(0)
            name, id = name.split( "_" )
            id = int(id)
            try:
                players[id][name] = value
            except KeyError:
                players[id] = {name:value}
        return players.values()

    def handle_command(self, info, sub, params ):
        server = self.info()
        players = self.players()
        if None in (server, players):
            return self.reply( info, "server unreachable" )
        server['hostname'] = server['hostname'].replace( chr(0xa0), " " )
        s = "playing %s on '%s': " % (server['maptitle'], server['hostname'])
        if len(players) > 0:
            players.sort( key=lambda x: x['frags'], reverse=True )
            pls = []
            for player in players:
                pls.append( "%s(%s)" % (player['player'], player['frags']) )
            s += ", ".join( pls )
        else:
            s += "no players"
        self.reply( info, s )

    def help(self, info):
        return ""

def main( exports ):
    return UTCmdPlugin( "ut", "ut", exports )

# vim: expandtab shiftwidth=4 softtabstop=4 textwidth=79:

