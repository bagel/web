import sys
import os
import re
import cStringIO
import yaml

def execute(environ, route, template=""):
    """Eval function by route, route: {"/test": ("test", "response")},
    route's key is url regex. If url match PATH_INFO, then values[0] will
    be imported and values[2] will execute."""
    app_route = ()
    if isinstance(route, dict):
        for k, v in route.iteritems():
            if re.match(re.compile(k), environ['PATH_INFO']):
                app_route = v
                break
    else:
        app_route = route
    if not app_route:
        app_route = route["default"]
    app_route_sp = app_route[0].strip('/').split('/')
    app_module = app_route_sp[-1]
    app_route_sp.remove(app_module)
    app_dir = '/'.join(app_route_sp)
    app_path = os.path.join(environ["DOCUMENT_ROOT"], app_dir)
    if environ["HTTP_HOST"] in sys.path[0]:
        sys.path.pop(0)
    if app_path:
        environ["APP_PATH"] = app_path
    if app_path not in sys.path:
        sys.path.insert(0, app_path)
    if os.path.isdir(template) and template not in environ["TEMP_PATH"]:
        environ["TEMP_PATH"].insert(0, template)
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
        return execute(environ, ("app/public/",))


class _Template(object):
    def __init__(self, environ, tempfile, value={}):
        self.temp_path = self.tempPath(environ)
        self.temp_file = self.tempFile(tempfile)
        self.temp_value = value
        self.environ = environ
        self.tempRegex()

    def tempPath(self, environ):
        """template dirs template under app dir and environ["TEMP_PATH"]"""
        if not environ.has_key("APP_PATH") or not environ["APP_PATH"]:
            return environ["TEMP_PATH"]
        temp_appdir = os.path.join(environ["APP_PATH"], "template")
        if os.path.isdir(temp_appdir):
            environ["TEMP_PATH"].insert(-2, temp_appdir)
        return environ["TEMP_PATH"]

    def tempFile(self, tempfile):
        """find template file from template dirs"""
        temp_file = ''
        print tempfile, self.temp_path
        for path in self.temp_path:
            if os.path.isdir(path) and tempfile in os.listdir(path):
                temp_file = os.path.join(path, tempfile)
                break
        return temp_file

    def tempRegex(self):
        """compile regular expression pattern"""
        signs = "#\$+%"
        self.regex = re.compile('{[%s]+\s*([\w\.]+)\s*[%s]+}' % (signs, signs))
        self.regexInclude = re.compile('{#\s*[\w\.]+\s*#}')
        self.regexDefine = re.compile('{\+\s*\w+\s*\+}')
        self.regexContent = re.compile('{%\s*\w+\s*%}')
        self.regexContentEnd = re.compile('{%\s*end\s*%}')
        self.regexScript = re.compile('<script\s+type="text/python">')
        self.regexScriptEnd = re.compile('</script>')
        self.regexValue = re.compile('({\$\s*\w+\s*\$})')
        self.regexSpace = re.compile('\s+$')

    def tempFind(self, line):
        """find vaule in {# value #}"""
        #return self.regex.sub(r'\1', line).strip() #sub slow
        return self.regex.findall(line)[0].strip()

    def tempExecValue(self, line):
        """replace {$ ... $} with value"""
        vals = self.regexValue.findall(line)
        for v in vals:
            line = line.replace(v, str(self.temp_value[self.tempFind(v)]))
        return line

    def tempExecScript(self, f):
        """execute script in html template"""
        f1 = cStringIO.StringIO()
        f.seek(0, 0)
        line = f.readline()
        dt = line.find(line.strip()[0]) #find first not space in line
        while line:
            if self.regexSpace.match(line[:dt]):
                line = line[dt:]
            if line.strip().split(' ')[0] == 'echo':
                line = line.replace('echo', 'res +=')
            f1.write(line)
            line = f.readline()
        f1.seek(0, 0)
        res = ""
        Tdict = self.temp_value
        exec(f1.read())
        return res

    def tempInclude(self, basefile, f):
        """{% content %} text... {% end %} in f, write text to basefile 
        replace {+ content +}, return basefile"""
        basefile = self.tempFile(basefile)
        f1 = open(basefile, "r")
        line = f1.readline()
        if self.regexInclude.match(line):
            f1 = self.tempInclude(self.tempFind(line), f1)
        f1.seek(0, 0)
        f2 = cStringIO.StringIO()
        contents = {}
        line = f.readline()
        while line: #find all {% ... %} in f
            if self.regexContent.match(line) and not self.regexContentEnd.match(line):
                contents[self.tempFind(line)] = f.tell()
            line = f.readline()
        line = f1.readline()
        while line: #replace {+ ... +} with find {% ... %} before in basefile
            if self.regexDefine.match(line):
                k = self.tempFind(line)
                if contents.has_key(k):
                    f.seek(contents[k], 0)
                    line_new = f.readline()
                    while line_new:
                        if self.regexContentEnd.match(line_new):
                            break
                        f2.write(line_new)
                        line_new = f.readline()
            else:
                f2.write(line)
            line = f1.readline()
        f2.seek(0, 0)
        return f2

    def tempParse(self):
        """parse template html file"""
        content = ""
        f1 = open(self.temp_file, "r")
        line = f1.readline()
        if self.regexInclude.match(line):
            f1 = self.tempInclude(self.tempFind(line), f1)
            line = f1.readline()
        while line:
            if self.regexValue.search(line): #replace value
                line = self.tempExecValue(line)
            if self.regexScript.match(line): #execute script
                f2 = cStringIO.StringIO()
                line = f1.readline()
                while line:
                    if self.regexScriptEnd.match(line):
                        content += self.tempExecScript(f2)
                        line = f1.readline()
                        break
                    f2.write(line)
                    line = f1.readline()
                continue
            content += line
            line = f1.readline()
        return content

def template(environ, tempfile, value={}):
    """find tempfile in template dirs which is defined in environ, 
    parse template with value if given."""
    value.update({"user": environ.get("USER", "")})
    return _Template(environ, tempfile, value).tempParse()


def response(f):
    """response decorator, return status, headers, body to wsgi."""
    def _response(*args, **kwargs):
        headers = {}
        r = f(*args, **kwargs)
        print r
        print f.func_name
        if len(r) == 2:
            ctype, response_body = r
        elif len(r) == 3:
            ctype, response_body, headers = r
        response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
        regex_status = re.compile('Status', re.I)
        status = "200 OK"
        for k, v in headers.iteritems():
            if regex_status.match(k):
                status = v
                continue
            response_headers.append((k, v))
        return (status, response_headers, response_body)
    return _response


