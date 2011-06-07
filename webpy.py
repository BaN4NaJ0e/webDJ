# coding: utf-8
import web
import createSearchTree
import os
import mpdPlayer
import thread
import votedb
from web.contrib.template import render_cheetah

render = render_cheetah('templates/')

urls = (
	'/', 'index', 
	'/images/(.*)', 'images', 
	'/liked/(.*)', 'liked', 
	'/hated/(.*)', 'hated',
	'/notification/', 'notification',
	'/request/', 'request',
	'/artists/', 'artists',
	'/history/', 'history'
)

app = web.application(urls, globals())

# html page for votes
class liked:
	def POST(self, id):
		userip = web.ctx.ip	
		# user hat fuer einen song gestimmt
		success = createSearchTree.handleVote(id, True, userip )	
		if success:
			raise web.seeother('/')
		else:
			raise web.seeother('/notification/')
				
class hated:
	def POST(self, id):
		userip = web.ctx.ip
		# user hat gegen einen song gestimmt
		success = createSearchTree.handleVote(id, False, userip )
		if success:
			raise web.seeother('/')
		else:
			#user hat schon für den song gestimmt
			raise web.seeother('/notification/')

# user notification (you already voted for this song)
class notification:
	def GET(self):
		return render.notification()

# history page
class history:		
	def GET(self):
		historyHtml = createSearchTree.buildHistory()
		return historyHtml

# index page
class index:		
	def GET(self):
		indexHtml = createSearchTree.buildIndex()
		return indexHtml

# all artists page
class artists:		
	def GET(self):
		urlInput = web.input(artist = '')
		artist = urlInput.artist
		if artist == "":
			requestHtml = createSearchTree.buildArtists()
			return requestHtml
		else:
			requestHtml = createSearchTree.buildAlben(artist)
			return requestHtml

# request song page
class request:		
	def GET(self):
		requestHtml = createSearchTree.buildRequest()
		return requestHtml

# handling images in website (albumart,..)
class images:
	def GET(self,name):
		ext = name.split(".")[-1] # Gather extension

		cType = {
			"png":"images/png",
			"jpg":"image/jpeg",
			"gif":"image/gif",
			"ico":"image/x-icon"	}

		if name in os.listdir('images'):  # Security
			web.header("Content-Type", cType[ext]) # Set the Header
			web.header("Cache-Control", "public")
			web.header("Expires", "Sun, 17 Jan 2038 19:14:07 GMT")
			return open('images/%s'%name,"rb").read() # Notice 'rb' for reading images
		else:
			raise web.notfound()

if __name__ == "__main__":
	# create votes per user count db
	votedb.setupDB()
	#make independant thread for musicplayer	
	thread.start_new_thread(mpdPlayer.manager, ()) 
	app.run()

		




