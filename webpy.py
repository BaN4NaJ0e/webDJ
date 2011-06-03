# coding: utf-8
import web
import createSearchTree
import os
import mpdPlayer
import thread
        
render = web.template.render('')

urls = (
    '/index/(.*)', 'index', '/images/(.*)', 'images', "/voted/(.*)", "voted"
)
app = web.application(urls, globals())


# page for votes
class voted:
    def GET(self, name):
	# werte den query string hinter dem fragezeichen aus        
	user_data = web.input(like="no data",hate="no data")
	userip = web.ctx.ip
	# ToDo: nachschauen ob der track gevoted werden durfte vom user. (max. votes per minutes vom user)
	
	# user hat fuer einen song gestimmt
	if user_data.like != "no data":
		# like vote in db eintragen
		print "######## user likes song with id: " +user_data.like +" -> " +str( createSearchTree.handleVote(user_data.like, True ) )
		createSearchTree.buildHTML()		
        	return ("""<head>
				<meta http-equiv="refresh" content="3; URL=/index/">
			  </head>
				<h1>You liked track with id: """ + user_data.like + "</h1> <br> Your ip is: """ +userip)
	# user gegen einen song gestimmt
	elif user_data.hate != "no data":
		# hate vote in db eintragen
		print "######## user hates song with id: " +user_data.hate +" -> " +str( createSearchTree.handleVote(user_data.hate, False ) )
		createSearchTree.buildHTML()		
        	return ("""<head>
				<meta http-equiv="refresh" content="3; URL=/index/">
			  </head>
				<h1>You disliked track with id: """ + user_data.hate + "</h1> <br> Your ip is: """ +userip)
	# fehlerfall	
	else:
		return ("""<head>
				<meta http-equiv="refresh" content="3; URL=/index/">
			  </head>
				<h1> error ! going back to index... </h1>""")
# index page
class index:        
    def GET(self, name):
	return render.artists_gen()

# handling images in website (albumart,..)
class images:
    def GET(self,name):
        ext = name.split(".")[-1] # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"            }

        if name in os.listdir('images'):  # Security
            web.header("Content-Type", cType[ext]) # Set the Header
            return open('images/%s'%name,"rb").read() # Notice 'rb' for reading images
        else:
            raise web.notfound()

if __name__ == "__main__":
    createSearchTree.buildHTML()
    #make thread for musicplayer    
    thread.start_new_thread(mpdPlayer.manager, ()) 
    app.run()

    	




