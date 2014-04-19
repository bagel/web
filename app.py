import sys
import os
import re

def execute(environ, route, template=""):
    """Eval function by route, route: {"/test": ("test", "response")},
    route's key is url regex. If url match PATH_INFO, then values[0] will
    be imported and values[2] will execute."""
    app_route = ()
    for k, v in route.iteritems():
        if re.match(re.compile(k), environ['PATH_INFO']):
            app_route = v
            break
    if not app_route:
        app_route = route["default"]
    app_route_sp = app_route[0].strip('/').split('/')
    app_module = app_route_sp[-1]
    app_route_sp.remove(app_module)
    app_dir = '/'.join(app_route_sp)
    app_path = os.path.join(environ["DOCUMENT_ROOT"], app_dir)
    if environ["HTTP_HOST"] in sys.path[0]:
        sys.path.pop(0)
    if app_path not in sys.path:
        sys.path.insert(0, app_path)
    #modules same name error fix
    #if app_module in sys.modules.keys():
    #    sys.modules.pop(app_module)
    exec('import %s' % app_module)
    app_route_len = len(app_route)
    if app_route_len == 1:
        return eval('%s.urls(environ)' % app_module)
    elif app_route_len == 2:
        if not template:
            if '.' in app_route[1]:
                app_func = app_route[1].replace('.', '(environ).') + '()'
            else:
                app_func = app_route[1] + '(environ)'
        else:
            if '.' in app_route[1]:
                app_func = app_route[1].replace('.', '(environ, template).') + '()'
            else:
                app_func = app_route[1] + '(environ, template)'
        return eval('%s.%s' % (app_module, app_func))
    else:
        return ("text/html", "It works!")

