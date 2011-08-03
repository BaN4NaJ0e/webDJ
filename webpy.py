# coding: utf-8
import web
import createSearchTree
import os
import mpdPlayer
import thread
import votedb
from web.contrib.template import render_cheetah
from Cheetah.Template import Template
import settings
import adminControls

render = render_cheetah('templates/')


urls = (
	'/', 'index', 
	'/images/(.*)', 'images', 
	'/liked/(.*)', 'liked', 
	'/hated/(.*)', 'hated',
	'/admin/(.*)', 'admin',
	'/notification/', 'notification',
	'/voted/', 'voted',
	'/tracks/', 'tracks',
	'/artists/', 'artists',
	'/login', 'login',
	'/reset', 'reset',
	'/search/', 'search',
	'/history/', 'history'
)

app = web.application(urls, globals())

class login:

	def GET(self):
		return render.login()
		
	def POST(self):
			passwd = web.input().passwd
			try:
				if passwd == settings.pw :
					return render.admin()
				else:
					return	render.login_error()
			except:
				return	render.login_error()

class admin:
	def POST(self, code):
		if code  == "resVotes" :
			adminControls.resetAllVotes()
		elif code == "resLastPlay":
			adminControls.resetLastPlayed()
		else:
			pass
		raise web.seeother('/')


# html page for votes
class liked:
	def POST(self, id):
		userip = web.ctx.ip 
		# user hat fuer einen song gestimmt
		success , time= createSearchTree.handleVote(id, True, userip )
		if success == 0:
			# vote in db eingetragen
			raise web.seeother('/voted/')
		elif success == 1:
			# user hat bereits fuer diesen song gestimmt
			raise web.seeother('/notification/')
		elif success == 2:
			# song ist noch gesperrt
			nameSpace = {'blockover': time, 'minutes': settings.repeatTime }
			t= Template(file="templates/songblocked.html", searchList=[nameSpace])
			return t
				
class hated:
	def POST(self, id):
		userip = web.ctx.ip
		# user hat gegen einen song gestimmt
		success , time = createSearchTree.handleVote(id, False, userip )
		if success == 0:
			# vote in db eingetragen
			raise web.seeother('/voted/')
		elif success == 1:
			# user hat bereits fuer diesen song gestimmt
			raise web.seeother('/notification/')
		elif success == 2:
			# song ist noch gesperrt
			nameSpace = {'blockover': time, 'minutes': settings.repeatTime }
			t= Template(file="templates/songblocked.html", searchList=[nameSpace])
			return t

# user notification (vote was succesfull)
class voted:
	def GET(self):
		return render.voted()
		

# user notification (you already voted for this song)
class notification:
	def GET(self):
		return render.notification()
		
# show all tracks of an album
class tracks:
	def GET(self):
		urlInput = web.input(artist = '', album='')
		artist = urlInput.artist
		album = urlInput.album
		
		if artist == "" or album == "":
			requestHtml = createSearchTree.buildArtists()
			return requestHtml
		else:
			tracksHtml = createSearchTree.buildTracks(album, artist)
			return tracksHtml
		
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
		
# search artist page
class search:		
	def GET(self):
		searchHtml = createSearchTree.buildSearchpage()
		return searchHtml

# handling images in website (albumart,..)
class images:
	def GET(self,name):
		ext = name.split(".")[-1] # Gather extension
		# umlaute in cover pathnames
		name = name.encode('utf-8', 'replace')

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


