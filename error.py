import sys
import os
import json
import core


@core.response
def errweb(errno):
    """error return with errno to web visitor"""
    errno = int(errno)
    ctype = "text/html"

    if errno == 403:
        return (ctype, "Permission denied", {"Status": str(errno)})
    elif errno == 404:
        return (ctype, "Not found", {"Status": str(errno)})


@core.response
def errapi(errno):
    """error return with errno to api visitor"""
    errno = int(errno)
    ctype = "application/json"

    if errno == 403:
        return (ctype, json.dumps({"errmsg": "Permission denied"}), {"Status": str(errno)})
    elif errno == 404:
        return (ctype, json.dumps({"errmsg": "Not found"}), {"Status": str(errno)})
