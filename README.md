web
=====

simple and lightweight python web framwork.


##core

#### web.execute

	import web

	route = {
            "default": ("app/public/",),
            "^/(home|profile|util)": ("app/public/",),
            "^/mon/data": ("app/mon/monMain", "Mon.chartData"),
	}

	def urls(environ):
	    return web.execute(environ, route)


#### web.template

	web.template(environ, "template.html", value={})


#### web.response

	import web
	
	@web.response
	def response(environ):
	    return ("text/html", "response_body", {"Status": "403", ...})


##util


##error


