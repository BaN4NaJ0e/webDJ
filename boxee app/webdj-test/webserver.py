import web
import time
from threading import Thread

urls = (
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

class hello:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Hello, ' + name + '!'

#def startserverthread():
#	time.sleep(5)
#	print("stopping server")
#	app.stop()

#sys.argv[1] = '8082'
if __name__ == '__main__' :
	#t = Thread(target=startserverthread, args=())
	#t.start()
	print("starting server")
	app.run()