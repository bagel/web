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

def errweb(errno, msg=""):
    """error return with errno to web visitor"""
    errno = int(errno)
    ctype = "text/plain"
    if not msg:
        msg = errmsg[str(errno)]
    return (ctype, msg, {"Status": str(errno)})

@core.response
def errweb_response(errno, msg=""):
    return errweb(errno, msg)

def errapi(errno, msg=""):
    """error return with errno to api visitor"""
    errno = int(errno)
    ctype = "application/json"
    if not msg:
        msg = errmsg[str(errno)]
    return (ctype, json.dumps({"errmsg": msg}), {"Status": str(errno)})

@core.response
def errapi_response(errno, msg=""):
    return errapi(errno, msg)

def error(errno, msg=""):
    if os.environ["HTTP_HOST"] == "api.dpool.cluster.sina.com.cn":
        return errapi(errno, msg)
    else:
        return errweb(errno, msg)

def error_response(errno, msg=""):
    if os.environ["HTTP_HOST"] == "api.dpool.cluster.sina.com.cn":
        return errapi_response(errno, msg)
    else:
        return errweb_response(errno, msg)

