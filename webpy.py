# coding: utf-8
import web
import createSearchTree
import os
import mpdPlayer
import thread
        

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
		# ToDo: nachschauen ob der track gevoted werden durfte vom user. (max. votes per minutes vom user)
	
		# user hat fuer einen song gestimmt
        print "######## user likes song with id: " + id +" -> " +str( createSearchTree.handleVote(id, True, userip ) )		
        raise web.seeother('/')
				
class hated:
    def POST(self, id):
    	# user gegen einen song gestimmt
		# hate vote in db eintragen
        userip = web.ctx.ip
        print "######## user hates song with id: " + id +" -> " +str( createSearchTree.handleVote(id, False, userip ) )		
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
    #make independant thread for musicplayer    
    thread.start_new_thread(mpdPlayer.manager, ()) 
    app.run()

    	




