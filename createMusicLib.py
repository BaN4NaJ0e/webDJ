# coding: utf-8
import os
import sys
import pprint
import sqlite3
import shutil
import eyeD3
import settings

fileList = []
coverArtList = []

# get musicfolder name from settings.py or from command line
if len(sys.argv) < 2 :
    print "importing music from folder: " + str(settings.musicfolder)
    rootdir = settings.musicfolder
else:
    print "importing music from folder: " + str(sys.argv[1])
    rootdir = sys.argv[1]


music_extList = [".mp3", ".ogg", ".MP3",".OGG",]

image_extList = [".jpg", ".png", ".JPG",".PNG",]

for root, subFolders, files in os.walk(rootdir):
    for file in files:
	if os.path.splitext(file)[1] in music_extList :
          fileList.append(os.path.join(root,file))
	elif os.path.splitext(file)[1] in image_extList and os.path.splitext(file)[0] == "folder" :
          coverArtList.append(os.path.join(root,file))

# open sqlite db connection
connection = sqlite3.connect("mucke.db")
cursor = connection.cursor()

# delete all inside the db
cursor.execute("""DROP TABLE IF EXISTS musiclib """)

# Pfad / Artist / Title / Album / Tracklaenge / Votes / LastTimePlayed in seconds

cursor.execute("""CREATE TABLE IF NOT EXISTS musiclib ( 
    		id INTEGER, path TEXT, artist TEXT, title TEXT, album TEXT, albumart TEXT, year TEXT, tracklength INTEGER , votes INTEGER, votetime FLOAT, lastplayed FLOAT)""")

# add every musicfile with id3tag information to db
id = 0
for file in fileList :

	tag = eyeD3.Tag()
     	tag.link(file)
	if eyeD3.isMp3File(file):
     		audioFile = eyeD3.Mp3AudioFile(file)

	albumartpath = ""

	# get album art path and copy all cover images to webserver folder
	for coverpath in coverArtList :
    	    if os.path.dirname(file) == os.path.split(coverpath)[0] :
		albumartpath = "images/"+tag.getArtist() +"_" +tag.getAlbum() +".jpg"	        
		shutil.copy2(coverpath, albumartpath)
		break

	# put in placeholder image for tracks with no albumart found		
	if albumartpath == "" :
		albumartpath = "images/no-album.png"

	
	try :
		fileinfos = [id,
		     file.decode('utf-8'),
		     tag.getArtist(), 
	         tag.getTitle(),  
		     tag.getAlbum(),  
		     albumartpath,
		     tag.getYear(), 
		     audioFile.getPlayTime(),
		     0,
             0,		
		     0]	

		sql = "INSERT INTO musiclib VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" 	
		cursor.execute(sql, fileinfos)
		id=id+1
	
	except sqlite3.ProgrammingError:
		print ( "fehler: " +unicode(tag.getArtist())+ unicode(tag.getTitle())+unicode(tag.getAlbum()) )

# commit all new entries
connection.commit()

#close db
connection.close()


