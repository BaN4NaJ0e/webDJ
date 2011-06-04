# coding: utf-8
import web
import createSearchTree
import os
import mpdPlayer
import thread
import votedb
        

urls = (
    '/', 'index', 
    '/images/(.*)', 'images', 
    '/liked/(.*)', 'liked', 
    '/hated/(.*)', 'hated'
)

app = web.application(urls, globals())

# html page for votes
class liked:
    def POST(self, id):
    	userip = web.ctx.ip	
	# user hat fuer einen song gestimmt
	success = createSearchTree.handleVote(id, True, userip )	
        raise web.seeother('/')
				
class hated:
    def POST(self, id):
        userip = web.ctx.ip
    	# user hat gegen einen song gestimmt
	success = createSearchTree.handleVote(id, False, userip )	
        raise web.seeother('/')
	    		
# index page
class index:        
    def GET(self):
        indexHtml = createSearchTree.buildHTML()
        return indexHtml
		    
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
    # create votes per user count db
    votedb.setupDB()
    #make independant thread for musicplayer    
    thread.start_new_thread(mpdPlayer.manager, ()) 
    app.run()

    	




