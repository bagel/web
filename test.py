import sys
import os
import web

def template_test():
    environ = {
        "TEMP_PATH": [
            "/data1/www/htdocs/admin.dpool.cluster.sina.com.cn/app/public/template"
        ],
        "APP_PATH": "/data1/www/htdocs/admin.dpool.cluster.sina.com.cn/app/info"
    }
    return web.template(environ, "info.html", {"user": ""})


if __name__ == "__main__":
    print template_test()
