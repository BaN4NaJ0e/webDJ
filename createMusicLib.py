# coding: utf-8
import os
import re
import sys
import pprint
import sqlite3
import shutil
import eyeD3
import settings
import coverGrabber

fileList = []
coverArtList = []

# get musicfolder name from settings.py 
if len(sys.argv) < 2 :
	print "importing music from folder: " + str(settings.musicfolder)
	rootdir = settings.musicfolder
# or from command line
else:
	print "importing music from folder: " + str(sys.argv[1])
	rootdir = sys.argv[1]

# allowed file extensions
music_extList = [".mp3", ".ogg", ".MP3",".OGG",]

image_extList = [".jpg", ".png", ".JPG",".PNG",]

# scan recursiv through all folders
for root, subFolders, files in os.walk(rootdir):
	for file in files:
		# add music file to fileList
		if os.path.splitext(file)[1] in music_extList :
			fileList.append(os.path.join(root,file))
		# add album folder image to coverArtList
		elif os.path.splitext(file)[1] in image_extList and os.path.splitext(file)[0] == "folder" :
			coverArtList.append(os.path.join(root,file))

# open sqlite db connection
connection = sqlite3.connect("mucke.db")
cursor = connection.cursor()

# delete everything inside the db
cursor.execute("""DROP TABLE IF EXISTS musiclib """)

# Table musiclib columns:
# Pfad / Artist / Title / Album / Tracklaenge / Votes / LastTimeVoted / LastTimePlayed in seconds

cursor.execute("""CREATE TABLE IF NOT EXISTS musiclib ( 
				id INTEGER,
				path TEXT, 
				artist TEXT, 
				title TEXT, album TEXT, 
				albumart TEXT, 
				year TEXT, 
				tracklength INTEGER, 
				votes INTEGER, 
				votetime FLOAT, 
				lastplayed FLOAT)""")

# remember already downloaded cover images from last.fm
# it is only necessary to download the cover for at least one file of every album
coverDictionary = {"artistAndAlbum" : "path"}

# add every musicfile with id3tag information to db
id = 0
for file in fileList :

	tag = eyeD3.Tag()
	try:
		tag.link(file)
	
		if eyeD3.isMp3File(file):
			audioFile = eyeD3.Mp3AudioFile(file)
			
		albumartpath = ""
		
		# prevent that empty tagged music files get into the db
		if tag.getArtist() == "" or tag.getAlbum() == "" or tag.getTitle() == "" :
			continue
			
		# get album cover path and copy all cover images to webserver image folder
		illegalChars = re.compile(r'[\/:*?"<>| ]+',re.U)
		for coverpath in coverArtList :
			if os.path.dirname(file) == os.path.split(coverpath)[0] :
				albumartpath = "images/" + illegalChars.sub(' ',tag.getArtist()) +"_" + illegalChars.sub(' ',tag.getAlbum()) +".jpg"
				try:
					shutil.copy2(coverpath, albumartpath)
				except IOError:
					albumartpath = ""
					print "error copy folderart:\n"+ str(coverpath) +"to\n" +str(albumartpath)
		
		# if no album cover was found localy or other file of same album with same cover was not found
		if albumartpath == "" and (tag.getArtist()+tag.getAlbum()) not in coverDictionary:
			# try to download missing album art from last.fm homepage
			if coverGrabber.downloadAlbumArt(tag.getArtist(),tag.getAlbum()):
				albumartpath = "images/" + illegalChars.sub(' ',tag.getArtist()) +"_" + illegalChars.sub(' ',tag.getAlbum()) +".png"
				newCover = {tag.getArtist()+tag.getAlbum(): albumartpath}
				coverDictionary.update(newCover)
			else:
				# put in placeholder image for tracks with no albumart found on last.fm
				albumartpath = "images/no-album.png"
				newCover = {tag.getArtist()+tag.getAlbum(): albumartpath}
				coverDictionary.update(newCover)
		elif albumartpath == "" and (tag.getArtist()+tag.getAlbum()) in coverDictionary:
			# no local cover found but already downloaded for another file of this album from last.fm
			albumartpath = coverDictionary[tag.getArtist()+tag.getAlbum()]
		else:
			newCover = {tag.getArtist()+tag.getAlbum(): albumartpath}
			coverDictionary.update(newCover)
		
		fileinfos = [id,
			file.decode('utf-8'),
			tag.getArtist(),
			tag.getTitle(),
			tag.getAlbum(),
			albumartpath,
			tag.getYear(),
			audioFile.getPlayTime(),
			0, # number of votes
			0, # votetime
			0] # lasttimeplayed

		sql = "INSERT INTO musiclib VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"	
		cursor.execute(sql, fileinfos)
		id=id+1
	
	except sqlite3.ProgrammingError:
		print ("## sqlite exception adding track:\n" +unicode(tag.getArtist())+ unicode(tag.getTitle())+unicode(tag.getAlbum()) )
	
	except eyeD3.tag.TagException:
		print "## Fehlerhafter id3 Tag:\n" + str(file)
		
	except eyeD3.tag.InvalidAudioFormatException:
		print "## Fehlerhafte mp3 codierung:\n" + str(file)
		
# commit all new entries
connection.commit()

#close db
connection.close()


