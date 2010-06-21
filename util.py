# Koen Bollen <meneer koenbollen nl>
# 2010 GPL

import logging
from time import time
from functools import wraps

try:
    import cPickle as pickle
except ImportError:
    import pickle

def query( cursor, sql, params=None ):

    logging.debug( "db query: %r, %.20r", sql, params )

    if params is not None:
        cursor.execute( sql, params )
    else:
        cursor.execute( sql )
    return cursor.fetchall()


class Cache( object ):

    def __init__(self, dbc ):
        self.dbc = dbc
        c = self.dbc.cursor()
        sql  = "CREATE TABLE IF NOT EXISTS `cache` (\n"
        sql += "  `key` UNIQUE NOT NULL,\n"
        sql += "  `value` NULL, `ttl`, `time` )\n"
        query( c, sql )
        c.close()
        self.dbc.commit()


    def set(self, key, value, ttl=None ):
        c = self.dbc.cursor()
        sql  = "INSERT OR REPLACE INTO `cache`\n"
        sql += "VALUES (?, ?, ?, ?)\n"
        query( c, sql, (key.lower(), pickle.dumps(value), ttl, time()) )
        c.close()
        self.dbc.commit()

    def get(self, key ):
        c = self.dbc.cursor()
        sql  = "SELECT `value`, `ttl`, `time`\n"
        sql += "FROM `cache` WHERE `key` = ?\n"
        result = query( c, sql, (key.lower(),) )
        c.close()
        if len(result) < 1:
            raise KeyError, "cache key %r not found"%key.lower()
        value, ttl, created = result[0]
        if ttl and created and ttl > 0:
            if time() - created > ttl:
                raise KeyError, "cache entry %r expired"%key.lower()
        return pickle.loads(value.encode("ascii"))

    def safe(self, key, default=None ):
        try:
            return self.get( key )
        except (KeyError, TypeError):
            return default


    def __wrap(self, func, ttl=None ):
        @wraps(func)
        def wrapper( *args ):
            try:
                h = "memoize_%s"%hash(args)
            except:
                return func( *args )
            try:
                value = self.get( h )
            except KeyError:
                value = func( *args )
                self.set( h, value )
        return wrapper

    def memoize(self, func=None, **kwargs ):
        if func:
            return self.__wrap( func )
        def wrapper( func ):
            return self.__wrap( func, ttl=kwargs.get("ttl",3600) )
        return wrapper


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

