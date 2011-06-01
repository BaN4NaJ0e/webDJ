# coding: utf-8
import os
import sys
import pprint
import tagpy
import sqlite3
import shutil

fileList = []
coverArtList = []
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

# Pfad / Artist / Title / Album / Tracklaenge / Votes / LastTimePlayed in seconds

cursor.execute("""CREATE TABLE IF NOT EXISTS musiclib ( 
    		id INTEGER, path TEXT, artist TEXT, title TEXT, album TEXT, albumart TEXT, year TEXT, tracklength INTEGER , votes INTEGER, lastplayed INTEGER)""")

# add every musicfile with id3tag information to db
id = 0
for file in fileList :
    	f = tagpy.FileRef(file)
	albumartpath = ""

	# get album art path
	for coverpath in coverArtList :
    	    if os.path.dirname(file) == os.path.split(coverpath)[0] :
		albumartpath = "images/"+f.tag().artist +"_" +f.tag().album +".jpg"
		#print albumartpath 	        
		shutil.copy2(coverpath, albumartpath)
		break

	# put in placeholder image for tracks with no albumart found		
	if albumartpath == "" :
		albumartpath = "images/no-album.png"

	
	try :
		fileinfos = [id,
		     file.decode('utf-8'),
		     f.tag().artist,
	             f.tag().title,
		     f.tag().album, 
		     albumartpath,
		     f.tag().year,
		     int(f.audioProperties().length),
		     0,
		     0]	

		sql = "INSERT INTO musiclib VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" 	
		cursor.execute(sql, fileinfos)
		id=id+1
	
	except sqlite3.ProgrammingError:
		print ( "fehler: " +unicode(f.tag().artist)+ unicode(f.tag().title)+unicode(f.tag().album) )

# commit all new entries
connection.commit()

# abfragen aller artists ohne doppelte einträge
cursor.execute("""SELECT DISTINCT artist FROM musiclib;""")

print "all artists in database: "
for artist in cursor:
	print(artist[0].encode('latin-1'))

#close db
connection.close()


