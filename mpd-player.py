import subprocess
import time
import sqlite3

import createSearchTree

currentSongPath = ""
# this should be set in a config file
musicfolder = "/home/hideki/Downloads"

def isNotPlaying():
	output = subprocess.Popen(['mpc'], stdout=subprocess.PIPE).communicate()[0]
	if output.find('playing') > 0:
		return False
	else:
		return True	

def manager():
	while(True):
		getTopVotedSong()

		if currentSongPath != "":
			addSong()
			if isNotPlaying():
				startPlaylist()
		else :
			print "top 10 is empty! waiting for incoming votes"
			time.sleep(5)

def addSong():
	# remove previous top hit in playlist, but keep playing current song
	retcode = subprocess.call(['mpc','-q','crop'])
	# make currentsongpath relative to music folder
	mpdSongPath = currentSongPath.lstrip(musicfolder)
	retcode = subprocess.call(['mpc','-q','add',mpdSongPath])
	currentSongPath = ""

def startPlaylist():
	retcode = subprocess.call(['mpc','-q','play'])


# lookup the song with most votes in database
def getTopVotedSong():
	global currentSongPath
	# open sqlite db connection
	connection = sqlite3.connect("mucke.db")
	cursor = connection.cursor()
	
	# get current top songs
	cursor.execute("""SELECT path FROM musiclib WHERE votes > '0' ORDER BY votes DESC;""")
	topvotesTuple = cursor.fetchall()

	# set number of votes back to 0
	if len(topvotesTuple) != 0:
		t = (topvotesTuple[0])
		cursor.execute("""UPDATE musiclib SET votes= 0 WHERE path==?;""", t )
		connection.commit()

		currentSongPath = str(topvotesTuple[0][0])

	print currentSongPath	
	connection.close()
	# update html top10 list
	createSearchTree.buildHTML()
