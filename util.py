import sys
import os
import yaml
import uwsgi
import time

def initenv(environ, conf="main.yaml"):
    """init environment and conf yaml into uwsgi cache"""
    document_root = environ["DOCUMENT_ROOT"]
    conf_file = os.path.join(document_root, "conf", conf)
    with open(conf_file, 'r') as f:
        envs = yaml.load(f.read())
    for k, v in envs.iteritems():
        uwsgi.cache_set(k, str(v))
    return 0

def setenv(k, v, expires=0):
    """set env use uwsgi.cache_set"""
    return uwsgi.cache_set(k, str(v), expires)

def getenv(k):
    """get env use uwsgi.cache_get"""
    v = uwsgi.cache_get(k)
    try:
        return eval(v, {}, {})
    except:
        return v

def delenv(k):
    """delete env use uwsgi.cache_del"""
    return uwsgi.cache_del(k)

def extenv(k):
    """check exists env use uwsgi.cache_exists"""
    return uwsgi.cache_exists(k)

def cachefunc(expire=600):
    """Cache function f return value in redis with `expire` time."""
    def _cachefunc(f):
        def __cachefunc(*args, **kwargs):
            keys = ["func-", f.func_name]
            keys.extend([ '-%s' % arg for arg in args ])
            keys.extend([ '-%s--%s' % (k, v) for k, v in kwargs.iteritems() ])
            key = ''.join(keys)
            print key
            if not extenv(key):
                print "miss"
                value = f(*args, **kwargs)
                setenv(key, value, expire)
                return value
            else:
                print "hit"
                return getenv(key)
        return __cachefunc
    return _cachefunc


def timefunc(f):
    """print the time that function f run use"""
    def _timefunc(*args, **kwargs):
        t = time.time()
        r = f(*args, **kwargs)
        print "%s: %s" % (f.func_name, time.time() - t)
        return r
    return _timefunc
