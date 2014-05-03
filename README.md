web
=====

simple and lightweight python web framwork.


#### web.execute

	import web

	route = {
            "default": ("app/public/",),
            "^/(home|profile|util)": ("app/public/",),
            "^/mon/data": ("app/mon/monMain", "Mon.chartData"),
	}

	def urls(environ):
	    return web.execute(environ, route)


