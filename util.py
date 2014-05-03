import sys
import os
import time
import core
import logging
import cStringIO

def cachefunc(expire=600):
    """Cache function f return value in uwsgi cache with `expire` time."""
    def _cachefunc(f):
        def __cachefunc(*args, **kwargs):
            keys = ["func-", f.func_name]
            keys.extend([ '-%s' % arg for arg in args ])
            keys.extend([ '-%s--%s' % (k, v) for k, v in kwargs.iteritems() ])
            key = ''.join(keys)
            #print key
            if not core.extenv(key):
                #print "miss"
                value = f(*args, **kwargs)
                core.setenv(key, value, expire)
                return value
            else:
                #print "hit"
                return core.getenv(key)
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

def logfunc(f):
    """log function print and run time to applogs by logging,
    format: `logging time|remote_addr|user|level|function|message|run time`,
    sys.stdout log in INFO level, sys.stderr log in ERROR level,
    """
    def _logfunc(*args, **kwargs):
        applogs_dir = core.getenv("APPLOGS_DIR")
        day = time.strftime("%Y%m%d")
        logfile = os.path.join(applogs_dir, day + '.log')
        logformat = "%(asctime)s|%(clientip)s|%(user)s|%(levelname)s|%(funcname)s|%(message)s|%(rtime)s"
        logging.basicConfig(filename=logfile, format=logformat, 
                            datefmt="%Y/%m/%d %H:%M:%S", level=logging.DEBUG)
        log_info = cStringIO.StringIO()
        stdout_old = sys.stdout
        sys.stdout = log_info
        log_error = cStringIO.StringIO()
        stderr_old = sys.stderr
        sys.stderr = log_error
        t = time.time()
        r = f(*args, **kwargs)
        data = {
            "clientip": os.environ.get("REMOTE_ADDR", "null"),
            "user": os.environ.get("USER", "null"),
            "funcname": f.func_name,
            "rtime": "%dus" % int((time.time() - t) * 1000000),
        }
        error = log_error.getvalue()
        if error:
            logging.error(error.replace('\n', '\\n'), extra=data)
        sys.stderr = stderr_old
        info = log_info.getvalue()
        logging.info(info.replace('\n', '\\n'), extra=data)
        sys.stdout = stdout_old
        return r
    return _logfunc
