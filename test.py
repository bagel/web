import sys
import os
import core

def template_test(value):
    environ = {
        "TEMP_PATH": [
            "/data1/www/htdocs/admin.dpool.cluster.sina.com.cn/app/public/template"
        ],
        "APP_PATH": "/data1/www/htdocs/admin.dpool.cluster.sina.com.cn/app/status"
    }
    return core.template(environ, "high.html", value)

def setenv_test():
    environ = {"DOCUMENT_ROOT": "/data1/www/htdocs/admin.dpool.cluster.sina.com.cn"}
    print core.setenv(environ)
    print sys.path


def log_test(s):
    core.log(s)


if __name__ == "__main__":
    print template_test(value)
    #setenv_test()
