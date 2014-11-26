import sys
import os
import json
import core
import re


errmsg = {
    "403": "Permission Denied",
    "404": "Not Found",
    "500": "Internal Server Error",
}

def errweb(errno, msg="", trace=""):
    """error return with errno to web visitor"""
    errno = int(errno)
    ctype = "text/plain"
    if not msg:
        msg = errmsg[str(errno)]
    if core.getenv("debug") == 1 and trace:
        return (ctype, msg, {"Status": str(errno), "X-Debug": trace})
    else:
        return (ctype, msg, {"Status": str(errno)})

@core.response
def errweb_response(errno, msg="", trace=""):
    return errweb(errno, msg, trace)

def errapi(errno, msg="", trace=""):
    """error return with errno to api visitor"""
    errno = int(errno)
    ctype = "application/json"
    if not msg:
        msg = errmsg[str(errno)]
    if core.getenv("debug") == 1 and trace:
        return (ctype, json.dumps({"errmsg": msg}), {"Status": str(errno), "X-Debug": trace})
    else:
        return (ctype, json.dumps({"errmsg": msg}), {"Status": str(errno)})

@core.response
def errapi_response(errno, msg="", trace=""):
    return errapi(errno, msg, trace)

def error(errno, msg="", trace=""):
    if re.match("api", os.environ["HTTP_HOST"]):
        return errapi(errno, msg, trace)
    else:
        return errweb(errno, msg, trace)

def error_response(errno, msg="", trace=""):
    if re.match("api", os.environ["HTTP_HOST"]):
        return errapi_response(errno, msg, trace)
    else:
        return errweb_response(errno, msg, trace)

