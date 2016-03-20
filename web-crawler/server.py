from webcrawler import app
from paste.translogger import TransLogger
from werkzeug.debug import DebuggedApplication

import cherrypy

if __name__ == '__main__':

	# Allow debugging and logging
	app_debug = DebuggedApplication(app, evalex=True)
	app_logged = TransLogger(app_debug)

	# Mount application
	cherrypy.tree.graft(app_logged, "/")

	cherrypy.server.unsubscribe()

	# Create and configure server object
	server = cherrypy._cpserver.Server()
	server.socket_host = "0.0.0.0"
	server.socket_port = 8080
	server.thread_pool = 2

	cherrypy.config.update({
		'engine.autoreload.on': True,
		'log.screen': True,
		'log.error_file': 'error.log',
		'log.access_file': 'access.log'
		})

	server.subscribe()

	cherrypy.engine.start()
	cherrypy.engine.block()
